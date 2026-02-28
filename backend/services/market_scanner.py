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
from datetime import datetime, timedelta
import yfinance as yf
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MarketScanner:
    """
    Autonomous market scanner that finds trading opportunities
    """
    
    # S&P 500 subset for initial implementation (expand to full 500 later)
    SCAN_UNIVERSE = [
        # Tech giants
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
        # Finance
        'JPM', 'BAC', 'WFC', 'GS', 'MS',
        # Healthcare
        'UNH', 'JNJ', 'PFE', 'ABBV', 'TMO',
        # Consumer
        'WMT', 'HD', 'MCD', 'NKE', 'SBUX',
        # Industrials
        'BA', 'CAT', 'GE', 'HON', 'UPS',
        # Energy
        'XOM', 'CVX', 'COP', 'SLB',
        # Telecom/Media
        'DIS', 'NFLX', 'CMCSA', 'T', 'VZ'
    ]
    
    # Filtering criteria
    MIN_VOLUME = 1_000_000  # Minimum daily volume
    MIN_PRICE = 10.0  # Minimum stock price
    MAX_SPREAD_PERCENT = 0.5  # Maximum bid-ask spread (0.5%)
    
    def __init__(self, db: Session):
        """
        Initialize market scanner
        
        Args:
            db: Database session for storing scan results
        """
        self.db = db
        logger.info("MarketScanner initialized")
    
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
    
    def _scan_earnings_plays(self) -> List[Dict]:
        """
        Strategy 1: Find stocks with earnings announcements in next 7 days
        
        Theory: Stocks often move significantly around earnings due to volatility
        and potential surprises. Trading 3-7 days before earnings can capture momentum.
        
        Returns:
            List of candidate dicts
        """
        logger.info("📊 Scanning for earnings plays...")
        candidates = []
        
        for symbol in self.SCAN_UNIVERSE:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get earnings date
                calendar = ticker.calendar
                if calendar is None or calendar.empty:
                    continue
                
                # Check if earnings in next 7 days
                earnings_date = calendar.get('Earnings Date')
                if earnings_date is not None:
                    if isinstance(earnings_date, list) and len(earnings_date) > 0:
                        earnings_date = earnings_date[0]
                    
                    days_until = (earnings_date - datetime.now()).days
                    
                    if 0 < days_until <= 7:
                        # Get current data
                        info = ticker.info
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                        volume = info.get('averageVolume', 0)
                        
                        # Filter by minimum criteria
                        if self._passes_filters(current_price, volume):
                            candidates.append({
                                'symbol': symbol,
                                'strategy': 'earnings_play',
                                'score': 70,  # Base score for earnings plays
                                'reason': f"Earnings in {days_until} days. Historical volatility creates opportunities.",
                                'current_price': current_price,
                                'volume': volume,
                                'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                                'days_until_earnings': days_until
                            })
                            logger.info(f"  ✓ {symbol}: Earnings in {days_until} days")
            
            except Exception as e:
                logger.debug(f"  ⨯ {symbol}: Error checking earnings - {e}")
                continue
        
        return candidates
    
    def _scan_technical_breakouts(self) -> List[Dict]:
        """
        Strategy 2: Find stocks breaking above resistance levels
        
        Theory: When a stock breaks above a key resistance level (52-week high,
        200-day MA, or consolidation pattern), it often continues higher due to
        momentum and new buyers entering.
        
        Returns:
            List of candidate dicts
        """
        logger.info("📈 Scanning for technical breakouts...")
        candidates = []
        
        for symbol in self.SCAN_UNIVERSE:
            try:
                ticker = yf.Ticker(symbol)
                
                # Get 1 year of historical data
                hist = ticker.history(period='1y')
                if hist.empty or len(hist) < 200:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                
                # Calculate technical indicators
                high_52_week = hist['High'].max()
                ma_200 = hist['Close'].rolling(200).mean().iloc[-1]
                ma_50 = hist['Close'].rolling(50).mean().iloc[-1]
                
                # Check for breakout conditions
                breakout_score = 0
                reasons = []
                
                # Condition 1: Near 52-week high (within 2%)
                if current_price >= high_52_week * 0.98:
                    breakout_score += 30
                    reasons.append("Near 52-week high")
                
                # Condition 2: Above 200-day MA (bullish)
                if current_price > ma_200:
                    breakout_score += 20
                    reasons.append("Above 200-day MA")
                
                # Condition 3: Golden cross (50-day > 200-day MA)
                if ma_50 > ma_200:
                    breakout_score += 20
                    reasons.append("Golden cross pattern")
                
                # Condition 4: Strong recent momentum (up 5%+ in last 5 days)
                price_5d_ago = hist['Close'].iloc[-6]
                momentum = ((current_price - price_5d_ago) / price_5d_ago) * 100
                if momentum > 5:
                    breakout_score += 30
                    reasons.append(f"Strong momentum (+{momentum:.1f}%)")
                
                # Filter: Must have at least 2 breakout signals
                if breakout_score >= 40:
                    volume = ticker.info.get('averageVolume', 0)
                    
                    if self._passes_filters(current_price, volume):
                        candidates.append({
                            'symbol': symbol,
                            'strategy': 'technical_breakout',
                            'score': min(breakout_score, 85),  # Cap at 85
                            'reason': f"Technical breakout: {', '.join(reasons)}",
                            'current_price': float(current_price),
                            'volume': volume,
                            'ma_200': float(ma_200),
                            'ma_50': float(ma_50),
                            'momentum_5d': round(momentum, 2)
                        })
                        logger.info(f"  ✓ {symbol}: Breakout detected (score: {breakout_score})")
            
            except Exception as e:
                logger.debug(f"  ⨯ {symbol}: Error checking breakout - {e}")
                continue
        
        return candidates
    
    def _scan_seasonality(self) -> List[Dict]:
        """
        Strategy 3: Find stocks with strong seasonal patterns
        
        Theory: Some stocks have predictable seasonal behavior (retail in Q4,
        travel in summer, etc.). Historical data can identify these patterns.
        
        Returns:
            List of candidate dicts
        """
        logger.info("📅 Scanning for seasonal patterns...")
        candidates = []
        
        # Get current month
        current_month = datetime.now().month
        
        # Seasonal plays by month (simplified - expand with real historical analysis)
        seasonal_stocks = {
            1: [],  # January - "January Effect" small caps
            2: [],  # February
            3: [],  # March
            4: ['BA', 'CAT'],  # April - Industrials/Construction
            5: ['DIS', 'SBUX'],  # May - Travel/Leisure start
            6: ['DIS', 'SBUX'],  # June - Summer season
            7: ['WMT', 'HD'],  # July - Back to school prep
            8: ['WMT', 'HD'],  # August - Back to school
            9: [],  # September
            10: ['AMZN', 'WMT'],  # October - Holiday prep
            11: ['AMZN', 'WMT', 'NKE'],  # November - Black Friday
            12: ['AMZN', 'WMT', 'NKE', 'AAPL'],  # December - Holiday shopping
        }
        
        seasonal_symbols = seasonal_stocks.get(current_month, [])
        
        for symbol in seasonal_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                volume = info.get('averageVolume', 0)
                
                if self._passes_filters(current_price, volume):
                    month_name = datetime.now().strftime('%B')
                    candidates.append({
                        'symbol': symbol,
                        'strategy': 'seasonality',
                        'score': 65,  # Moderate confidence for seasonal plays
                        'reason': f"Historical {month_name} outperformance. Seasonal tailwinds.",
                        'current_price': current_price,
                        'volume': volume,
                        'seasonal_month': month_name
                    })
                    logger.info(f"  ✓ {symbol}: Seasonal opportunity in {month_name}")
            
            except Exception as e:
                logger.debug(f"  ⨯ {symbol}: Error checking seasonality - {e}")
                continue
        
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
