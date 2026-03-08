"""
Historical Data Manager

Downloads and maintains historical price data for all stocks in universe.
Handles:
- Initial bulk download (10 years for all stocks)
- Daily incremental updates
- Database caching for fast access
- Support for S&P 500, DOW, NASDAQ, Russell 2000
- Uses Alpaca Data API for reliable, fast downloads
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import HistoricalPrice
from app.database import SessionLocal
from services.universe_builder import UniverseBuilder
from app.services.alpaca_service import get_alpaca_service

logger = logging.getLogger(__name__)


class HistoricalDataManager:
    """
    Manages historical price data for stock universe
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.universe_builder = UniverseBuilder()
        self.alpaca_service = get_alpaca_service(paper=True)
    
    def initial_bulk_download(
        self,
        years: int = 10,
        include_indices: List[str] = ['SP500', 'DOW', 'NASDAQ100', 'RUSSELL2000']
    ) -> Dict[str, int]:
        """
        Initial bulk download of historical data for entire universe
        
        Args:
            years: Number of years of history to download
            include_indices: Which indices to include
            
        Returns:
            Dict with download statistics
        """
        logger.info(f"🚀 Starting bulk download: {years} years of data")
        
        # Build universe from multiple indices
        universe = self.universe_builder.build_universe(include_indices)
        logger.info(f"   Universe size: {len(universe)} stocks")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        logger.info(f"   Date range: {start_date.date()} to {end_date.date()}")
        
        stats = {
            'total_stocks': len(universe),
            'successful': 0,
            'failed': 0,
            'already_cached': 0,
            'total_rows': 0
        }
        
        # Download in batches to manage memory
        batch_size = 50
        for i in range(0, len(universe), batch_size):
            batch = universe[i:i+batch_size]
            logger.info(f"   Batch {i//batch_size + 1}/{(len(universe)-1)//batch_size + 1}: Processing {len(batch)} stocks...")
            
            batch_stats = self._download_batch(batch, start_date, end_date)
            stats['successful'] += batch_stats['successful']
            stats['failed'] += batch_stats['failed']
            stats['already_cached'] += batch_stats['already_cached']
            stats['total_rows'] += batch_stats['total_rows']
        
        logger.info(f"\n✅ BULK DOWNLOAD COMPLETE")
        logger.info(f"   Successful: {stats['successful']}")
        logger.info(f"   Failed: {stats['failed']}")
        logger.info(f"   Already cached: {stats['already_cached']}")
        logger.info(f"   Total rows: {stats['total_rows']:,}")
        
        return stats
    
    def _download_batch(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Download and cache a batch of symbols using Alpaca"""
        stats = {
            'successful': 0,
            'failed': 0,
            'already_cached': 0,
            'total_rows': 0
        }
        
        # Download all symbols in batch from Alpaca
        try:
            bars_dict = self.alpaca_service.get_historical_bars(
                symbols=symbols,
                start=start_date,
                end=end_date,
                timeframe="1Day"
            )
            
            # Process each symbol's data
            for symbol in symbols:
                try:
                    # Check if already cached
                    if self._is_cached(symbol, start_date, end_date):
                        stats['already_cached'] += 1
                        logger.debug(f"      ✓ {symbol}: Already cached")
                        continue
                    
                    # Get bars for this symbol
                    hist = bars_dict.get(symbol, pd.DataFrame())
                    
                    if hist.empty:
                        stats['failed'] += 1
                        logger.warning(f"      ❌ {symbol}: No data available")
                        continue
                    
                    # Rename columns to match expected format (open, high, low, close, volume)
                    # Alpaca already provides these columns in lowercase
                    
                    # Save to database
                    rows_saved = self._save_to_cache(symbol, hist)
                    stats['successful'] += 1
                    stats['total_rows'] += rows_saved
                    
                    logger.debug(f"      ✅ {symbol}: {rows_saved} days saved")
                    
                except Exception as e:
                    stats['failed'] += 1
                    logger.warning(f"      ❌ {symbol}: {str(e)[:100]}")
                    
        except Exception as e:
            logger.error(f"Batch download failed: {e}")
            # Mark all as failed
            stats['failed'] = len(symbols)
        
        return stats
    
    def daily_update(self) -> Dict[str, int]:
        """
        Daily incremental update - only downloads yesterday's data
        
        Should be run daily after market close
        
        Returns:
            Dict with update statistics
        """
        logger.info("📅 Running daily update...")
        
        # Get universe
        universe = self.universe_builder.build_universe()
        
        # Only download last 2 days (in case previous run failed)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)
        
        stats = {
            'total_stocks': len(universe),
            'updated': 0,
            'failed': 0,
            'total_rows': 0
        }
        
        # Download all symbols in batch using Alpaca
        try:
            bars_dict = self.alpaca_service.get_historical_bars(
                symbols=universe,
                start=start_date,
                end=end_date,
                timeframe="1Day"
            )
            
            for symbol in universe:
                try:
                    hist = bars_dict.get(symbol, pd.DataFrame())
                    
                    if not hist.empty:
                        rows_saved = self._save_to_cache(symbol, hist, update_mode=True)
                        stats['updated'] += 1
                        stats['total_rows'] += rows_saved
                except Exception as e:
                    stats['failed'] += 1
                    logger.warning(f"   ❌ {symbol}: {str(e)[:100]}")
                    
        except Exception as e:
            logger.error(f"Daily update batch download failed: {e}")
            stats['failed'] = len(universe)
        
        logger.info(f"✅ Daily update complete: {stats['updated']} stocks, {stats['total_rows']} rows")
        return stats
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Get historical data from cache (or download if missing)
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with OHLCV data
        """
        # Adjust end_date if it's in the future (can't have data for future dates)
        today = datetime.now().date()
        effective_end_date = min(end_date.date(), today)
        
        # Try cache first
        cached = self.db.query(HistoricalPrice).filter(
            and_(
                HistoricalPrice.symbol == symbol,
                HistoricalPrice.date >= start_date.date(),
                HistoricalPrice.date <= effective_end_date
            )
        ).order_by(HistoricalPrice.date).all()
        
        # Convert cached data to DataFrame (ALWAYS use cache, never download during backtesting)
        if cached:
            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'Date': row.date,
                    'Open': row.open,
                    'High': row.high,
                    'Low': row.low,
                    'Close': row.close,
                    'Volume': row.volume
                }
                for row in cached
            ])
            df.set_index('Date', inplace=True)
            return df
        
        # No cached data - return empty DataFrame (backtesting should use existing data only)
        logger.warning(f"No cached data for {symbol} in requested range")
        return pd.DataFrame()
    
    def get_batch_historical_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical data for multiple symbols (uses cache)
        
        Args:
            symbols: List of symbols
            start_date: Start date
            end_date: End date
            
        Returns:
            Dict mapping symbol to DataFrame
        """
        result = {}
        
        for symbol in symbols:
            try:
                df = self.get_historical_data(symbol, start_date, end_date)
                if not df.empty:
                    result[symbol] = df
            except Exception as e:
                logger.warning(f"Failed to get data for {symbol}: {e}")
        
        return result
    
    def _is_cached(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """Check if symbol is fully cached for date range"""
        count = self.db.query(HistoricalPrice).filter(
            and_(
                HistoricalPrice.symbol == symbol,
                HistoricalPrice.date >= start_date.date(),
                HistoricalPrice.date <= end_date.date()
            )
        ).count()
        
        # Rough check: Should have ~252 trading days per year
        expected_days = (end_date - start_date).days * 0.7  # ~70% are trading days
        return count >= expected_days * 0.9  # 90% threshold
    
    def _cache_is_complete(
        self,
        cached_rows: List[HistoricalPrice],
        start_date: datetime,
        end_date: datetime
    ) -> bool:
        """
        Check if cached data is reasonably complete.
        
        Returns True if:
        1. We have at least 90% of expected trading days, OR
        2. The latest cached date is within 7 days of end_date (data is current)
        
        This handles cases where stocks stopped trading or have gaps.
        """
        if not cached_rows:
            return False
        
        # Check 1: Do we have enough data points?
        days_requested = (end_date - start_date).days
        expected_days = days_requested * 0.7  # ~70% are trading days
        
        if len(cached_rows) >= expected_days * 0.9:  # 90% threshold
            return True
        
        # Check 2: Is the data current (latest date close to end_date)?
        latest_cached = max(row.date for row in cached_rows)
        days_from_end = (end_date.date() - latest_cached).days
        
        # If latest cached data is within 7 days of requested end, consider it complete
        # (stock might have been delisted, halted, or have recent gaps)
        if days_from_end <= 7:
            return True
        
        return False
    
    def _save_to_cache(
        self,
        symbol: str,
        hist: pd.DataFrame,
        update_mode: bool = False
    ) -> int:
        """
        Save historical data to database
        
        Args:
            symbol: Stock symbol
            hist: DataFrame with OHLCV data
            update_mode: If True, update existing records instead of failing
            
        Returns:
            Number of rows saved
        """
        rows_saved = 0
        
        for idx, row in hist.iterrows():
            try:
                # Convert pandas Timestamp to date
                if isinstance(idx, pd.Timestamp):
                    date_value = idx.date()
                else:
                    date_value = idx
                
                # Check if already exists
                existing = self.db.query(HistoricalPrice).filter(
                    and_(
                        HistoricalPrice.symbol == symbol,
                        HistoricalPrice.date == date_value
                    )
                ).first()
                
                if existing:
                    if update_mode:
                        # Update existing record
                        existing.open = float(row.get('open', row.get('Open', 0)))
                        existing.high = float(row.get('high', row.get('High', 0)))
                        existing.low = float(row.get('low', row.get('Low', 0)))
                        existing.close = float(row.get('close', row.get('Close', 0)))
                        existing.volume = int(row.get('volume', row.get('Volume', 0)))
                        rows_saved += 1
                    # else: skip (already exists)
                else:
                    # Insert new record
                    price = HistoricalPrice(
                        symbol=symbol,
                        date=date_value,
                        open=float(row.get('open', row.get('Open', 0))),
                        high=float(row.get('high', row.get('High', 0))),
                        low=float(row.get('low', row.get('Low', 0))),
                        close=float(row.get('close', row.get('Close', 0))),
                        volume=int(row.get('volume', row.get('Volume', 0)))
                    )
                    self.db.add(price)
                    rows_saved += 1
                
            except Exception as e:
                logger.warning(f"Failed to save {symbol} {idx}: {e}")
        
        # Commit batch
        try:
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to commit batch for {symbol}: {e}")
            self.db.rollback()
            return 0
        
        return rows_saved


# Convenience function
def run_initial_download(db: Session, years: int = 10):
    """
    Run initial bulk download
    
    Usage:
        from database import SessionLocal
        db = SessionLocal()
        run_initial_download(db, years=10)
    """
    manager = HistoricalDataManager(db)
    return manager.initial_bulk_download(years=years)
