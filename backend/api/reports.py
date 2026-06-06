"""
Reports API (Phase F.8)

Strategy performance history and Paper vs Live comparison.

GET /api/reports/strategy-history   — all activated variants with computed P&L per period
GET /api/reports/paper-vs-live      — side-by-side comparison for variants run in both modes
GET /api/reports/summary            — top-line totals across all periods
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
from datetime import datetime, timezone

from app.database import get_db
from app.models.strategy_variant import StrategyVariant
from app.models.paper_trade import PaperTrade

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _compute_period_stats(trades):
    """Given a list of closed PaperTrade rows, return aggregate stats."""
    if not trades:
        return {"trade_count": 0, "win_rate": None, "total_pnl": 0.0, "avg_return_pct": None, "best_trade_pct": None, "worst_trade_pct": None}
    wins = [t for t in trades if (t.return_pct or 0) > 0]
    returns = [t.return_pct or 0 for t in trades]
    pnl = [t.profit_loss_usd or 0 for t in trades]
    return {
        "trade_count": len(trades),
        "win_count": len(wins),
        "loss_count": len(trades) - len(wins),
        "win_rate": round(len(wins) / len(trades), 3),
        "total_pnl": round(sum(pnl), 2),
        "avg_return_pct": round(sum(returns) / len(returns), 2),
        "best_trade_pct": round(max(returns), 2),
        "worst_trade_pct": round(min(returns), 2),
    }


@router.get("/strategy-history")
def get_strategy_history(user_id: str = "default", db: Session = Depends(get_db)):
    """
    All strategy variants that have ever been activated, with their performance stats.
    Each row = one strategy period (a variant + its date range + all trades during that period).
    """
    variants = (
        db.query(StrategyVariant)
        .filter(
            StrategyVariant.user_id == user_id,
            StrategyVariant.activated_at.isnot(None),
            StrategyVariant.is_archived == False,
        )
        .order_by(StrategyVariant.activated_at.desc())
        .all()
    )

    result = []
    for v in variants:
        trades = (
            db.query(PaperTrade)
            .filter(
                PaperTrade.strategy_variant_id == v.id,
                PaperTrade.status == "closed",
            )
            .all()
        )
        open_count = (
            db.query(func.count(PaperTrade.id))
            .filter(PaperTrade.strategy_variant_id == v.id, PaperTrade.status == "open")
            .scalar() or 0
        )

        stats = _compute_period_stats(trades)

        # Determine how long this period ran
        start = v.activated_at
        end = v.deactivated_at or (datetime.now(timezone.utc) if v.is_active else None)
        days_running = None
        if start and end:
            delta = end - (start.replace(tzinfo=timezone.utc) if start.tzinfo is None else start)
            days_running = delta.days

        result.append({
            "id": v.id,
            "name": v.name,
            "version": v.version,
            "mode": v.mode,
            "source": v.source,
            "is_active": v.is_active,
            "is_halted": v.is_halted,
            "activated_at": v.activated_at.isoformat() if v.activated_at else None,
            "deactivated_at": v.deactivated_at.isoformat() if v.deactivated_at else None,
            "days_running": days_running,
            "open_positions": open_count,
            "backtest_return_pct": v.backtest_return_pct,
            "backtest_win_rate": v.backtest_win_rate,
            **stats,
        })

    return result


@router.get("/paper-vs-live")
def get_paper_vs_live(user_id: str = "default", db: Session = Depends(get_db)):
    """
    Side-by-side comparison: for each strategy name, show paper performance vs live performance.
    Useful for answering: "did live match paper predictions?"
    """
    variants = (
        db.query(StrategyVariant)
        .filter(
            StrategyVariant.user_id == user_id,
            StrategyVariant.activated_at.isnot(None),
        )
        .all()
    )

    # Group by strategy name
    by_name = defaultdict(lambda: {"paper": [], "live": []})
    for v in variants:
        mode = v.mode or "paper"
        trades = (
            db.query(PaperTrade)
            .filter(PaperTrade.strategy_variant_id == v.id, PaperTrade.status == "closed")
            .all()
        )
        if mode in ("paper", "live"):
            by_name[v.name][mode].append({
                "variant_id": v.id,
                "version": v.version,
                "activated_at": v.activated_at.isoformat() if v.activated_at else None,
                "deactivated_at": v.deactivated_at.isoformat() if v.deactivated_at else None,
                "stats": _compute_period_stats(trades),
            })

    # Only include strategies that have BOTH paper and live records
    comparison = []
    for name, modes in by_name.items():
        comparison.append({
            "strategy_name": name,
            "has_paper": len(modes["paper"]) > 0,
            "has_live": len(modes["live"]) > 0,
            "paper": modes["paper"],
            "live": modes["live"],
        })

    comparison.sort(key=lambda x: (not x["has_live"], not x["has_paper"], x["strategy_name"]))
    return comparison


@router.get("/summary")
def get_summary(user_id: str = "default", db: Session = Depends(get_db)):
    """Top-line totals across all strategy periods."""
    all_closed = db.query(PaperTrade).filter(PaperTrade.status == "closed").all()
    all_open = db.query(func.count(PaperTrade.id)).filter(PaperTrade.status == "open").scalar() or 0

    paper_trades = [t for t in all_closed if True]  # all for now; scope by user when user_id is on PaperTrade
    stats = _compute_period_stats(paper_trades)

    active_paper = db.query(StrategyVariant).filter(
        StrategyVariant.mode == "paper", StrategyVariant.is_active == True
    ).first()
    active_live = db.query(StrategyVariant).filter(
        StrategyVariant.mode == "live", StrategyVariant.is_active == True
    ).first()

    return {
        **stats,
        "open_positions": all_open,
        "active_paper_strategy": active_paper.name if active_paper else None,
        "active_live_strategy": active_live.name if active_live else None,
        "total_strategy_periods": db.query(func.count(StrategyVariant.id)).filter(
            StrategyVariant.activated_at.isnot(None)
        ).scalar() or 0,
    }
