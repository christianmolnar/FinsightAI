"""
sentiment_data.py — News sentiment fetching and scoring for a single symbol.

Uses yfinance ticker.news (no API key required).
Results are cached per-symbol for 1 hour to avoid hammering the API during batch scans.

Exported:
    get_sentiment_snapshot(symbol, as_of=None) -> dict
"""

import logging
from datetime import datetime, timedelta
from threading import Lock
from typing import Optional

import yfinance as yf

logger = logging.getLogger(__name__)

# ── In-memory cache ────────────────────────────────────────────────────────────
_cache: dict[str, dict] = {}      # symbol -> {'ts': datetime, 'data': dict}
_cache_lock = Lock()
_CACHE_TTL_SECONDS = 3600         # 1-hour TTL

# ── Sentiment keyword lists ────────────────────────────────────────────────────
_POSITIVE_WORDS = [
    'surge', 'gain', 'soar', 'profit', 'growth', 'beat', 'upgrade',
    'strong', 'rally', 'record', 'bullish', 'outperform', 'raise',
    'boost', 'exceed', 'top', 'jump', 'rise', 'high', 'breakout',
]
_NEGATIVE_WORDS = [
    'fall', 'drop', 'loss', 'decline', 'weak', 'miss', 'downgrade',
    'cut', 'sell', 'bearish', 'underperform', 'warn', 'concern',
    'risk', 'low', 'below', 'pressure', 'slump', 'plunge', 'hurt',
]


def _classify(text: str) -> str:
    """Keyword-based headline classifier. Returns 'positive'|'negative'|'neutral'."""
    t = text.lower()
    pos = sum(1 for w in _POSITIVE_WORDS if w in t)
    neg = sum(1 for w in _NEGATIVE_WORDS if w in t)
    if pos > neg:
        return 'positive'
    if neg > pos:
        return 'negative'
    return 'neutral'


def _fetch_news(symbol: str) -> dict:
    """
    Pull up to 10 news headlines for *symbol* from yfinance.
    Returns a scored snapshot dict.
    """
    try:
        ticker = yf.Ticker(symbol)
        raw_news = ticker.news or []
        news_items = raw_news[:10]

        headlines = []
        for item in news_items:
            title = item.get('title', '') or ''
            headlines.append({
                'title': title,
                'publisher': item.get('publisher', ''),
                'published': item.get('providerPublishTime', 0),
                'sentiment': _classify(title),
            })

        total = len(headlines)
        if total == 0:
            return {
                'symbol': symbol,
                'total_articles': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'sentiment_score': 0.0,   # -1.0 … +1.0
                'positive_ratio': 0.0,
                'headlines': [],
                'fetched_at': datetime.utcnow().isoformat(),
            }

        pos_count  = sum(1 for h in headlines if h['sentiment'] == 'positive')
        neg_count  = sum(1 for h in headlines if h['sentiment'] == 'negative')
        neut_count = total - pos_count - neg_count

        # Score: +1 per positive, -1 per negative, normalised to [-1, +1]
        sentiment_score = round((pos_count - neg_count) / total, 3)
        positive_ratio  = round(pos_count / total, 3)

        return {
            'symbol': symbol,
            'total_articles': total,
            'positive': pos_count,
            'negative': neg_count,
            'neutral': neut_count,
            'sentiment_score': sentiment_score,
            'positive_ratio': positive_ratio,
            'headlines': headlines,
            'fetched_at': datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.debug(f"sentiment_data: error fetching {symbol}: {e}")
        return {
            'symbol': symbol,
            'total_articles': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'sentiment_score': 0.0,
            'positive_ratio': 0.0,
            'headlines': [],
            'fetched_at': datetime.utcnow().isoformat(),
            'error': str(e),
        }


def get_sentiment_snapshot(symbol: str, as_of: Optional[datetime] = None) -> dict:
    """
    Return a cached sentiment snapshot for *symbol*.

    *as_of* is accepted for API consistency with other snapshot functions but
    live news cannot be filtered by date — when *as_of* is more than 1 day in the
    past (backtest scenario) we return a neutral placeholder so backtests are not
    polluted by look-ahead bias.

    Cache TTL: 1 hour.
    """
    now = datetime.utcnow()

    # Backtest guard: don't use live news for historical dates
    if as_of is not None:
        as_of_dt = as_of if isinstance(as_of, datetime) else datetime(as_of.year, as_of.month, as_of.day)
        if (now - as_of_dt).total_seconds() > 86400:   # more than 1 day ago
            return {
                'symbol': symbol,
                'total_articles': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'sentiment_score': 0.0,
                'positive_ratio': 0.0,
                'headlines': [],
                'fetched_at': now.isoformat(),
                'backtest_placeholder': True,
            }

    with _cache_lock:
        entry = _cache.get(symbol)
        if entry and (now - entry['ts']).total_seconds() < _CACHE_TTL_SECONDS:
            return entry['data']

    data = _fetch_news(symbol)

    with _cache_lock:
        _cache[symbol] = {'ts': now, 'data': data}

    return data
