"""
Watchlist Models

Database models for user watchlist management with Alpaca sync.
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class UserWatchlist(Base):
    """
    User's watchlist with real-time price tracking
    Syncs with Alpaca watchlist API
    """
    __tablename__ = "user_watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Price tracking
    price = Column(Numeric(10, 2))
    initial_price = Column(Numeric(10, 2))  # Price when first added (for change calculation)
    change = Column(Numeric(10, 2))
    change_percent = Column(Numeric(5, 2))
    last_updated = Column(DateTime)
    
    # Alpaca sync
    alpaca_synced = Column(Boolean, default=False)
    alpaca_watchlist_id = Column(String(50))  # Alpaca's watchlist ID
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='unique_user_symbol'),
    )
    
    # Relationships
    user = relationship("User", back_populates="watchlist")
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": float(self.price) if self.price else None,
            "initial_price": float(self.initial_price) if self.initial_price else None,
            "change": float(self.change) if self.change else 0,
            "change_percent": float(self.change_percent) if self.change_percent else 0,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "alpaca_synced": self.alpaca_synced
        }
