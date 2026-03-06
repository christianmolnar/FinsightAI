"""
Models Package
Consolidated models using modern FastAPI/SQLAlchemy structure.
All models now live in app/models/ and import from app.database
"""

# Import Base and utilities from app.database
from app.database import Base, SessionLocal, engine, get_db

# Import all model classes from their respective modules
from app.models.user import User
from app.models.portfolio import (
    Portfolio,
    Position,
    Trade,
    Transaction,  # Alias for Trade
    TradeStatus,
    TradeSide,
    StrategyType
)
from app.models.strategy import (
    StrategyConfig,
    AIOptimization
)
from app.models.market_data import MarketDataCache
from app.models.strategy_parameters import (
    StrategyParameter,
    StockParameterOverride,
    OptimizationHistory,
    ParameterType
)
from app.models.agent_config import AgentConfig
from app.models.historical_price import HistoricalPrice

# Backward compatibility alias - already defined in portfolio module
# Trade = Transaction

# Placeholder models for future implementation
# TODO: Move these to proper model files when implementing their features
class MarketData:
    """Placeholder for MarketData model - will be implemented in Phase 3"""
    pass

class TradingSignal:
    """Placeholder for TradingSignal model - will be implemented in Phase 3"""
    pass

class NewsEvent:
    """Placeholder for NewsEvent model - will be implemented in Phase 3"""
    pass


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)


__all__ = [
    # Database utilities
    'Base',
    'SessionLocal',
    'engine',
    'get_db',
    'create_tables',
    'drop_tables',
    
    # User models
    'User',
    
    # Portfolio models
    'Portfolio',
    'Position',
    'Trade',
    'Transaction',  # Alias for Trade
    'TradeStatus',
    'TradeSide',
    'StrategyType',
    
    # Strategy models
    'StrategyConfig',
    'AIOptimization',
    'StrategyParameter',
    'StockParameterOverride',
    'OptimizationHistory',
    'StrategyType',
    'ParameterType',
    
    # Market data models
    'MarketDataCache',
    'MarketData',
    'TradingSignal',
    'NewsEvent',
    'HistoricalPrice',
    
    # Agent models
    'AgentConfig',
]
