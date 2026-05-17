"""
Earnings Data Service

Fetches and caches real earnings data from yfinance.
Used by StrategyExecutor to find actual earnings dates and EPS history.
"""

import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, date, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

# In-memory cache: symbol -> (fetched_at, earnings_df)
_earnings_cache: Dict[str, Tuple[datetime, pd.DataFrame]] = {}
CACHE_TTL_HOURS = 12


def get_earnings_dates(symbol: str) -> Optional[pd.DataFrame]:
    """
    Fetch earnings dates for a symbol, with in-memory caching.
    
    Returns DataFrame with columns:
        EPS Estimate, Reported EPS, Surprise(%)
    Index: Earnings Date (timezone-aware datetime)
    
    Returns None if unavailable.
    """
    now = datetime.now()

    # Return cached data if fresh
    if symbol in _earnings_cache:
        fetched_at, df = _earnings_cache[symbol]
        age_hours = (now - fetched_at).total_seconds() / 3600
        if age_hours < CACHE_TTL_HOURS:
            return df

    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        df = ticker.earnings_dates

        if df is None or df.empty:
            _earnings_cache[symbol] = (now, pd.DataFrame())
            return None

        _earnings_cache[symbol] = (now, df)
        logger.debug(f"   Fetched {len(df)} earnings dates for {symbol}")
        return df

    except Exception as e:
        logger.debug(f"   Could not fetch earnings dates for {symbol}: {e}")
        return None


def get_next_earnings_date(symbol: str, as_of: date) -> Optional[date]:
    """
    Return the next earnings date on or after `as_of`.
    Returns None if no upcoming earnings found.
    """
    df = get_earnings_dates(symbol)
    if df is None or df.empty:
        return None

    future = []
    for idx in df.index:
        # Normalize timezone-aware index to date
        try:
            d = idx.date() if hasattr(idx, 'date') else idx
        except Exception:
            continue
        if d >= as_of:
            future.append(d)

    return min(future) if future else None


def get_days_until_earnings(symbol: str, as_of: date) -> Optional[int]:
    """
    Returns how many calendar days until the next earnings date.
    Returns None if no upcoming earnings found.
    """
    next_date = get_next_earnings_date(symbol, as_of)
    if next_date is None:
        return None
    return (next_date - as_of).days


def get_historical_beat_rate(symbol: str, lookback_quarters: int = 8) -> Optional[float]:
    """
    Calculate historical EPS beat rate over the last N quarters.
    Returns percentage (0-100) or None if insufficient data.
    
    A 'beat' = Reported EPS > EPS Estimate (Surprise % > 0)
    """
    df = get_earnings_dates(symbol)
    if df is None or df.empty:
        return None

    # Only past earnings (has Reported EPS)
    past = df[df['Reported EPS'].notna()].copy()
    if len(past) < 2:
        return None

    # Sort descending, take last N quarters
    past = past.sort_index(ascending=False).head(lookback_quarters)

    beats = (past['Surprise(%)'] > 0).sum()
    beat_rate = (beats / len(past)) * 100
    return float(beat_rate)


def get_avg_eps_surprise(symbol: str, lookback_quarters: int = 4) -> Optional[float]:
    """
    Calculate average EPS surprise % over last N quarters.
    Returns percentage or None if insufficient data.
    """
    df = get_earnings_dates(symbol)
    if df is None or df.empty:
        return None

    past = df[df['Reported EPS'].notna()].copy()
    if len(past) < 2:
        return None

    past = past.sort_index(ascending=False).head(lookback_quarters)
    surprise_pct = past['Surprise(%)'].dropna()

    if surprise_pct.empty:
        return None

    return float(surprise_pct.mean())


def get_eps_growth_yoy(symbol: str, as_of: date) -> Optional[float]:
    """
    Calculate most recent YoY EPS growth (most recent quarter vs same quarter 1 year ago).
    Returns percentage or None if insufficient data.
    """
    df = get_earnings_dates(symbol)
    if df is None or df.empty:
        return None

    past = df[df['Reported EPS'].notna()].copy()
    if len(past) < 5:  # Need at least 5 quarters to compare YoY
        return None

    past = past.sort_index(ascending=False)

    # Most recent reported quarter
    latest_eps = float(past['Reported EPS'].iloc[0])
    # Same quarter one year ago (4 quarters back)
    year_ago_eps = float(past['Reported EPS'].iloc[4])

    if year_ago_eps == 0:
        return None

    growth = ((latest_eps - year_ago_eps) / abs(year_ago_eps)) * 100
    return growth


def is_near_earnings(symbol: str, as_of: date, days_before: int, days_after: int = 1) -> bool:
    """
    Returns True if `as_of` is within `days_before` days before earnings
    or `days_after` days after earnings.
    """
    df = get_earnings_dates(symbol)
    if df is None or df.empty:
        return False

    for idx in df.index:
        try:
            d = idx.date() if hasattr(idx, 'date') else idx
        except Exception:
            continue
        delta = (d - as_of).days
        if -days_after <= delta <= days_before:
            return True

    return False
