"""
TradeProposal model

A signal that passed StrategyExecutor + AITradeScorer and is queued
for execution review. Each live scan cycle writes approved signals here.
The autonomous executor (Phase E) reads pending proposals and places orders.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class TradeProposal(Base):
    """
    Stores AI-approved trade signals from the live scanner.

    Status lifecycle:
        pending   → created by scanner, awaiting execution
        executed  → Alpaca order placed
        rejected  → manually rejected or expired
        expired   → not executed within max_age_hours
    """
    __tablename__ = "trade_proposals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Signal identity
    symbol = Column(String(10), nullable=False, index=True)
    strategy = Column(String(50), nullable=False)          # earnings, seasonality, etc.

    # Signal quality
    score = Column(Integer, nullable=False)                # StrategyExecutor score 0–100
    ai_score = Column(Integer, nullable=True)              # AITradeScorer score 0–100
    ai_reasoning = Column(Text, nullable=True)

    # Execution parameters (from signal's exit_params)
    entry_price = Column(Float, nullable=True)
    profit_target_pct = Column(Float, nullable=True)       # e.g. 8.0 = 8%
    stop_loss_pct = Column(Float, nullable=True)           # e.g. -4.0 = -4%
    max_portfolio_weight = Column(Float, nullable=True)    # e.g. 0.10 = 10%

    # Full signal payload for auditability
    signal_metadata = Column(JSON, nullable=True)
    params_used = Column(JSON, nullable=True)

    # Status
    status = Column(String(20), nullable=False, default='pending', index=True)
    source = Column(String(50), default='autonomous_scanner')
    user_id = Column(String(50), default='default', index=True)

    # Execution tracking (Phase E)
    alpaca_order_id = Column(String(100), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    execution_price = Column(Float, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'symbol': self.symbol,
            'strategy': self.strategy,
            'score': self.score,
            'ai_score': self.ai_score,
            'ai_reasoning': self.ai_reasoning,
            'entry_price': self.entry_price,
            'profit_target_pct': self.profit_target_pct,
            'stop_loss_pct': self.stop_loss_pct,
            'max_portfolio_weight': self.max_portfolio_weight,
            'signal_metadata': self.signal_metadata,
            'status': self.status,
            'source': self.source,
            'alpaca_order_id': self.alpaca_order_id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_price': self.execution_price,
        }
