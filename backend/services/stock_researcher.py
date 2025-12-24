"""
Stock Research Engine
Gathers fundamental, technical, and news data for AI analysis.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yfinance as yf

logger = logging.getLogger(__name__)


class StockResearcher:
    """
    Comprehensive stock research gathering fundamental, technical, and news data.
    Uses yfinance for market data and includes technical indicators.
    """
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=1)
    
    async def research_stock(self, symbol: str) -> Dict:
        """
        Perform comprehensive stock research.
        
        Returns:
            Dict with 'fundamental', 'technical', and 'news' keys
        """
        # Check cache first
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            logger.info(f"📦 Using cached research for {symbol}")
            return self.cache[cache_key]
        
        logger.info(f"🔍 Researching {symbol}...")
        
        # Fetch data
        ticker = yf.Ticker(symbol)
        
        # Gather all research data
        fundamental = await self._get_fundamental_data(ticker)
        technical = await self._get_technical_data(ticker)
        news = await self._get_news_data(ticker)
        
        research = {
            'symbol': symbol,
            'fundamental': fundamental,
            'technical': technical,
            'news': news,
            'timestamp': datetime.now().isoformat()
        }
        
        # Cache results
        self.cache[cache_key] = research
        
        logger.info(f"✅ Research complete for {symbol}")
        return research
    
    async def _get_fundamental_data(self, ticker: yf.Ticker) -> Dict:
        """Get fundamental analysis data"""
        try:
            info = ticker.info
            
            fundamental = {
                'pe_ratio': info.get('forwardPE') or info.get('trailingPE'),
                'eps': info.get('trailingEps'),
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                'debt_to_equity': info.get('debtToEquity'),
                'market_cap': info.get('marketCap'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None,
            }
            
            logger.debug(f"📊 Fundamental data: P/E={fundamental.get('pe_ratio')}, EPS=${fundamental.get('eps')}")
            return fundamental
            
        except Exception as e:
            logger.error(f"❌ Error fetching fundamental data: {e}")
            return {}
    
    async def _get_technical_data(self, ticker: yf.Ticker) -> Dict:
        """Get technical analysis data with indicators"""
        try:
            # Get historical data (6 months for moving averages)
            hist = ticker.history(period='6mo')
            
            if hist.empty:
                logger.warning(f"⚠️ No historical data available")
                return {}
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate technical indicators
            technical = {
                'current_price': round(current_price, 2),
                'rsi': self._calculate_rsi(hist['Close']),
                'macd': self._calculate_macd(hist['Close']),
                'ma_50': self._calculate_ma(hist['Close'], 50),
                'ma_200': self._calculate_ma(hist['Close'], 200),
                'volume_avg': int(hist['Volume'].mean()),
                'volume_current': int(hist['Volume'].iloc[-1]),
                'high_52w': round(hist['High'].max(), 2),
                'low_52w': round(hist['Low'].min(), 2),
            }
            
            # Add price position relative to moving averages
            if technical['ma_50'] and technical['ma_200']:
                technical['above_ma_50'] = current_price > technical['ma_50']
                technical['above_ma_200'] = current_price > technical['ma_200']
                technical['golden_cross'] = technical['ma_50'] > technical['ma_200']
            
            logger.debug(f"📈 Technical data: Price=${technical['current_price']}, RSI={technical.get('rsi')}")
            return technical
            
        except Exception as e:
            logger.error(f"❌ Error fetching technical data: {e}")
            return {}
    
    async def _get_news_data(self, ticker: yf.Ticker) -> List[Dict]:
        """Get recent news with sentiment analysis"""
        try:
            news_items = ticker.news[:10]  # Get last 10 news items
            
            news = []
            for item in news_items:
                news.append({
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': item.get('providerPublishTime', 0),
                    'sentiment': self._analyze_sentiment(item.get('title', ''))
                })
            
            logger.debug(f"📰 Found {len(news)} news items")
            return news
            
        except Exception as e:
            logger.error(f"❌ Error fetching news: {e}")
            return []
    
    def _calculate_rsi(self, prices, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            deltas = prices.diff()
            gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
            loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi.iloc[-1], 2) if not rsi.empty else None
        except:
            return None
    
    def _calculate_macd(self, prices) -> Optional[Dict]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            ema_12 = prices.ewm(span=12, adjust=False).mean()
            ema_26 = prices.ewm(span=26, adjust=False).mean()
            macd_line = ema_12 - ema_26
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': round(macd_line.iloc[-1], 2),
                'signal': round(signal_line.iloc[-1], 2),
                'histogram': round(histogram.iloc[-1], 2),
                'bullish': histogram.iloc[-1] > 0
            }
        except:
            return None
    
    def _calculate_ma(self, prices, period: int) -> Optional[float]:
        """Calculate Moving Average"""
        try:
            if len(prices) < period:
                return None
            ma = prices.rolling(window=period).mean()
            return round(ma.iloc[-1], 2) if not ma.empty else None
        except:
            return None
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Simple keyword-based sentiment analysis.
        TODO: Use proper NLP model in future.
        """
        text_lower = text.lower()
        
        positive_words = ['surge', 'gain', 'soar', 'profit', 'growth', 'beat', 'upgrade', 'strong']
        negative_words = ['fall', 'drop', 'loss', 'decline', 'weak', 'miss', 'downgrade', 'cut']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'


# Singleton instance
_researcher: Optional[StockResearcher] = None


def get_researcher() -> StockResearcher:
    """Get or create singleton researcher instance"""
    global _researcher
    if _researcher is None:
        _researcher = StockResearcher()
        logger.info("✅ Stock Researcher initialized")
    return _researcher
