"""
User Preferences Service

Business logic for managing user preferences including:
- Auto-refresh settings (enabled/disabled, intervals per component)
- Display preferences (rows per page)
- Theme preferences (light/dark)
"""

from sqlalchemy.orm import Session
from models.preferences import UserPreferences
from uuid import UUID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PreferencesService:
    """Service for managing user preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_preferences(self, user_id: UUID) -> UserPreferences:
        """
        Get user preferences or create with defaults if not exist
        
        Default values:
        - auto_refresh_enabled: True
        - refresh_interval_watchlist: 15000ms (15 seconds)
        - refresh_interval_portfolio: 30000ms (30 seconds)
        - refresh_interval_orders: 20000ms (20 seconds)
        - default_rows_per_page: 10
        - theme: 'light'
        
        Args:
            user_id: User UUID
            
        Returns:
            UserPreferences object
        """
        try:
            # Try to get existing preferences
            preferences = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            # Create with defaults if not exist
            if not preferences:
                preferences = UserPreferences(
                    user_id=user_id,
                    auto_refresh_enabled=True,
                    refresh_interval_watchlist=15000,  # 15 seconds
                    refresh_interval_portfolio=30000,   # 30 seconds
                    refresh_interval_orders=20000,      # 20 seconds
                    default_rows_per_page=10,
                    theme='light'
                )
                self.db.add(preferences)
                self.db.commit()
                self.db.refresh(preferences)
                logger.info(f"Created default preferences for user {user_id}")
            
            return preferences
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error getting/creating preferences: {str(e)}")
            raise
    
    def get_preferences(self, user_id: UUID) -> UserPreferences:
        """
        Get user preferences (does not create if missing)
        
        Args:
            user_id: User UUID
            
        Returns:
            UserPreferences object or None if not found
        """
        try:
            preferences = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            raise
    
    def update_preferences(self, user_id: UUID, updates: dict) -> UserPreferences:
        """
        Update user preferences
        
        Args:
            user_id: User UUID
            updates: Dict with fields to update (e.g., {"theme": "dark", "auto_refresh_enabled": False})
            
        Returns:
            Updated UserPreferences object
        """
        try:
            # Get or create preferences
            preferences = self.get_or_create_preferences(user_id)
            
            # Update provided fields
            for key, value in updates.items():
                if hasattr(preferences, key):
                    setattr(preferences, key, value)
                else:
                    logger.warning(f"Attempted to update unknown preference field: {key}")
            
            # Timestamp updates automatically via SQLAlchemy
            
            self.db.commit()
            self.db.refresh(preferences)
            
            logger.info(f"Updated preferences for user {user_id}: {list(updates.keys())}")
            return preferences
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating preferences: {str(e)}")
            raise
    
    def reset_to_defaults(self, user_id: UUID) -> UserPreferences:
        """
        Reset user preferences to default values
        
        Args:
            user_id: User UUID
            
        Returns:
            UserPreferences with default values
        """
        try:
            defaults = {
                'auto_refresh_enabled': True,
                'refresh_interval_watchlist': 15000,
                'refresh_interval_portfolio': 30000,
                'refresh_interval_orders': 20000,
                'default_rows_per_page': 10,
                'theme': 'light'
            }
            
            return self.update_preferences(user_id, defaults)
            
        except Exception as e:
            logger.error(f"Error resetting preferences: {str(e)}")
            raise
    
    def delete_preferences(self, user_id: UUID) -> bool:
        """
        Delete user preferences
        
        Args:
            user_id: User UUID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            preferences = self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                logger.warning(f"No preferences found for user {user_id}")
                return False
            
            self.db.delete(preferences)
            self.db.commit()
            
            logger.info(f"Deleted preferences for user {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting preferences: {str(e)}")
            raise
