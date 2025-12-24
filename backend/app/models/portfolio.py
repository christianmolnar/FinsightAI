"""
Portfolio Models
Models for portfolio management, positions, and trades
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Float, Enum
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class TradeStatus(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled" 
    REJECTED = "rejected"
    PARTIAL = "partial"


class TradeSide(enum.Enum):
    BUY = "buy"
    SELL = "sell"


class StrategyType(enum.Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    SENTIMENT = "sentiment"
    EARNINGS = "earnings"
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    total_value = Column(Decimal(15, 2), nullable=False, default=0.0)
    cash_balance = Column(Decimal(15, 2), nullable=False, default=0.0)
    invested_value = Column(Decimal(15, 2), nullable=False, default=0.0)
    total_pnl = Column(Decimal(15, 2), nullable=False, default=0.0)
    daily_pnl = Column(Decimal(15, 2), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(10), nullable=False, index=True)
    shares = Column(Decimal(15, 4), nullable=False, default=0.0)
    avg_cost = Column(Decimal(10, 4), nullable=False, default=0.0)
    current_price = Column(Decimal(10, 4), nullable=False, default=0.0)
    market_value = Column(Decimal(15, 2), nullable=False, default=0.0)
    unrealized_pnl = Column(Decimal(15, 2), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Trade(Base):
    """Trade execution records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(10), nullable=False, index=True)
    side = Column(Enum(TradeSide), nullable=False)
    quantity = Column(Decimal(15, 4), nullable=False)
    price = Column(Decimal(10, 4), nullable=False)
    total_amount = Column(Decimal(15, 2), nullable=False)
    status = Column(Enum(TradeStatus), nullable=False, default=TradeStatus.PENDING)
    strategy = Column(Enum(StrategyType), nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    broker_order_id = Column(String(100), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")


# Alias for backward compatibility
Transaction = Trade


# Remove the old classes that don't match the database
# TradeFactor and PortfolioSnapshot are not in the current database schema
