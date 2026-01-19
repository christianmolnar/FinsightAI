"""
User Watchlist Service
Manages watchlist CRUD operations and Alpaca synchronization
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
import logging

from models.watchlist import UserWatchlist
from app.services.alpaca_service import AlpacaService

logger = logging.getLogger(__name__)


class WatchlistService:
    """Service for managing user watchlists"""
    
    def __init__(self, db: Session, alpaca_service: AlpacaService):
        self.db = db
        self.alpaca = alpaca_service
    
    def get_user_watchlist(self, user_id: UUID) -> List[UserWatchlist]:
        """
        Get all watchlist items for a user
        
        Args:
            user_id: User UUID
            
        Returns:
            List of UserWatchlist objects
        """
        try:
            stmt = select(UserWatchlist).where(
                UserWatchlist.user_id == user_id
            ).order_by(UserWatchlist.added_at.desc())
            
            items = self.db.execute(stmt).scalars().all()
            logger.info(f"Retrieved {len(items)} watchlist items for user {user_id}")
            return list(items)
            
        except Exception as e:
            logger.error(f"Error getting watchlist for user {user_id}: {str(e)}")
            return []
    
    def add_to_watchlist(
        self, 
        user_id: UUID, 
        symbol: str
    ) -> Optional[UserWatchlist]:
        """
        Add symbol to user's watchlist
        
        Args:
            user_id: User UUID
            symbol: Stock symbol
            
        Returns:
            Created UserWatchlist object, or None if symbol already exists
        """
        try:
            # Check if symbol already exists
            stmt = select(UserWatchlist).where(
                UserWatchlist.user_id == user_id,
                UserWatchlist.symbol == symbol.upper()
            )
            existing = self.db.execute(stmt).scalar_one_or_none()
            
            if existing:
                logger.warning(f"Symbol {symbol} already in watchlist for user {user_id}")
                return None
            
            # Create new watchlist item (no notes column exists in database)
            item = UserWatchlist(
                user_id=user_id,
                symbol=symbol.upper()
            )
            
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            
            logger.info(f"Added {symbol} to watchlist for user {user_id}")
            return item
            
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {str(e)}")
            self.db.rollback()
            raise
    
    def remove_from_watchlist(self, user_id: UUID, symbol: str) -> bool:
        """
        Remove symbol from user's watchlist
        
        Args:
            user_id: User UUID
            symbol: Stock symbol to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            stmt = select(UserWatchlist).where(
                UserWatchlist.user_id == user_id,
                UserWatchlist.symbol == symbol.upper()
            )
            item = self.db.execute(stmt).scalar_one_or_none()
            
            if not item:
                logger.warning(f"Symbol {symbol} not found in watchlist for user {user_id}")
                return False
            
            self.db.delete(item)
            self.db.commit()
            
            logger.info(f"Removed {symbol} from watchlist for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing {symbol} from watchlist: {str(e)}")
            self.db.rollback()
            raise
    
    def update_notes(
        self, 
        user_id: UUID, 
        symbol: str,
        notes: str
    ) -> Optional[UserWatchlist]:
        """
        Update notes for a watchlist item
        
        Args:
            user_id: User UUID
            symbol: Stock symbol
            notes: New notes text
            
        Returns:
            Updated UserWatchlist object, or None if not found
        """
        # REMOVED: update_notes method - notes column doesn't exist in database
        raise NotImplementedError("Notes feature not available - column doesn't exist in database schema")
    
    def sync_from_alpaca(self, user_id: UUID) -> List[UserWatchlist]:
        """
        Sync watchlist FROM Alpaca TO local database
        Adds any symbols from Alpaca that aren't in local watchlist
        
        Args:
            user_id: User UUID
            
        Returns:
            Updated list of watchlist items
        """
        try:
            # Get Alpaca watchlist
            alpaca_watchlist = self.alpaca.get_watchlist()
            alpaca_symbols = set(w['symbol'] for w in alpaca_watchlist)
            
            # Get current local watchlist
            local_items = self.get_user_watchlist(user_id)
            local_symbols = set(item.symbol for item in local_items)
            
            # Add missing symbols from Alpaca
            new_symbols = alpaca_symbols - local_symbols
            for symbol in new_symbols:
                self.add_to_watchlist(user_id, symbol, notes="Synced from Alpaca")
            
            logger.info(f"Synced {len(new_symbols)} new symbols from Alpaca for user {user_id}")
            
            # Return updated watchlist
            return self.get_user_watchlist(user_id)
            
        except Exception as e:
            logger.error(f"Error syncing from Alpaca: {str(e)}")
            raise
    
    def sync_to_alpaca(self, user_id: UUID) -> bool:
        """
        Sync watchlist FROM local database TO Alpaca
        Updates Alpaca watchlist with all local symbols
        
        Args:
            user_id: User UUID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get local watchlist
            local_items = self.get_user_watchlist(user_id)
            local_symbols = [item.symbol for item in local_items]
            
            # Update Alpaca watchlist
            success = self.alpaca.update_watchlist(local_symbols)
            
            if success:
                logger.info(f"Synced {len(local_symbols)} symbols to Alpaca for user {user_id}")
            else:
                logger.error(f"Failed to sync watchlist to Alpaca for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing to Alpaca: {str(e)}")
            return False
