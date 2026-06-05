"""
Tests for PaperTradingLoop (Phase E)

Tests guardrail enforcement, entry/exit logic, and performance summary.
Does not require live market data — prices are mocked.
"""

import pytest
import asyncio
import uuid
import sys
import os
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.paper_trading_loop import PaperTradingLoop, DEFAULT_GUARDRAILS


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_mock_proposal(
    symbol="AAPL",
    strategy="earnings",
    ai_score=75,
    entry_price=150.0,
    profit_target_pct=12.0,
    stop_loss_pct=5.0,
    max_portfolio_weight=5.0,
    status="pending",
):
    p = MagicMock()
    p.id = str(uuid.uuid4())
    p.symbol = symbol
    p.strategy = strategy
    p.ai_score = ai_score
    p.entry_price = entry_price
    p.profit_target_pct = profit_target_pct
    p.stop_loss_pct = stop_loss_pct
    p.max_portfolio_weight = max_portfolio_weight
    p.status = status
    p.ai_reasoning = "Strong earnings signal"
    p.signal_metadata = {}
    p.executed_at = None
    p.execution_price = None
    p.rejection_reason = None
    return p


def make_mock_trade(
    symbol="AAPL",
    strategy="earnings",
    entry_price=150.0,
    shares=6.67,
    position_usd=1000.0,
    ai_score=75,
    profit_target_pct=12.0,
    stop_loss_pct=5.0,
    status="open",
    days_ago=3,
):
    t = MagicMock()
    t.id = str(uuid.uuid4())
    t.symbol = symbol
    t.strategy = strategy
    t.entry_price = entry_price
    t.shares = shares
    t.position_usd = position_usd
    t.ai_score = ai_score
    t.profit_target_pct = profit_target_pct
    t.stop_loss_pct = stop_loss_pct
    t.status = status
    t.max_hold_until = datetime.now(timezone.utc) + timedelta(days=7)
    t.return_pct = None
    t.profit_loss_usd = None
    t.exit_price = None
    t.exit_time = None
    t.exit_reason = None
    return t


def make_loop(guardrails=None):
    db = MagicMock()
    db.commit = MagicMock()
    db.add = MagicMock()
    loop = PaperTradingLoop(db=db, guardrails=guardrails, enable_alerts=False)
    return loop, db


# ── Guardrail Tests ───────────────────────────────────────────────────────────

class TestGuardrails:
    @pytest.mark.asyncio
    async def test_rejects_below_min_ai_score(self):
        loop, db = make_loop()
        proposal = make_mock_proposal(ai_score=40)  # Below default 60

        # Mock: no duplicate open position
        db.query.return_value.filter.return_value.first.return_value = None

        executed, reason = await loop._execute_entry(proposal, current_exposure_pct=0)
        assert not executed
        assert "AI score" in reason

    @pytest.mark.asyncio
    async def test_rejects_duplicate_open_position(self):
        loop, db = make_loop()
        proposal = make_mock_proposal(symbol="AAPL", ai_score=80)

        # Mock: existing open trade for AAPL
        mock_existing = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_existing

        executed, reason = await loop._execute_entry(proposal, current_exposure_pct=0)
        assert not executed
        assert "Duplicate" in reason

    @pytest.mark.asyncio
    async def test_rejects_when_exposure_would_exceed_cap(self):
        loop, db = make_loop({"max_portfolio_exposure_pct": 40.0, "max_single_position_pct": 5.0, "paper_portfolio_size": 10000.0})
        proposal = make_mock_proposal(ai_score=80, max_portfolio_weight=5.0)

        # Mock: no duplicate
        db.query.return_value.filter.return_value.first.return_value = None

        # Current exposure already at 38% — adding 5% would exceed 40%
        with patch.object(loop, '_get_current_price', return_value=150.0):
            executed, reason = await loop._execute_entry(proposal, current_exposure_pct=38.0)
        assert not executed
        assert "exposure cap" in reason.lower()

    @pytest.mark.asyncio
    async def test_executes_when_guardrails_pass(self):
        loop, db = make_loop()
        proposal = make_mock_proposal(ai_score=80, max_portfolio_weight=5.0)

        db.query.return_value.filter.return_value.first.return_value = None

        with patch.object(loop, '_get_current_price', return_value=150.0):
            executed, reason = await loop._execute_entry(proposal, current_exposure_pct=0.0)

        assert executed
        assert reason == "executed"
        db.add.assert_called_once()
        db.commit.assert_called()


# ── Exit Logic Tests ──────────────────────────────────────────────────────────

class TestExitLogic:
    @pytest.mark.asyncio
    async def test_closes_on_profit_target(self):
        loop, db = make_loop()
        trade = make_mock_trade(entry_price=100.0, profit_target_pct=12.0)

        # Current price is 115 — 15% above entry, exceeds 12% target
        with patch.object(loop, '_get_current_price', return_value=115.0):
            # Simulate _process_exits manually for a single trade
            db.query.return_value.filter.return_value.all.return_value = [trade]
            closed = await loop._process_exits()

        assert trade.exit_reason == "profit_target"
        assert trade.status == "closed"

    @pytest.mark.asyncio
    async def test_closes_on_stop_loss(self):
        loop, db = make_loop()
        trade = make_mock_trade(entry_price=100.0, stop_loss_pct=5.0)

        # Current price is 93 — 7% drop, exceeds 5% stop
        with patch.object(loop, '_get_current_price', return_value=93.0):
            db.query.return_value.filter.return_value.all.return_value = [trade]
            closed = await loop._process_exits()

        assert trade.exit_reason == "stop_loss"
        assert trade.status == "closed"

    @pytest.mark.asyncio
    async def test_closes_on_max_hold_expiry(self):
        loop, db = make_loop()
        trade = make_mock_trade(entry_price=100.0, profit_target_pct=20.0, stop_loss_pct=10.0)
        # Set max_hold_until in the past
        trade.max_hold_until = datetime.now(timezone.utc) - timedelta(hours=1)

        with patch.object(loop, '_get_current_price', return_value=105.0):
            db.query.return_value.filter.return_value.all.return_value = [trade]
            closed = await loop._process_exits()

        assert trade.exit_reason == "max_hold_expired"

    @pytest.mark.asyncio
    async def test_does_not_close_within_range(self):
        loop, db = make_loop()
        trade = make_mock_trade(entry_price=100.0, profit_target_pct=12.0, stop_loss_pct=5.0)

        # Price at +3% — not at target or stop
        with patch.object(loop, '_get_current_price', return_value=103.0):
            db.query.return_value.filter.return_value.all.return_value = [trade]
            closed = await loop._process_exits()

        assert trade.status == "open"
        assert closed == 0


# ── Performance Summary Tests ─────────────────────────────────────────────────

class TestPerformanceSummary:
    def _make_closed_trade(self, symbol, strategy, return_pct, position_usd=1000.0):
        t = MagicMock()
        t.symbol = symbol
        t.strategy = strategy
        t.return_pct = return_pct
        t.profit_loss_usd = position_usd * return_pct / 100
        t.status = "closed"
        return t

    def test_win_rate_calculation(self):
        loop, db = make_loop()
        trades = [
            self._make_closed_trade("A", "earnings", 10.0),
            self._make_closed_trade("B", "earnings", 8.0),
            self._make_closed_trade("C", "macro", -4.0),
            self._make_closed_trade("D", "earnings", 5.0),
        ]
        db.query.return_value.filter.return_value.all.return_value = trades

        summary = loop.get_performance_summary()
        assert summary["total_trades"] == 4
        assert summary["wins"] == 3
        assert summary["win_rate_pct"] == 75.0

    def test_total_pnl_calculated(self):
        loop, db = make_loop()
        trades = [
            self._make_closed_trade("A", "earnings", 10.0, 1000),  # +$100
            self._make_closed_trade("B", "earnings", -5.0, 1000),  # -$50
        ]
        db.query.return_value.filter.return_value.all.return_value = trades

        summary = loop.get_performance_summary()
        assert summary["total_return_usd"] == pytest.approx(50.0, abs=0.01)

    def test_empty_trades_returns_zeros(self):
        loop, db = make_loop()
        db.query.return_value.filter.return_value.all.return_value = []

        summary = loop.get_performance_summary()
        assert summary["total_trades"] == 0

    def test_by_strategy_breakdown(self):
        loop, db = make_loop()
        trades = [
            self._make_closed_trade("A", "earnings", 12.0),
            self._make_closed_trade("B", "earnings", 8.0),
            self._make_closed_trade("C", "seasonality", 15.0),
        ]
        db.query.return_value.filter.return_value.all.return_value = trades

        summary = loop.get_performance_summary()
        assert "earnings" in summary["by_strategy"]
        assert "seasonality" in summary["by_strategy"]
        assert summary["by_strategy"]["earnings"]["count"] == 2


# ── Default Guardrails Test ───────────────────────────────────────────────────

class TestDefaultGuardrails:
    def test_all_required_keys_present(self):
        required = [
            "max_single_position_pct",
            "max_portfolio_exposure_pct",
            "max_daily_trades",
            "min_ai_score",
            "max_hold_days",
            "paper_portfolio_size",
        ]
        for key in required:
            assert key in DEFAULT_GUARDRAILS, f"Missing guardrail: {key}"

    def test_guardrails_override(self):
        loop, _ = make_loop({"min_ai_score": 80, "max_daily_trades": 3})
        assert loop.guardrails["min_ai_score"] == 80
        assert loop.guardrails["max_daily_trades"] == 3
        # Other keys still have defaults
        assert loop.guardrails["max_hold_days"] == DEFAULT_GUARDRAILS["max_hold_days"]
