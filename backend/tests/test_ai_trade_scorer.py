"""
Tests for AITradeScorer (Phase C)

These tests validate scoring behaviour WITHOUT calling live AI APIs,
using monkeypatching to simulate responses.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.ai_trade_scorer import AITradeScorer, get_ai_trade_scorer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EARNINGS_SIGNAL = {
    "symbol": "AAPL",
    "strategy": "earnings",
    "score": 82.0,
    "price": 185.0,
    "reason": "Earnings play: Earnings in 3d, beat rate 80%, EPS growth +22% YoY",
    "signal_metadata": {
        "days_until_earnings": 3,
        "beat_rate_pct": 80.0,
        "eps_growth_yoy_pct": 22.0,
        "avg_eps_surprise_pct": 4.5,
    },
    "params_used": {
        "daysBeforeEarnings": 5,
        "minEpsGrowth": 15,
        "historicalBeatRate": 70,
    },
    "exit_params": {
        "profit_target": 12,
        "stop_loss": 5,
        "max_portfolio_weight": 20,
    },
}

WEAK_SIGNAL = {
    "symbol": "XYZ",
    "strategy": "macro",
    "score": 45.0,
    "price": 50.0,
    "reason": "Macro: VIX 24.8",
    "signal_metadata": {"vix": 24.8, "yield_spread": -0.1},
    "params_used": {"maxVix": 25.0},
    "exit_params": {"profit_target": 15, "stop_loss": 7},
}


def _make_scorer_no_ai() -> AITradeScorer:
    """Return a scorer with no AI client (forces heuristic path)."""
    scorer = AITradeScorer.__new__(AITradeScorer)
    scorer.ai_provider = "fallback"
    scorer._client = None
    scorer._model = None
    return scorer


# ---------------------------------------------------------------------------
# Heuristic fallback tests (no API keys needed)
# ---------------------------------------------------------------------------

class TestHeuristicFallback:

    def test_heuristic_strong_signal_approved(self):
        scorer = _make_scorer_no_ai()
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        assert result["approved"] is True
        assert result["score"] > 60
        assert result["provider"] == "fallback"

    def test_heuristic_weak_signal_rejected(self):
        scorer = _make_scorer_no_ai()
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(WEAK_SIGNAL, threshold=60)
        )
        # 45 * 0.85 = 38 → below 60 → rejected
        assert result["approved"] is False
        assert result["score"] < 60

    def test_heuristic_threshold_boundary(self):
        scorer = _make_scorer_no_ai()
        # score = 70.6 (83 * 0.85) — check at boundary
        signal = dict(EARNINGS_SIGNAL, score=83.0)
        result60 = asyncio.get_event_loop().run_until_complete(
            scorer.score(signal, threshold=60)
        )
        assert result60["approved"] is True

    def test_heuristic_score_capped_at_100(self):
        scorer = _make_scorer_no_ai()
        signal = dict(EARNINGS_SIGNAL, score=200.0)
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(signal, threshold=60)
        )
        assert result["score"] <= 100

    def test_heuristic_score_floored_at_0(self):
        scorer = _make_scorer_no_ai()
        signal = dict(EARNINGS_SIGNAL, score=-50.0)
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(signal, threshold=60)
        )
        assert result["score"] >= 0


# ---------------------------------------------------------------------------
# Mocked Claude tests
# ---------------------------------------------------------------------------

class TestClaudeMockedResponse:

    def _scorer_with_mock_claude(self, mock_text: str) -> AITradeScorer:
        scorer = AITradeScorer.__new__(AITradeScorer)
        scorer.ai_provider = "anthropic"
        scorer._model = "claude-3-haiku-20240307"
        mock_client = MagicMock()
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=mock_text)]
        mock_client.messages.create.return_value = mock_msg
        scorer._client = mock_client
        return scorer

    def test_claude_high_score_approved(self):
        scorer = self._scorer_with_mock_claude('{"score": 78, "reasoning": "Strong setup."}')
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        assert result["score"] == 78
        assert result["approved"] is True
        assert result["reasoning"] == "Strong setup."
        assert result["provider"] == "anthropic"

    def test_claude_low_score_rejected(self):
        scorer = self._scorer_with_mock_claude('{"score": 40, "reasoning": "Weak setup."}')
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        assert result["score"] == 40
        assert result["approved"] is False

    def test_claude_score_clamped_above_100(self):
        scorer = self._scorer_with_mock_claude('{"score": 150, "reasoning": "Too high."}')
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        assert result["score"] == 100

    def test_claude_malformed_json_falls_back_to_neutral(self):
        scorer = self._scorer_with_mock_claude("not json at all")
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        assert result["score"] == 50  # neutral parse-error fallback

    def test_claude_api_exception_uses_heuristic(self):
        scorer = AITradeScorer.__new__(AITradeScorer)
        scorer.ai_provider = "anthropic"
        scorer._model = "claude-3-haiku-20240307"
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API timeout")
        scorer._client = mock_client
        result = asyncio.get_event_loop().run_until_complete(
            scorer.score(EARNINGS_SIGNAL, threshold=60)
        )
        # Should fall through to heuristic, not raise
        assert "score" in result
        assert "approved" in result


# ---------------------------------------------------------------------------
# Singleton tests
# ---------------------------------------------------------------------------

class TestSingleton:

    def test_get_ai_trade_scorer_returns_same_instance(self):
        import services.ai_trade_scorer as module
        module._scorer = None  # reset singleton
        s1 = get_ai_trade_scorer()
        s2 = get_ai_trade_scorer()
        assert s1 is s2

    def test_get_ai_trade_scorer_is_aitradeScorer(self):
        import services.ai_trade_scorer as module
        module._scorer = None
        scorer = get_ai_trade_scorer()
        assert isinstance(scorer, AITradeScorer)
