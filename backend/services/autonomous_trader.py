"""
AutonomousTrader (Phase F)

One trader, two modes: 'paper' and 'live'.
Identical logic for both — only the execution step differs:
  - paper: creates a PaperTrade row
  - live:  submits an Alpaca order, then creates a LiveTrade row

Operator controls:
  - halt(reason)  → sets is_halted on the active StrategyVariant, blocks all entries
  - resume()      → clears halt, resumes normal operation
  - pause()       → no new entries; open positions run to natural exit

Circuit breakers (evaluated each cycle):
  - max_daily_loss_pct  → auto-halt if today's P&L drops below threshold
  - max_total_loss_pct  → auto-halt if total variant P&L drops below threshold

Every trade is tagged with the active StrategyVariant ID so performance
is always scoped to a specific strategy period.
"""

import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Literal, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# ── Default guardrails ────────────────────────────────────────────────────────
DEFAULT_GUARDRAILS = {
    "max_single_position_pct": 5.0,
    "max_portfolio_exposure_pct": 40.0,
    "max_daily_trades": 5,
    "min_ai_score": 60,
    "max_hold_days": 21,
    "paper_portfolio_size": 10_000.0,
    "max_daily_loss_pct": 5.0,
    "max_total_loss_pct": 15.0,
}


class AutonomousTrader:
    """
    Unified autonomous trader for both paper and live modes.

    Usage:
        trader = AutonomousTrader(mode='paper', db=db)
        result = await trader.run_cycle()
        trader.halt("manual override")
        trader.resume()
    """

    def __init__(
        self,
        mode: Literal["paper", "live"],
        db: Session,
        guardrails: Optional[Dict] = None,
        enable_alerts: bool = True,
    ):
        self.mode = mode
        self.db = db
        self.guardrails = {**DEFAULT_GUARDRAILS, **(guardrails or {})}
        self.enable_alerts = enable_alerts

    # ── Active Variant ────────────────────────────────────────────────────────

    def _get_active_variant(self):
        """Return the currently-active StrategyVariant for this mode, or None."""
        from app.models.strategy_variant import StrategyVariant
        return (
            self.db.query(StrategyVariant)
            .filter(
                StrategyVariant.mode == self.mode,
                StrategyVariant.is_active == True,
                StrategyVariant.is_archived == False,
            )
            .first()
        )

    # ── Operator Controls ─────────────────────────────────────────────────────

    def halt(self, reason: str = "manual") -> Dict:
        """Immediately halt the trader. No new entries. Open positions continue to natural exit."""
        variant = self._get_active_variant()
        if not variant:
            return {"ok": False, "error": f"No active {self.mode} variant found"}
        variant.is_halted = True
        variant.halted_at = datetime.now(timezone.utc)
        variant.halted_reason = reason
        self.db.commit()
        logger.warning(f"🛑 Trader HALTED ({self.mode}): {reason}")
        self._fire_alert(f"🛑 {self.mode.upper()} TRADER HALTED\nReason: {reason}")
        return {"ok": True, "halted_at": variant.halted_at.isoformat(), "reason": reason}

    def resume(self) -> Dict:
        """Clear halt/pause. Resumes normal cycle execution."""
        variant = self._get_active_variant()
        if not variant:
            return {"ok": False, "error": f"No active {self.mode} variant found"}
        if not variant.is_halted:
            return {"ok": True, "message": "Trader was not halted"}
        variant.is_halted = False
        variant.halted_at = None
        variant.halted_reason = None
        self.db.commit()
        logger.info(f"▶️ Trader RESUMED ({self.mode})")
        self._fire_alert(f"▶️ {self.mode.upper()} TRADER RESUMED")
        return {"ok": True}

    def get_status(self) -> Dict:
        """Return current trader state including halt status, daily P&L, circuit breaker state."""
        variant = self._get_active_variant()
        if not variant:
            return {
                "mode": self.mode,
                "active": False,
                "is_halted": False,
                "message": f"No active {self.mode} variant. Activate one from Strategy Config.",
            }

        daily_pnl = self._get_daily_pnl(variant.id)
        total_pnl = self._get_total_pnl(variant.id)
        open_count = self._get_open_count()
        portfolio_size = self.guardrails["paper_portfolio_size"]

        daily_loss_pct = (daily_pnl / portfolio_size) * 100
        total_loss_pct = (total_pnl / portfolio_size) * 100

        max_daily = variant.max_daily_loss_pct or self.guardrails["max_daily_loss_pct"]
        max_total = variant.max_total_loss_pct or self.guardrails["max_total_loss_pct"]

        return {
            "mode": self.mode,
            "active": True,
            "variant_id": variant.id,
            "variant_name": variant.name,
            "variant_version": variant.version,
            "activated_at": variant.activated_at.isoformat() if variant.activated_at else None,
            "is_halted": variant.is_halted,
            "halted_reason": variant.halted_reason,
            "halted_at": variant.halted_at.isoformat() if variant.halted_at else None,
            "open_positions": open_count,
            "daily_pnl_usd": round(daily_pnl, 2),
            "daily_pnl_pct": round(daily_loss_pct, 2),
            "total_pnl_usd": round(total_pnl, 2),
            "total_pnl_pct": round(total_loss_pct, 2),
            "circuit_breakers": {
                "max_daily_loss_pct": max_daily,
                "max_total_loss_pct": max_total,
                "daily_breaker_triggered": daily_loss_pct <= -abs(max_daily),
                "total_breaker_triggered": total_loss_pct <= -abs(max_total),
            },
            "guardrails": self.guardrails,
        }

    # ── Main Cycle ────────────────────────────────────────────────────────────

    async def run_cycle(self) -> Dict:
        """
        Run one full cycle: check circuit breakers, process exits, enter new positions.
        """
        from app.models.trade_proposal import TradeProposal
        from app.models.paper_trade import PaperTrade

        cycle_start = datetime.now(timezone.utc)
        results = {
            "mode": self.mode,
            "timestamp": cycle_start.isoformat(),
            "exits_processed": 0,
            "entries_attempted": 0,
            "entries_executed": 0,
            "entries_rejected": [],
            "portfolio_exposure_pct": 0.0,
            "halted": False,
            "errors": [],
        }

        try:
            # Step 1: Check halt flag
            variant = self._get_active_variant()
            if not variant:
                results["errors"].append(f"No active {self.mode} variant. Activate one from Strategy Config.")
                return results

            if variant.is_halted:
                results["halted"] = True
                results["errors"].append(f"Trader is halted: {variant.halted_reason}")
                logger.info(f"⏸ Cycle skipped — trader halted: {variant.halted_reason}")
                return results

            # Step 2: Check circuit breakers
            tripped, reason = self._check_circuit_breakers(variant)
            if tripped:
                self.halt(reason)
                results["halted"] = True
                results["errors"].append(f"Circuit breaker triggered: {reason}")
                return results

            # Step 3: Process exits on open positions
            exits = await self._process_exits(variant.id)
            results["exits_processed"] = exits

            # Step 4: Check daily trade cap
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            trades_today = self.db.query(PaperTrade).filter(
                PaperTrade.entry_time >= today_start,
                PaperTrade.strategy_variant_id == variant.id,
            ).count()

            if trades_today >= self.guardrails["max_daily_trades"]:
                results["entries_rejected"].append(f"Daily cap {self.guardrails['max_daily_trades']} reached")
                return results

            # Step 5: Check exposure cap
            portfolio_size = self.guardrails["paper_portfolio_size"]
            open_value = self._calculate_open_exposure()
            exposure_pct = (open_value / portfolio_size) * 100
            results["portfolio_exposure_pct"] = round(exposure_pct, 2)

            if exposure_pct >= self.guardrails["max_portfolio_exposure_pct"]:
                results["entries_rejected"].append(
                    f"Exposure cap {self.guardrails['max_portfolio_exposure_pct']}% reached"
                )
                return results

            # Step 6: Execute pending proposals
            pending = (
                self.db.query(TradeProposal)
                .filter(TradeProposal.status == "pending")
                .filter(TradeProposal.ai_score >= self.guardrails["min_ai_score"])
                .order_by(TradeProposal.ai_score.desc())
                .limit(self.guardrails["max_daily_trades"] - trades_today)
                .all()
            )

            results["entries_attempted"] = len(pending)
            for proposal in pending:
                executed, reason = await self._execute_entry(proposal, exposure_pct, variant.id)
                if executed:
                    results["entries_executed"] += 1
                    open_value = self._calculate_open_exposure()
                    exposure_pct = (open_value / portfolio_size) * 100
                else:
                    results["entries_rejected"].append(f"{proposal.symbol}: {reason}")

        except Exception as e:
            logger.error(f"AutonomousTrader cycle error ({self.mode}): {e}", exc_info=True)
            results["errors"].append(str(e))

        logger.info(
            f"📊 [{self.mode.upper()}] Cycle: {results['exits_processed']} exits, "
            f"{results['entries_executed']}/{results['entries_attempted']} entries, "
            f"{results['portfolio_exposure_pct']:.1f}% exposure"
        )
        return results

    # ── Entry Execution ───────────────────────────────────────────────────────

    async def _execute_entry(
        self, proposal, current_exposure_pct: float, variant_id: str
    ) -> Tuple[bool, str]:
        from app.models.paper_trade import PaperTrade

        symbol = proposal.symbol
        portfolio_size = self.guardrails["paper_portfolio_size"]

        if proposal.ai_score is not None and proposal.ai_score < self.guardrails["min_ai_score"]:
            return False, f"AI score {proposal.ai_score} below minimum"

        # No duplicate open position for same symbol
        existing = (
            self.db.query(PaperTrade)
            .filter(PaperTrade.symbol == symbol, PaperTrade.status == "open")
            .first()
        )
        if existing:
            proposal.status = "rejected"
            self.db.commit()
            return False, "Duplicate open position"

        weight_pct = min(
            proposal.max_portfolio_weight or self.guardrails["max_single_position_pct"],
            self.guardrails["max_single_position_pct"],
        )
        if current_exposure_pct + weight_pct > self.guardrails["max_portfolio_exposure_pct"]:
            return False, f"Would exceed exposure cap"

        position_usd = portfolio_size * weight_pct / 100.0
        entry_price = proposal.entry_price or await self._get_current_price(symbol)
        if not entry_price:
            return False, "Could not determine entry price"

        shares = position_usd / entry_price

        if self.mode == "paper":
            await self._create_paper_trade(proposal, symbol, entry_price, shares, position_usd, variant_id)
        else:
            # live mode: submit Alpaca order first, then record
            order_ok, order_err = await self._submit_live_order(symbol, shares, entry_price)
            if not order_ok:
                return False, f"Alpaca order failed: {order_err}"
            await self._create_paper_trade(proposal, symbol, entry_price, shares, position_usd, variant_id)
            # TODO: create LiveTrade row when that model is built

        proposal.status = "executed"
        proposal.executed_at = datetime.now(timezone.utc)
        proposal.execution_price = entry_price
        self.db.commit()

        logger.info(
            f"✅ [{self.mode.upper()}] ENTERED: {symbol} @ ${entry_price:.2f} | "
            f"${position_usd:.0f} ({weight_pct:.1f}%) | AI={proposal.ai_score}"
        )
        self._fire_alert(
            f"📈 [{self.mode.upper()}] Entered {symbol} @ ${entry_price:.2f}\n"
            f"Strategy: {proposal.strategy} | AI: {proposal.ai_score}\n"
            f"Target: +{proposal.profit_target_pct}% | Stop: -{proposal.stop_loss_pct}%"
        )
        return True, "executed"

    async def _create_paper_trade(self, proposal, symbol, entry_price, shares, position_usd, variant_id):
        from app.models.paper_trade import PaperTrade
        trade = PaperTrade(
            id=str(uuid.uuid4()),
            proposal_id=proposal.id,
            strategy_variant_id=variant_id,
            symbol=symbol,
            strategy=proposal.strategy,
            entry_price=entry_price,
            shares=shares,
            position_usd=position_usd,
            ai_score=proposal.ai_score,
            ai_reasoning=getattr(proposal, "ai_reasoning", None),
            profit_target_pct=proposal.profit_target_pct,
            stop_loss_pct=proposal.stop_loss_pct,
            status="open",
            entry_time=datetime.now(timezone.utc),
            max_hold_until=datetime.now(timezone.utc) + timedelta(days=self.guardrails["max_hold_days"]),
            signal_metadata=getattr(proposal, "signal_metadata", None),
        )
        self.db.add(trade)

    async def _submit_live_order(self, symbol: str, shares: float, price: float) -> Tuple[bool, str]:
        """Submit a live order to Alpaca. Returns (success, error_message)."""
        try:
            import os
            from alpaca.trading.client import TradingClient
            from alpaca.trading.requests import MarketOrderRequest
            from alpaca.trading.enums import OrderSide, TimeInForce

            client = TradingClient(
                api_key=os.getenv("ALPACA_LIVE_API_KEY_ID"),
                secret_key=os.getenv("ALPACA_LIVE_API_SECRET_KEY"),
                paper=False,
            )
            req = MarketOrderRequest(
                symbol=symbol,
                qty=round(shares, 4),
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY,
            )
            client.submit_order(req)
            return True, ""
        except Exception as e:
            logger.error(f"Alpaca live order failed for {symbol}: {e}")
            return False, str(e)

    # ── Exit Processing ───────────────────────────────────────────────────────

    async def _process_exits(self, variant_id: str) -> int:
        from app.models.paper_trade import PaperTrade

        open_trades = (
            self.db.query(PaperTrade)
            .filter(PaperTrade.status == "open", PaperTrade.strategy_variant_id == variant_id)
            .all()
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
            elif trade.max_hold_until:
                max_hold = trade.max_hold_until
                if max_hold.tzinfo is None:
                    max_hold = max_hold.replace(tzinfo=timezone.utc)
                if now >= max_hold:
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
                    f"{emoji} [{self.mode.upper()}] CLOSED: {trade.symbol} | "
                    f"{return_pct:+.1f}% | ${trade.profit_loss_usd:+.0f} | {exit_reason}"
                )
                self._fire_alert(
                    f"{emoji} [{self.mode.upper()}] Closed {trade.symbol} {return_pct:+.1f}%\n"
                    f"Reason: {exit_reason} | P&L: ${trade.profit_loss_usd:+.0f}"
                )

        return closed

    # ── Circuit Breakers ──────────────────────────────────────────────────────

    def _check_circuit_breakers(self, variant) -> Tuple[bool, str]:
        """Returns (tripped, reason). Called at the start of every cycle."""
        portfolio_size = self.guardrails["paper_portfolio_size"]
        max_daily = variant.max_daily_loss_pct or self.guardrails["max_daily_loss_pct"]
        max_total = variant.max_total_loss_pct or self.guardrails["max_total_loss_pct"]

        daily_pnl = self._get_daily_pnl(variant.id)
        daily_loss_pct = (daily_pnl / portfolio_size) * 100
        if daily_loss_pct <= -abs(max_daily):
            return True, f"Daily loss {daily_loss_pct:.1f}% exceeded limit -{max_daily}%"

        total_pnl = self._get_total_pnl(variant.id)
        total_loss_pct = (total_pnl / portfolio_size) * 100
        if total_loss_pct <= -abs(max_total):
            return True, f"Total loss {total_loss_pct:.1f}% exceeded limit -{max_total}%"

        return False, ""

    def _get_daily_pnl(self, variant_id: str) -> float:
        try:
            from app.models.paper_trade import PaperTrade
            from sqlalchemy import func as sqlfunc
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            result = (
                self.db.query(sqlfunc.sum(PaperTrade.profit_loss_usd))
                .filter(
                    PaperTrade.strategy_variant_id == variant_id,
                    PaperTrade.status == "closed",
                    PaperTrade.exit_time >= today_start,
                )
                .scalar()
            )
            return float(result or 0.0)
        except Exception:
            return 0.0

    def _get_total_pnl(self, variant_id: str) -> float:
        try:
            from app.models.paper_trade import PaperTrade
            from sqlalchemy import func as sqlfunc
            result = (
                self.db.query(sqlfunc.sum(PaperTrade.profit_loss_usd))
                .filter(
                    PaperTrade.strategy_variant_id == variant_id,
                    PaperTrade.status == "closed",
                )
                .scalar()
            )
            return float(result or 0.0)
        except Exception:
            return 0.0

    def _get_open_count(self) -> int:
        try:
            from app.models.paper_trade import PaperTrade
            return self.db.query(PaperTrade).filter(PaperTrade.status == "open").count()
        except Exception:
            return 0

    # ── Performance Summary ───────────────────────────────────────────────────

    def get_performance_summary(self, variant_id: Optional[str] = None) -> Dict:
        """
        Aggregate closed trade P&L scoped to a strategy variant period.
        If variant_id is None, uses the active variant.
        """
        try:
            from app.models.paper_trade import PaperTrade

            if not variant_id:
                v = self._get_active_variant()
                variant_id = v.id if v else None

            query = self.db.query(PaperTrade).filter(PaperTrade.status == "closed")
            if variant_id:
                query = query.filter(PaperTrade.strategy_variant_id == variant_id)

            closed = query.all()
            if not closed:
                return {"total_trades": 0, "win_rate": 0, "total_pnl": 0}

            wins = [t for t in closed if (t.return_pct or 0) > 0]
            total_pnl = sum(t.profit_loss_usd or 0 for t in closed)

            return {
                "variant_id": variant_id,
                "total_trades": len(closed),
                "wins": len(wins),
                "losses": len(closed) - len(wins),
                "win_rate": round(len(wins) / len(closed), 3),
                "total_pnl": round(total_pnl, 2),
                "total_return_pct": round(total_pnl / self.guardrails["paper_portfolio_size"] * 100, 2),
                "open_positions": self._get_open_count(),
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
            s: {"count": len(r), "avg_return_pct": round(sum(r) / len(r), 2)}
            for s, r in groups.items()
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _calculate_open_exposure(self) -> float:
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

    def _fire_alert(self, message: str):
        if not self.enable_alerts:
            return
        try:
            from services.pushover_service import PushoverService
            PushoverService().send(title="FinsightAI", message=message)
        except Exception:
            pass
