"""
User Preferences Service
Manages user-specific settings and configurations
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
import logging

from models.preferences import UserPreferences

logger = logging.getLogger(__name__)


class PreferencesService:
    """Service for managing user preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_preference(self, user_id: int, preference_key: str) -> Optional[str]:
        """
        Get a single preference value
        
        Args:
            user_id: User ID
            preference_key: Preference key to retrieve
            
        Returns:
            Preference value as string, or None if not found
        """
        try:
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            )
            result = self.db.execute(stmt).scalar_one_or_none()
            
            if result:
                logger.info(f"Retrieved preference {preference_key} for user {user_id}")
                return result.preference_value
            
            logger.debug(f"Preference {preference_key} not found for user {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting preference {preference_key} for user {user_id}: {str(e)}")
            raise
    
    def get_all_preferences(self, user_id: int) -> Dict[str, str]:
        """
        Get all preferences for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary of preference_key -> preference_value
        """
        try:
            stmt = select(UserPreference).where(UserPreference.user_id == user_id)
            results = self.db.execute(stmt).scalars().all()
            
            preferences = {pref.preference_key: pref.preference_value for pref in results}
            logger.info(f"Retrieved {len(preferences)} preferences for user {user_id}")
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting all preferences for user {user_id}: {str(e)}")
            raise
    
    def set_preference(
        self, 
        user_id: int, 
        preference_key: str, 
        preference_value: str,
        category: Optional[str] = None
    ) -> UserPreference:
        """
        Set or update a preference
        
        Args:
            user_id: User ID
            preference_key: Preference key
            preference_value: Preference value
            category: Optional category (e.g., 'display', 'trading', 'notifications')
            
        Returns:
            Updated UserPreference object
        """
        try:
            # Check if preference exists
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            )
            existing = self.db.execute(stmt).scalar_one_or_none()
            
            if existing:
                # Update existing preference
                existing.preference_value = preference_value
                if category:
                    existing.category = category
                
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated preference {preference_key} for user {user_id}")
                return existing
            else:
                # Create new preference
                new_pref = UserPreference(
                    user_id=user_id,
                    preference_key=preference_key,
                    preference_value=preference_value,
                    category=category or 'general'
                )
                self.db.add(new_pref)
                self.db.commit()
                self.db.refresh(new_pref)
                logger.info(f"Created preference {preference_key} for user {user_id}")
                return new_pref
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error setting preference {preference_key} for user {user_id}: {str(e)}")
            raise
    
    def set_multiple_preferences(
        self, 
        user_id: int, 
        preferences: Dict[str, str],
        category: Optional[str] = None
    ) -> Dict[str, UserPreference]:
        """
        Set or update multiple preferences at once
        
        Args:
            user_id: User ID
            preferences: Dictionary of preference_key -> preference_value
            category: Optional category to apply to all preferences
            
        Returns:
            Dictionary of preference_key -> UserPreference object
        """
        try:
            result = {}
            for key, value in preferences.items():
                pref = self.set_preference(user_id, key, value, category)
                result[key] = pref
            
            logger.info(f"Set {len(result)} preferences for user {user_id}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error setting multiple preferences for user {user_id}: {str(e)}")
            raise
    
    def delete_preference(self, user_id: int, preference_key: str) -> bool:
        """
        Delete a preference
        
        Args:
            user_id: User ID
            preference_key: Preference key to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.preference_key == preference_key
            )
            existing = self.db.execute(stmt).scalar_one_or_none()
            
            if existing:
                self.db.delete(existing)
                self.db.commit()
                logger.info(f"Deleted preference {preference_key} for user {user_id}")
                return True
            
            logger.debug(f"Preference {preference_key} not found for user {user_id}")
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting preference {preference_key} for user {user_id}: {str(e)}")
            raise
    
    def get_preferences_by_category(self, user_id: int, category: str) -> Dict[str, str]:
        """
        Get all preferences in a specific category
        
        Args:
            user_id: User ID
            category: Category to filter by
            
        Returns:
            Dictionary of preference_key -> preference_value
        """
        try:
            stmt = select(UserPreference).where(
                UserPreference.user_id == user_id,
                UserPreference.category == category
            )
            results = self.db.execute(stmt).scalars().all()
            
            preferences = {pref.preference_key: pref.preference_value for pref in results}
            logger.info(f"Retrieved {len(preferences)} {category} preferences for user {user_id}")
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting {category} preferences for user {user_id}: {str(e)}")
            raise
