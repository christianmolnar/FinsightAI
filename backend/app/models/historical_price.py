"""
Historical Price Data Model

Stores historical OHLCV data for backtesting and analysis.
"""

from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, Index
from app.database import Base


class HistoricalPrice(Base):
    """Historical price data for stocks"""
    
    __tablename__ = 'historical_prices'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Composite index for fast symbol+date lookups
    __table_args__ = (
        Index('ix_historical_prices_symbol_date', 'symbol', 'date', unique=True),
    )
    
    def __repr__(self):
        return f"<HistoricalPrice(symbol='{self.symbol}', date={self.date}, close={self.close})>"
