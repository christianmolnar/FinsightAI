"""
Market Data Models
Models for market data caching and retrieval
"""
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.database import Base


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
