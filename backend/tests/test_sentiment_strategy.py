"""
Tests for sentiment strategy in StrategyExecutor.

All yfinance calls are mocked via get_sentiment_snapshot to keep tests fast and offline.
"""

import pytest
from unittest.mock import patch
from datetime import datetime
import pandas as pd
import numpy as np

from services.strategy_executor import StrategyExecutor

# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_hist(price=150.0, volume=2_000_000, days=60):
    dates = pd.date_range(end='2025-06-15', periods=days, freq='B')
    closes = np.linspace(price * 0.9, price, days)
    return pd.DataFrame({
        'Close': closes,
        'Open':  closes * 0.99,
        'High':  closes * 1.01,
        'Low':   closes * 0.98,
        'Volume': [volume] * days,
    }, index=dates)


def _make_config(enabled=True, min_score=0.2, min_pos_ratio=0.4, min_articles=3):
    return {
        'earnings':   {'enabled': False, 'params': {}},
        'seasonality': {'enabled': False, 'params': {}},
        'macro':      {'enabled': False, 'params': {}},
        'sentiment': {
            'enabled': enabled,
            'params': {
                'minSentimentScore': {'value': min_score},
                'minPositiveRatio':  {'value': min_pos_ratio},
                'minArticles':       {'value': min_articles},
                'profitTarget':      {'value': 15},
                'stopLoss':          {'value': 7},
                'maxPortfolioWeight':{'value': 10},
            },
        },
    }


_POSITIVE_SNAPSHOT = {
    'symbol': 'AAPL',
    'total_articles': 8,
    'positive': 6,
    'negative': 1,
    'neutral': 1,
    'sentiment_score': 0.625,   # (6-1)/8
    'positive_ratio': 0.75,
    'headlines': [
        {'title': 'Apple surges to record high', 'publisher': 'Reuters',
         'published': 0, 'sentiment': 'positive'},
        {'title': 'Strong iPhone sales beat estimates', 'publisher': 'CNBC',
         'published': 0, 'sentiment': 'positive'},
        {'title': 'Analysts raise AAPL price target', 'publisher': 'Barrons',
         'published': 0, 'sentiment': 'positive'},
    ],
    'fetched_at': '2025-06-15T12:00:00',
}

_NEGATIVE_SNAPSHOT = {
    'symbol': 'AAPL',
    'total_articles': 7,
    'positive': 1,
    'negative': 5,
    'neutral': 1,
    'sentiment_score': -0.571,
    'positive_ratio': 0.143,
    'headlines': [],
    'fetched_at': '2025-06-15T12:00:00',
}

_THIN_SNAPSHOT = {
    'symbol': 'AAPL',
    'total_articles': 2,       # below minArticles=3
    'positive': 2,
    'negative': 0,
    'neutral': 0,
    'sentiment_score': 1.0,
    'positive_ratio': 1.0,
    'headlines': [],
    'fetched_at': '2025-06-15T12:00:00',
}

_BACKTEST_SNAPSHOT = {
    'symbol': 'AAPL',
    'total_articles': 0,
    'positive': 0, 'negative': 0, 'neutral': 0,
    'sentiment_score': 0.0,
    'positive_ratio': 0.0,
    'headlines': [],
    'fetched_at': '2025-06-15T12:00:00',
    'backtest_placeholder': True,
}

SCAN_DATE = datetime(2025, 6, 15)
HIST = _make_hist()


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestSentimentStrategyDisabled:
    def test_returns_none_when_disabled(self):
        cfg = _make_config(enabled=False)
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is None


class TestSentimentStrategyPositive:
    def test_triggers_on_positive_sentiment(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is not None
        assert result['strategy'] == 'sentiment'
        assert result['symbol'] == 'AAPL'

    def test_score_is_within_bounds(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert 0 <= result['score'] <= 100

    def test_signal_metadata_populated(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        meta = result['signal_metadata']
        assert meta['sentiment_score'] == pytest.approx(0.625)
        assert meta['total_articles'] == 8
        assert meta['positive'] == 6
        assert len(meta['top_headlines']) <= 3

    def test_exit_params_present(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        ep = result['exit_params']
        assert ep['profit_target'] == 15
        assert ep['stop_loss'] == 7


class TestSentimentStrategyBlocked:
    def test_blocked_on_negative_sentiment(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_NEGATIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is None

    def test_blocked_on_too_few_articles(self):
        cfg = _make_config(min_articles=3)
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_THIN_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is None

    def test_blocked_in_backtest_mode(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_BACKTEST_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is None

    def test_blocked_below_min_score_threshold(self):
        cfg = _make_config(min_score=0.7)   # tighter threshold than snapshot's 0.625
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            result = executor.scan_sentiment_opportunities('AAPL', HIST, SCAN_DATE, {})
        assert result is None


class TestSentimentInScanAll:
    def test_sentiment_included_in_scan_all(self):
        cfg = _make_config()
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            opps = executor.scan_all_strategies('AAPL', HIST, SCAN_DATE)
        strategies = [o['strategy'] for o in opps]
        assert 'sentiment' in strategies

    def test_scan_all_no_sentiment_when_disabled(self):
        cfg = _make_config(enabled=False)
        executor = StrategyExecutor(cfg)
        with patch('services.strategy_executor.get_sentiment_snapshot',
                   return_value=_POSITIVE_SNAPSHOT):
            opps = executor.scan_all_strategies('AAPL', HIST, SCAN_DATE)
        strategies = [o['strategy'] for o in opps]
        assert 'sentiment' not in strategies
