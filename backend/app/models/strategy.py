"""
Strategy Models
Models for strategy configuration and AI optimization
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.database import Base


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
