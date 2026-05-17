"""
Tests for Phase B: Macro Strategy Signals

Verifies that:
1. scan_macro_opportunities() fires when VIX is low, yield curve not inverted, sectors positive
2. Signal blocked when VIX too high
3. Signal blocked when yield curve deeply inverted
4. Signal blocked when most sectors negative
5. Signal blocked when macro strategy disabled
6. Signal includes full metadata (vix, yield_spread, sector_momentum)
7. Score range is valid (0-100)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, date
from unittest.mock import patch
import pandas as pd
import numpy as np

from services.strategy_executor import StrategyExecutor


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_executor(max_vix=25, min_yield_spread=-0.5, require_positive_sector=True) -> StrategyExecutor:
    return StrategyExecutor({
        'macro': {
            'enabled': True,
            'params': {
                'maxVix': {'value': max_vix},
                'minYieldSpread': {'value': min_yield_spread},
                'requirePositiveSectorMomentum': {'value': require_positive_sector},
                'profitTarget': {'value': 12},
                'stopLoss': {'value': 6},
                'maxPortfolioWeight': {'value': 10},
            }
        }
    })


def make_hist_data(days=30, price=150.0) -> pd.DataFrame:
    idx = pd.date_range(end=date(2024, 6, 15), periods=days, freq='B')
    return pd.DataFrame({'Close': price, 'Volume': 1_000_000}, index=idx)


GOOD_SNAPSHOT = {
    'vix': 14.0,
    'yield_spread': 0.5,
    'sector_momentum': {
        'XLK': 3.2, 'XLE': 1.5, 'XLF': 2.1, 'XLV': 0.8,
        'XLI': 1.2, 'XLC': 2.5, 'XLY': 3.1, 'XLP': 0.3,
        'XLB': 1.8, 'XLRE': 0.5, 'XLU': -0.2,
    },
    'top_sector': 'XLK',
    'top_sector_return': 3.2,
}

BAD_HIGH_VIX = {**GOOD_SNAPSHOT, 'vix': 32.0}
BAD_INVERTED_CURVE = {**GOOD_SNAPSHOT, 'yield_spread': -1.2}
BAD_SECTORS = {
    **GOOD_SNAPSHOT,
    'sector_momentum': {k: -abs(v) for k, v in GOOD_SNAPSHOT['sector_momentum'].items()},
    'top_sector_return': -0.2,
}

SCAN_DATE = datetime(2024, 6, 15)


# ── Tests ─────────────────────────────────────────────────────────────────────

@patch('services.strategy_executor.get_macro_snapshot', return_value=GOOD_SNAPSHOT)
def test_signal_fires_on_good_macro(mock_snap):
    ex = make_executor()
    hist = make_hist_data()
    result = ex.scan_macro_opportunities('AAPL', hist, SCAN_DATE, {})
    assert result is not None
    assert result['strategy'] == 'macro'
    assert result['symbol'] == 'AAPL'


@patch('services.strategy_executor.get_macro_snapshot', return_value=BAD_HIGH_VIX)
def test_blocked_when_vix_too_high(mock_snap):
    ex = make_executor(max_vix=25)
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is None


@patch('services.strategy_executor.get_macro_snapshot', return_value=BAD_INVERTED_CURVE)
def test_blocked_when_yield_curve_inverted(mock_snap):
    ex = make_executor(min_yield_spread=-0.5)
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is None


@patch('services.strategy_executor.get_macro_snapshot', return_value=BAD_SECTORS)
def test_blocked_when_sectors_mostly_negative(mock_snap):
    ex = make_executor(require_positive_sector=True)
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is None


@patch('services.strategy_executor.get_macro_snapshot', return_value=BAD_SECTORS)
def test_signal_fires_when_sector_check_disabled(mock_snap):
    ex = make_executor(require_positive_sector=False)
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    # VIX and spread are fine in BAD_SECTORS snapshot
    assert result is not None


def test_no_signal_when_disabled():
    ex = StrategyExecutor({'macro': {'enabled': False, 'params': {}}})
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is None


@patch('services.strategy_executor.get_macro_snapshot', return_value=GOOD_SNAPSHOT)
def test_signal_metadata_complete(mock_snap):
    ex = make_executor()
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is not None
    meta = result['signal_metadata']
    assert 'vix' in meta
    assert 'yield_spread' in meta
    assert 'sector_momentum' in meta
    assert 'top_sector' in meta


@patch('services.strategy_executor.get_macro_snapshot', return_value=GOOD_SNAPSHOT)
def test_score_range(mock_snap):
    ex = make_executor()
    result = ex.scan_macro_opportunities('AAPL', make_hist_data(), SCAN_DATE, {})
    assert result is not None
    assert 0 <= result['score'] <= 100
