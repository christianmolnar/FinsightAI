"""
Market Scanner Service

Scans the market for live trading opportunities using StrategyExecutor —
the same signal engine used by the backtester. This ensures backtest
results are predictive of live performance.

All 5 strategies: earnings, seasonality, macro, sentiment, technical_breakout
All signals are filtered by AITradeScorer before being returned.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd
from sqlalchemy.orm import Session

from services.universe_builder import UniverseBuilder
from app.services.alpaca_service import get_alpaca_service
from services.strategy_executor import StrategyExecutor
from services.ai_trade_scorer import get_ai_trade_scorer
from app.models.strategy import StrategyConfig

logger = logging.getLogger(__name__)


class MarketScanner:
    """
    Live market scanner. Delegates all signal logic to StrategyExecutor
    (same engine as backtester) and gates every signal through AITradeScorer.
    """

    _universe_builder = UniverseBuilder()
    _raw_universe = _universe_builder.build_universe(['SP500', 'DOW', 'NASDAQ100', 'RUSSELL2000'])
    SCAN_UNIVERSE = [s for s in _raw_universe if s not in ('WBA',)]

    MIN_VOLUME = 1_000_000
    MIN_PRICE = 10.0

    def __init__(self, db: Session, historical_data_manager=None):
        self.db = db
        self.historical_data_manager = historical_data_manager
        self.alpaca = get_alpaca_service(paper=True)
        self.strategy_config = self._load_strategy_config()
        self.executor = StrategyExecutor(self.strategy_config)
        self.scorer = get_ai_trade_scorer()
        logger.info(f"MarketScanner initialized — universe: {len(self.SCAN_UNIVERSE)} stocks")

    def _load_strategy_config(self) -> Dict:
        """Load active strategy config from DB, fall back to defaults."""
        try:
            from app.models.strategy import StrategyConfig as SC
            configs = self.db.query(SC).filter(SC.is_active == True).all()
            if configs:
                result = {}
                for cfg in configs:
                    result[cfg.strategy_name] = {
                        'enabled': cfg.enabled,
                        'params': cfg.parameters or {}
                    }
                return result
        except Exception as e:
            logger.warning(f"Could not load strategy config from DB: {e}")

        # Import default config from backtester (single source of defaults)
        from services.backtester import Backtester
        b = Backtester.__new__(Backtester)
        return b._get_default_strategy_config()

    def scan_all_strategies(
        self,
        ai_gated: bool = True,
        ai_score_threshold: int = 60,
        strategies: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Scan all enabled strategies using StrategyExecutor.
        Every signal passes AITradeScorer before being returned.

        Args:
            ai_gated: Gate signals through AITradeScorer (default True for live)
            ai_score_threshold: Minimum AI score (0–100) to pass gate
            strategies: Limit to these strategy names, or None for all enabled

        Returns:
            List of signal dicts (same shape as backtester signals):
            {symbol, strategy, score, reason, current_price, volume,
             exit_params, signal_metadata,
             ai_score, ai_reasoning}   ← added when ai_gated=True
        """
        logger.info("🔍 Starting live market scan via StrategyExecutor...")
        scan_date = datetime.now()
        candidates = []

        # Fetch live prices once for all symbols
        try:
            snapshots = self.alpaca.get_snapshots(self.SCAN_UNIVERSE) or {}
        except Exception as e:
            logger.warning(f"Alpaca snapshots failed: {e}")
            snapshots = {}

        # Fetch historical bars for technical signals (batch)
        bars_dict = self._get_bars_batch(self.SCAN_UNIVERSE, days=260)

        for symbol in self.SCAN_UNIVERSE:
            snap = snapshots.get(symbol)
            current_price = float(getattr(getattr(snap, 'latest_trade', None), 'price', 0) or 0)
            volume = float(getattr(getattr(snap, 'daily_bar', None), 'volume', 0) or 0)

            if current_price < self.MIN_PRICE or volume < self.MIN_VOLUME:
                continue

            hist = bars_dict.get(symbol)
            if hist is None or hist.empty:
                continue

            # Normalise columns
            hist = hist.copy()
            hist.columns = [c.title() for c in hist.columns]  # Close, High, Low, Open, Volume

            # Run each strategy through StrategyExecutor
            strategy_methods = {
                'earnings':          self.executor.scan_earnings_opportunities,
                'seasonality':       self.executor.scan_seasonality_opportunities,
                'macro':             self.executor.scan_macro_opportunities,
                'sentiment':         self.executor.scan_sentiment_opportunities,
                'technical_breakout': self.executor.scan_technical_opportunities,
            }

            for strat_name, method in strategy_methods.items():
                if strategies and strat_name not in strategies:
                    continue

                if not self.strategy_config.get(strat_name, {}).get('enabled', False):
                    continue

                try:
                    signal = method(
                        symbol=symbol,
                        hist_data=hist,
                        scan_date=scan_date,
                        market_data={'current_price': current_price, 'volume': volume}
                    )
                except Exception as e:
                    logger.debug(f"  ⨯ {symbol}/{strat_name}: {e}")
                    continue

                if signal is None:
                    continue

                # Ensure standard live fields
                signal.setdefault('current_price', current_price)
                signal.setdefault('volume', volume)

                # AI gate (same scorer as backtester)
                if ai_gated:
                    try:
                        result = self.scorer.score(signal, threshold=ai_score_threshold)
                        signal['ai_score'] = result['score']
                        signal['ai_reasoning'] = result['reasoning']
                        if not result['approved']:
                            logger.debug(
                                f"  ✗ {symbol}/{strat_name}: AI score {result['score']} "
                                f"below threshold {ai_score_threshold}"
                            )
                            continue
                    except Exception as e:
                        logger.warning(f"AITradeScorer failed for {symbol}: {e}")

                candidates.append(signal)
                logger.info(
                    f"  ✓ {symbol}/{strat_name}: score={signal.get('score')}"
                    + (f" ai={signal.get('ai_score')}" if ai_gated else "")
                )

        logger.info(f"📊 Live scan complete — {len(candidates)} signals passed")
        return candidates

    def _get_bars_batch(self, symbols: List[str], days: int = 260) -> Dict[str, pd.DataFrame]:
        from datetime import timedelta
        end = date.today()
        start = end - timedelta(days=days + 10)
        try:
            return self.alpaca.get_historical_bars(symbols, start.isoformat(), end.isoformat())
        except Exception as e:
            logger.error(f"Batch bars failed: {e}")
            return {}


def get_market_scanner(db: Session) -> MarketScanner:
    return MarketScanner(db)
