"""
Strategy Parameter Models
Defines configurable parameters for trading strategies with AI optimization support.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, CheckConstraint, Enum as SQLEnum, Text
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import enum
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from decimal import Decimal as PyDecimal

from app.database import Base


class StrategyType(enum.Enum):
    """Available trading strategies"""
    EARNINGS = "earnings"
    SEASONALITY = "seasonality"
    MACRO = "macro"
    SENTIMENT = "sentiment"
    IPO = "ipo"


class ParameterType(enum.Enum):
    """Parameter data types"""
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"


# SQLAlchemy Models
class StrategyParameter(Base):
    """
    Database model for strategy parameters.
    Each parameter can be AI-optimized and have per-stock overrides.
    """
    __tablename__ = "strategy_parameters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Parameter identification
    name = Column(String(100), nullable=False)  # e.g., "min_eps_growth", "seasonality_lookback_years"
    display_name = Column(String(255), nullable=False)  # e.g., "Minimum EPS Growth"
    description = Column(String(500))
    strategy = Column(String(50), nullable=False)  # earnings, seasonality, macro, sentiment, ipo
    parameter_type = Column(String(50), nullable=False)  # integer, float, percentage, boolean
    
    # Value constraints
    min_value = Column(Decimal(15, 4))
    max_value = Column(Decimal(15, 4))
    default_value = Column(Decimal(15, 4), nullable=False)
    current_value = Column(Decimal(15, 4), nullable=False)
    
    # AI optimization
    ai_optimizable = Column(Boolean, default=True, nullable=False)
    ai_suggested_value = Column(Decimal(15, 4))
    last_optimized_at = Column(DateTime(timezone=True))
    optimization_performance = Column(Decimal(8, 4))  # How well AI suggestion performed
    
    # Metadata
    unit = Column(String(20))  # e.g., "%", "days", "ratio"
    category = Column(String(50))  # e.g., "entry_criteria", "exit_rules", "risk_management"
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("current_value >= min_value AND current_value <= max_value", 
                       name="check_value_in_range"),
    )
    
    # Relationships
    user = relationship("User", back_populates="strategy_parameters")
    stock_overrides = relationship("StockParameterOverride", back_populates="parameter", 
                                  cascade="all, delete-orphan")


class StockParameterOverride(Base):
    """
    Per-stock parameter overrides.
    Allows customizing parameters for specific stocks (e.g., more aggressive for tech, conservative for utilities).
    """
    __tablename__ = "stock_parameter_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey("strategy_parameters.id", ondelete="CASCADE"), 
                         nullable=False)
    
    # Stock identification
    symbol = Column(String(20), nullable=False)
    
    # Override value
    override_value = Column(Decimal(15, 4), nullable=False)
    reason = Column(String(500))  # Why this override exists
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc))
    
    # Constraints
    __table_args__ = (
        # Ensure only one active override per parameter-symbol combination
        CheckConstraint("symbol = UPPER(symbol)", name="check_symbol_uppercase"),
    )
    
    # Relationships
    parameter = relationship("StrategyParameter", back_populates="stock_overrides")


class OptimizationHistory(Base):
    """
    Track AI optimization attempts and their performance.
    """
    __tablename__ = "optimization_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parameter_id = Column(UUID(as_uuid=True), ForeignKey("strategy_parameters.id", ondelete="CASCADE"), 
                         nullable=False)
    
    # Optimization details
    old_value = Column(Decimal(15, 4), nullable=False)
    new_value = Column(Decimal(15, 4), nullable=False)
    ai_rationale = Column(Text)  # Why AI suggested this change
    
    # Performance tracking
    trades_count = Column(Integer, default=0)
    win_rate = Column(Decimal(5, 4))
    avg_return = Column(Decimal(8, 4))
    sharpe_ratio = Column(Decimal(8, 4))
    
    # Approval
    status = Column(String(20), default="pending")  # pending, approved, rejected, testing
    approved_by_user = Column(Boolean, default=False)
    approved_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    parameter = relationship("StrategyParameter")


# Pydantic Schemas for API
class StrategyParameterBase(BaseModel):
    """Base schema for strategy parameters"""
    name: str = Field(..., max_length=100)
    display_name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    strategy: StrategyType
    parameter_type: ParameterType
    min_value: Optional[PyDecimal] = None
    max_value: Optional[PyDecimal] = None
    default_value: PyDecimal
    current_value: PyDecimal
    ai_optimizable: bool = True
    unit: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=50)
    is_active: bool = True
    
    @validator('current_value')
    def validate_current_value(cls, v, values):
        """Ensure current_value is within min/max bounds"""
        min_val = values.get('min_value')
        max_val = values.get('max_value')
        if min_val is not None and v < min_val:
            raise ValueError(f'current_value must be >= {min_val}')
        if max_val is not None and v > max_val:
            raise ValueError(f'current_value must be <= {max_val}')
        return v
    
    class Config:
        from_attributes = True


class StrategyParameterCreate(StrategyParameterBase):
    """Schema for creating a new parameter"""
    pass


class StrategyParameterUpdate(BaseModel):
    """Schema for updating a parameter"""
    display_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    current_value: Optional[PyDecimal] = None
    ai_optimizable: Optional[bool] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True


class StrategyParameterResponse(StrategyParameterBase):
    """Schema for parameter responses"""
    id: uuid.UUID
    user_id: uuid.UUID
    ai_suggested_value: Optional[PyDecimal] = None
    last_optimized_at: Optional[datetime] = None
    optimization_performance: Optional[PyDecimal] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockParameterOverrideBase(BaseModel):
    """Base schema for stock overrides"""
    symbol: str = Field(..., max_length=20)
    override_value: PyDecimal
    reason: Optional[str] = Field(None, max_length=500)
    is_active: bool = True
    
    @validator('symbol')
    def uppercase_symbol(cls, v):
        """Ensure symbol is uppercase"""
        return v.upper()
    
    class Config:
        from_attributes = True


class StockParameterOverrideCreate(StockParameterOverrideBase):
    """Schema for creating a stock override"""
    parameter_id: uuid.UUID


class StockParameterOverrideUpdate(BaseModel):
    """Schema for updating a stock override"""
    override_value: Optional[PyDecimal] = None
    reason: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True


class StockParameterOverrideResponse(StockParameterOverrideBase):
    """Schema for override responses"""
    id: uuid.UUID
    parameter_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OptimizationRequest(BaseModel):
    """Request to optimize parameter(s)"""
    parameter_ids: Optional[list[uuid.UUID]] = None  # If None, optimize all for strategy
    strategy: Optional[StrategyType] = None  # If provided, optimize all parameters for this strategy
    
    class Config:
        from_attributes = True


class OptimizationResponse(BaseModel):
    """Response from optimization"""
    parameter_id: uuid.UUID
    parameter_name: str
    current_value: PyDecimal
    suggested_value: PyDecimal
    rationale: str
    expected_improvement: Optional[PyDecimal] = None  # Expected % improvement
    confidence: PyDecimal  # 0-1 scale
    
    class Config:
        from_attributes = True
