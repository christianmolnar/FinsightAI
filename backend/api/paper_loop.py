"""
Paper Trading Loop API (Phase E)

Endpoints for controlling the autonomous paper trading loop:
  - POST /api/paper-loop/cycle       — Run one scan/execute/exit cycle
  - GET  /api/paper-loop/positions   — All open paper trades
  - GET  /api/paper-loop/history     — All closed paper trades
  - GET  /api/paper-loop/performance — Aggregate performance summary
  - POST /api/paper-loop/close/{id}  — Manually close a position
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.database import get_db
from app.models.paper_trade import PaperTrade
from services.paper_trading_loop import PaperTradingLoop, DEFAULT_GUARDRAILS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/paper-loop", tags=["paper_trading_loop"])


# ── Request Models ────────────────────────────────────────────────────────────

class RunCycleRequest(BaseModel):
    guardrails: Optional[dict] = None
    enable_alerts: bool = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/cycle")
async def run_cycle(request: RunCycleRequest, db: Session = Depends(get_db)):
    """
    Run one full paper trading cycle:
    1. Close any positions that hit profit target / stop loss / max hold
    2. Execute pending TradeProposals that pass guardrails
    """
    loop = PaperTradingLoop(
        db=db,
        guardrails=request.guardrails,
        enable_alerts=request.enable_alerts,
    )
    result = await loop.run_cycle()
    return result


@router.get("/positions")
def get_open_positions(db: Session = Depends(get_db)):
    """Get all open paper trade positions."""
    trades = db.query(PaperTrade).filter(PaperTrade.status == "open").order_by(
        PaperTrade.entry_time.desc()
    ).all()
    return {"positions": [t.to_dict() for t in trades]}


@router.get("/history")
def get_trade_history(
    limit: int = 50,
    strategy: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get closed paper trade history."""
    query = db.query(PaperTrade).filter(PaperTrade.status == "closed")
    if strategy:
        query = query.filter(PaperTrade.strategy == strategy)
    trades = query.order_by(PaperTrade.exit_time.desc()).limit(limit).all()
    return {"trades": [t.to_dict() for t in trades]}


@router.get("/performance")
def get_performance(db: Session = Depends(get_db)):
    """
    Aggregate performance summary across all closed paper trades.
    This is the data that feeds back into the next optimization cycle.
    """
    loop = PaperTradingLoop(db=db)
    return loop.get_performance_summary()


@router.post("/close/{trade_id}")
def close_position_manually(trade_id: str, db: Session = Depends(get_db)):
    """Manually close an open paper trade position."""
    trade = db.query(PaperTrade).filter(PaperTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    if trade.status != "open":
        raise HTTPException(status_code=400, detail=f"Trade is not open (status: {trade.status})")

    from datetime import datetime, timezone
    import asyncio

    # Get current price for P&L calculation
    async def _close():
        loop = PaperTradingLoop(db=db)
        price = await loop._get_current_price(trade.symbol)
        return price

    try:
        price = asyncio.get_event_loop().run_until_complete(_close())
    except RuntimeError:
        price = trade.entry_price  # Fallback if no event loop

    return_pct = ((price - trade.entry_price) / trade.entry_price * 100) if price else 0
    trade.status = "closed"
    trade.exit_price = price
    trade.exit_time = datetime.now(timezone.utc)
    trade.exit_reason = "manual"
    trade.return_pct = round(return_pct, 2)
    trade.profit_loss_usd = round(trade.shares * ((price or trade.entry_price) - trade.entry_price), 2)
    db.commit()

    return {"success": True, "trade": trade.to_dict()}


@router.get("/guardrails")
def get_guardrails():
    """Return current default guardrail configuration."""
    return DEFAULT_GUARDRAILS
