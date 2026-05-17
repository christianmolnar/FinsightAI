"""
Tests for Phase B: Seasonality Strategy Signals

Verifies that:
1. scan_seasonality_opportunities() computes real monthly patterns from hist_data
2. Signal fires when upcoming month has strong seasonal avg return
3. Signal blocked when insufficient data, pattern too weak, or wrong params
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, datetime, timedelta
import pandas as pd
import numpy as np

from services.strategy_executor import StrategyExecutor


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_executor(weeks_before=3, min_years=3, min_seasonal_return=8) -> StrategyExecutor:
    return StrategyExecutor({
        'seasonality': {
            'enabled': True,
            'params': {
                'weeksBeforePeak': {'value': weeks_before},
                'minHistoricalYears': {'value': min_years},
                'minSeasonalReturn': {'value': min_seasonal_return},
                'profitTarget': {'value': 15},
                'stopLoss': {'value': 7},
                'maxPortfolioWeight': {'value': 15},
            }
        }
    })


def make_hist_data_with_seasonality(
    years: int = 6,
    strong_month: int = 6,   # June has strong returns
    strong_return_pct: float = 12.0,
    base_price: float = 100.0,
) -> pd.DataFrame:
    """
    Build multi-year daily price DataFrame where `strong_month` has
    consistently high returns and other months are flat.
    """
    end = date(date.today().year - 1, 12, 31)
    start = date(end.year - years + 1, 1, 1)
    idx = pd.bdate_range(start=start, end=end)

    closes = []
    price = base_price
    for dt in idx:
        if dt.month == strong_month:
            # Strong month: +strong_return_pct% spread over ~21 trading days
            price *= (1 + (strong_return_pct / 100) / 21)
        else:
            price *= 1.0001  # nearly flat other months
        closes.append(price)

    return pd.DataFrame({'Close': closes, 'Volume': [1_000_000] * len(idx)}, index=idx)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_signal_fires_before_strong_month():
    """Signal fires when scanning 1-2 months before the historically strong month."""
    strong_month = 6  # June is strong
    hist = make_hist_data_with_seasonality(years=6, strong_month=strong_month, strong_return_pct=12.0)
    executor = make_executor(min_years=3, min_seasonal_return=8)

    # Scan in April — June is 2 months away, within the 3-month lookahead
    scan_dt = datetime(date.today().year - 1, 4, 15)
    result = executor.scan_seasonality_opportunities('AAPL', hist, scan_dt, {})

    assert result is not None, "Expected seasonal signal before strong month"
    assert result['strategy'] == 'seasonality'
    assert result['signal_metadata']['peak_month'] == strong_month
    assert result['signal_metadata']['avg_return_pct'] > 8


def test_no_signal_when_disabled():
    """No signal when seasonality strategy is disabled."""
    hist = make_hist_data_with_seasonality(years=6, strong_month=6, strong_return_pct=15.0)
    executor = StrategyExecutor({'seasonality': {'enabled': False, 'params': {}}})
    result = executor.scan_seasonality_opportunities('AAPL', hist, datetime.now(), {})
    assert result is None


def test_no_signal_insufficient_data():
    """No signal when hist_data has fewer years than min_years requires."""
    # Only 1 year of data, but min_years=3 → need 756 bars minimum
    idx = pd.bdate_range(end=date.today() - timedelta(days=1), periods=250)
    hist = pd.DataFrame({'Close': np.linspace(100, 110, 250), 'Volume': [1_000_000] * 250}, index=idx)
    executor = make_executor(min_years=3)
    result = executor.scan_seasonality_opportunities('AAPL', hist, datetime.now(), {})
    assert result is None


def test_no_signal_weak_seasonal_pattern():
    """No signal when upcoming months have weak avg returns (below threshold)."""
    # All months flat — no seasonal edge
    end = date(date.today().year - 1, 12, 31)
    start = date(end.year - 6, 1, 1)
    idx = pd.bdate_range(start=start, end=end)
    closes = [100.0 * (1.00005 ** i) for i in range(len(idx))]  # tiny drift only
    hist = pd.DataFrame({'Close': closes, 'Volume': [1_000_000] * len(idx)}, index=idx)

    executor = make_executor(min_seasonal_return=8)
    scan_dt = datetime(date.today().year - 1, 4, 15)
    result = executor.scan_seasonality_opportunities('AAPL', hist, scan_dt, {})
    assert result is None


def test_signal_metadata_complete():
    """Signal carries full signal_metadata dict."""
    hist = make_hist_data_with_seasonality(years=6, strong_month=6, strong_return_pct=12.0)
    executor = make_executor(min_years=3, min_seasonal_return=8)
    scan_dt = datetime(date.today().year - 1, 4, 15)
    result = executor.scan_seasonality_opportunities('AAPL', hist, scan_dt, {})

    assert result is not None
    meta = result['signal_metadata']
    assert 'peak_month' in meta
    assert 'peak_month_name' in meta
    assert 'avg_return_pct' in meta
    assert 'consistency_pct' in meta
    assert 'years_analyzed' in meta
    assert 'monthly_avg' in meta
    assert len(meta['monthly_avg']) == 12


def test_score_range():
    """Score is within 0-100."""
    hist = make_hist_data_with_seasonality(years=6, strong_month=6, strong_return_pct=20.0)
    executor = make_executor(min_years=3, min_seasonal_return=8)
    scan_dt = datetime(date.today().year - 1, 4, 15)
    result = executor.scan_seasonality_opportunities('AAPL', hist, scan_dt, {})
    assert result is not None
    assert 0 <= result['score'] <= 100


def test_exit_params_present():
    """Exit params are present in result."""
    hist = make_hist_data_with_seasonality(years=6, strong_month=6, strong_return_pct=12.0)
    executor = make_executor()
    scan_dt = datetime(date.today().year - 1, 4, 15)
    result = executor.scan_seasonality_opportunities('AAPL', hist, scan_dt, {})
    assert result is not None
    assert result['exit_params']['profit_target'] == 15
    assert result['exit_params']['stop_loss'] == 7


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
