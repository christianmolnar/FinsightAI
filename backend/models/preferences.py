"""
User Preferences Models

Database models for user preferences and settings.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class UserPreferences(Base):
    """
    User preferences for auto-refresh, table display, and UI settings
    """
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Auto-refresh settings (milliseconds)
    auto_refresh_enabled = Column(Boolean, default=True)
    refresh_interval_watchlist = Column(Integer, default=15000)  # 15 seconds
    refresh_interval_portfolio = Column(Integer, default=30000)  # 30 seconds
    refresh_interval_orders = Column(Integer, default=20000)     # 20 seconds
    
    # Table display settings
    default_rows_per_page = Column(Integer, default=10)
    
    # UI preferences
    theme = Column(String(20), default='light')  # 'light' or 'dark'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "auto_refresh_enabled": self.auto_refresh_enabled,
            "refresh_interval_watchlist": self.refresh_interval_watchlist,
            "refresh_interval_portfolio": self.refresh_interval_portfolio,
            "refresh_interval_orders": self.refresh_interval_orders,
            "default_rows_per_page": self.default_rows_per_page,
            "theme": self.theme,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_default_preferences():
        """Get default preferences for new users"""
        return {
            "auto_refresh_enabled": True,
            "refresh_interval_watchlist": 15000,
            "refresh_interval_portfolio": 30000,
            "refresh_interval_orders": 20000,
            "default_rows_per_page": 10,
            "theme": "light"
        }
