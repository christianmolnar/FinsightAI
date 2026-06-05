"""
Paper Trading Loop (Phase E)

Autonomous loop:
    1. Read pending TradeProposals from DB
    2. Apply position sizing guardrails
    3. Execute as paper trades (no real money)
    4. Track open positions and check exits (profit target / stop loss)
    5. Record P&L → feeds back into next optimization cycle
    6. Send Pushover alerts for AI-approved entries and exits

This is the bridge between "we have a signal" and "we have a position".
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ── Default guardrails (overridable per run) ──────────────────────────────────
DEFAULT_GUARDRAILS = {
    "max_single_position_pct": 5.0,       # Max % of portfolio in any one trade
    "max_portfolio_exposure_pct": 40.0,   # Max % of portfolio in open positions
    "max_daily_trades": 5,                # Max new paper trades per day
    "min_ai_score": 60,                   # Minimum AI score to execute
    "max_hold_days": 21,                  # Force-close positions after this many days
    "paper_portfolio_size": 10000.0,      # Virtual portfolio size (USD)
}


class PaperTradingLoop:
    """
    Reads pending TradeProposal rows and executes them as paper trades.
    Checks existing open positions for profit target / stop loss exits.
    """

    def __init__(
        self,
        db: Session,
        guardrails: Optional[Dict] = None,
        enable_alerts: bool = True,
    ):
        self.db = db
        self.guardrails = {**DEFAULT_GUARDRAILS, **(guardrails or {})}
        self.enable_alerts = enable_alerts
        self._alert_service = None

    # ── Main Loop ─────────────────────────────────────────────────────────────

    async def run_cycle(self) -> Dict:
        """
        Run one full cycle: check exits on open positions, then enter new ones.

        Returns summary dict of what happened.
        """
        from app.models.trade_proposal import TradeProposal
        from app.models.paper_trade import PaperTrade

        cycle_start = datetime.now(timezone.utc)
        results = {
            "timestamp": cycle_start.isoformat(),
            "exits_processed": 0,
            "entries_attempted": 0,
            "entries_executed": 0,
            "entries_rejected": [],
            "portfolio_exposure_pct": 0.0,
            "errors": [],
        }

        try:
            # Step 1: Process exits on open positions
            exits = await self._process_exits()
            results["exits_processed"] = exits

            # Step 2: Check daily trade cap
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            trades_today = self.db.query(PaperTrade).filter(
                PaperTrade.entry_time >= today_start,
                PaperTrade.status == "open",
            ).count()

            if trades_today >= self.guardrails["max_daily_trades"]:
                logger.info(f"⚠️ Daily trade cap reached ({trades_today}). Skipping entries.")
                results["entries_rejected"].append(
                    f"Daily cap {self.guardrails['max_daily_trades']} reached"
                )
                return results

            # Step 3: Calculate current exposure
            portfolio_size = self.guardrails["paper_portfolio_size"]
            open_value = self._calculate_open_exposure()
            exposure_pct = (open_value / portfolio_size) * 100
            results["portfolio_exposure_pct"] = round(exposure_pct, 2)

            if exposure_pct >= self.guardrails["max_portfolio_exposure_pct"]:
                logger.info(f"⚠️ Portfolio exposure {exposure_pct:.1f}% at cap. Skipping entries.")
                results["entries_rejected"].append(
                    f"Exposure cap {self.guardrails['max_portfolio_exposure_pct']}% reached"
                )
                return results

            # Step 4: Process pending proposals
            pending = (
                self.db.query(TradeProposal)
                .filter(TradeProposal.status == "pending")
                .filter(
                    TradeProposal.ai_score >= self.guardrails["min_ai_score"]
                    if TradeProposal.ai_score is not None
                    else True
                )
                .order_by(TradeProposal.ai_score.desc())
                .limit(self.guardrails["max_daily_trades"] - trades_today)
                .all()
            )

            results["entries_attempted"] = len(pending)
            for proposal in pending:
                executed, reason = await self._execute_entry(proposal, exposure_pct)
                if executed:
                    results["entries_executed"] += 1
                    # Refresh exposure
                    open_value = self._calculate_open_exposure()
                    exposure_pct = (open_value / portfolio_size) * 100
                else:
                    results["entries_rejected"].append(f"{proposal.symbol}: {reason}")

        except Exception as e:
            logger.error(f"PaperTradingLoop cycle error: {e}")
            results["errors"].append(str(e))

        logger.info(
            f"📊 Paper loop cycle: {results['exits_processed']} exits, "
            f"{results['entries_executed']}/{results['entries_attempted']} entries, "
            f"{results['portfolio_exposure_pct']:.1f}% exposure"
        )
        return results

    # ── Entry Execution ───────────────────────────────────────────────────────

    async def _execute_entry(
        self, proposal, current_exposure_pct: float
    ) -> Tuple[bool, str]:
        """
        Validate guardrails and execute a paper trade entry.
        Returns (success, reason).
        """
        from app.models.paper_trade import PaperTrade

        symbol = proposal.symbol
        portfolio_size = self.guardrails["paper_portfolio_size"]

        # Guardrail: AI score
        if proposal.ai_score is not None and proposal.ai_score < self.guardrails["min_ai_score"]:
            return False, f"AI score {proposal.ai_score} < min {self.guardrails['min_ai_score']}"

        # Guardrail: no duplicate open position
        existing = (
            self.db.query(PaperTrade)
            .filter(PaperTrade.symbol == symbol, PaperTrade.status == "open")
            .first()
        )
        if existing:
            # Mark proposal as rejected (duplicate)
            proposal.status = "rejected"
            proposal.rejection_reason = "Duplicate open position"
            self.db.commit()
            return False, "Duplicate open position"

        # Compute position size
        weight_pct = min(
            proposal.max_portfolio_weight or self.guardrails["max_single_position_pct"],
            self.guardrails["max_single_position_pct"],
        )
        new_exposure_pct = current_exposure_pct + weight_pct
        if new_exposure_pct > self.guardrails["max_portfolio_exposure_pct"]:
            return False, (
                f"Would exceed exposure cap: {new_exposure_pct:.1f}% > "
                f"{self.guardrails['max_portfolio_exposure_pct']}%"
            )

        position_usd = portfolio_size * weight_pct / 100.0
        entry_price = proposal.entry_price or await self._get_current_price(symbol)
        if not entry_price:
            return False, "Could not determine entry price"

        shares = position_usd / entry_price

        # Create paper trade record
        trade = PaperTrade(
            id=str(uuid.uuid4()),
            proposal_id=proposal.id,
            symbol=symbol,
            strategy=proposal.strategy,
            entry_price=entry_price,
            shares=shares,
            position_usd=position_usd,
            ai_score=proposal.ai_score,
            ai_reasoning=proposal.ai_reasoning,
            profit_target_pct=proposal.profit_target_pct,
            stop_loss_pct=proposal.stop_loss_pct,
            status="open",
            entry_time=datetime.now(timezone.utc),
            max_hold_until=datetime.now(timezone.utc) + timedelta(days=self.guardrails["max_hold_days"]),
            signal_metadata=proposal.signal_metadata,
        )
        self.db.add(trade)
        proposal.status = "executed"
        proposal.executed_at = datetime.now(timezone.utc)
        proposal.execution_price = entry_price
        self.db.commit()

        logger.info(
            f"✅ Paper trade ENTERED: {symbol} @ ${entry_price:.2f} | "
            f"${position_usd:.0f} ({weight_pct:.1f}%) | AI={proposal.ai_score}"
        )

        # Alert
        await self._send_alert(
            f"📈 Paper trade entered: {symbol} @ ${entry_price:.2f}\n"
            f"Strategy: {proposal.strategy} | AI score: {proposal.ai_score}\n"
            f"Target: +{proposal.profit_target_pct}% | Stop: -{proposal.stop_loss_pct}%"
        )
        return True, "executed"

    # ── Exit Processing ───────────────────────────────────────────────────────

    async def _process_exits(self) -> int:
        """
        Check open paper trades for profit target, stop loss, or max hold expiry.
        Returns number of positions closed.
        """
        from app.models.paper_trade import PaperTrade

        open_trades = (
            self.db.query(PaperTrade).filter(PaperTrade.status == "open").all()
        )
        closed = 0
        now = datetime.now(timezone.utc)

        for trade in open_trades:
            current_price = await self._get_current_price(trade.symbol)
            if not current_price:
                continue

            return_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
            exit_reason = None

            if trade.profit_target_pct and return_pct >= trade.profit_target_pct:
                exit_reason = "profit_target"
            elif trade.stop_loss_pct and return_pct <= -abs(trade.stop_loss_pct):
                exit_reason = "stop_loss"
            elif trade.max_hold_until and now >= trade.max_hold_until.replace(tzinfo=timezone.utc):
                exit_reason = "max_hold_expired"

            if exit_reason:
                trade.status = "closed"
                trade.exit_price = current_price
                trade.exit_time = now
                trade.exit_reason = exit_reason
                trade.return_pct = return_pct
                trade.profit_loss_usd = trade.shares * (current_price - trade.entry_price)
                self.db.commit()
                closed += 1

                emoji = "✅" if return_pct > 0 else "❌"
                logger.info(
                    f"{emoji} Paper trade CLOSED: {trade.symbol} | "
                    f"{return_pct:+.1f}% | ${trade.profit_loss_usd:+.0f} | {exit_reason}"
                )
                await self._send_alert(
                    f"{emoji} Paper trade closed: {trade.symbol} {return_pct:+.1f}%\n"
                    f"Reason: {exit_reason} | P&L: ${trade.profit_loss_usd:+.0f}"
                )

        return closed

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _calculate_open_exposure(self) -> float:
        """Sum of position_usd across all open paper trades."""
        try:
            from app.models.paper_trade import PaperTrade
            from sqlalchemy import func as sqlfunc
            result = (
                self.db.query(sqlfunc.sum(PaperTrade.position_usd))
                .filter(PaperTrade.status == "open")
                .scalar()
            )
            return float(result or 0.0)
        except Exception:
            return 0.0

    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current market price using yfinance."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if hist.empty:
                return None
            return float(hist["Close"].iloc[-1])
        except Exception as e:
            logger.debug(f"Price fetch failed for {symbol}: {e}")
            return None

    async def _send_alert(self, message: str):
        """Send Pushover notification if available."""
        if not self.enable_alerts:
            return
        try:
            from services.pushover_service import PushoverService
            svc = PushoverService()
            svc.send(title="FinsightAI Paper Trade", message=message)
        except Exception:
            pass  # Alerts are non-critical

    # ── Performance Summary ───────────────────────────────────────────────────

    def get_performance_summary(self) -> Dict:
        """
        Aggregate closed paper trade P&L for feeding back into optimization.
        Returns metrics suitable for BacktestOptimizer input.
        """
        try:
            from app.models.paper_trade import PaperTrade

            closed = (
                self.db.query(PaperTrade).filter(PaperTrade.status == "closed").all()
            )
            if not closed:
                return {"total_trades": 0, "win_rate": 0, "total_return_usd": 0}

            wins = [t for t in closed if (t.return_pct or 0) > 0]
            total_pnl = sum(t.profit_loss_usd or 0 for t in closed)
            win_rate = len(wins) / len(closed) * 100

            return {
                "total_trades": len(closed),
                "wins": len(wins),
                "losses": len(closed) - len(wins),
                "win_rate_pct": round(win_rate, 1),
                "total_return_usd": round(total_pnl, 2),
                "total_return_pct": round(
                    total_pnl / self.guardrails["paper_portfolio_size"] * 100, 2
                ),
                "avg_win_pct": round(
                    sum(t.return_pct or 0 for t in wins) / len(wins), 2
                ) if wins else 0,
                "avg_loss_pct": round(
                    sum(t.return_pct or 0 for t in closed if (t.return_pct or 0) <= 0)
                    / max(len(closed) - len(wins), 1), 2
                ),
                "by_strategy": self._group_by_strategy(closed),
            }
        except Exception as e:
            logger.error(f"Performance summary error: {e}")
            return {"error": str(e)}

    def _group_by_strategy(self, trades) -> Dict:
        from collections import defaultdict
        groups = defaultdict(list)
        for t in trades:
            groups[t.strategy or "unknown"].append(t.return_pct or 0)
        return {
            strat: {
                "count": len(rets),
                "avg_return_pct": round(sum(rets) / len(rets), 2) if rets else 0,
            }
            for strat, rets in groups.items()
        }
