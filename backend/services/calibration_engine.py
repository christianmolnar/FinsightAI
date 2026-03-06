"""
Calibration Engine

Analyzes backtest results and generates data-driven parameter recommendations.

Core functionality:
- Analyzes BacktestMetrics to identify optimization opportunities
- Generates recommendations for all configurable parameters
- Calculates confidence scores based on statistical significance
- Maps recommendations to UI parameter paths
- Saves recommendations to database for tracking
- Uses AI to provide human-readable reasoning for recommendations
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import json
import os
from openai import OpenAI
from anthropic import Anthropic

from services.backtester import BacktestMetrics, BacktestResult
from app.models.backtest import CalibrationRecommendation

logger = logging.getLogger(__name__)


class CalibrationEngine:
    """
    Analyzes backtest results and generates parameter recommendations
    """
    
    # Parameter metadata: path, current range, optimal range hints
    PARAMETER_METADATA = {
        # Earnings Strategy
        "earnings.profitTarget": {
            "category": "strategy",
            "display_name": "Earnings Profit Target",
            "unit": "%",
            "min": 5.0,
            "max": 25.0,
            "current_default": 12.0
        },
        "earnings.stopLoss": {
            "category": "strategy",
            "display_name": "Earnings Stop Loss",
            "unit": "%",
            "min": 3.0,
            "max": 15.0,
            "current_default": 8.0
        },
        "earnings.maxWeight": {
            "category": "strategy",
            "display_name": "Earnings Max Weight",
            "unit": "%",
            "min": 5.0,
            "max": 15.0,
            "current_default": 10.0
        },
        "earnings.minEPSGrowth": {
            "category": "strategy",
            "display_name": "Min EPS Growth",
            "unit": "%",
            "min": 5.0,
            "max": 30.0,
            "current_default": 15.0
        },
        
        # Seasonality Strategy
        "seasonality.profitTarget": {
            "category": "strategy",
            "display_name": "Seasonality Profit Target",
            "unit": "%",
            "min": 5.0,
            "max": 20.0,
            "current_default": 10.0
        },
        "seasonality.stopLoss": {
            "category": "strategy",
            "display_name": "Seasonality Stop Loss",
            "unit": "%",
            "min": 3.0,
            "max": 12.0,
            "current_default": 7.0
        },
        
        # Macro Strategy
        "macro.profitTarget": {
            "category": "strategy",
            "display_name": "Macro Profit Target",
            "unit": "%",
            "min": 5.0,
            "max": 20.0,
            "current_default": 12.0
        },
        "macro.stopLoss": {
            "category": "strategy",
            "display_name": "Macro Stop Loss",
            "unit": "%",
            "min": 3.0,
            "max": 12.0,
            "current_default": 8.0
        },
        
        # Sentiment Strategy
        "sentiment.profitTarget": {
            "category": "strategy",
            "display_name": "Sentiment Profit Target",
            "unit": "%",
            "min": 5.0,
            "max": 20.0,
            "current_default": 10.0
        },
        "sentiment.stopLoss": {
            "category": "strategy",
            "display_name": "Sentiment Stop Loss",
            "unit": "%",
            "min": 3.0,
            "max": 12.0,
            "current_default": 7.0
        },
        
        # Risk Management
        "riskManagement.maxSinglePosition": {
            "category": "risk",
            "display_name": "Max Single Position",
            "unit": "%",
            "min": 1.0,
            "max": 10.0,
            "current_default": 5.0
        },
        "riskManagement.maxSectorExposure": {
            "category": "risk",
            "display_name": "Max Sector Exposure",
            "unit": "%",
            "min": 10.0,
            "max": 50.0,
            "current_default": 25.0
        },
        "riskManagement.maxDrawdown": {
            "category": "risk",
            "display_name": "Max Drawdown",
            "unit": "%",
            "min": 5.0,
            "max": 25.0,
            "current_default": 15.0
        },
        "riskManagement.dailyLossLimit": {
            "category": "risk",
            "display_name": "Daily Loss Limit",
            "unit": "%",
            "min": 1.0,
            "max": 5.0,
            "current_default": 3.0
        },
        "riskManagement.vixThreshold": {
            "category": "risk",
            "display_name": "VIX Threshold",
            "unit": "",
            "min": 15.0,
            "max": 40.0,
            "current_default": 25.0
        },
        
        # Technical Filters
        "technical.rsiMin": {
            "category": "technical",
            "display_name": "RSI Min",
            "unit": "%",
            "min": 20.0,
            "max": 50.0,
            "current_default": 40.0
        },
        "technical.rsiMax": {
            "category": "technical",
            "display_name": "RSI Max",
            "unit": "%",
            "min": 60.0,
            "max": 80.0,
            "current_default": 70.0
        },
        "technical.minVolume": {
            "category": "technical",
            "display_name": "Min Volume",
            "unit": "K",
            "min": 100.0,
            "max": 2000.0,
            "current_default": 500.0
        },
        "technical.volumeMultiplier": {
            "category": "technical",
            "display_name": "Volume Multiplier",
            "unit": "x",
            "min": 1.0,
            "max": 2.0,
            "current_default": 1.2
        },
        "technical.ma200Distance": {
            "category": "technical",
            "display_name": "MA200 Distance",
            "unit": "%",
            "min": 0.0,
            "max": 15.0,
            "current_default": 5.0
        },
    }
    
    def __init__(self, db: Session):
        """
        Initialize calibration engine
        
        Args:
            db: Database session
        """
        self.db = db
        
        # Initialize AI clients
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.ai_preference = os.getenv("AI_MODEL_PREFERENCE", "openai-gpt4")
        
        # Create AI clients if keys available
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None
        self.anthropic_client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
        if not self.openai_client and not self.anthropic_client:
            logger.warning("No AI API keys found - recommendations will use statistical reasoning only")
    
    def validate_parameter(self, parameter_name: str, value: float) -> Tuple[bool, str]:
        """
        Validate a parameter value against its metadata constraints
        
        Args:
            parameter_name: Parameter path (e.g., "earnings.profitTarget")
            value: Proposed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if parameter_name not in self.PARAMETER_METADATA:
            return False, f"Unknown parameter: {parameter_name}"
        
        meta = self.PARAMETER_METADATA[parameter_name]
        min_val = meta.get("min", float('-inf'))
        max_val = meta.get("max", float('inf'))
        
        if value < min_val:
            return False, f"{meta['display_name']} must be >= {min_val}{meta.get('unit', '')}"
        if value > max_val:
            return False, f"{meta['display_name']} must be <= {max_val}{meta.get('unit', '')}"
        
        return True, ""
    
    def get_parameter_info(self, parameter_name: str) -> Optional[Dict]:
        """
        Get metadata for a parameter
        
        Args:
            parameter_name: Parameter path (e.g., "earnings.profitTarget")
            
        Returns:
            Parameter metadata dict or None if not found
        """
        return self.PARAMETER_METADATA.get(parameter_name)
    
    def get_all_parameters(self) -> Dict[str, Dict]:
        """
        Get all parameter metadata organized by category
        
        Returns:
            Dict mapping category to list of parameters
        """
        categories = {}
        for param_name, meta in self.PARAMETER_METADATA.items():
            category = meta["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append({
                "name": param_name,
                **meta
            })
        return categories
    
    def create_config_snapshot(self, config: Dict, recommendations: List[Dict]) -> Tuple[Dict, Dict]:
        """
        Create before/after config snapshots for recommendations
        
        Args:
            config: Current configuration
            recommendations: List of recommendations to apply
            
        Returns:
            Tuple of (before_config, after_config)
        """
        import copy
        
        before_config = copy.deepcopy(config)
        after_config = copy.deepcopy(config)
        
        # Apply each recommendation to after_config
        for rec in recommendations:
            param_path = rec["parameter"]
            new_value = rec["recommended_value"]
            
            # Split path and navigate config dict
            parts = param_path.split(".")
            if len(parts) == 2:
                section, param = parts
                if section not in after_config:
                    after_config[section] = {}
                after_config[section][param] = new_value
        
        return before_config, after_config
    
    def save_backtest_report(
        self,
        metrics: BacktestMetrics,
        config: Dict,
        recommendations: List[Dict],
        start_date: datetime,
        end_date: datetime,
        user_id: str = "default"
    ) -> int:
        """
        Save backtest report with recommendations to database
        
        Args:
            metrics: BacktestMetrics from backtest run
            config: Configuration used for backtest
            recommendations: Generated recommendations
            start_date: Backtest start date
            end_date: Backtest end date
            user_id: User identifier
            
        Returns:
            Report ID
        """
        from app.models.backtest import BacktestReport
        
        # Helper to convert numpy types to Python types
        def to_python_type(value):
            """Convert numpy types to Python native types"""
            if value is None:
                return None
            # Check if it's a numpy type
            if hasattr(value, 'item'):
                return value.item()
            return float(value) if isinstance(value, (int, float)) else value
        
        # Create backtest report
        report = BacktestReport(
            user_id=user_id,
            config_snapshot=config,
            start_date=start_date.date() if isinstance(start_date, datetime) else start_date,
            end_date=end_date.date() if isinstance(end_date, datetime) else end_date,
            initial_capital=to_python_type(metrics.initial_capital),
            
            # Performance metrics
            total_trades=int(metrics.total_trades),
            winning_trades=int(metrics.winning_trades),
            losing_trades=int(metrics.losing_trades),
            win_rate=to_python_type(metrics.win_rate),
            total_return=to_python_type(metrics.total_return_pct),
            final_portfolio_value=to_python_type(metrics.final_capital),
            max_drawdown=to_python_type(metrics.max_drawdown),
            sharpe_ratio=to_python_type(metrics.sharpe_ratio),
            profit_factor=to_python_type(metrics.profit_factor),
            
            # Trade statistics
            avg_win_size=to_python_type(metrics.avg_win_size),
            avg_loss_size=to_python_type(metrics.avg_loss_size),
            largest_win=to_python_type(metrics.largest_win),
            largest_loss=to_python_type(metrics.largest_loss),
            avg_hold_days=to_python_type(metrics.avg_hold_days),
            
            # Additional data
            daily_pnl=metrics.daily_pnl,
            recommendations=recommendations
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        logger.info(f"💾 Saved backtest report #{report.id} with {len(recommendations)} recommendations")
        
        return report.id
    
    def get_backtest_report(self, report_id: int) -> Optional[Dict]:
        """
        Retrieve a backtest report by ID
        
        Args:
            report_id: Report ID
            
        Returns:
            Report dict or None if not found
        """
        from app.models.backtest import BacktestReport
        
        report = self.db.query(BacktestReport).filter(BacktestReport.id == report_id).first()
        
        if not report:
            return None
        
        return {
            "id": report.id,
            "user_id": report.user_id,
            "run_date": report.run_date.isoformat(),
            "config_snapshot": report.config_snapshot,
            "start_date": report.start_date.isoformat(),
            "end_date": report.end_date.isoformat(),
            "initial_capital": report.initial_capital,
            "total_trades": report.total_trades,
            "winning_trades": report.winning_trades,
            "losing_trades": report.losing_trades,
            "win_rate": report.win_rate,
            "total_return": report.total_return,
            "final_portfolio_value": report.final_portfolio_value,
            "max_drawdown": report.max_drawdown,
            "sharpe_ratio": report.sharpe_ratio,
            "profit_factor": report.profit_factor,
            "avg_win_size": report.avg_win_size,
            "avg_loss_size": report.avg_loss_size,
            "largest_win": report.largest_win,
            "largest_loss": report.largest_loss,
            "avg_hold_days": report.avg_hold_days,
            "recommendations": report.recommendations,
            "applied": report.applied,
            "applied_recommendations": report.applied_recommendations,
            "created_at": report.created_at.isoformat(),
            "expires_at": report.expires_at.isoformat() if report.expires_at else None
        }
    
    def get_recent_reports(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        """
        Get recent backtest reports for a user
        
        Args:
            user_id: User identifier
            limit: Maximum number of reports to return
            
        Returns:
            List of report dicts (most recent first)
        """
        from app.models.backtest import BacktestReport
        
        reports = (
            self.db.query(BacktestReport)
            .filter(BacktestReport.user_id == user_id)
            .order_by(BacktestReport.run_date.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": r.id,
                "run_date": r.run_date.isoformat(),
                "start_date": r.start_date.isoformat(),
                "end_date": r.end_date.isoformat(),
                "total_trades": r.total_trades,
                "win_rate": r.win_rate,
                "total_return": r.total_return,
                "sharpe_ratio": r.sharpe_ratio,
                "recommendations_count": len(r.recommendations) if r.recommendations else 0,
                "applied": r.applied
            }
            for r in reports
        ]
    
    def mark_recommendations_applied(
        self,
        report_id: int,
        applied_params: List[str]
    ) -> bool:
        """
        Mark which recommendations were applied by the user
        
        Args:
            report_id: Report ID
            applied_params: List of parameter names that were applied
            
        Returns:
            True if successful
        """
        from app.models.backtest import BacktestReport
        
        report = self.db.query(BacktestReport).filter(BacktestReport.id == report_id).first()
        
        if not report:
            return False
        
        report.applied = True
        report.applied_recommendations = applied_params
        self.db.commit()
        
        logger.info(f"✅ Marked {len(applied_params)} recommendations as applied for report #{report_id}")
        
        return True
    
    def generate_recommendations(
        self,
        metrics: BacktestMetrics,
        current_config: Dict,
        trades: List[BacktestResult] = None
    ) -> List[Dict]:
        """
        Generate calibration recommendations from backtest results
        
        Args:
            metrics: BacktestMetrics from backtest run
            current_config: Current strategy configuration
            trades: Optional list of individual trades for detailed analysis
            
        Returns:
            List of recommendation dicts
        """
        logger.info("🔍 Generating calibration recommendations...")
        logger.info(f"   Backtest: {metrics.total_trades} trades, {metrics.win_rate:.1f}% win rate")
        
        recommendations = []
        
        # Analyze profit targets vs actual performance
        recommendations.extend(self._analyze_profit_targets(metrics, current_config, trades))
        
        # Analyze stop losses vs actual losses
        recommendations.extend(self._analyze_stop_losses(metrics, current_config, trades))
        
        # Analyze position sizing vs risk metrics
        recommendations.extend(self._analyze_position_sizing(metrics, current_config))
        
        # Analyze technical filters vs opportunity count
        recommendations.extend(self._analyze_technical_filters(metrics, current_config))
        
        # Validate all recommendations
        validated_recommendations = []
        for rec in recommendations:
            param_name = rec["parameter"]
            recommended_value = rec["recommended_value"]
            
            # Validate the recommended value
            is_valid, error_msg = self.validate_parameter(param_name, recommended_value)
            if not is_valid:
                logger.warning(f"Invalid recommendation for {param_name}: {error_msg}")
                # Clamp to valid range
                meta = self.PARAMETER_METADATA[param_name]
                rec["recommended_value"] = max(meta["min"], min(meta["max"], recommended_value))
                logger.info(f"   Clamped {param_name} to {rec['recommended_value']}")
            
            validated_recommendations.append(rec)
        
        # Sort by confidence score (highest first)
        validated_recommendations.sort(key=lambda r: r['confidence'], reverse=True)
        
        logger.info(f"✅ Generated {len(validated_recommendations)} validated recommendations")
        
        return validated_recommendations
    
    def _build_analysis_prompt(
        self,
        parameter_name: str,
        current_value: float,
        suggested_value: float,
        metrics: BacktestMetrics,
        context: str
    ) -> str:
        """
        Build AI prompt for recommendation reasoning
        
        Args:
            parameter_name: Parameter being analyzed (e.g., "earnings.profitTarget")
            current_value: Current parameter value
            suggested_value: Recommended new value
            metrics: BacktestMetrics with performance data
            context: Additional context about why this change is suggested
            
        Returns:
            Formatted prompt string
        """
        param_meta = self.PARAMETER_METADATA.get(parameter_name, {})
        display_name = param_meta.get("display_name", parameter_name)
        unit = param_meta.get("unit", "")
        
        prompt = f"""You are a quantitative trading analyst reviewing backtest results. 

BACKTEST PERFORMANCE:
- Total Trades: {metrics.total_trades}
- Win Rate: {metrics.win_rate:.1f}%
- Total Return: {metrics.total_return_pct:.1f}%
- Sharpe Ratio: {metrics.sharpe_ratio:.2f}
- Max Drawdown: {metrics.max_drawdown:.1f}%
- Average Win: ${metrics.avg_win_size:.2f}
- Average Loss: ${metrics.avg_loss_size:.2f}

PARAMETER RECOMMENDATION:
- Parameter: {display_name}
- Current Value: {current_value}{unit}
- Suggested Value: {suggested_value}{unit}
- Change: {((suggested_value - current_value) / current_value * 100):.1f}%

STATISTICAL CONTEXT:
{context}

TASK:
Provide a concise 2-3 sentence explanation of why this parameter change makes sense based on the backtest data. Focus on the statistical evidence and expected impact on performance. Be specific and data-driven.

Your response should be professional but conversational, as if explaining to a trader."""
        
        return prompt
    
    def _get_ai_reasoning(
        self,
        parameter_name: str,
        current_value: float,
        suggested_value: float,
        metrics: BacktestMetrics,
        context: str,
        statistical_reasoning: str
    ) -> str:
        """
        Get AI-generated reasoning for a recommendation
        
        Args:
            parameter_name: Parameter being analyzed
            current_value: Current parameter value
            suggested_value: Recommended new value
            metrics: BacktestMetrics with performance data
            context: Statistical context
            statistical_reasoning: Fallback reasoning if AI unavailable
            
        Returns:
            Human-readable reasoning string
        """
        # If no AI available, return statistical reasoning
        if not self.openai_client and not self.anthropic_client:
            return statistical_reasoning
        
        try:
            # Build prompt
            prompt = self._build_analysis_prompt(
                parameter_name, current_value, suggested_value, metrics, context
            )
            
            # Try OpenAI first (if preferred or only option)
            if self.openai_client and (self.ai_preference.startswith("openai") or not self.anthropic_client):
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",  # Fast and cost-effective
                    messages=[
                        {"role": "system", "content": "You are a quantitative trading analyst."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            
            # Try Anthropic if OpenAI not available or preferred
            elif self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",  # Fast and cost-effective
                    max_tokens=200,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
            
            # Fallback to statistical reasoning
            return statistical_reasoning
            
        except Exception as e:
            logger.warning(f"AI reasoning failed for {parameter_name}: {e}")
            return statistical_reasoning
    
    def _analyze_profit_targets(
        self,
        metrics: BacktestMetrics,
        current_config: Dict,
        trades: List[BacktestResult] = None
    ) -> List[Dict]:
        """Analyze if profit targets are too conservative or aggressive"""
        recommendations = []
        
        if not metrics.avg_win_size or metrics.winning_trades == 0:
            return recommendations
        
        # Calculate average winner as percentage
        # Estimate: If avg win is $493 on $10k positions = ~4.93%
        avg_win_pct = (metrics.avg_win_size / 10000.0) * 100  # Rough estimate
        
        # Current profit target (from config or default)
        current_target = current_config.get('earnings', {}).get('profitTarget', 12.0)
        
        # If average winners are significantly higher than target, we're leaving money on table
        if avg_win_pct > current_target * 1.2:  # 20% higher
            recommended_target = min(avg_win_pct * 0.95, 20.0)  # 95% of avg win, capped at 20%
            money_left = (recommended_target - current_target) / 100.0 * metrics.winning_trades * 10000
            
            # Build statistical context for AI
            statistical_context = f"Average winning trade gained {avg_win_pct:.1f}%, which is {((avg_win_pct / current_target - 1) * 100):.0f}% higher than the current {current_target}% target. This suggests approximately ${money_left:,.0f} was left on the table across {metrics.winning_trades} winning trades."
            
            # Generate fallback reasoning
            statistical_reasoning = f"Average winning trade gained {avg_win_pct:.1f}%. Current {current_target}% target left approximately ${money_left:,.0f} on the table."
            
            # Get AI-enhanced reasoning
            ai_reasoning = self._get_ai_reasoning(
                parameter_name="earnings.profitTarget",
                current_value=current_target,
                suggested_value=recommended_target,
                metrics=metrics,
                context=statistical_context,
                statistical_reasoning=statistical_reasoning
            )
            
            recommendations.append({
                "parameter": "earnings.profitTarget",
                "category": "strategy",
                "current_value": current_target,
                "recommended_value": round(recommended_target, 1),
                "reasoning": ai_reasoning,
                "confidence": min(0.85, (avg_win_pct - current_target) / current_target),
                "expected_improvement": f"+{((recommended_target - current_target) / current_target * metrics.total_return_pct * 0.3):.1f}% annual return"
            })
        
        return recommendations
    
    def _analyze_stop_losses(
        self,
        metrics: BacktestMetrics,
        current_config: Dict,
        trades: List[BacktestResult] = None
    ) -> List[Dict]:
        """Analyze if stop losses are too tight or too loose"""
        recommendations = []
        
        if not metrics.avg_loss_size or metrics.losing_trades == 0:
            return recommendations
        
        # Calculate average loser as percentage
        avg_loss_pct = abs((metrics.avg_loss_size / 10000.0) * 100)
        
        # Current stop loss
        current_stop = current_config.get('earnings', {}).get('stopLoss', 8.0)
        
        # If average losses are hitting stop too often, stop might be too tight
        # If average losses are much smaller than stop, stop is appropriate or could be tighter
        
        if avg_loss_pct < current_stop * 0.7:  # Losses are 30% smaller than stop
            recommended_stop = max(avg_loss_pct * 1.1, 5.0)  # 110% of avg loss, floor at 5%
            
            # Build statistical context for AI
            statistical_context = f"Average losing trade was -{avg_loss_pct:.1f}%, which is {((1 - avg_loss_pct / current_stop) * 100):.0f}% smaller than the current -{current_stop}% stop loss. This indicates the stop is wider than necessary, allowing trades to lose more capital than typical."
            
            # Generate fallback reasoning
            statistical_reasoning = f"Average losing trade was -{avg_loss_pct:.1f}%. Current -{current_stop}% stop is too wide, tighten to preserve capital."
            
            # Get AI-enhanced reasoning
            ai_reasoning = self._get_ai_reasoning(
                parameter_name="earnings.stopLoss",
                current_value=current_stop,
                suggested_value=recommended_stop,
                metrics=metrics,
                context=statistical_context,
                statistical_reasoning=statistical_reasoning
            )
            
            recommendations.append({
                "parameter": "earnings.stopLoss",
                "category": "strategy",
                "current_value": current_stop,
                "recommended_value": round(recommended_stop, 1),
                "reasoning": ai_reasoning,
                "confidence": 0.72,
                "expected_improvement": f"-{((current_stop - recommended_stop) / current_stop * 0.5):.1f}% max drawdown"
            })
        
        return recommendations
    
    def _analyze_position_sizing(
        self,
        metrics: BacktestMetrics,
        current_config: Dict
    ) -> List[Dict]:
        """Analyze if position sizing is appropriate for win rate and volatility"""
        recommendations = []
        
        # Current max position size
        current_max_pos = current_config.get('riskManagement', {}).get('maxSinglePosition', 5.0)
        
        # If win rate is high and drawdown is low, can increase position sizing
        if metrics.win_rate > 55.0 and metrics.max_drawdown and metrics.max_drawdown < 10.0:
            # Kelly criterion suggests position sizing based on win rate and avg win/loss ratio
            if metrics.avg_win_size and metrics.avg_loss_size and metrics.avg_loss_size > 0:
                win_loss_ratio = metrics.avg_win_size / metrics.avg_loss_size
                kelly_fraction = (metrics.win_rate / 100.0 * win_loss_ratio - (1 - metrics.win_rate / 100.0)) / win_loss_ratio
                kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
                
                suggested_position = kelly_fraction * 100 * 0.5  # Use half-Kelly for safety
                
                if suggested_position > current_max_pos * 1.15:  # 15% larger
                    recommended_pos = min(suggested_position, current_max_pos * 1.3, 8.0)  # Max 30% increase, cap at 8%
                    
                    # Build statistical context for AI
                    statistical_context = f"Win rate of {metrics.win_rate:.1f}% with max drawdown of only {metrics.max_drawdown:.1f}% indicates strong risk-adjusted performance. Kelly criterion calculates optimal position size at {suggested_position:.1f}% (full Kelly). Using half-Kelly for safety suggests {recommended_pos:.1f}% vs current {current_max_pos:.1f}%."
                    
                    # Generate fallback reasoning
                    statistical_reasoning = f"Win rate of {metrics.win_rate:.1f}% and low drawdown ({metrics.max_drawdown:.1f}%) support larger position sizing. Kelly criterion suggests {suggested_position:.1f}%."
                    
                    # Get AI-enhanced reasoning
                    ai_reasoning = self._get_ai_reasoning(
                        parameter_name="riskManagement.maxSinglePosition",
                        current_value=current_max_pos,
                        suggested_value=recommended_pos,
                        metrics=metrics,
                        context=statistical_context,
                        statistical_reasoning=statistical_reasoning
                    )
                    
                    recommendations.append({
                        "parameter": "riskManagement.maxSinglePosition",
                        "category": "risk",
                        "current_value": current_max_pos,
                        "recommended_value": round(recommended_pos, 1),
                        "reasoning": ai_reasoning,
                        "confidence": 0.68,
                        "expected_improvement": f"+{((recommended_pos - current_max_pos) / current_max_pos * metrics.total_return_pct * 0.4):.1f}% annual return"
                    })
        
        return recommendations
    
    def _analyze_technical_filters(
        self,
        metrics: BacktestMetrics,
        current_config: Dict
    ) -> List[Dict]:
        """Analyze if technical filters are too restrictive or too loose"""
        recommendations = []
        
        # Current RSI filter
        current_rsi_min = current_config.get('technical', {}).get('rsiMin', 40.0)
        
        # If win rate is high but trade count is low, filters might be too restrictive
        if metrics.win_rate > 57.0 and metrics.total_trades < 100:
            recommended_rsi = max(current_rsi_min - 5.0, 30.0)
            
            # Build statistical context for AI
            statistical_context = f"Strategy achieved {metrics.win_rate:.1f}% win rate but only generated {metrics.total_trades} trades in the backtest period. This high-quality, low-quantity pattern suggests technical filters (RSI minimum: {current_rsi_min}) are too restrictive and leaving profitable opportunities on the table."
            
            # Generate fallback reasoning
            statistical_reasoning = f"High win rate ({metrics.win_rate:.1f}%) with low trade count ({metrics.total_trades}) suggests filters are too strict. Lowering RSI minimum would capture more opportunities."
            
            # Get AI-enhanced reasoning
            ai_reasoning = self._get_ai_reasoning(
                parameter_name="technical.rsiMin",
                current_value=current_rsi_min,
                suggested_value=recommended_rsi,
                metrics=metrics,
                context=statistical_context,
                statistical_reasoning=statistical_reasoning
            )
            
            recommendations.append({
                "parameter": "technical.rsiMin",
                "category": "technical",
                "current_value": current_rsi_min,
                "recommended_value": recommended_rsi,
                "reasoning": ai_reasoning,
                "confidence": 0.75,
                "expected_improvement": f"+{(5.0 / current_rsi_min * 20):.0f}% more trading opportunities"
            })
        
        return recommendations


def get_calibration_engine(db: Session) -> CalibrationEngine:
    """
    Get CalibrationEngine instance
    
    Args:
        db: Database session
    
    Returns:
        CalibrationEngine instance
    """
    return CalibrationEngine(db)
