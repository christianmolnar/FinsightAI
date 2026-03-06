"""
Backtest Models

Models for backtesting system, calibration, and performance tracking.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date, JSON, CheckConstraint, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel
from decimal import Decimal

from app.database import Base


# ========================================
# DATABASE MODELS (SQLAlchemy)
# ========================================

class BacktestReport(Base):
    """
    Stores every backtest run with full results and recommendations
    
    Retention: 1 year (auto-expires)
    """
    __tablename__ = "backtest_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default='default', index=True)
    run_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Configuration snapshot at time of backtest
    config_snapshot = Column(JSON, nullable=False)  # All strategy/risk/filter settings
    
    # Backtest parameters
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Float, default=100000.00)
    
    # Overall performance metrics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)  # 58.5% = 58.5
    total_return = Column(Float)  # 8.63% = 8.63
    final_portfolio_value = Column(Float)
    max_drawdown = Column(Float)  # Calculated during backtest
    sharpe_ratio = Column(Float, nullable=True)  # Risk-adjusted return
    profit_factor = Column(Float, nullable=True)  # Total wins / Total losses
    
    # Trade statistics
    avg_win_size = Column(Float, nullable=True)
    avg_loss_size = Column(Float, nullable=True)
    largest_win = Column(Float, nullable=True)
    largest_loss = Column(Float, nullable=True)
    avg_hold_days = Column(Float, nullable=True)
    
    # Strategy breakdown (JSON array)
    strategy_performance = Column(JSON, nullable=True)
    # Example: [{"strategy": "technical_breakout", "trades": 345, "win_rate": 62.1, ...}]
    
    # Daily P&L for drawdown calculation
    daily_pnl = Column(JSON, nullable=True)  # {"2025-12-01": 234.50, ...}
    
    # Generated recommendations
    recommendations = Column(JSON, nullable=True)
    # Example: [{"parameter": "earnings.profitTarget", "current": 12, "recommended": 14, ...}]
    
    # User interaction
    applied = Column(Boolean, default=False)  # Did user apply any recommendations?
    applied_recommendations = Column(JSON, nullable=True)  # Which ones were applied
    user_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), 
                       server_default=func.text("NOW() + INTERVAL '1 year'"))
    
    __table_args__ = (
        CheckConstraint('win_rate >= 0 AND win_rate <= 100', name='valid_win_rate'),
    )


class ConfigChange(Base):
    """
    Tracks every time user changes strategy configuration
    
    Used for performance attribution and historical analysis
    """
    __tablename__ = "config_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default='default', index=True)
    change_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Configuration snapshots
    before_config = Column(JSON, nullable=False)  # Full config before change
    after_config = Column(JSON, nullable=False)   # Full config after change
    changed_parameters = Column(JSON, nullable=True)  # Just the diffs
    # Example: [{"parameter": "earnings.profitTarget", "before": 12, "after": 14, ...}]
    
    # What triggered this change?
    trigger_type = Column(String(50), nullable=True)  # 'manual', 'backtest_calibration', 'ai_optimize'
    backtest_report_id = Column(Integer, ForeignKey('backtest_reports.id'), nullable=True, index=True)
    
    # Performance tracking (calculated later after sufficient time has passed)
    performance_before = Column(JSON, nullable=True)  # Metrics from period before this config
    performance_after = Column(JSON, nullable=True)   # Metrics from period after this config
    # Calculated after 30-90 days
    
    # User notes
    user_notes = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PortfolioSnapshot(Base):
    """
    Daily portfolio snapshots for performance tracking
    
    Used to generate timeline graphs and track config impact
    """
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default='default', index=True)
    account_type = Column(String(20), nullable=False, index=True)  # 'paper' or 'live'
    snapshot_date = Column(Date, nullable=False, index=True)
    
    # Portfolio metrics
    portfolio_value = Column(Float, nullable=False)
    cash_balance = Column(Float, nullable=False)
    positions_value = Column(Float, nullable=False)
    
    # Daily performance
    daily_return = Column(Float, nullable=True)  # % return for this day
    daily_pnl = Column(Float, nullable=True)    # $ P&L for this day
    
    # Position count
    open_positions = Column(Integer, default=0)
    
    # Link to current config
    config_change_id = Column(Integer, ForeignKey('config_changes.id'), nullable=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("account_type IN ('paper', 'live')", name='valid_account_type'),
    )


# ========================================
# PYDANTIC MODELS (API Request/Response)
# ========================================

class CalibrationRecommendation(BaseModel):
    """Single recommendation from backtest calibration"""
    parameter: str  # e.g., "earnings.profitTarget"
    category: str  # 'strategy', 'risk', 'technical'
    current_value: float
    recommended_value: float
    reasoning: str
    confidence: float  # 0.0 to 1.0
    expected_improvement: str  # e.g., "+1.2% annual return"
    
    class Config:
        json_schema_extra = {
            "example": {
                "parameter": "earnings.profitTarget",
                "category": "strategy",
                "current_value": 12.0,
                "recommended_value": 14.0,
                "reasoning": "Average winning trade was +15%, leaving money on table",
                "confidence": 0.85,
                "expected_improvement": "+1.2% annual return"
            }
        }


class BacktestMetrics(BaseModel):
    """Overall backtest performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    final_portfolio_value: float
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    profit_factor: Optional[float] = None
    avg_win_size: Optional[float] = None
    avg_loss_size: Optional[float] = None
    largest_win: Optional[float] = None
    largest_loss: Optional[float] = None
    avg_hold_days: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_trades": 874,
                "winning_trades": 511,
                "losing_trades": 363,
                "win_rate": 58.5,
                "total_return": 8.63,
                "final_portfolio_value": 108634.13,
                "max_drawdown": 5.2,
                "sharpe_ratio": 1.85,
                "profit_factor": 1.41
            }
        }


class StrategyPerformance(BaseModel):
    """Performance breakdown for a single strategy"""
    strategy: str
    trades: int
    win_rate: float
    total_return: float
    profit_factor: float
    avg_win: float
    avg_loss: float


class CalibrationRequest(BaseModel):
    """Request to run backtest calibration"""
    days: int = 90  # Backtest period
    initial_capital: float = 100000.00
    use_current_config: bool = True  # Use current strategy config
    
    class Config:
        json_schema_extra = {
            "example": {
                "days": 90,
                "initial_capital": 100000.00,
                "use_current_config": True
            }
        }


class CalibrationResponse(BaseModel):
    """Response from backtest calibration"""
    backtest_report_id: int
    run_date: datetime
    metrics: BacktestMetrics
    strategy_performance: List[StrategyPerformance]
    recommendations: List[CalibrationRecommendation]
    config_snapshot: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "backtest_report_id": 123,
                "run_date": "2026-03-02T10:30:00Z",
                "metrics": {
                    "total_trades": 874,
                    "win_rate": 58.5,
                    "total_return": 8.63
                },
                "recommendations": [
                    {
                        "parameter": "earnings.profitTarget",
                        "recommended_value": 14.0,
                        "reasoning": "Avg winning trade +15%"
                    }
                ]
            }
        }


class ApplyRecommendationsRequest(BaseModel):
    """Request to apply calibration recommendations"""
    backtest_report_id: int
    applied_recommendations: List[str]  # List of parameter names to apply
    user_notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "backtest_report_id": 123,
                "applied_recommendations": [
                    "earnings.profitTarget",
                    "riskManagement.maxSinglePosition"
                ],
                "user_notes": "Applying after reviewing results"
            }
        }


class ConfigChangeResponse(BaseModel):
    """Response after applying config changes"""
    config_change_id: int
    change_date: datetime
    changed_parameters: List[Dict]
    backtest_report_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "config_change_id": 456,
                "change_date": "2026-03-02T10:35:00Z",
                "changed_parameters": [
                    {
                        "parameter": "earnings.profitTarget",
                        "before": 12.0,
                        "after": 14.0
                    }
                ],
                "backtest_report_id": 123
            }
        }


class PortfolioSnapshotCreate(BaseModel):
    """Data for creating a portfolio snapshot"""
    account_type: str  # 'paper' or 'live'
    portfolio_value: float
    cash_balance: float
    positions_value: float
    open_positions: int
    daily_return: Optional[float] = None
    daily_pnl: Optional[float] = None
