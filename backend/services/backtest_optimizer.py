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
                recommendations = await self.ai_analyzer.analyze_trades(
                    trades=backtest_result['trades'],
                    current_params=current_params,
                    backtest_metrics=metrics,
                    ai_provider=ai_provider
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
        
        Handles type conversion and parameter mapping.
        """
        updated_params = current_params.copy()
        param_name = recommendation['parameter']
        suggested_value = recommendation['suggested_value']
        
        # Parameter name mapping (AI uses human names, we use code names)
        param_map = {
            'confidence_threshold': 'confidence_threshold',
            'position_size': 'position_size',
            'max_hold_days': 'max_hold_days',
            'initial_capital': 'initial_capital',
            'enable_compounding': 'enable_compounding'
        }
        
        # Find actual parameter name
        actual_param = None
        for ai_name, code_name in param_map.items():
            if ai_name.lower() in param_name.lower():
                actual_param = code_name
                break
                
        if not actual_param:
            logger.warning(f"Could not map parameter: {param_name}")
            return updated_params
            
        # Type conversion
        try:
            if actual_param == 'enable_compounding':
                updated_params[actual_param] = suggested_value.lower() in ['true', 'yes', 'enabled', '1']
            elif actual_param == 'confidence_threshold':
                # AI might suggest as percentage or decimal
                value = float(suggested_value.replace('%', ''))
                updated_params[actual_param] = value / 100 if value > 1 else value
            else:
                # Numeric parameters
                value_str = str(suggested_value).replace('$', '').replace(',', '')
                updated_params[actual_param] = int(float(value_str))
                
            logger.info(f"✅ Applied: {actual_param} = {updated_params[actual_param]}")
            
        except Exception as e:
            logger.error(f"Failed to convert {suggested_value} for {param_name}: {e}")
            
        return updated_params
