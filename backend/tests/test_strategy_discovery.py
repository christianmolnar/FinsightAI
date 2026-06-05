"""
Tests for StrategyDiscovery service (Phase D — Item 3)

Tests pattern extraction and proposal building without calling live AI.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.strategy_discovery import StrategyDiscovery


# ── Fixtures ──────────────────────────────────────────────────────────────────

WINNING_TRADES = [
    {"symbol": "AAPL", "strategy": "earnings", "return_pct": 14.0, "hold_days": 4, "profit_loss": 140, "exit_reason": "profit_target", "signal_metadata": {"days_until_earnings": 3}, "params_used": {}},
    {"symbol": "MSFT", "strategy": "earnings", "return_pct": 10.5, "hold_days": 3, "profit_loss": 105, "exit_reason": "profit_target", "signal_metadata": {"days_until_earnings": 2}, "params_used": {}},
    {"symbol": "NVDA", "strategy": "earnings", "return_pct": 18.2, "hold_days": 5, "profit_loss": 182, "exit_reason": "profit_target", "signal_metadata": {"days_until_earnings": 4}, "params_used": {}},
    {"symbol": "AMD",  "strategy": "earnings", "return_pct": 9.1,  "hold_days": 4, "profit_loss": 91,  "exit_reason": "profit_target", "signal_metadata": {}, "params_used": {}},
    {"symbol": "GOOG", "strategy": "seasonality", "return_pct": 12.0, "hold_days": 20, "profit_loss": 120, "exit_reason": "profit_target", "signal_metadata": {}, "params_used": {}},
    {"symbol": "META", "strategy": "seasonality", "return_pct": 8.5,  "hold_days": 18, "profit_loss": 85,  "exit_reason": "profit_target", "signal_metadata": {}, "params_used": {}},
]

LOSING_TRADES = [
    {"symbol": "TSLA", "strategy": "earnings", "return_pct": -6.0, "hold_days": 4, "profit_loss": -60, "exit_reason": "stop_loss", "signal_metadata": {}, "params_used": {}},
    {"symbol": "NFLX", "strategy": "macro",    "return_pct": -4.5, "hold_days": 7, "profit_loss": -45, "exit_reason": "stop_loss", "signal_metadata": {}, "params_used": {}},
]

ALL_TRADES = WINNING_TRADES + LOSING_TRADES

SAMPLE_CONFIG = {
    "strategy_config": {
        "earnings": {"params": {"profitTarget": {"value": 12}, "stopLoss": {"value": 5}}},
        "seasonality": {"params": {"weeksBeforePeak": {"value": 3}}},
    }
}

SAMPLE_METRICS = {"total_return_pct": 22.4, "win_rate": 75.0, "sharpe_ratio": 1.4}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestPatternExtraction:
    def setup_method(self):
        self.discovery = StrategyDiscovery(db=None, ai_provider="anthropic")

    def test_extracts_strategy_clusters(self):
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        types = [p["type"] for p in patterns]
        assert "strategy_cluster" in types

    def test_extracts_hold_duration_buckets(self):
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        types = [p["type"] for p in patterns]
        assert "hold_duration" in types

    def test_earnings_cluster_has_correct_count(self):
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        earnings = next((p for p in patterns if p.get("strategy") == "earnings"), None)
        assert earnings is not None
        assert earnings["count"] == 4

    def test_avg_return_computed_correctly(self):
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        earnings = next((p for p in patterns if p.get("strategy") == "earnings"), None)
        expected_avg = (14.0 + 10.5 + 18.2 + 9.1) / 4
        assert abs(earnings["avg_return_pct"] - round(expected_avg, 2)) < 0.01

    def test_short_hold_bucket_classified(self):
        """Trades with hold_days < 5 should land in 'short' bucket."""
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        short_bucket = next((p for p in patterns if "short" in p.get("bucket", "")), None)
        assert short_bucket is not None
        assert short_bucket["count"] > 0


class TestHeuristicFallback:
    def setup_method(self):
        self.discovery = StrategyDiscovery(db=None)

    def test_heuristic_returns_best_strategy(self):
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        result = self.discovery._heuristic_analysis(WINNING_TRADES, patterns, SAMPLE_CONFIG)
        assert "summary" in result
        assert "variant_proposals" in result
        assert len(result["variant_proposals"]) > 0

    def test_heuristic_identifies_earnings_as_best(self):
        """Earnings has 4 trades; seasonality has 2 — earnings should be best."""
        patterns = self.discovery._extract_patterns(WINNING_TRADES)
        result = self.discovery._heuristic_analysis(WINNING_TRADES, patterns, SAMPLE_CONFIG)
        assert "earnings" in result["summary"].lower()

    def test_empty_trades_returns_graceful(self):
        result = self.discovery._heuristic_analysis([], [], SAMPLE_CONFIG)
        assert result["variant_proposals"] == []


class TestProposalBuilder:
    def setup_method(self):
        self.discovery = StrategyDiscovery(db=None)

    def test_builds_proposal_from_ai_result(self):
        ai_result = {
            "summary": "Tight earnings plays outperform.",
            "variant_proposals": [
                {
                    "name": "Tight Earnings Momentum",
                    "rationale": "Enter 2-3 days before earnings for less uncertainty.",
                    "param_overrides": {"earnings.daysBeforeEarnings": 3}
                }
            ]
        }
        proposals = self.discovery._build_proposals(ai_result, SAMPLE_CONFIG, WINNING_TRADES)
        assert len(proposals) == 1
        assert proposals[0]["name"] == "Tight Earnings Momentum"
        assert proposals[0]["source"] == "ai_discovery"
        assert "config" in proposals[0]

    def test_param_overrides_applied_to_config(self):
        import copy
        ai_result = {
            "summary": "",
            "variant_proposals": [
                {
                    "name": "Override Test",
                    "rationale": "",
                    "param_overrides": {"earnings.profitTarget": 16}
                }
            ]
        }
        proposals = self.discovery._build_proposals(ai_result, SAMPLE_CONFIG, WINNING_TRADES)
        config = proposals[0]["config"]
        pt = config.get("strategy_config", {}).get("earnings", {}).get("params", {}).get("profitTarget", {})
        assert pt.get("value") == 16

    def test_empty_proposals_handled(self):
        proposals = self.discovery._build_proposals({"variant_proposals": []}, SAMPLE_CONFIG, [])
        assert proposals == []


class TestMinimumTradeGuard:
    def setup_method(self):
        self.discovery = StrategyDiscovery(db=None)

    @pytest.mark.asyncio
    async def test_skips_if_insufficient_winners(self):
        # Only 2 winning trades, min_winning_trades=5
        few_trades = WINNING_TRADES[:2] + LOSING_TRADES
        result = await self.discovery.discover_from_trades(
            trades=few_trades,
            current_config=SAMPLE_CONFIG,
            backtest_metrics=SAMPLE_METRICS,
            min_winning_trades=5,
        )
        assert result["variant_proposals"] == []
        assert "Insufficient" in result["analysis_summary"]

    @pytest.mark.asyncio
    async def test_proceeds_with_enough_winners(self):
        with patch.object(
            StrategyDiscovery,
            "_ai_analyze_patterns",
            return_value={
                "summary": "Test summary.",
                "discovered_patterns": [],
                "variant_proposals": [
                    {"name": "Test Variant", "rationale": "Test", "param_overrides": {}}
                ]
            }
        ):
            result = await self.discovery.discover_from_trades(
                trades=ALL_TRADES,
                current_config=SAMPLE_CONFIG,
                backtest_metrics=SAMPLE_METRICS,
                min_winning_trades=5,
            )
        assert result["winning_trades_analyzed"] == len(WINNING_TRADES)
        assert len(result["variant_proposals"]) == 1
