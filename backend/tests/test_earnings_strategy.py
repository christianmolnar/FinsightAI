"""
Tests for Phase B: Real Earnings Strategy Signals

Verifies that:
1. earnings_data.py fetches real data from yfinance
2. scan_earnings_opportunities() uses real dates/EPS, not proxies
3. Signal filters (days_before, beat_rate, eps_growth) work correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from services.earnings_data import (
    get_next_earnings_date,
    get_days_until_earnings,
    get_historical_beat_rate,
    get_avg_eps_surprise,
    get_eps_growth_yoy,
    is_near_earnings,
)
from services.strategy_executor import StrategyExecutor


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_earnings_df(records: list) -> pd.DataFrame:
    """Build a mock earnings_dates DataFrame like yfinance returns."""
    index = pd.DatetimeIndex([r['date'] for r in records], tz='America/New_York')
    df = pd.DataFrame(
        {
            'EPS Estimate': [r.get('estimate') for r in records],
            'Reported EPS': [r.get('reported') for r in records],
            'Surprise(%)': [r.get('surprise') for r in records],
        },
        index=index,
    )
    df.index.name = 'Earnings Date'
    return df


def make_hist_data(days: int = 100) -> pd.DataFrame:
    """Minimal price DataFrame ending yesterday."""
    idx = pd.date_range(end=date.today() - timedelta(days=1), periods=days, freq='B')
    close = np.linspace(100, 120, days)
    return pd.DataFrame({'Close': close, 'Volume': [1_000_000] * days}, index=idx)


SAMPLE_EARNINGS = make_earnings_df([
    # Future earnings
    {'date': date.today() + timedelta(days=4), 'estimate': 2.0, 'reported': None, 'surprise': None},
    # Past quarters (newest first)
    {'date': date.today() - timedelta(days=90),  'estimate': 1.8, 'reported': 1.95, 'surprise': 8.3},
    {'date': date.today() - timedelta(days=180), 'estimate': 1.7, 'reported': 1.80, 'surprise': 5.9},
    {'date': date.today() - timedelta(days=270), 'estimate': 1.6, 'reported': 1.70, 'surprise': 6.3},
    {'date': date.today() - timedelta(days=360), 'estimate': 1.5, 'reported': 1.55, 'surprise': 3.3},
    {'date': date.today() - timedelta(days=450), 'estimate': 1.4, 'reported': 1.40, 'surprise': 0.0},  # no beat
    {'date': date.today() - timedelta(days=540), 'estimate': 1.3, 'reported': 1.38, 'surprise': 6.2},
])


# ── earnings_data.py unit tests ───────────────────────────────────────────────

def _mock_get_earnings(symbol):
    return SAMPLE_EARNINGS


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_get_next_earnings_date(mock_fetch):
    d = get_next_earnings_date('AAPL', date.today())
    assert d == date.today() + timedelta(days=4)


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_get_days_until_earnings(mock_fetch):
    days = get_days_until_earnings('AAPL', date.today())
    assert days == 4


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_get_historical_beat_rate(mock_fetch):
    rate = get_historical_beat_rate('AAPL', lookback_quarters=6)
    # 5 beats out of 6 past quarters = 83.3%
    assert rate is not None
    assert 80 < rate < 90


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_get_avg_eps_surprise(mock_fetch):
    surprise = get_avg_eps_surprise('AAPL', lookback_quarters=4)
    assert surprise is not None
    assert surprise > 0


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_get_eps_growth_yoy(mock_fetch):
    growth = get_eps_growth_yoy('AAPL', date.today())
    # latest=1.95, year_ago=1.55 → ~25.8% growth
    assert growth is not None
    assert growth > 20


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_is_near_earnings_true(mock_fetch):
    assert is_near_earnings('AAPL', date.today(), days_before=5)


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_is_near_earnings_false(mock_fetch):
    # 4 days away, only looking 2 days ahead
    assert not is_near_earnings('AAPL', date.today(), days_before=2)


# ── StrategyExecutor earnings integration tests ───────────────────────────────

def make_executor(
    days_before=7, min_eps_growth=15, beat_rate=70
) -> StrategyExecutor:
    return StrategyExecutor({
        'earnings': {
            'enabled': True,
            'params': {
                'daysBeforeEarnings': {'value': days_before},
                'minEpsGrowth': {'value': min_eps_growth},
                'minRevenueGrowth': {'value': 10},
                'historicalBeatRate': {'value': beat_rate},
                'profitTarget': {'value': 12},
                'stopLoss': {'value': 5},
                'maxPortfolioWeight': {'value': 20},
            }
        }
    })


import services.earnings_data as _earnings_data_module


@patch('services.earnings_data.get_earnings_dates', side_effect=_mock_get_earnings)
def test_earnings_signal_fires(mock_fetch):
    """Signal fires when all real data conditions are met (using real earnings_data with mocked yfinance)."""
    # Clear cache so our mock actually gets called
    _earnings_data_module._earnings_cache.clear()
    executor = make_executor(days_before=7, beat_rate=70, min_eps_growth=15)
    hist = make_hist_data()
    scan_dt = datetime.combine(date.today(), datetime.min.time())
    result = executor.scan_earnings_opportunities('AAPL', hist, scan_dt, {})
    assert result is not None, f"Expected signal but got None"
    assert result['strategy'] == 'earnings'
    assert result['signal_metadata']['days_until_earnings'] == 4
    assert result['signal_metadata']['beat_rate_pct'] is not None


@patch('services.strategy_executor.get_days_until_earnings', return_value=10)  # outside window
@patch('services.strategy_executor.get_historical_beat_rate', return_value=83.0)
@patch('services.strategy_executor.get_eps_growth_yoy', return_value=25.0)
@patch('services.strategy_executor.get_avg_eps_surprise', return_value=6.2)
def test_earnings_no_signal_outside_window(mock_surprise, mock_growth, mock_beat, mock_days):
    executor = make_executor(days_before=7)
    result = executor.scan_earnings_opportunities('AAPL', make_hist_data(), datetime.now(), {})
    assert result is None


@patch('services.strategy_executor.get_days_until_earnings', return_value=4)
@patch('services.strategy_executor.get_historical_beat_rate', return_value=55.0)  # below 70%
@patch('services.strategy_executor.get_eps_growth_yoy', return_value=25.0)
@patch('services.strategy_executor.get_avg_eps_surprise', return_value=6.2)
def test_earnings_no_signal_low_beat_rate(mock_surprise, mock_growth, mock_beat, mock_days):
    executor = make_executor(beat_rate=70)
    result = executor.scan_earnings_opportunities('AAPL', make_hist_data(), datetime.now(), {})
    assert result is None


@patch('services.strategy_executor.get_days_until_earnings', return_value=4)
@patch('services.strategy_executor.get_historical_beat_rate', return_value=83.0)
@patch('services.strategy_executor.get_eps_growth_yoy', return_value=5.0)  # below 15%
@patch('services.strategy_executor.get_avg_eps_surprise', return_value=6.2)
def test_earnings_no_signal_low_eps_growth(mock_surprise, mock_growth, mock_beat, mock_days):
    executor = make_executor(min_eps_growth=15)
    result = executor.scan_earnings_opportunities('AAPL', make_hist_data(), datetime.now(), {})
    assert result is None


@patch('services.strategy_executor.get_days_until_earnings', return_value=None)  # no upcoming earnings
@patch('services.strategy_executor.get_historical_beat_rate', return_value=83.0)
@patch('services.strategy_executor.get_eps_growth_yoy', return_value=25.0)
@patch('services.strategy_executor.get_avg_eps_surprise', return_value=6.2)
def test_earnings_no_signal_no_upcoming_date(mock_surprise, mock_growth, mock_beat, mock_days):
    executor = make_executor()
    result = executor.scan_earnings_opportunities('AAPL', make_hist_data(), datetime.now(), {})
    assert result is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
