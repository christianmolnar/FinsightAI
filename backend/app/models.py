from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


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
    """Portfolio table for tracking overall portfolio state"""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    total_value = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    cash_balance = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    invested_value = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    total_pnl = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    daily_pnl = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    positions = relationship("Position", back_populates="portfolio")
    trades = relationship("Trade", back_populates="portfolio")


class Position(Base):
    """Current portfolio positions"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(10), nullable=False, index=True)
    shares = Column(DECIMAL(15, 4), nullable=False, default=0.0)
    avg_cost = Column(DECIMAL(10, 4), nullable=False, default=0.0)
    current_price = Column(DECIMAL(10, 4), nullable=False, default=0.0)
    market_value = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    unrealized_pnl = Column(DECIMAL(15, 2), nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Trade(Base):
    """Trade execution records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(10), nullable=False, index=True)
    side = Column(Enum(TradeSide), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False)
    price = Column(DECIMAL(10, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(Enum(TradeStatus), nullable=False, default=TradeStatus.PENDING)
    strategy = Column(Enum(StrategyType), nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    broker_order_id = Column(String(100), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="trades")


class MarketData(Base):
    """Real-time and historical market data"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    price = Column(DECIMAL(10, 4), nullable=False)
    volume = Column(Integer, nullable=False, default=0)
    high = Column(DECIMAL(10, 4), nullable=False)
    low = Column(DECIMAL(10, 4), nullable=False)
    open_price = Column(DECIMAL(10, 4), nullable=False)
    change = Column(DECIMAL(10, 4), nullable=False, default=0.0)
    change_percent = Column(Float, nullable=False, default=0.0)
    bid = Column(DECIMAL(10, 4), nullable=True)
    ask = Column(DECIMAL(10, 4), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Strategy(Base):
    """Trading strategy configurations"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(Enum(StrategyType), nullable=False)
    is_active = Column(Boolean, default=True)
    parameters = Column(Text, nullable=True)  # JSON configuration
    performance_score = Column(Float, nullable=True)  # 0.0 to 1.0
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(DECIMAL(15, 2), default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TradingSignal(Base):
    """Generated trading signals from strategies"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    symbol = Column(String(10), nullable=False, index=True)
    side = Column(Enum(TradeSide), nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    target_price = Column(DECIMAL(10, 4), nullable=True)
    stop_loss = Column(DECIMAL(10, 4), nullable=True)
    take_profit = Column(DECIMAL(10, 4), nullable=True)
    reasoning = Column(Text, nullable=True)
    is_executed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    strategy = relationship("Strategy")


class TechnicalIndicator(Base):
    """Technical analysis indicators"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    indicator_name = Column(String(50), nullable=False)  # RSI, MACD, MA, etc.
    value = Column(Float, nullable=False)
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 1h, 1d, etc.
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsEvent(Base):
    """News and events affecting trading decisions"""
    __tablename__ = "news_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    symbols = Column(String(500), nullable=True)  # Comma-separated symbols
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    impact_score = Column(Float, nullable=True)  # 0.0 to 1.0
    published_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
