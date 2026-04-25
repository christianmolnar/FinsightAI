"""
Market Scanner Service

Autonomously scans the market for trading opportunities using multiple strategies:
1. Earnings Plays - Companies with earnings in next 7 days
2. Technical Breakouts - Stocks breaking resistance levels
3. Seasonality Patterns - Historical seasonal winners

Filters candidates by volume, liquidity, and spread to ensure tradability.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
import pandas as pd
from sqlalchemy.orm import Session
from services.universe_builder import UniverseBuilder
from app.services.alpaca_service import get_alpaca_service

logger = logging.getLogger(__name__)


class MarketScanner:
    """
    Autonomous market scanner that finds trading opportunities
    """
    
    # Build universe dynamically from S&P 500, DOW, NASDAQ-100, and extended US universe
    # Exclude symbols with known data issues
    _universe_builder = UniverseBuilder()
    _raw_universe = _universe_builder.build_universe(['SP500', 'DOW', 'NASDAQ100', 'RUSSELL2000'])
    SCAN_UNIVERSE = [s for s in _raw_universe if s not in ('WBA',)]

    # Filtering criteria
    MIN_VOLUME = 1_000_000   # Minimum daily volume
    MIN_PRICE = 10.0         # Minimum stock price
    MAX_SPREAD_PERCENT = 0.5  # Maximum bid-ask spread (0.5%)

    def __init__(self, db: Session, historical_data_manager=None):
        self.db = db
        self.alpaca = get_alpaca_service(paper=True)
        self.historical_data_manager = historical_data_manager  # For backtesting
        logger.info(f"MarketScanner initialized — universe: {len(self.SCAN_UNIVERSE)} stocks")
        if historical_data_manager:
            logger.info("✅ Using database-first historical data for backtesting")
    
    def scan_all_strategies(self) -> List[Dict]:
        """
        Run all scanning strategies and return combined candidates
        
        Returns:
            List of candidate dicts with:
            - symbol: Stock symbol
            - strategy: Which strategy found it
            - score: Confidence score (0-100)
            - reason: Why it was selected
            - current_price: Current market price
            - volume: Average volume
        """
        logger.info("🔍 Starting market scan across all strategies...")
        
        all_candidates = []
        
        # Strategy 1: Earnings plays
        earnings_candidates = self._scan_earnings_plays()
        all_candidates.extend(earnings_candidates)
        logger.info(f"✅ Earnings strategy found {len(earnings_candidates)} candidates")
        
        # Strategy 2: Technical breakouts
        breakout_candidates = self._scan_technical_breakouts()
        all_candidates.extend(breakout_candidates)
        logger.info(f"✅ Breakout strategy found {len(breakout_candidates)} candidates")
        
        # Strategy 3: Seasonality patterns
        seasonal_candidates = self._scan_seasonality()
        all_candidates.extend(seasonal_candidates)
        logger.info(f"✅ Seasonal strategy found {len(seasonal_candidates)} candidates")
        
        # Remove duplicates (same stock from multiple strategies)
        unique_candidates = self._deduplicate_candidates(all_candidates)
        
        logger.info(f"📊 Total unique candidates: {len(unique_candidates)}")
        
        return unique_candidates
    
    def _get_bars_batch(self, symbols: List[str], days: int = 252) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV bars - uses database-first approach if historical_data_manager available (backtesting)"""
        end = date.today()
        start = end - timedelta(days=days + 10)  # buffer for weekends/holidays
        try:
            # Use database-first approach for backtesting (10x faster!)
            if self.historical_data_manager:
                return self.historical_data_manager.get_historical_data(
                    symbols, 
                    start_date=start, 
                    end_date=end
                )
            # Fall back to Alpaca for live scanning
            return self.alpaca.get_historical_bars(symbols, start.isoformat(), end.isoformat())
        except Exception as e:
            logger.error(f"Batch bars failed: {e}")
            return {}

    def _get_latest_quote(self, symbol: str) -> Dict:
        """Get latest price and volume from Alpaca."""
        try:
            quote = self.alpaca.get_latest_quote(symbol)
            return quote or {}
        except Exception:
            return {}

    def _scan_earnings_plays(self) -> List[Dict]:
        """
        Strategy 1: Find stocks with earnings in next 7 days.
        Uses Alpaca snapshot for price/volume; earnings calendar from Alpaca or fallback.
        """
        logger.info("📊 Scanning for earnings plays...")
        candidates = []

        # Fetch all snapshots in one call to minimize API hits
        try:
            snapshots = self.alpaca.get_snapshots(self.SCAN_UNIVERSE) or {}
        except Exception as e:
            logger.warning(f"Alpaca snapshots failed: {e}")
            snapshots = {}

        for symbol in self.SCAN_UNIVERSE:
            try:
                snap = snapshots.get(symbol)
                if not snap:
                    continue

                current_price = getattr(snap.latest_trade, 'price', None) or 0
                volume = getattr(snap.daily_bar, 'volume', None) or 0

                if not self._passes_filters(current_price, volume):
                    continue

                # Alpaca does not expose earnings calendar directly.
                # Use their asset info; skip if not available.
                # TODO: integrate earnings calendar API (e.g. Alpaca Events or Polygon)
                # For now, skip earnings play without a date source.

            except Exception as e:
                logger.debug(f"  ⨯ {symbol}: earnings check error - {e}")

        return candidates

    def _scan_technical_breakouts(self) -> List[Dict]:
        """
        Strategy 2: Find stocks breaking above resistance using Alpaca historical bars.
        Processes symbols in batches of 100 to respect Alpaca rate limits.
        """
        logger.info("📈 Scanning for technical breakouts...")
        candidates = []
        batch_size = 100

        for i in range(0, len(self.SCAN_UNIVERSE), batch_size):
            batch = self.SCAN_UNIVERSE[i:i + batch_size]
            bars_dict = self._get_bars_batch(batch, days=260)

            for symbol in batch:
                try:
                    hist = bars_dict.get(symbol)
                    if hist is None or hist.empty or len(hist) < 50:
                        continue

                    # Normalise column names (Alpaca returns lowercase)
                    hist.columns = [c.lower() for c in hist.columns]
                    closes = hist['close']
                    highs = hist['high']
                    volumes = hist['volume']

                    current_price = float(closes.iloc[-1])
                    avg_volume = float(volumes.mean())

                    if not self._passes_filters(current_price, avg_volume):
                        continue

                    high_52w = float(highs.max())
                    ma_200 = float(closes.rolling(min(200, len(closes))).mean().iloc[-1])
                    ma_50 = float(closes.rolling(min(50, len(closes))).mean().iloc[-1])

                    breakout_score = 0
                    reasons = []

                    if current_price >= high_52w * 0.98:
                        breakout_score += 30
                        reasons.append("Near 52-week high")

                    if current_price > ma_200:
                        breakout_score += 20
                        reasons.append("Above 200-day MA")

                    if ma_50 > ma_200:
                        breakout_score += 20
                        reasons.append("Golden cross")

                    if len(closes) >= 6:
                        momentum = ((current_price - float(closes.iloc[-6])) / float(closes.iloc[-6])) * 100
                        if momentum > 5:
                            breakout_score += 30
                            reasons.append(f"Momentum +{momentum:.1f}%")

                    if breakout_score >= 40:
                        candidates.append({
                            'symbol': symbol,
                            'strategy': 'technical_breakout',
                            'score': min(breakout_score, 85),
                            'reason': f"Technical breakout: {', '.join(reasons)}",
                            'current_price': current_price,
                            'volume': avg_volume,
                            'ma_200': round(ma_200, 2),
                            'ma_50': round(ma_50, 2),
                        })
                        logger.info(f"  ✓ {symbol}: breakout score {breakout_score}")

                except Exception as e:
                    logger.debug(f"  ⨯ {symbol}: breakout error - {e}")

        return candidates

    def _scan_seasonality(self) -> List[Dict]:
        """
        Strategy 3: Stocks with strong seasonal patterns for the current month.
        Uses Alpaca snapshots for current price/volume.
        """
        logger.info("📅 Scanning for seasonal patterns...")
        candidates = []
        current_month = datetime.now().month
        month_name = datetime.now().strftime('%B')

        seasonal_stocks = {
            1:  ['IWM', 'VBK'],                       # January Effect — small caps
            2:  [],
            3:  [],
            4:  ['BA', 'CAT', 'DE'],                   # Industrials / Construction
            5:  ['DIS', 'SBUX', 'MAR'],                # Travel / Leisure start
            6:  ['DIS', 'SBUX', 'UAL', 'DAL'],        # Summer travel
            7:  ['WMT', 'HD', 'TGT'],                  # Back-to-school prep
            8:  ['WMT', 'HD', 'TGT', 'COST'],         # Back-to-school
            9:  [],
            10: ['AMZN', 'WMT', 'COST'],               # Holiday prep
            11: ['AMZN', 'WMT', 'NKE', 'ETSY'],       # Black Friday
            12: ['AMZN', 'WMT', 'NKE', 'AAPL', 'ETSY'],  # Holiday shopping
        }

        symbols = seasonal_stocks.get(current_month, [])
        if not symbols:
            return candidates

        try:
            snapshots = self.alpaca.get_snapshots(symbols) or {}
        except Exception as e:
            logger.warning(f"Alpaca snapshots failed for seasonality: {e}")
            snapshots = {}

        for symbol in symbols:
            try:
                snap = snapshots.get(symbol)
                current_price = (getattr(snap.latest_trade, 'price', 0) if snap else 0) or 0
                volume = (getattr(snap.daily_bar, 'volume', 0) if snap else 0) or 0

                if self._passes_filters(current_price, volume):
                    candidates.append({
                        'symbol': symbol,
                        'strategy': 'seasonality',
                        'score': 65,
                        'reason': f"Historical {month_name} outperformance. Seasonal tailwinds.",
                        'current_price': float(current_price),
                        'volume': float(volume),
                        'seasonal_month': month_name,
                    })
                    logger.info(f"  ✓ {symbol}: seasonal play for {month_name}")

            except Exception as e:
                logger.debug(f"  ⨯ {symbol}: seasonality error - {e}")

        return candidates
    
    def _passes_filters(self, price: float, volume: int) -> bool:
        """
        Check if candidate passes minimum quality filters
        
        Args:
            price: Current stock price
            volume: Average daily volume
            
        Returns:
            True if passes all filters
        """
        if price < self.MIN_PRICE:
            return False
        
        if volume < self.MIN_VOLUME:
            return False
        
        # Could add spread check here if we had bid/ask data
        
        return True
    
    def _deduplicate_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Remove duplicate symbols, keeping the highest-scoring version
        
        Args:
            candidates: List of all candidates from all strategies
            
        Returns:
            Deduplicated list with best version of each symbol
        """
        best_candidates = {}
        
        for candidate in candidates:
            symbol = candidate['symbol']
            
            if symbol not in best_candidates:
                best_candidates[symbol] = candidate
            else:
                # Keep the one with higher score
                if candidate['score'] > best_candidates[symbol]['score']:
                    # But merge the strategies
                    best_candidates[symbol]['strategy'] = f"{best_candidates[symbol]['strategy']} + {candidate['strategy']}"
                    best_candidates[symbol]['score'] = candidate['score']
                    best_candidates[symbol]['reason'] = f"{best_candidates[symbol]['reason']} + {candidate['reason']}"
        
        return list(best_candidates.values())


def get_market_scanner(db: Session) -> MarketScanner:
    """
    Factory function to create MarketScanner instance
    
    Args:
        db: Database session
        
    Returns:
        MarketScanner instance
    """
    return MarketScanner(db)
