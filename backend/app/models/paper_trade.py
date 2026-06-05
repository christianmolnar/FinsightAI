"""
PaperTrade model (Phase E)

Tracks paper (simulated) trade executions triggered by TradeProposals.
Lifecycle: open → closed (profit_target | stop_loss | max_hold_expired)

P&L from closed trades feeds back into optimization cycles.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
import uuid

from app.database import Base


class PaperTrade(Base):
    """
    A single simulated trade position.

    Created when PaperTradingLoop executes a TradeProposal.
    Closed automatically when profit target, stop loss, or max hold is hit.
    """
    __tablename__ = "paper_trades"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Link to the proposal that triggered this trade
    proposal_id = Column(String, nullable=True, index=True)

    # Which strategy variant was active when this trade was placed (Phase F)
    strategy_variant_id = Column(String, nullable=True, index=True)

    # Trade identity
    symbol = Column(String(10), nullable=False, index=True)
    strategy = Column(String(50), nullable=True)

    # Entry details
    entry_price = Column(Float, nullable=False)
    shares = Column(Float, nullable=False)               # Number of shares (fractional OK)
    position_usd = Column(Float, nullable=False)         # Dollar value at entry

    # AI scoring at entry
    ai_score = Column(Integer, nullable=True)
    ai_reasoning = Column(Text, nullable=True)

    # Exit parameters
    profit_target_pct = Column(Float, nullable=True)     # e.g. 12.0 = 12%
    stop_loss_pct = Column(Float, nullable=True)         # e.g. 5.0 = 5% (stored positive)
    max_hold_until = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String(20), nullable=False, default="open", index=True)
    entry_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Exit details (populated on close)
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    exit_reason = Column(String(50), nullable=True)      # profit_target | stop_loss | max_hold_expired | manual
    return_pct = Column(Float, nullable=True)            # e.g. 8.5 or -4.2
    profit_loss_usd = Column(Float, nullable=True)       # Dollar P&L

    # Full signal payload
    signal_metadata = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "proposal_id": self.proposal_id,
            "strategy_variant_id": self.strategy_variant_id,
            "symbol": self.symbol,
            "strategy": self.strategy,
            "entry_price": self.entry_price,
            "shares": self.shares,
            "position_usd": self.position_usd,
            "ai_score": self.ai_score,
            "profit_target_pct": self.profit_target_pct,
            "stop_loss_pct": self.stop_loss_pct,
            "status": self.status,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat() if self.exit_time else None,
            "exit_reason": self.exit_reason,
            "return_pct": self.return_pct,
            "profit_loss_usd": self.profit_loss_usd,
        }
