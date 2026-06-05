"""
StrategyVariant model

A named, versioned snapshot of a full strategy configuration.
Created by: the AI optimizer after a run, or manually by the user.
Used to: compare variants in backtesting, apply the best one to live scanning.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class StrategyVariant(Base):
    """
    A named, versioned strategy configuration with its backtest performance.

    Every optimization run that improves on baseline should produce a variant.
    Variants can be backtested head-to-head and promoted to the active config.
    """
    __tablename__ = "strategy_variants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Identity
    name = Column(String(100), nullable=False)             # e.g. "Aggressive Earnings v3"
    description = Column(Text, nullable=True)
    user_id = Column(String(50), default='default', index=True)

    # Provenance
    source = Column(String(50), nullable=False)            # 'optimization', 'manual', 'ai_discovery'
    source_id = Column(String(100), nullable=True)         # optimization_run.id if applicable
    parent_variant_id = Column(String, nullable=True)      # which variant this evolved from
    version = Column(Integer, default=1)                   # monotonically increments per name

    # Full strategy config (same shape as StrategyConfig params in DB)
    config = Column(JSON, nullable=False)

    # Backtest performance (populated after backtesting this variant)
    backtest_return_pct = Column(Float, nullable=True)
    backtest_win_rate = Column(Float, nullable=True)
    backtest_profit_factor = Column(Float, nullable=True)
    backtest_total_trades = Column(Integer, nullable=True)
    backtest_run_id = Column(String, nullable=True)        # backtest_reports.id
    backtest_date_range = Column(String(50), nullable=True) # e.g. "2025-01-01 to 2026-03-01"

    # AI analysis summary for this variant
    ai_summary = Column(Text, nullable=True)               # Why this variant is promising
    ai_proposed_changes = Column(JSON, nullable=True)      # What the AI changed vs parent

    # Lifecycle
    is_active = Column(Boolean, default=False)             # Is this the live config?
    is_favorite = Column(Boolean, default=False)           # User starred
    is_archived = Column(Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'name': self.name,
            'description': self.description,
            'source': self.source,
            'source_id': self.source_id,
            'parent_variant_id': self.parent_variant_id,
            'version': self.version,
            'config': self.config,
            'backtest_return_pct': self.backtest_return_pct,
            'backtest_win_rate': self.backtest_win_rate,
            'backtest_profit_factor': self.backtest_profit_factor,
            'backtest_total_trades': self.backtest_total_trades,
            'backtest_run_id': self.backtest_run_id,
            'backtest_date_range': self.backtest_date_range,
            'ai_summary': self.ai_summary,
            'ai_proposed_changes': self.ai_proposed_changes,
            'is_active': self.is_active,
            'is_favorite': self.is_favorite,
            'is_archived': self.is_archived,
        }
