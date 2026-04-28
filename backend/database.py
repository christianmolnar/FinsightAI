from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Use DATABASE_URL from .env, or construct from Supabase if available, or use local default
if os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
elif SUPABASE_URL and SUPABASE_API_KEY:
    DATABASE_URL = f"postgresql://postgres:{SUPABASE_API_KEY}@{SUPABASE_URL}:5432/postgres"
else:
    DATABASE_URL = "postgresql://finsight:finsight123@127.0.0.1:5432/finsight"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    echo=True if os.getenv("DEBUG") == "true" else False,
    pool_pre_ping=False,  # Don't ping on checkout to avoid hanging
    connect_args={"connect_timeout": 5}  # 5 second timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True)
    schwab_account_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    strategy_configs = relationship("StrategyConfig", back_populates="user", cascade="all, delete-orphan")
    ai_optimizations = relationship("AIOptimization", back_populates="user", cascade="all, delete-orphan")
    strategy_parameters = relationship("StrategyParameter", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("UserWatchlist", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    portfolio_type = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    starting_cash = Column(Decimal(15, 2), nullable=False, default=10000.00)
    current_cash = Column(Decimal(15, 2), nullable=False, default=10000.00)
    total_value = Column(Decimal(15, 2), nullable=False, default=10000.00)
    total_return = Column(Decimal(15, 2), default=0.00)
    total_return_percent = Column(Decimal(8, 4), default=0.00)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (CheckConstraint("portfolio_type IN ('live', 'paper')", name="check_portfolio_type"),)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
    snapshots = relationship("PortfolioSnapshot", back_populates="portfolio", cascade="all, delete-orphan")


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Decimal(15, 4), nullable=False)
    average_cost = Column(Decimal(10, 4), nullable=False)
    current_price = Column(Decimal(10, 4), default=0.00)
    market_value = Column(Decimal(15, 2), default=0.00)
    cost_basis = Column(Decimal(15, 2), nullable=False)
    unrealized_pnl = Column(Decimal(15, 2), default=0.00)
    unrealized_pnl_percent = Column(Decimal(8, 4), default=0.00)
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    strategy_used = Column(String(50))
    ai_confidence = Column(Decimal(3, 2))
    target_price = Column(Decimal(10, 4))
    stop_loss = Column(Decimal(10, 4))
    days_held = Column(Integer, default=0)
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("ai_confidence >= 0 AND ai_confidence <= 1", name="check_ai_confidence_range"),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(20), nullable=False)
    transaction_type = Column(String(10), nullable=False)
    quantity = Column(Decimal(15, 4), nullable=False)
    price = Column(Decimal(10, 4), nullable=False)
    total_amount = Column(Decimal(15, 2), nullable=False)
    commission = Column(Decimal(10, 2), default=1.00)
    net_amount = Column(Decimal(15, 2), nullable=False)
    strategy_used = Column(String(50))
    ai_confidence = Column(Decimal(3, 2))
    ai_factors = Column(JSONB)
    notes = Column(Text)
    executed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("transaction_type IN ('BUY', 'SELL')", name="check_transaction_type"),
        CheckConstraint("ai_confidence >= 0 AND ai_confidence <= 1", name="check_ai_confidence_range"),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    trade_factors = relationship("TradeFactor", back_populates="transaction", cascade="all, delete-orphan")


class StrategyConfig(Base):
    __tablename__ = "strategy_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_name = Column(String(50), nullable=False)
    parameters = Column(JSONB, nullable=False)
    is_active = Column(Boolean, default=True)
    performance_metrics = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="strategy_configs")


class TradeFactor(Base):
    __tablename__ = "trade_factors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    factor_type = Column(String(50), nullable=False)
    factor_value = Column(Decimal(12, 4))
    factor_description = Column(Text)
    weight = Column(Decimal(3, 2))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    transaction = relationship("Transaction", back_populates="trade_factors")


class MarketDataCache(Base):
    __tablename__ = "market_data_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False)
    price = Column(Decimal(10, 4), nullable=False)
    volume = Column(Integer)
    high = Column(Decimal(10, 4))
    low = Column(Decimal(10, 4))
    open = Column(Decimal(10, 4))
    previous_close = Column(Decimal(10, 4))
    change_amount = Column(Decimal(10, 4))
    change_percent = Column(Decimal(8, 4))
    market_cap = Column(Integer)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    source = Column(String(50), default="yahoo")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AIOptimization(Base):
    __tablename__ = "ai_optimizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    strategy_type = Column(String(50), nullable=False)
    original_parameters = Column(JSONB, nullable=False)
    optimized_parameters = Column(JSONB, nullable=False)
    confidence_score = Column(Decimal(3, 2))
    expected_return = Column(Decimal(8, 4))
    expected_sharpe = Column(Decimal(6, 4))
    expected_max_drawdown = Column(Decimal(8, 4))
    reasoning = Column(Text)
    market_analysis = Column(Text)
    risk_assessment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="ai_optimizations")


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    total_value = Column(Decimal(15, 2), nullable=False)
    cash_value = Column(Decimal(15, 2), nullable=False)
    positions_value = Column(Decimal(15, 2), nullable=False)
    total_return = Column(Decimal(15, 2), nullable=False)
    total_return_percent = Column(Decimal(8, 4), nullable=False)
    daily_return = Column(Decimal(15, 2))
    daily_return_percent = Column(Decimal(8, 4))
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="snapshots")


# Import optimization models to ensure they're registered
from models.optimization_run import OptimizationRun, StrategyConfigSnapshot


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)
