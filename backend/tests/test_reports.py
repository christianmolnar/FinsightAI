"""
Tests for Reports API (Phase F.8)

Calls endpoint functions directly (same pattern as the rest of the suite),
bypassing HTTP to avoid TestClient version incompatibilities.

Tests:
- get_summary()
- get_strategy_history()
- get_paper_vs_live()
"""

import pytest
import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.strategy_variant import StrategyVariant
from app.models.paper_trade import PaperTrade


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """Real DB session; skip if unavailable."""
    try:
        from app.database import SessionLocal
        import sqlalchemy
        session = SessionLocal()
        session.execute(sqlalchemy.text("SELECT 1"))
        yield session
        session.close()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────

USER = "report_test_user"


def make_variant(db, name, mode=None, is_active=False):
    existing = db.query(StrategyVariant).filter(
        StrategyVariant.name == name,
        StrategyVariant.user_id == USER,
    ).count()
    v = StrategyVariant(
        id=str(uuid.uuid4()),
        name=name,
        source="manual",
        user_id=USER,
        version=existing + 1,
        config={"strategies": {}},
        is_active=is_active,
        is_favorite=False,
    )
    if mode is not None:
        v.mode = mode
    if is_active and mode:
        v.activated_at = datetime.utcnow() - timedelta(days=3)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def make_trade(db, variant_id, return_pct, pnl_usd, is_open=False):
    """Create a PaperTrade with explicit return_pct and profit_loss_usd (what reports use)."""
    t = PaperTrade(
        id=str(uuid.uuid4()),
        symbol="AAPL",
        shares=10.0,
        entry_price=100.0,
        position_usd=1000.0,
        exit_price=None if is_open else (100.0 * (1 + return_pct / 100)),
        status="open" if is_open else "closed",
        strategy_variant_id=variant_id,
        return_pct=None if is_open else return_pct,
        profit_loss_usd=None if is_open else pnl_usd,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def cleanup(db):
    db.query(PaperTrade).filter(
        PaperTrade.strategy_variant_id.in_(
            db.query(StrategyVariant.id).filter(StrategyVariant.user_id == USER)
        )
    ).delete(synchronize_session=False)
    db.query(StrategyVariant).filter(StrategyVariant.user_id == USER).delete()
    db.commit()


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestReportsSummary:

    def test_summary_has_expected_keys(self, db):
        from api.reports import get_summary
        result = get_summary(user_id=USER, db=db)
        for key in ("trade_count", "win_rate", "total_pnl", "open_positions",
                    "total_strategy_periods"):
            assert key in result, f"Missing key: {key}"

    def test_summary_trade_count_non_negative(self, db):
        from api.reports import get_summary
        result = get_summary(user_id=USER, db=db)
        assert result["trade_count"] >= 0

    def test_summary_strategy_periods_non_negative(self, db):
        from api.reports import get_summary
        result = get_summary(user_id=USER, db=db)
        assert result["total_strategy_periods"] >= 0

    def test_summary_active_paper_is_str_or_none(self, db):
        from api.reports import get_summary
        result = get_summary(user_id=USER, db=db)
        assert result["active_paper_strategy"] is None or isinstance(result["active_paper_strategy"], str)


class TestStrategyHistory:

    def test_history_is_list(self, db):
        from api.reports import get_strategy_history
        result = get_strategy_history(user_id=USER, db=db)
        assert isinstance(result, list)

    def test_history_entry_has_expected_keys(self, db):
        cleanup(db)
        v = make_variant(db, "HistoryTest", mode="paper", is_active=True)
        make_trade(db, v.id, return_pct=8.5, pnl_usd=85.0)
        make_trade(db, v.id, return_pct=-4.2, pnl_usd=-42.0)

        from api.reports import get_strategy_history
        entries = [e for e in get_strategy_history(user_id=USER, db=db) if e["id"] == v.id]
        assert len(entries) == 1, f"Variant {v.id} not found in history"
        entry = entries[0]

        for key in ("id", "name", "version", "mode", "trade_count", "win_rate",
                    "total_pnl", "is_active"):
            assert key in entry, f"Missing key: {key}"
        cleanup(db)

    def test_history_trade_stats_accurate(self, db):
        cleanup(db)
        v = make_variant(db, "StatsAccuracy", mode="paper", is_active=True)
        make_trade(db, v.id, return_pct=10.0, pnl_usd=100.0)   # win
        make_trade(db, v.id, return_pct=-5.0, pnl_usd=-50.0)   # loss

        from api.reports import get_strategy_history
        entry = next((e for e in get_strategy_history(user_id=USER, db=db) if e["id"] == v.id), None)
        assert entry is not None
        assert entry["trade_count"] == 2
        assert abs(entry["total_pnl"] - 50.0) < 0.01
        assert abs(entry["win_rate"] - 0.5) < 0.01
        cleanup(db)

    def test_history_only_includes_activated_variants(self, db):
        cleanup(db)
        # variant with activated_at = None should NOT appear
        v_unactivated = make_variant(db, "NeverActivated", mode=None, is_active=False)
        v_activated = make_variant(db, "WasActivated", mode="paper", is_active=True)

        from api.reports import get_strategy_history
        ids = [e["id"] for e in get_strategy_history(user_id=USER, db=db)]
        assert v_unactivated.id not in ids
        assert v_activated.id in ids
        cleanup(db)


class TestPaperVsLive:

    def test_paper_vs_live_is_list(self, db):
        from api.reports import get_paper_vs_live
        result = get_paper_vs_live(user_id=USER, db=db)
        assert isinstance(result, list)

    def test_paper_vs_live_entry_keys(self, db):
        cleanup(db)
        name = "PvL_KeyTest"
        vp = make_variant(db, name, mode="paper", is_active=False)
        vl = make_variant(db, name, mode="live", is_active=True)
        vp.activated_at = datetime.utcnow() - timedelta(days=7)
        vl.activated_at = datetime.utcnow() - timedelta(days=2)
        db.commit()
        make_trade(db, vp.id, return_pct=6.0, pnl_usd=60.0)
        make_trade(db, vl.id, return_pct=5.5, pnl_usd=55.0)

        from api.reports import get_paper_vs_live
        rows = get_paper_vs_live(user_id=USER, db=db)
        row = next((r for r in rows if r["strategy_name"] == name), None)
        assert row is not None, "Strategy not found in paper-vs-live"
        for key in ("strategy_name", "has_paper", "has_live", "paper", "live"):
            assert key in row, f"Missing key: {key}"
        assert isinstance(row["paper"], list)
        assert isinstance(row["live"], list)
        cleanup(db)

    def test_paper_vs_live_stats_populated(self, db):
        cleanup(db)
        name = "PvL_StatsTest"
        vp = make_variant(db, name, mode="paper")
        vp.activated_at = datetime.utcnow() - timedelta(days=5)
        db.commit()
        make_trade(db, vp.id, return_pct=12.0, pnl_usd=120.0)
        make_trade(db, vp.id, return_pct=-3.0, pnl_usd=-30.0)

        from api.reports import get_paper_vs_live
        rows = get_paper_vs_live(user_id=USER, db=db)
        row = next((r for r in rows if r["strategy_name"] == name), None)
        assert row is not None
        assert len(row["paper"]) >= 1
        p = row["paper"][0]
        assert "stats" in p
        assert p["stats"]["trade_count"] == 2
        assert abs(p["stats"]["total_pnl"] - 90.0) < 0.01
        cleanup(db)
