"""
Database models for backtest optimization runs.

Tracks optimization history, best configurations, and provenance.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class OptimizationRun(Base):
    """
    Stores historical optimization runs with full configuration and results.
    
    This allows users to:
    - Compare multiple optimization runs
    - Apply optimized settings to Strategy Config
    - Track provenance of current strategy settings
    """
    __tablename__ = "optimization_runs"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User tracking
    user_id = Column(String, nullable=True, index=True)
    
    # Optimization metadata
    name = Column(String, nullable=True)  # User-friendly name
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Input configuration
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    strategies = Column(JSON, nullable=True)  # List of strategy names
    
    # Initial parameters
    initial_params = Column(JSON, nullable=False)  # Full initial config
    
    # Optimization settings
    max_iterations = Column(Integer, default=5)
    min_improvement_threshold = Column(Float, default=0.02)
    ai_provider = Column(String, default='anthropic')
    
    # Results
    initial_return_pct = Column(Float, nullable=False)
    best_return_pct = Column(Float, nullable=False)
    total_improvement = Column(Float, nullable=False)
    total_iterations = Column(Integer, nullable=False)
    converged = Column(Boolean, default=False)
    
    # Best configuration found
    best_config = Column(JSON, nullable=False)
    
    # Iteration history (full timeline)
    iterations = Column(JSON, nullable=False)  # Array of iteration data
    
    # Status tracking
    is_applied = Column(Boolean, default=False)  # Applied to Strategy Config?
    applied_at = Column(DateTime, nullable=True)
    is_favorite = Column(Boolean, default=False)  # User starred this run
    
    # Performance summary
    total_time_seconds = Column(Float, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'strategies': self.strategies,
            'initial_params': self.initial_params,
            'max_iterations': self.max_iterations,
            'min_improvement_threshold': self.min_improvement_threshold,
            'ai_provider': self.ai_provider,
            'initial_return_pct': self.initial_return_pct,
            'best_return_pct': self.best_return_pct,
            'total_improvement': self.total_improvement,
            'total_iterations': self.total_iterations,
            'converged': self.converged,
            'best_config': self.best_config,
            'iterations': self.iterations,
            'is_applied': self.is_applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'is_favorite': self.is_favorite,
            'total_time_seconds': self.total_time_seconds
        }


class StrategyConfigSnapshot(Base):
    """
    Tracks changes to Strategy Config with provenance.
    
    Records:
    - What changed
    - When it changed
    - Why it changed (manual edit, optimization, calibration, etc.)
    """
    __tablename__ = "strategy_config_snapshots"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User tracking
    user_id = Column(String, nullable=True, index=True)
    
    # Snapshot metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String, nullable=False)  # 'optimization', 'calibration', 'manual'
    source_id = Column(String, nullable=True)  # optimization_run.id or backtest_id
    
    # Configuration snapshot
    config = Column(JSON, nullable=False)  # Full strategy config at this point
    
    # Changes made
    changes = Column(JSON, nullable=False)  # Array of {param, old_value, new_value, reason}
    
    # Validation
    is_active = Column(Boolean, default=True)  # Is this the current config?
    
    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source': self.source,
            'source_id': self.source_id,
            'config': self.config,
            'changes': self.changes,
            'is_active': self.is_active
        }
