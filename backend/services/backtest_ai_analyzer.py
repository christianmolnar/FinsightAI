"""
Backtest AI Analyzer - Sends trade results to AI for parameter optimization recommendations

This service analyzes backtest results and provides intelligent recommendations for
strategy parameter adjustments using Claude/GPT.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import anthropic
from openai import OpenAI

class BacktestAIAnalyzer:
    """Analyzes backtest results and provides AI-powered optimization recommendations"""
    
    def __init__(self, ai_provider: str = "anthropic"):
        """
        Initialize AI analyzer
        
        Args:
            ai_provider: "anthropic" (Claude) or "openai" (GPT)
        """
        self.ai_provider = ai_provider
        
        if ai_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-3-5-sonnet-20241022"
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
    
    async def analyze_and_recommend(
        self,
        trades: List[Dict],
        current_params: Dict,
        metrics: Dict
    ) -> Dict:
        """
        Analyze trades and provide parameter recommendations
        
        Args:
            trades: List of trade dictionaries from backtest
            current_params: Current strategy parameters
            metrics: Backtest metrics (sharpe, win_rate, etc.)
        
        Returns:
            Dictionary with recommendations, analysis, and expected impact
        """
        # Batch trades (100 at a time to avoid token limits)
        batches = self._batch_trades(trades, batch_size=100)
        
        all_recommendations = []
        
        for i, batch in enumerate(batches):
            batch_recs = await self._analyze_batch(
                batch, 
                current_params, 
                metrics,
                batch_num=i+1,
                total_batches=len(batches)
            )
            all_recommendations.extend(batch_recs['recommendations'])
        
        # Consolidate recommendations
        consolidated = self._consolidate_recommendations(all_recommendations)
        
        return {
            'recommendations': consolidated,
            'total_trades_analyzed': len(trades),
            'batches_processed': len(batches),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _analyze_batch(
        self,
        trades: List[Dict],
        current_params: Dict,
        metrics: Dict,
        batch_num: int,
        total_batches: int
    ) -> Dict:
        """Analyze single batch of trades"""
        
        # Prepare trade summary
        trade_summary = self._summarize_trades(trades)
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(
            trade_summary,
            current_params,
            metrics,
            batch_num,
            total_batches
        )
        
        # Call AI
        if self.ai_provider == "anthropic":
            response = await self._call_claude(prompt)
        else:
            response = await self._call_openai(prompt)
        
        # Parse response
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return {
                'recommendations': [],
                'error': 'Failed to parse AI response',
                'raw_response': response
            }
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Claude API"""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return message.content[0].text
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=2048
        )
        return response.choices[0].message.content
    
    def _summarize_trades(self, trades: List[Dict]) -> str:
        """Convert trades to AI-readable summary"""
        summary = []
        
        for trade in trades:
            summary.append({
                'symbol': trade.get('symbol'),
                'strategy': trade.get('strategy'),
                'entry_date': trade.get('entry_date'),
                'exit_date': trade.get('exit_date'),
                'hold_days': trade.get('hold_days'),
                'return_pct': round(trade.get('return_pct', 0), 2),
                'outcome': 'win' if trade.get('profit_loss', 0) > 0 else 'loss',
                'exit_reason': trade.get('exit_reason'),
                'params_used': trade.get('params_used', {})  # Parameters that triggered this trade
            })
        
        return json.dumps(summary, indent=2)
    
    def _create_analysis_prompt(
        self,
        trade_summary: str,
        current_params: Dict,
        metrics: Dict,
        batch_num: int,
        total_batches: int
    ) -> str:
        """Create prompt for AI analysis"""
        
        return f"""You are a quantitative trading analyst optimizing strategy parameters based on backtest results.

CURRENT STRATEGY PARAMETERS:
{json.dumps(current_params, indent=2)}

BACKTEST METRICS:
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
- Total Return: {metrics.get('total_return_pct', 0):.1f}%
- Win Rate: {metrics.get('win_rate', 0):.1f}%
- Average Win: {metrics.get('avg_win_pct', 0):.2f}%
- Average Loss: {metrics.get('avg_loss_pct', 0):.2f}%
- Max Drawdown: {metrics.get('max_drawdown_pct', 0):.1f}%

TRADE RESULTS (Batch {batch_num}/{total_batches} - {len(json.loads(trade_summary))} trades):
{trade_summary}

ANALYSIS REQUIRED:
1. Identify patterns in losing trades
2. Suggest specific parameter adjustments to reduce losses
3. Explain expected impact of each change
4. Prioritize recommendations by potential improvement

CRITICAL: Only suggest changes to parameters that appear in 'params_used' field of losing trades.

Return JSON format:
{{
  "recommendations": [
    {{
      "parameter": "earnings.minEpsGrowth",
      "current_value": 15,
      "suggested_value": 20,
      "reason": "55% of losses had EPS growth 15-18%. Raising threshold would filter weak candidates.",
      "expected_impact": "+5% win rate, -10% trade frequency",
      "confidence": "high|medium|low",
      "priority": 1
    }}
  ],
  "overall_assessment": "Brief summary of main findings",
  "risk_level": "low|medium|high"
}}"""
    
    def _batch_trades(self, trades: List[Dict], batch_size: int = 100) -> List[List[Dict]]:
        """Split trades into batches"""
        batches = []
        for i in range(0, len(trades), batch_size):
            batches.append(trades[i:i + batch_size])
        return batches
    
    def _consolidate_recommendations(self, all_recs: List[Dict]) -> List[Dict]:
        """
        Consolidate recommendations from multiple batches
        Merge similar recommendations and prioritize
        """
        # Group by parameter
        param_recs = {}
        
        for rec in all_recs:
            param = rec.get('parameter')
            if param not in param_recs:
                param_recs[param] = []
            param_recs[param].append(rec)
        
        # Consolidate each parameter
        consolidated = []
        for param, recs in param_recs.items():
            if len(recs) == 1:
                consolidated.append(recs[0])
            else:
                # Average suggested values, combine reasons
                avg_value = sum(r.get('suggested_value', 0) for r in recs) / len(recs)
                reasons = " | ".join(set(r.get('reason', '') for r in recs))
                
                consolidated.append({
                    'parameter': param,
                    'current_value': recs[0].get('current_value'),
                    'suggested_value': round(avg_value, 2),
                    'reason': reasons,
                    'expected_impact': recs[0].get('expected_impact'),
                    'confidence': self._consolidate_confidence(recs),
                    'priority': min(r.get('priority', 99) for r in recs),
                    'times_suggested': len(recs)
                })
        
        # Sort by priority
        consolidated.sort(key=lambda x: x.get('priority', 99))
        
        return consolidated
    
    def _consolidate_confidence(self, recs: List[Dict]) -> str:
        """Determine consolidated confidence level"""
        confidences = [r.get('confidence', 'low') for r in recs]
        high_count = confidences.count('high')
        
        if high_count >= len(confidences) * 0.7:
            return 'high'
        elif high_count >= len(confidences) * 0.4:
            return 'medium'
        else:
            return 'low'
    
    async def analyze_failure(
        self,
        worse_metrics: Dict,
        previous_best: Dict,
        failed_adjustments: List[Dict]
    ) -> List[Dict]:
        """
        Analyze why adjustments made things worse
        Provide alternative recommendations
        
        Args:
            worse_metrics: Metrics from failed iteration
            previous_best: Parameters that performed better
            failed_adjustments: Recommendations that were applied
        
        Returns:
            New recommendations to try
        """
        prompt = f"""You are a quantitative trading analyst. Previous parameter adjustments made performance WORSE.

PREVIOUS BEST METRICS:
- Sharpe Ratio: {previous_best.get('sharpe_ratio', 0):.2f}
- Total Return: {previous_best.get('total_return_pct', 0):.1f}%
- Win Rate: {previous_best.get('win_rate', 0):.1f}%

CURRENT (WORSE) METRICS:
- Sharpe Ratio: {worse_metrics.get('sharpe_ratio', 0):.2f}
- Total Return: {worse_metrics.get('total_return_pct', 0):.1f}%
- Win Rate: {worse_metrics.get('win_rate', 0):.1f}%

FAILED ADJUSTMENTS:
{json.dumps(failed_adjustments, indent=2)}

ANALYSIS REQUIRED:
1. Why did these adjustments fail?
2. What alternative approach should we try?
3. Should we reverse some changes?

Return JSON format:
{{
  "recommendations": [
    {{
      "parameter": "...",
      "suggested_value": ...,
      "reason": "Why this different approach",
      "expected_impact": "...",
      "confidence": "...",
      "priority": 1
    }}
  ],
  "failure_analysis": "Brief explanation of why previous changes failed",
  "approach": "conservative|moderate|aggressive"
}}"""
        
        if self.ai_provider == "anthropic":
            response = await self._call_claude(prompt)
        else:
            response = await self._call_openai(prompt)
        
        try:
            result = json.loads(response)
            return result['recommendations']
        except:
            return []


def apply_recommendations(current_params: Dict, recommendations: List[Dict]) -> Dict:
    """
    Apply AI recommendations to strategy parameters
    
    Args:
        current_params: Current parameter dict
        recommendations: List of recommendation dicts
    
    Returns:
        Updated parameters dict
    """
    updated = current_params.copy()
    
    for rec in recommendations:
        param_path = rec['parameter'].split('.')
        
        # Navigate to nested parameter
        target = updated
        for key in param_path[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # Update value
        final_key = param_path[-1]
        if final_key in target:
            target[final_key] = rec['suggested_value']
    
    return updated
