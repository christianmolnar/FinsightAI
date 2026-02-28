"""
User Model
Core user model for authentication and user management
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    schwab_account_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    # Note: Portfolio doesn't have user_id in the current schema
    strategy_configs = relationship("StrategyConfig", back_populates="user", cascade="all, delete-orphan")
    ai_optimizations = relationship("AIOptimization", back_populates="user", cascade="all, delete-orphan")
    strategy_parameters = relationship("StrategyParameter", back_populates="user", cascade="all, delete-orphan")
    # watchlist = relationship("UserWatchlist", back_populates="user", cascade="all, delete-orphan")  # TODO: Implement UserWatchlist model
    # preferences = relationship("UserPreferences", back_populates="user", cascade="all, delete-orphan", uselist=False)  # TODO: Implement UserPreferences model
