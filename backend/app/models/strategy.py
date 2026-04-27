"""
Strategy Models
Models for strategy configuration and AI optimization
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
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


class AIDiscoveredPattern(Base):
    """
    AI-discovered trading patterns.
    
    The AI can analyze backtest results and discover new patterns
    that are then registered in the PatternRegistry for future detection.
    """
    __tablename__ = "ai_discovered_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    detection_logic = Column(Text, nullable=False)  # Python expression for pattern detection
    discovered_by = Column(String(20), default='AI')  # 'AI' or 'built-in'
    discovered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    performance_metrics = Column(JSONB)  # Win rate, avg return when pattern detected
    times_detected = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AIDiscoveredPattern(name='{self.name}', detected={self.times_detected})>"
