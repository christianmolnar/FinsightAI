"""
Historical Data Service - Database-First Approach

Provides historical price data from:
1. Railway PostgreSQL database (fast, local cache) - PRIMARY
2. Yahoo Finance API (fallback for missing data) - SECONDARY
3. Alpaca API (fallback for real-time) - TERTIARY

This dramatically speeds up backtesting by avoiding API calls for cached data.
"""

import os
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
import yfinance as yf
import logging

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


class HistoricalDataService:
    """Smart historical data provider with database caching"""
    
    def __init__(self):
        """Initialize with database connection"""
        self.conn = psycopg2.connect(DATABASE_URL)
        logger.info("HistoricalDataService initialized with database connection")
    
    def get_historical_bars(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime,
        timeframe: str = "1Day"
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical bars - database first, then fallback to API
        
        Args:
            symbols: List of stock symbols
            start: Start date
            end: End date  
            timeframe: Bar timeframe (only '1Day' supported from database)
            
        Returns:
            Dict mapping symbol to DataFrame with columns:
            - timestamp: Bar timestamp
            - open, high, low, close, volume
        """
        result = {}
        
        # Only use database for daily bars
        if timeframe == "1Day":
            result = self._get_from_database(symbols, start, end)
            
            # Check for missing symbols
            missing_symbols = [s for s in symbols if s not in result or result[s].empty]
            
            if missing_symbols:
                logger.info(f"Fetching {len(missing_symbols)} missing symbols from Yahoo Finance")
                yahoo_data = self._get_from_yahoo(missing_symbols, start, end)
                result.update(yahoo_data)
        else:
            # For intraday data, must use API (not in database)
            logger.warning(f"Intraday timeframe {timeframe} requested - database only has daily. Use Alpaca for intraday.")
            result = {symbol: pd.DataFrame() for symbol in symbols}
        
        return result
    
    def _get_from_database(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime
    ) -> Dict[str, pd.DataFrame]:
        """Query database for historical data"""
        result = {}
        
        try:
            cur = self.conn.cursor()
            
            # Format dates for SQL
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            
            for symbol in symbols:
                # Query database
                cur.execute("""
                    SELECT date, open, high, low, close, volume
                    FROM historical_prices
                    WHERE symbol = %s
                      AND date >= %s
                      AND date <= %s
                    ORDER BY date ASC
                """, (symbol, start_str, end_str))
                
                rows = cur.fetchall()
                
                if rows:
                    # Convert to DataFrame
                    df = pd.DataFrame(rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df = df.set_index('timestamp')
                    result[symbol] = df
                    logger.debug(f"Database: {symbol} - {len(rows)} bars")
                else:
                    result[symbol] = pd.DataFrame()
                    logger.debug(f"Database: {symbol} - no data")
            
            cur.close()
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            # Return empty DataFrames on error
            result = {symbol: pd.DataFrame() for symbol in symbols}
        
        return result
    
    def _get_from_yahoo(
        self,
        symbols: List[str],
        start: datetime,
        end: datetime
    ) -> Dict[str, pd.DataFrame]:
        """Fallback to Yahoo Finance API"""
        result = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start.strftime("%Y-%m-%d"),
                    end=end.strftime("%Y-%m-%d"),
                    interval="1d"
                )
                
                if not df.empty:
                    # Rename columns to match expected format
                    df = df.rename(columns={
                        'Open': 'open',
                        'High': 'high',
                        'Low': 'low',
                        'Close': 'close',
                        'Volume': 'volume'
                    })
                    df.index.name = 'timestamp'
                    result[symbol] = df[['open', 'high', 'low', 'close', 'volume']]
                    logger.info(f"Yahoo Finance: {symbol} - {len(df)} bars")
                else:
                    result[symbol] = pd.DataFrame()
                    logger.warning(f"Yahoo Finance: {symbol} - no data")
                    
            except Exception as e:
                logger.error(f"Yahoo Finance error for {symbol}: {e}")
                result[symbol] = pd.DataFrame()
        
        return result
    
    def get_historical_bars_single(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day"
    ) -> pd.DataFrame:
        """Get historical bars for a single symbol"""
        result = self.get_historical_bars([symbol], start, end, timeframe)
        return result.get(symbol, pd.DataFrame())
    
    def get_data_coverage_stats(self) -> Dict:
        """Get statistics about database coverage"""
        try:
            cur = self.conn.cursor()
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total_bars,
                    COUNT(DISTINCT symbol) as total_symbols,
                    MIN(date) as earliest_date,
                    MAX(date) as latest_date
                FROM historical_prices
            """)
            
            total_bars, total_symbols, earliest, latest = cur.fetchone()
            
            cur.close()
            
            return {
                "total_bars": total_bars,
                "total_symbols": total_symbols,
                "earliest_date": earliest,
                "latest_date": latest,
                "source": "database"
            }
            
        except Exception as e:
            logger.error(f"Error getting coverage stats: {e}")
            return {
                "total_bars": 0,
                "total_symbols": 0,
                "earliest_date": None,
                "latest_date": None,
                "source": "error"
            }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Singleton instance for import
_instance = None

def get_historical_data_service() -> HistoricalDataService:
    """Get or create singleton instance"""
    global _instance
    if _instance is None:
        _instance = HistoricalDataService()
    return _instance
