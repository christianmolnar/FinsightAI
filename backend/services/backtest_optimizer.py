"""
PHASE 5: Iterative Backtest Optimizer with AI Learning

Automatically runs multiple backtests, gets AI recommendations,
applies changes, and tracks the best configuration found.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session

from .backtester import Backtester
from .backtest_ai_analyzer import BacktestAIAnalyzer
try:
    from models.optimization_run import OptimizationRun
except ImportError:
    from ..models.optimization_run import OptimizationRun

logger = logging.getLogger(__name__)


class BacktestOptimizer:
    """
    Orchestrates iterative optimization loop:
    1. Run backtest with current params
    2. Get AI analysis and recommendations
    3. Apply highest-priority recommendation
    4. Repeat until convergence or max iterations
    5. Return best configuration found
    """
    
    def __init__(
        self, 
        backtester: Backtester, 
        ai_analyzer: BacktestAIAnalyzer,
        db: Session = None
    ):
        self.backtester = backtester
        self.ai_analyzer = ai_analyzer
        self.db = db  # For saving optimization runs
        
    async def optimize(
        self,
        initial_params: Dict[str, Any],
        max_iterations: int = 5,
        min_improvement_threshold: float = 0.02,  # 2% minimum improvement
        ai_provider: str = 'anthropic',
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Run iterative optimization loop.
        
        Args:
            initial_params: Starting backtest configuration
            max_iterations: Maximum optimization iterations
            min_improvement_threshold: Stop if improvement < this (as decimal)
            ai_provider: 'anthropic' or 'openai'
            
        Returns:
            {
                'best_config': {...},
                'best_metrics': {...},
                'iterations': [...],
                'improvement': float,
                'total_time_seconds': float
            }
        """
        start_time = datetime.now()
        
        current_params = initial_params.copy()
        best_config = None
        best_return_pct = float('-inf')
        iterations_history = []
        
        logger.info(f"🚀 Starting optimization with max {max_iterations} iterations")
        logger.info(f"Initial params: {current_params}")
        
        for iteration in range(max_iterations):
            iteration_start = datetime.now()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 ITERATION {iteration + 1}/{max_iterations}")
            logger.info(f"{'='*60}")
            
            # Step 1: Run backtest with current params
            logger.info("Step 1: Running backtest...")
            backtest_result = await self._run_backtest(current_params)
            
            if not backtest_result['success']:
                logger.error(f"Backtest failed: {backtest_result.get('error')}")
                break
                
            metrics = backtest_result['metrics']
            current_return_pct = metrics['returns']['total_return_pct']
            
            logger.info(f"✅ Backtest complete: {current_return_pct:.2f}% return")
            
            # Track this iteration
            iteration_data = {
                'iteration': iteration + 1,
                'params': current_params.copy(),
                'return_pct': current_return_pct,
                'metrics': metrics,
                'timestamp': iteration_start.isoformat()
            }
            
            # Update best if this is better
            if current_return_pct > best_return_pct:
                improvement = current_return_pct - best_return_pct if best_return_pct != float('-inf') else 0
                best_return_pct = current_return_pct
                best_config = current_params.copy()
                
                logger.info(f"🎉 NEW BEST: {current_return_pct:.2f}% (+{improvement:.2f}%)")
                iteration_data['is_best'] = True
                iteration_data['improvement'] = improvement
            else:
                logger.info(f"⚠️ No improvement (best: {best_return_pct:.2f}%)")
                iteration_data['is_best'] = False
                
            # Step 2: Get AI recommendations
            logger.info("Step 2: Getting AI recommendations...")
            
            try:
                recommendations = await self.ai_analyzer.analyze_and_recommend(
                    trades=backtest_result['trades'],
                    current_params=current_params,
                    metrics=metrics
                )
                
                iteration_data['recommendations'] = recommendations.get('recommendations', [])
                
                if not recommendations.get('recommendations'):
                    logger.info("✅ No recommendations - parameters are optimized!")
                    break
                    
                logger.info(f"📋 Got {len(recommendations['recommendations'])} recommendations")
                
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                iteration_data['ai_error'] = str(e)
                break
            
            # Step 3: Apply highest-priority recommendation
            logger.info("Step 3: Applying recommendation...")
            
            top_rec = recommendations['recommendations'][0]  # Already sorted by priority
            logger.info(f"Applying: {top_rec['parameter']} = {top_rec['suggested_value']}")
            
            updated_params = self._apply_recommendation(current_params, top_rec)
            iteration_data['applied_recommendation'] = top_rec
            
            # Check for convergence
            if iteration > 0:
                prev_return = iterations_history[-1]['return_pct']
                improvement = current_return_pct - prev_return
                
                if abs(improvement) < min_improvement_threshold * 100:
                    logger.info(f"✅ Converged (improvement {improvement:.2f}% < threshold {min_improvement_threshold*100}%)")
                    iteration_data['converged'] = True
                    iterations_history.append(iteration_data)
                    break
                    
            iterations_history.append(iteration_data)
            current_params = updated_params
            
            iteration_duration = (datetime.now() - iteration_start).total_seconds()
            logger.info(f"⏱️ Iteration completed in {iteration_duration:.1f}s")
            
        # Calculate final statistics
        total_time = (datetime.now() - start_time).total_seconds()
        initial_return = iterations_history[0]['return_pct'] if iterations_history else 0
        total_improvement = best_return_pct - initial_return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 OPTIMIZATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Initial return: {initial_return:.2f}%")
        logger.info(f"Best return: {best_return_pct:.2f}%")
        logger.info(f"Total improvement: +{total_improvement:.2f}%")
        logger.info(f"Iterations: {len(iterations_history)}")
        logger.info(f"Time: {total_time:.1f}s")
        
        result = {
            'success': True,
            'best_config': best_config,
            'best_return_pct': best_return_pct,
            'initial_return_pct': initial_return,
            'total_improvement': total_improvement,
            'iterations': iterations_history,
            'total_iterations': len(iterations_history),
            'total_time_seconds': total_time,
            'converged': iterations_history[-1].get('converged', False) if iterations_history else False
        }
        
        # Save optimization run to database
        if save_to_db and self.db:
            try:
                optimization_run = OptimizationRun(
                    user_id=initial_params.get('user_id'),
                    start_date=initial_params['start_date'],
                    end_date=initial_params['end_date'],
                    strategies=initial_params.get('strategies'),
                    initial_params=initial_params,
                    max_iterations=max_iterations,
                    min_improvement_threshold=min_improvement_threshold,
                    ai_provider=ai_provider,
                    initial_return_pct=initial_return,
                    best_return_pct=best_return_pct,
                    total_improvement=total_improvement,
                    total_iterations=len(iterations_history),
                    converged=result['converged'],
                    best_config=best_config,
                    iterations=iterations_history,
                    total_time_seconds=total_time
                )
                
                self.db.add(optimization_run)
                self.db.commit()
                self.db.refresh(optimization_run)
                
                result['optimization_run_id'] = optimization_run.id
                logger.info(f"💾 Saved optimization run: {optimization_run.id}")

                # Save a StrategyVariant if this run improved over baseline
                if total_improvement > 0:
                    try:
                        from app.models.strategy_variant import StrategyVariant
                        variant_name = (
                            f"Optimized {datetime.now().strftime('%Y-%m-%d')} "
                            f"+{total_improvement:.1f}%"
                        )
                        # Build human-readable proposed changes by diffing initial vs best config
                        ai_proposed_changes = self._diff_configs(initial_params, best_config)
                        # Build AI summary from iteration recommendations
                        ai_summary = self._build_ai_summary(
                            iterations_history, total_improvement, best_return_pct, initial_return
                        )
                        # Compute version for this variant name
                        existing_count = self.db.query(StrategyVariant).filter(
                            StrategyVariant.name == variant_name
                        ).count()
                        variant = StrategyVariant(
                            name=variant_name,
                            description=(
                                f"Auto-generated by optimizer. "
                                f"{len(iterations_history)} iterations, "
                                f"{total_improvement:.2f}% improvement."
                            ),
                            source='optimization',
                            source_id=optimization_run.id,
                            config=best_config,
                            version=existing_count + 1,
                            backtest_return_pct=best_return_pct,
                            backtest_date_range=(
                                f"{initial_params['start_date']} to {initial_params['end_date']}"
                            ),
                            ai_summary=ai_summary,
                            ai_proposed_changes=ai_proposed_changes,
                            is_active=False,
                        )
                        self.db.add(variant)
                        self.db.commit()
                        result['strategy_variant_id'] = variant.id
                        logger.info(f"🧬 Saved StrategyVariant: {variant.id} ({variant_name})")
                    except Exception as e:
                        logger.warning(f"StrategyVariant save failed (non-critical): {e}")
                        self.db.rollback()
                
            except Exception as e:
                logger.error(f"Failed to save optimization run: {e}")
                self.db.rollback()
        
        return result
        
    async def _run_backtest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a backtest with given parameters."""
        try:
            # Create a new Backtester instance with the parameters
            backtester = Backtester(
                db=self.backtester.db,
                initial_capital=params.get('initial_capital', 10000),
                position_size_pct=params.get('position_size', 1000) / params.get('initial_capital', 10000),  # Convert to percentage
                max_hold_days=params.get('max_hold_days', 14),
                enable_compounding=params.get('enable_compounding', True),
                user_id=params.get('user_id'),
                strategy_config=params.get('strategy_config')
            )
            
            # Run backtest
            metrics = await backtester.run_backtest(
                start_date=params['start_date'],
                end_date=params['end_date'],
                strategies=params.get('strategies')
            )
            
            # Convert BacktestMetrics to dict
            return {
                'success': True,
                'metrics': {
                    'returns': {
                        'initial_capital': metrics.initial_capital,
                        'final_capital': metrics.final_capital,
                        'net_profit': metrics.net_profit,
                        'total_return_pct': metrics.total_return_pct
                    },
                    'summary': {
                        'total_trades': metrics.total_trades,
                        'winning_trades': metrics.winning_trades,
                        'losing_trades': metrics.losing_trades,
                        'win_rate': metrics.win_rate
                    },
                    'performance': {
                        'profit_factor': metrics.profit_factor,
                        'avg_win': metrics.avg_win,
                        'avg_loss': metrics.avg_loss,
                        'avg_hold_days': metrics.avg_hold_days
                    }
                },
                'trades': [
                    {
                        'symbol': t.symbol,
                        'strategy': t.strategy,
                        'entry_date': str(t.entry_date),
                        'exit_date': str(t.exit_date),
                        'entry_price': t.entry_price,
                        'exit_price': t.exit_price,
                        'shares': t.shares,
                        'profit_loss': t.profit_loss,
                        'return_pct': t.return_pct,
                        'hold_days': t.hold_days,
                        'exit_reason': t.exit_reason
                    }
                    for t in metrics.trades
                ],
                'config': params
            }
            
        except Exception as e:
            logger.error(f"Backtest execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    def _apply_recommendation(self, current_params: Dict, recommendation: Dict) -> Dict:
        """
        Apply a single AI recommendation to parameters.

        Handles two namespaces:
        1. Top-level backtest params: confidence_threshold, position_size, max_hold_days,
           initial_capital, enable_compounding
        2. Strategy-specific params: earnings.stopLoss, seasonality.profitTarget, etc.
           These live in strategy_config[strategy]['params'][param]['value']

        The AI surfaces param names like "earnings.stopLoss" or "earnings Stop Loss" —
        we normalise both dot-notation and space/human formats.
        """
        import copy
        updated_params = copy.deepcopy(current_params)
        param_name = recommendation.get('parameter', '')
        suggested_value = recommendation.get('suggested_value', recommendation.get('recommended_value', ''))

        def _parse_float(v) -> float:
            return float(str(v).replace('%', '').replace('$', '').replace(',', '').strip())

        def _parse_bool(v) -> bool:
            return str(v).lower() in ('true', 'yes', 'enabled', '1')

        # ── Top-level param map (AI label → param key) ─────────────────────
        TOP_LEVEL = {
            'confidence_threshold': 'confidence_threshold',
            'position_size':        'position_size',
            'max_hold_days':        'max_hold_days',
            'initial_capital':      'initial_capital',
            'enable_compounding':   'enable_compounding',
        }

        # ── Strategy-specific param map ─────────────────────────────────────
        # Keys: lower-case fragments the AI might use.
        # Both dot-notation ("earnings.stopLoss") and human labels ("earnings Stop Loss")
        # are supported. We match on substrings after normalisation.
        STRATEGY_PARAMS = {
            # Earnings
            'earnings.stoploss':           ('earnings', 'stopLoss'),
            'earnings.stop.loss':          ('earnings', 'stopLoss'),
            'earnings.profittarget':       ('earnings', 'profitTarget'),
            'earnings.profit.target':      ('earnings', 'profitTarget'),
            'earnings.daysbeforeearnings': ('earnings', 'daysBeforeEarnings'),
            'earnings.days.before':        ('earnings', 'daysBeforeEarnings'),
            'earnings.minepsgrowth':       ('earnings', 'minEpsGrowth'),
            'earnings.min.eps':            ('earnings', 'minEpsGrowth'),
            'earnings.minrevenuegrowth':   ('earnings', 'minRevenueGrowth'),
            'earnings.min.revenue':        ('earnings', 'minRevenueGrowth'),
            'earnings.historicalbeatrate': ('earnings', 'historicalBeatRate'),
            'earnings.historical.beat':    ('earnings', 'historicalBeatRate'),
            'earnings.maxportfolioweight': ('earnings', 'maxPortfolioWeight'),
            'earnings.max.portfolio':      ('earnings', 'maxPortfolioWeight'),
            # Seasonality
            'seasonality.stoploss':              ('seasonality', 'stopLoss'),
            'seasonality.stop.loss':             ('seasonality', 'stopLoss'),
            'seasonality.profittarget':          ('seasonality', 'profitTarget'),
            'seasonality.profit.target':         ('seasonality', 'profitTarget'),
            'seasonality.weeksbeforepeak':       ('seasonality', 'weeksBeforePeak'),
            'seasonality.weeks.before':          ('seasonality', 'weeksBeforePeak'),
            'seasonality.minhistoricalyears':    ('seasonality', 'minHistoricalYears'),
            'seasonality.min.historical':        ('seasonality', 'minHistoricalYears'),
            'seasonality.minseasonalreturn':     ('seasonality', 'minSeasonalReturn'),
            'seasonality.min.seasonal':          ('seasonality', 'minSeasonalReturn'),
            'seasonality.maxportfolioweight':    ('seasonality', 'maxPortfolioWeight'),
            'seasonality.max.portfolio':         ('seasonality', 'maxPortfolioWeight'),
            # Macro
            'macro.stoploss':           ('macro', 'stopLoss'),
            'macro.stop.loss':          ('macro', 'stopLoss'),
            'macro.profittarget':       ('macro', 'profitTarget'),
            'macro.profit.target':      ('macro', 'profitTarget'),
            'macro.maxportfolioweight': ('macro', 'maxPortfolioWeight'),
            'macro.max.portfolio':      ('macro', 'maxPortfolioWeight'),
            # Sentiment
            'sentiment.stoploss':           ('sentiment', 'stopLoss'),
            'sentiment.stop.loss':          ('sentiment', 'stopLoss'),
            'sentiment.profittarget':       ('sentiment', 'profitTarget'),
            'sentiment.profit.target':      ('sentiment', 'profitTarget'),
            'sentiment.maxportfolioweight': ('sentiment', 'maxPortfolioWeight'),
            'sentiment.max.portfolio':      ('sentiment', 'maxPortfolioWeight'),
        }

        # Normalise: "earnings Stop Loss" → "earnings.stop.loss", underscores kept
        # Then match fragments. We keep underscores so "position_size" stays matchable.
        norm = param_name.lower().replace(' ', '.').replace('..', '.')

        # ── Try top-level first ──────────────────────────────────────────────
        matched_top = None
        for fragment, key in TOP_LEVEL.items():
            if fragment in norm:
                matched_top = key
                break

        if matched_top:
            try:
                if matched_top == 'enable_compounding':
                    updated_params[matched_top] = _parse_bool(suggested_value)
                elif matched_top == 'confidence_threshold':
                    v = _parse_float(suggested_value)
                    updated_params[matched_top] = v / 100 if v > 1 else v
                else:
                    updated_params[matched_top] = int(_parse_float(suggested_value))
                logger.info(f"✅ Applied top-level: {matched_top} = {updated_params[matched_top]}")
            except Exception as e:
                logger.error(f"Failed applying top-level param {param_name}: {e}")
            return updated_params

        # ── Try strategy-specific ────────────────────────────────────────────
        matched_strategy = None
        for fragment, (strat, param) in STRATEGY_PARAMS.items():
            if fragment in norm:
                matched_strategy = (strat, param)
                break

        if matched_strategy:
            strat_key, param_key = matched_strategy
            try:
                value = _parse_float(suggested_value)
                # Ensure nested path exists
                sc = updated_params.setdefault('strategy_config', {})
                sc.setdefault(strat_key, {}).setdefault('params', {}).setdefault(param_key, {})
                sc[strat_key]['params'][param_key]['value'] = value
                logger.info(f"✅ Applied strategy param: {strat_key}.{param_key} = {value}")
            except Exception as e:
                logger.error(f"Failed applying strategy param {param_name}: {e}")
            return updated_params

        logger.warning(f"⚠️ Could not map parameter: '{param_name}' (normalised: '{norm}')")
        return updated_params

    # ── Variant helper methods ────────────────────────────────────────────────

    def _diff_configs(self, initial: Dict, best: Dict) -> Dict:
        """
        Produce a human-readable diff between initial_params and best_config.
        Returns: { "paramName": { "from": old, "to": new } }
        Only captures flat scalar values that changed; skips nested strategy_config diffs
        (those would be too verbose — the AI summary covers them narratively).
        """
        changes = {}
        SKIP_KEYS = {'start_date', 'end_date', 'strategies', 'user_id', 'strategy_config'}
        all_keys = set(initial.keys()) | set(best.keys())
        for key in all_keys:
            if key in SKIP_KEYS:
                continue
            old_val = initial.get(key)
            new_val = best.get(key)
            if old_val != new_val and not isinstance(new_val, dict):
                changes[key] = {"from": old_val, "to": new_val}

        # Also surface strategy-level param changes
        init_sc = initial.get('strategy_config', {})
        best_sc = best.get('strategy_config', {})
        for strat in set(list(init_sc.keys()) + list(best_sc.keys())):
            init_params = init_sc.get(strat, {}).get('params', {})
            best_params = best_sc.get(strat, {}).get('params', {})
            for param in set(list(init_params.keys()) + list(best_params.keys())):
                old_v = init_params.get(param, {}).get('value') if isinstance(init_params.get(param), dict) else init_params.get(param)
                new_v = best_params.get(param, {}).get('value') if isinstance(best_params.get(param), dict) else best_params.get(param)
                if old_v != new_v and new_v is not None:
                    changes[f"{strat}.{param}"] = {"from": old_v, "to": new_v}
        return changes

    def _build_ai_summary(
        self,
        iterations_history: List[Dict],
        total_improvement: float,
        best_return_pct: float,
        initial_return: float
    ) -> str:
        """
        Build a human-readable narrative summary of what the optimizer did.
        Pulls the top recommendation reasons from each iteration.
        """
        lines = [
            f"Optimizer ran {len(iterations_history)} iteration(s), "
            f"improving return from {initial_return:.1f}% to {best_return_pct:.1f}% "
            f"(+{total_improvement:.1f}% total improvement)."
        ]
        seen_params = set()
        for it in iterations_history:
            rec = it.get('applied_recommendation')
            if rec:
                param = rec.get('parameter', '')
                reason = rec.get('reasoning') or rec.get('expected_impact', '')
                if param and param not in seen_params:
                    seen_params.add(param)
                    lines.append(f"• {param}: {reason}" if reason else f"• Adjusted {param}")
        return " ".join(lines[:1]) + (" — Changes: " + "; ".join(lines[1:]) if len(lines) > 1 else "")
