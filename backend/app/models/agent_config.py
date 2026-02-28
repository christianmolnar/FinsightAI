"""
Agent Configuration Model

Stores user preferences for the autonomous trading agent.
Controls scanning behavior, risk parameters, and execution rules.
"""

from sqlalchemy import Column, Integer, Float, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base


class AgentConfig(Base):
    """
    Agent configuration settings
    
    Controls autonomous agent behavior including:
    - Which strategies to use
    - Confidence thresholds
    - Position limits and sizing
    - Auto-execution rules
    """
    __tablename__ = "agent_config"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, default="default", index=True)  # For multi-user support later
    
    # Agent status
    enabled = Column(Boolean, default=False, comment="Master switch - enables/disables agent")
    
    # Scanner configuration
    enabled_strategies = Column(
        JSON,
        default=["technical_breakout", "earnings_play", "seasonality"],
        comment="List of enabled scanner strategies"
    )
    confidence_threshold = Column(
        Float,
        default=0.75,
        comment="Minimum AI confidence to create proposal (0.0-1.0)"
    )
    max_opportunities_per_scan = Column(
        Integer,
        default=5,
        comment="Maximum opportunities to find per scan"
    )
    scan_frequency_minutes = Column(
        Integer,
        default=15,
        comment="How often to run scans (in minutes)"
    )
    
    # Position management
    max_positions = Column(
        Integer,
        default=10,
        comment="Maximum number of open positions"
    )
    max_position_size = Column(
        Float,
        default=1000.00,
        comment="Maximum dollar value per position"
    )
    default_position_shares = Column(
        Integer,
        default=10,
        comment="Default number of shares per position"
    )
    
    # Risk management
    max_portfolio_risk = Column(
        Float,
        default=0.02,
        comment="Maximum portfolio risk per trade (2% default)"
    )
    require_stop_loss = Column(
        Boolean,
        default=True,
        comment="Require stop loss on all trades"
    )
    
    # Auto-execution
    auto_execute_enabled = Column(
        Boolean,
        default=False,
        comment="Allow agent to execute trades automatically"
    )
    auto_execute_threshold = Column(
        Float,
        default=0.85,
        comment="Min AI confidence for auto-execution (0.0-1.0)"
    )
    auto_execute_max_per_day = Column(
        Integer,
        default=3,
        comment="Max auto-executed trades per day"
    )
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "enabled": self.enabled,
            "enabled_strategies": self.enabled_strategies,
            "confidence_threshold": self.confidence_threshold,
            "max_opportunities_per_scan": self.max_opportunities_per_scan,
            "scan_frequency_minutes": self.scan_frequency_minutes,
            "max_positions": self.max_positions,
            "max_position_size": self.max_position_size,
            "default_position_shares": self.default_position_shares,
            "max_portfolio_risk": self.max_portfolio_risk,
            "require_stop_loss": self.require_stop_loss,
            "auto_execute_enabled": self.auto_execute_enabled,
            "auto_execute_threshold": self.auto_execute_threshold,
            "auto_execute_max_per_day": self.auto_execute_max_per_day,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
