"""
Macro Data Service — Phase B

Fetches real macro indicators via yfinance:
  - VIX (^VIX): market fear gauge
  - 10Y Treasury yield (^TNX)
  - 2Y Treasury yield (^IRX)
  - Sector ETF performance for rotation signals (XLK, XLE, XLF, XLV, XLI, XLC, XLY, XLP, XLB, XLRE, XLU)

All results cached for 1 hour to avoid hammering Yahoo Finance.
"""

import logging
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)

# 1-hour in-memory cache
_cache: Dict[str, tuple] = {}  # key -> (fetched_at: datetime, value)
CACHE_TTL_HOURS = 1

SECTOR_ETFS = ["XLK", "XLE", "XLF", "XLV", "XLI", "XLC", "XLY", "XLP", "XLB", "XLRE", "XLU"]


def _cached(key: str, fetch_fn):
    """Return cached value or call fetch_fn() and cache result."""
    now = datetime.utcnow()
    if key in _cache:
        fetched_at, value = _cache[key]
        if (now - fetched_at).total_seconds() < CACHE_TTL_HOURS * 3600:
            return value
    value = fetch_fn()
    _cache[key] = (now, value)
    return value


def get_vix(as_of: Optional[datetime] = None) -> Optional[float]:
    """
    Return the most recent VIX close on or before `as_of`.
    Uses today's cached value when as_of is None or today.
    """
    cache_key = f"vix_{(as_of or datetime.utcnow()).date()}"

    def fetch():
        try:
            end = (as_of or datetime.utcnow()) + timedelta(days=1)
            start = end - timedelta(days=10)
            df = yf.download("^VIX", start=start.strftime("%Y-%m-%d"),
                             end=end.strftime("%Y-%m-%d"), progress=False, auto_adjust=True)
            if df.empty:
                return None
            # Filter to on-or-before as_of
            if as_of:
                df = df[df.index <= pd.Timestamp(as_of.date())]
            if df.empty:
                return None
            return float(df["Close"].iloc[-1])
        except Exception as e:
            logger.warning(f"VIX fetch failed: {e}")
            return None

    return _cached(cache_key, fetch)


def get_yield_curve_spread(as_of: Optional[datetime] = None) -> Optional[float]:
    """
    Return 10Y minus 2Y Treasury yield spread (in percentage points).
    Positive = normal curve, Negative = inverted (recessionary signal).
    """
    cache_key = f"yield_spread_{(as_of or datetime.utcnow()).date()}"

    def fetch():
        try:
            end = (as_of or datetime.utcnow()) + timedelta(days=1)
            start = end - timedelta(days=10)
            fmt = "%Y-%m-%d"

            df_10y = yf.download("^TNX", start=start.strftime(fmt),
                                 end=end.strftime(fmt), progress=False, auto_adjust=True)
            df_2y = yf.download("^IRX", start=start.strftime(fmt),
                                end=end.strftime(fmt), progress=False, auto_adjust=True)

            if df_10y.empty or df_2y.empty:
                return None

            if as_of:
                ts = pd.Timestamp(as_of.date())
                df_10y = df_10y[df_10y.index <= ts]
                df_2y = df_2y[df_2y.index <= ts]

            if df_10y.empty or df_2y.empty:
                return None

            ten_y = float(df_10y["Close"].iloc[-1])
            two_y = float(df_2y["Close"].iloc[-1])
            return round(ten_y - two_y, 3)
        except Exception as e:
            logger.warning(f"Yield curve fetch failed: {e}")
            return None

    return _cached(cache_key, fetch)


def get_sector_momentum(lookback_days: int = 20, as_of: Optional[datetime] = None) -> Dict[str, float]:
    """
    Return {ticker: pct_change} for each sector ETF over `lookback_days`.
    Filters to data on-or-before as_of when provided.
    """
    cache_key = f"sector_momentum_{lookback_days}_{(as_of or datetime.utcnow()).date()}"

    def fetch():
        results = {}
        try:
            end = (as_of or datetime.utcnow()) + timedelta(days=1)
            start = end - timedelta(days=lookback_days + 10)
            df = yf.download(
                SECTOR_ETFS,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                progress=False,
                auto_adjust=True,
            )["Close"]

            if as_of:
                df = df[df.index <= pd.Timestamp(as_of.date())]

            if len(df) < 2:
                return results

            # Use last `lookback_days` trading days
            df = df.tail(lookback_days)
            for ticker in SECTOR_ETFS:
                if ticker in df.columns:
                    col = df[ticker].dropna()
                    if len(col) >= 2:
                        pct = ((col.iloc[-1] - col.iloc[0]) / col.iloc[0]) * 100
                        results[ticker] = round(float(pct), 2)
        except Exception as e:
            logger.warning(f"Sector momentum fetch failed: {e}")
        return results

    return _cached(cache_key, fetch)


def get_macro_snapshot(as_of: Optional[datetime] = None) -> Dict:
    """
    Return a single dict with all macro indicators, suitable for passing to scan_macro_opportunities().

    Keys:
        vix: float | None
        yield_spread: float | None          # 10Y - 2Y, pct pts
        sector_momentum: Dict[str, float]   # {ticker: pct_change_20d}
        top_sector: str | None              # strongest sector ETF
        top_sector_return: float | None
    """
    vix = get_vix(as_of)
    spread = get_yield_curve_spread(as_of)
    sector_mom = get_sector_momentum(as_of=as_of)

    top_sector = max(sector_mom, key=sector_mom.get) if sector_mom else None
    top_sector_return = sector_mom.get(top_sector) if top_sector else None

    return {
        "vix": vix,
        "yield_spread": spread,
        "sector_momentum": sector_mom,
        "top_sector": top_sector,
        "top_sector_return": top_sector_return,
    }
