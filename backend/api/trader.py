"""
Trader Control API (Phase F)

Endpoints for controlling the autonomous trader in paper or live mode.

POST /api/trader/{mode}/halt        — immediately halt the trader
POST /api/trader/{mode}/resume      — clear halt, resume normal cycles
POST /api/trader/{mode}/cycle       — manually trigger one cycle
GET  /api/trader/{mode}/status      — mode, halt state, daily P&L, circuit breakers
GET  /api/trader/{mode}/positions   — open positions for this mode
GET  /api/trader/{mode}/history     — closed trades for active variant
GET  /api/trader/{mode}/performance — aggregate P&L for active variant period
GET  /api/trader/{mode}/guardrails  — all configurable limits
PATCH /api/trader/{mode}/guardrails — update limits live

mode must be 'paper' or 'live'.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Literal, Optional
from pydantic import BaseModel
import logging

from app.database import get_db
from app.models.paper_trade import PaperTrade
from app.models.strategy_variant import StrategyVariant
from services.autonomous_trader import AutonomousTrader, DEFAULT_GUARDRAILS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trader", tags=["autonomous_trader"])

ValidMode = Literal["paper", "live"]


class HaltRequest(BaseModel):
    reason: str = "manual"


class GuardrailsUpdate(BaseModel):
    max_single_position_pct: Optional[float] = None
    max_portfolio_exposure_pct: Optional[float] = None
    max_daily_trades: Optional[int] = None
    min_ai_score: Optional[int] = None
    max_hold_days: Optional[int] = None
    paper_portfolio_size: Optional[float] = None
    max_daily_loss_pct: Optional[float] = None
    max_total_loss_pct: Optional[float] = None


def _get_trader(mode: str, db: Session) -> AutonomousTrader:
    if mode not in ("paper", "live"):
        raise HTTPException(status_code=400, detail="mode must be 'paper' or 'live'")
    return AutonomousTrader(mode=mode, db=db)


# ── Halt / Resume ─────────────────────────────────────────────────────────────

@router.post("/{mode}/halt")
def halt_trader(
    mode: str = Path(...),
    body: HaltRequest = HaltRequest(),
    db: Session = Depends(get_db),
):
    """Immediately halt the trader. No new entries. Open positions run to natural exit."""
    trader = _get_trader(mode, db)
    result = trader.halt(body.reason)
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


@router.post("/{mode}/resume")
def resume_trader(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Clear halt flag. Trader resumes normal cycle execution."""
    trader = _get_trader(mode, db)
    result = trader.resume()
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("error"))
    return result


# ── Manual Cycle ──────────────────────────────────────────────────────────────

@router.post("/{mode}/cycle")
async def run_cycle(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Manually trigger one scan → score → execute → exit cycle."""
    trader = _get_trader(mode, db)
    return await trader.run_cycle()


# ── Status ────────────────────────────────────────────────────────────────────

@router.get("/{mode}/status")
def get_status(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Return trader state: active variant, halt state, daily P&L, circuit breaker status."""
    trader = _get_trader(mode, db)
    return trader.get_status()


# ── Positions ─────────────────────────────────────────────────────────────────

@router.get("/{mode}/positions")
def get_positions(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Open positions for the active variant in this mode."""
    trader = _get_trader(mode, db)
    variant = trader._get_active_variant()
    if not variant:
        return []
    trades = (
        db.query(PaperTrade)
        .filter(PaperTrade.status == "open", PaperTrade.strategy_variant_id == variant.id)
        .order_by(PaperTrade.entry_time.desc())
        .all()
    )
    return [t.to_dict() for t in trades]


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/{mode}/history")
def get_history(
    mode: str = Path(...),
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Closed trades for the active variant period."""
    trader = _get_trader(mode, db)
    variant = trader._get_active_variant()
    if not variant:
        return []
    trades = (
        db.query(PaperTrade)
        .filter(PaperTrade.status == "closed", PaperTrade.strategy_variant_id == variant.id)
        .order_by(PaperTrade.exit_time.desc())
        .limit(limit)
        .all()
    )
    return [t.to_dict() for t in trades]


# ── Performance ───────────────────────────────────────────────────────────────

@router.get("/{mode}/performance")
def get_performance(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Aggregate P&L for the active variant period."""
    trader = _get_trader(mode, db)
    return trader.get_performance_summary()


# ── Guardrails ────────────────────────────────────────────────────────────────

@router.get("/{mode}/guardrails")
def get_guardrails(
    mode: str = Path(...),
    db: Session = Depends(get_db),
):
    """Return all configurable guardrails + circuit breaker limits."""
    trader = _get_trader(mode, db)
    variant = trader._get_active_variant()
    guardrails = dict(DEFAULT_GUARDRAILS)
    if variant:
        guardrails["max_daily_loss_pct"] = variant.max_daily_loss_pct or guardrails["max_daily_loss_pct"]
        guardrails["max_total_loss_pct"] = variant.max_total_loss_pct or guardrails["max_total_loss_pct"]
    return guardrails


@router.patch("/{mode}/guardrails")
def update_guardrails(
    mode: str = Path(...),
    body: GuardrailsUpdate = GuardrailsUpdate(),
    db: Session = Depends(get_db),
):
    """Update circuit breaker limits live — takes effect on the next cycle."""
    trader = _get_trader(mode, db)
    variant = trader._get_active_variant()
    if not variant:
        raise HTTPException(status_code=404, detail=f"No active {mode} variant")

    if body.max_daily_loss_pct is not None:
        variant.max_daily_loss_pct = body.max_daily_loss_pct
    if body.max_total_loss_pct is not None:
        variant.max_total_loss_pct = body.max_total_loss_pct
    db.commit()

    return {"ok": True, "updated": body.dict(exclude_none=True)}
