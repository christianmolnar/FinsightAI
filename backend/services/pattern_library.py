"""
Trading Pattern Library

Extensible pattern recognition system that can identify trading patterns
and learn new ones via AI analysis.

Key Features:
- Base TradingPattern class for extensibility
- PatternRegistry for dynamic pattern registration
- Built-in patterns: Mean Reversion, Momentum, Whale Hunting, etc.
- AI can discover and register new patterns at runtime
- Database persistence for AI-discovered patterns
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Type, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

logger = logging.getLogger(__name__)


class TradingPattern(ABC):
    """
    Base class for trading patterns.
    
    AI can extend this class to create new patterns discovered during analysis.
    Each pattern defines how to detect itself and what characteristics it has.
    """
    
    name: str = "base_pattern"
    description: str = "Base trading pattern"
    discovered_by: str = "built-in"  # "built-in" or "AI"
    
    @abstractmethod
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """
        Returns True if this pattern matches the trade.
        
        Args:
            trade: BacktestResult.to_dict() with trade details
            market_data: Additional market data (volume, MA, etc.)
            
        Returns:
            bool: True if pattern detected
        """
        pass
    
    @abstractmethod
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """
        Returns pattern-specific characteristics for analysis.
        
        Args:
            trade: BacktestResult.to_dict()
            market_data: Additional market data
            
        Returns:
            Dict with pattern characteristics
        """
        pass


class MeanReversionPattern(TradingPattern):
    """
    Detects mean reversion trades: Buy dips, exit on rebound to MA.
    
    Characteristics:
    - Entry below moving average
    - Exit above moving average
    - Typically short hold period
    """
    
    name = "mean_reversion"
    description = "Entry below moving average, exit on rebound"
    discovered_by = "built-in"
    
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """Detect if trade is mean reversion"""
        entry_price = trade.get('entry_price', 0)
        exit_price = trade.get('exit_price', 0)
        ma20 = market_data.get('ma20', 0)
        
        if ma20 == 0:
            return False
        
        # Entry below MA, exit above MA
        return (entry_price < ma20 and exit_price > ma20)
    
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """Get mean reversion characteristics"""
        entry_price = trade.get('entry_price', 0)
        ma20 = market_data.get('ma20', 1)  # Avoid division by zero
        
        dip_pct = ((entry_price - ma20) / ma20) * 100
        
        return {
            'pattern': self.name,
            'dip_pct': dip_pct,
            'rebound_pct': trade.get('return_pct', 0),
            'hold_days': trade.get('hold_days', 0),
            'ma_level': ma20
        }


class MomentumPattern(TradingPattern):
    """
    Detects momentum trades: Breakout entry, trend following.
    
    Characteristics:
    - Entry on breakout (near 50-day high)
    - High volume confirmation
    - Ride the trend
    """
    
    name = "momentum"
    description = "Breakout entry with trend following"
    discovered_by = "built-in"
    
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """Detect if trade is momentum/breakout"""
        entry_price = trade.get('entry_price', 0)
        high_50d = market_data.get('high_50d', 0)
        volume_ratio = market_data.get('volume_ratio', 0)
        
        if high_50d == 0:
            return False
        
        # Entry within 5% of 50-day high + volume spike
        distance_from_high = ((entry_price / high_50d) - 1) * 100
        return (distance_from_high > -5 and volume_ratio > 1.3)
    
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """Get momentum characteristics"""
        entry_price = trade.get('entry_price', 0)
        high_50d = market_data.get('high_50d', 1)
        
        distance_from_high = ((entry_price / high_50d) - 1) * 100
        
        return {
            'pattern': self.name,
            'distance_from_high_pct': distance_from_high,
            'volume_ratio': market_data.get('volume_ratio', 0),
            'return_pct': trade.get('return_pct', 0),
            'hold_days': trade.get('hold_days', 0)
        }


class WhaleHuntingPattern(TradingPattern):
    """
    Detects whale hunting trades: High volume, institutional flows.
    
    Characteristics:
    - Extreme volume spike (3x+ average)
    - Large position size
    - Institutional buying pressure
    """
    
    name = "whale_hunting"
    description = "High volume spike with institutional buying pressure"
    discovered_by = "built-in"
    
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """Detect if trade is whale hunting"""
        volume_ratio = market_data.get('volume_ratio', 0)
        position_size_pct = trade.get('position_size_pct', 0)
        
        # High volume (3x+) + Large position (10%+)
        return (volume_ratio > 3.0 and position_size_pct > 10)
    
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """Get whale hunting characteristics"""
        return {
            'pattern': self.name,
            'volume_spike': market_data.get('volume_ratio', 0),
            'position_size': trade.get('position_size_pct', 0),
            'institutional_flow': market_data.get('institutional_flow', 0),
            'return_pct': trade.get('return_pct', 0)
        }


class EarningsDriftPattern(TradingPattern):
    """
    Detects earnings drift trades: Post-earnings continuation.
    
    Characteristics:
    - Entry near earnings date
    - Short hold period (< 10 days)
    - Momentum continuation after earnings
    """
    
    name = "earnings_drift"
    description = "Post-earnings momentum continuation"
    discovered_by = "built-in"
    
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """Detect if trade is earnings drift"""
        strategy = trade.get('strategy', '')
        hold_days = trade.get('hold_days', 0)
        
        # Earnings strategy + short hold
        return (strategy == 'earnings' and hold_days <= 10)
    
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """Get earnings drift characteristics"""
        return {
            'pattern': self.name,
            'hold_days': trade.get('hold_days', 0),
            'return_pct': trade.get('return_pct', 0),
            'earnings_surprise': market_data.get('earnings_surprise_pct', 0)
        }


class SeasonalPattern(TradingPattern):
    """
    Detects seasonal trades: Calendar-based entries.
    
    Characteristics:
    - Entry during historically strong month/quarter
    - Based on multi-year seasonal patterns
    """
    
    name = "seasonal"
    description = "Calendar-based seasonal pattern"
    discovered_by = "built-in"
    
    def detect(self, trade: Dict, market_data: Dict) -> bool:
        """Detect if trade is seasonal"""
        strategy = trade.get('strategy', '')
        return (strategy == 'seasonality')
    
    def get_characteristics(self, trade: Dict, market_data: Dict) -> Dict:
        """Get seasonal characteristics"""
        return {
            'pattern': self.name,
            'month': market_data.get('entry_month', 0),
            'historical_return': market_data.get('avg_seasonal_return', 0),
            'years_analyzed': market_data.get('years_analyzed', 0),
            'return_pct': trade.get('return_pct', 0)
        }


class PatternRegistry:
    """
    Central registry for all trading patterns (built-in + AI-discovered).
    
    AI can register new patterns discovered during optimization iterations.
    """
    
    _patterns: Dict[str, Type[TradingPattern]] = {}
    _db_session: Optional[Session] = None
    
    @classmethod
    def set_db_session(cls, db: Session):
        """Set database session for persistence"""
        cls._db_session = db
    
    @classmethod
    def register(cls, pattern_class: Type[TradingPattern]):
        """
        Register a new pattern (built-in or AI-discovered).
        
        Args:
            pattern_class: Class extending TradingPattern
        """
        cls._patterns[pattern_class.name] = pattern_class
        logger.info(f"📝 Registered pattern: {pattern_class.name} ({pattern_class.description})")
    
    @classmethod
    def register_from_ai(
        cls,
        name: str,
        description: str,
        detection_logic: str,
        performance_metrics: Optional[Dict] = None
    ):
        """
        AI can discover and register new patterns at runtime.
        
        Example:
        AI analyzes 1000 trades and discovers:
        "Stocks that gap up >5% on earnings + held for 3 days = 80% win rate"
        
        AI calls:
        PatternRegistry.register_from_ai(
            name="earnings_gap_continuation",
            description="Post-earnings gap up with short hold",
            detection_logic="trade['strategy'] == 'earnings' and 'gap' in trade.get('entry_reason', '') and trade['hold_days'] <= 3"
        )
        
        Args:
            name: Pattern name (snake_case)
            description: Human-readable description
            detection_logic: Python expression that evaluates to True/False
            performance_metrics: Optional dict with win_rate, avg_return, etc.
        """
        logger.info(f"🤖 AI discovering new pattern: {name}")
        
        # Create dynamic pattern class
        def detect_method(self, trade: Dict, market_data: Dict) -> bool:
            try:
                # Evaluate detection logic with trade and market_data in scope
                return eval(detection_logic)
            except Exception as e:
                logger.error(f"Pattern {name} detection failed: {e}")
                return False
        
        def characteristics_method(self, trade: Dict, market_data: Dict) -> Dict:
            return {
                'pattern': name,
                'detected_by': 'AI',
                'description': description,
                'trade_data': {
                    'symbol': trade.get('symbol', ''),
                    'return_pct': trade.get('return_pct', 0),
                    'hold_days': trade.get('hold_days', 0)
                }
            }
        
        # Create pattern class dynamically
        pattern_class = type(
            name.title().replace('_', ''),  # CamelCase class name
            (TradingPattern,),
            {
                'name': name,
                'description': description,
                'discovered_by': 'AI',
                'detect': detect_method,
                'get_characteristics': characteristics_method
            }
        )
        
        # Register the pattern
        cls.register(pattern_class)
        
        # Persist to database
        if cls._db_session:
            cls._save_ai_pattern(name, description, detection_logic, performance_metrics)
    
    @classmethod
    def _save_ai_pattern(
        cls,
        name: str,
        description: str,
        detection_logic: str,
        performance_metrics: Optional[Dict]
    ):
        """Save AI-discovered pattern to database"""
        try:
            from app.models.strategy import AIDiscoveredPattern
            
            pattern = AIDiscoveredPattern(
                name=name,
                description=description,
                detection_logic=detection_logic,
                discovered_by='AI',
                performance_metrics=performance_metrics or {}
            )
            
            cls._db_session.add(pattern)
            cls._db_session.commit()
            logger.info(f"💾 Saved AI pattern '{name}' to database")
            
        except Exception as e:
            logger.error(f"Failed to save AI pattern to database: {e}")
    
    @classmethod
    def load_ai_patterns_from_db(cls, db: Session):
        """Load all AI-discovered patterns from database on startup"""
        try:
            from app.models.strategy import AIDiscoveredPattern
            
            patterns = db.query(AIDiscoveredPattern).filter(
                AIDiscoveredPattern.is_active == True
            ).all()
            
            for pattern in patterns:
                cls.register_from_ai(
                    name=pattern.name,
                    description=pattern.description,
                    detection_logic=pattern.detection_logic,
                    performance_metrics=pattern.performance_metrics
                )
            
            logger.info(f"📚 Loaded {len(patterns)} AI-discovered patterns from database")
            
        except Exception as e:
            logger.error(f"Failed to load AI patterns from database: {e}")
    
    @classmethod
    def get_all_patterns(cls) -> List[Type[TradingPattern]]:
        """Get all registered patterns (built-in + AI-discovered)"""
        return list(cls._patterns.values())
    
    @classmethod
    def get_pattern(cls, name: str) -> Optional[Type[TradingPattern]]:
        """Get specific pattern by name"""
        return cls._patterns.get(name)
    
    @classmethod
    def list_pattern_names(cls) -> List[str]:
        """List all registered pattern names"""
        return list(cls._patterns.keys())


# Register built-in patterns on module load
PatternRegistry.register(MeanReversionPattern)
PatternRegistry.register(MomentumPattern)
PatternRegistry.register(WhaleHuntingPattern)
PatternRegistry.register(EarningsDriftPattern)
PatternRegistry.register(SeasonalPattern)

logger.info(f"✅ Pattern library initialized with {len(PatternRegistry.get_all_patterns())} built-in patterns")
