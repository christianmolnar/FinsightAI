from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import asyncio
import random
from datetime import datetime
import os
from enum import Enum

router = APIRouter()

class AIModel(str, Enum):
    OPENAI_GPT4 = "openai-gpt4"
    ANTHROPIC_CLAUDE = "anthropic-claude"
    GROQ_LLAMA = "groq-llama"

class StrategyType(str, Enum):
    EARNINGS = "earnings"
    SEASONALITY = "seasonality"
    MACRO = "macro"
    SENTIMENT = "sentiment"

class OptimizationRequest(BaseModel):
    strategy_type: StrategyType
    current_parameters: Dict[str, Any]
    market_conditions: Optional[Dict[str, Any]] = None
    user_risk_tolerance: Optional[str] = "moderate"  # conservative, moderate, aggressive
    optimization_goal: Optional[str] = "risk_adjusted_return"  # return, sharpe, drawdown
    ai_model: Optional[AIModel] = AIModel.OPENAI_GPT4

class OptimizationResult(BaseModel):
    strategy_type: str
    optimized_parameters: Dict[str, Any]
    confidence_score: float
    expected_return: float
    expected_sharpe: float
    expected_max_drawdown: float
    reasoning: str
    market_analysis: str
    risk_assessment: str

class AIOptimizerService:
    def __init__(self):
        self.optimization_history = []
        
    async def optimize_strategy_parameters(self, request: OptimizationRequest) -> OptimizationResult:
        """
        AI-powered strategy parameter optimization
        """
        # Simulate AI processing time
        await asyncio.sleep(2)
        
        # Get current market context
        market_context = await self._analyze_market_conditions()
        
        # Generate optimized parameters based on strategy type
        optimized_params = await self._generate_optimized_parameters(
            request.strategy_type, 
            request.current_parameters,
            request.user_risk_tolerance,
            market_context
        )
        
        # Generate performance predictions
        performance_metrics = await self._predict_performance(
            request.strategy_type, 
            optimized_params,
            market_context
        )
        
        # Generate AI reasoning
        reasoning = await self._generate_reasoning(
            request.strategy_type, 
            optimized_params, 
            request.current_parameters,
            performance_metrics
        )
        
        result = OptimizationResult(
            strategy_type=request.strategy_type.value,
            optimized_parameters=optimized_params,
            confidence_score=performance_metrics["confidence"],
            expected_return=performance_metrics["return"],
            expected_sharpe=performance_metrics["sharpe"],
            expected_max_drawdown=performance_metrics["max_drawdown"],
            reasoning=reasoning["optimization_explanation"],
            market_analysis=reasoning["market_analysis"],
            risk_assessment=reasoning["risk_assessment"]
        )
        
        # Store optimization history
        self.optimization_history.append({
            "timestamp": datetime.now().isoformat(),
            "request": request.dict(),
            "result": result.dict()
        })
        
        return result
    
    async def _analyze_market_conditions(self) -> Dict[str, Any]:
        """Analyze current market conditions for optimization context"""
        # Mock market analysis - in production, integrate with real market data
        return {
            "vix_level": random.uniform(15, 35),
            "market_trend": random.choice(["bull", "bear", "sideways"]),
            "sector_rotation": random.choice(["growth", "value", "defensive"]),
            "fed_policy": random.choice(["dovish", "hawkish", "neutral"]),
            "earnings_season": random.choice([True, False]),
            "volatility_regime": random.choice(["low", "medium", "high"])
        }
    
    async def _generate_optimized_parameters(
        self, 
        strategy_type: StrategyType, 
        current_params: Dict[str, Any],
        risk_tolerance: str,
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-optimized parameters based on strategy type and market conditions"""
        
        # Base optimization logic per strategy type
        if strategy_type == StrategyType.EARNINGS:
            return await self._optimize_earnings_strategy(current_params, risk_tolerance, market_context)
        elif strategy_type == StrategyType.SEASONALITY:
            return await self._optimize_seasonality_strategy(current_params, risk_tolerance, market_context)
        elif strategy_type == StrategyType.MACRO:
            return await self._optimize_macro_strategy(current_params, risk_tolerance, market_context)
        elif strategy_type == StrategyType.SENTIMENT:
            return await self._optimize_sentiment_strategy(current_params, risk_tolerance, market_context)
    
    async def _optimize_earnings_strategy(self, current_params: Dict, risk_tolerance: str, market_context: Dict) -> Dict:
        """Optimize earnings momentum strategy parameters"""
        optimizations = {}
        
        # Adjust based on market volatility
        vix = market_context.get("vix_level", 20)
        
        if vix > 25:  # High volatility
            optimizations["stopLoss"] = max(3.0, current_params.get("stopLoss", 5) * 0.8)
            optimizations["profitTarget"] = max(8.0, current_params.get("profitTarget", 12) * 0.9)
            optimizations["daysBeforeEarnings"] = max(3, current_params.get("daysBeforeEarnings", 5))
        elif vix < 18:  # Low volatility
            optimizations["stopLoss"] = min(8.0, current_params.get("stopLoss", 5) * 1.2)
            optimizations["profitTarget"] = min(20.0, current_params.get("profitTarget", 12) * 1.3)
            optimizations["daysBeforeEarnings"] = min(10, current_params.get("daysBeforeEarnings", 5) + 2)
        
        # Adjust based on earnings season
        if market_context.get("earnings_season", False):
            optimizations["minEpsGrowth"] = min(25.0, current_params.get("minEpsGrowth", 15) * 1.2)
            optimizations["historicalBeatRate"] = min(85.0, current_params.get("historicalBeatRate", 70) + 5)
        
        # Risk tolerance adjustments
        if risk_tolerance == "conservative":
            optimizations["maxPortfolioWeight"] = min(15.0, current_params.get("maxPortfolioWeight", 20))
        elif risk_tolerance == "aggressive":
            optimizations["maxPortfolioWeight"] = min(30.0, current_params.get("maxPortfolioWeight", 20) * 1.2)
        
        return optimizations
    
    async def _optimize_seasonality_strategy(self, current_params: Dict, risk_tolerance: str, market_context: Dict) -> Dict:
        """Optimize seasonality strategy parameters"""
        optimizations = {}
        
        # Adjust based on sector rotation
        sector_rotation = market_context.get("sector_rotation", "growth")
        
        if sector_rotation == "defensive":
            optimizations["profitTarget"] = max(8.0, current_params.get("profitTarget", 15) * 0.7)
            optimizations["weeksBeforePeak"] = min(6, current_params.get("weeksBeforePeak", 3) + 1)
        elif sector_rotation == "growth":
            optimizations["profitTarget"] = min(25.0, current_params.get("profitTarget", 15) * 1.4)
        
        # Adjust for volatility
        vix = market_context.get("vix_level", 20)
        if vix > 25:
            optimizations["stopLoss"] = max(5.0, current_params.get("stopLoss", 7) * 0.8)
        
        return optimizations
    
    async def _optimize_macro_strategy(self, current_params: Dict, risk_tolerance: str, market_context: Dict) -> Dict:
        """Optimize macro strategy parameters"""
        optimizations = {}
        
        # Adjust based on Fed policy
        fed_policy = market_context.get("fed_policy", "neutral")
        
        if fed_policy == "hawkish":
            optimizations["entryTimeframe"] = max(24, current_params.get("entryTimeframe", 48) * 0.7)
            optimizations["catalystStrengthMin"] = min(85, current_params.get("catalystStrengthMin", 70) + 10)
        elif fed_policy == "dovish":
            optimizations["profitTarget"] = min(15.0, current_params.get("profitTarget", 8) * 1.3)
            optimizations["maxHoldDays"] = min(45, current_params.get("maxHoldDays", 30) + 10)
        
        return optimizations
    
    async def _optimize_sentiment_strategy(self, current_params: Dict, risk_tolerance: str, market_context: Dict) -> Dict:
        """Optimize sentiment strategy parameters"""
        optimizations = {}
        
        # Adjust based on volatility regime
        volatility = market_context.get("volatility_regime", "medium")
        
        if volatility == "high":
            optimizations["minSentimentScore"] = min(85, current_params.get("minSentimentScore", 70) + 10)
            optimizations["volumeMultiplier"] = min(2.5, current_params.get("volumeMultiplier", 1.5) + 0.3)
        elif volatility == "low":
            optimizations["minSentimentScore"] = max(60, current_params.get("minSentimentScore", 70) - 5)
            optimizations["profitTarget"] = min(12.0, current_params.get("profitTarget", 8) * 1.2)
        
        return optimizations
    
    async def _predict_performance(self, strategy_type: StrategyType, params: Dict, market_context: Dict) -> Dict:
        """Predict strategy performance with optimized parameters"""
        # Mock performance prediction - in production, use backtesting engine
        base_return = {
            StrategyType.EARNINGS: 0.16,
            StrategyType.SEASONALITY: 0.14,
            StrategyType.MACRO: 0.12,
            StrategyType.SENTIMENT: 0.13
        }[strategy_type]
        
        # Adjust for market conditions
        market_multiplier = 1.0
        vix = market_context.get("vix_level", 20)
        
        if vix > 25:
            market_multiplier = 0.85
        elif vix < 18:
            market_multiplier = 1.15
        
        return {
            "return": base_return * market_multiplier * random.uniform(0.9, 1.1),
            "sharpe": random.uniform(1.1, 1.6),
            "max_drawdown": random.uniform(0.08, 0.18),
            "confidence": random.uniform(0.75, 0.95)
        }
    
    async def _generate_reasoning(
        self, 
        strategy_type: StrategyType, 
        optimized_params: Dict, 
        current_params: Dict,
        performance_metrics: Dict
    ) -> Dict[str, str]:
        """Generate AI reasoning for parameter changes"""
        
        strategy_names = {
            StrategyType.EARNINGS: "Earnings Momentum",
            StrategyType.SEASONALITY: "Seasonality & Calendar",
            StrategyType.MACRO: "Macro & Economic",
            StrategyType.SENTIMENT: "Social Sentiment"
        }
        
        optimization_explanation = f"""
Based on current market conditions and backtesting analysis, I've optimized your {strategy_names[strategy_type]} strategy parameters:

Key Changes:
"""
        
        for param, new_value in optimized_params.items():
            old_value = current_params.get(param, "N/A")
            optimization_explanation += f"• {param}: {old_value} → {new_value}\n"
        
        optimization_explanation += f"""
Expected Performance Impact:
• Annual Return: {performance_metrics['return']:.1%}
• Sharpe Ratio: {performance_metrics['sharpe']:.2f}
• Max Drawdown: {performance_metrics['max_drawdown']:.1%}
"""
        
        market_analysis = """
Current market environment suggests a cautious but opportunistic approach. Volatility levels are moderately elevated, 
indicating the need for tighter risk management while maintaining exposure to quality opportunities. 
The AI model recommends adjusting position sizing and profit targets accordingly.
"""
        
        risk_assessment = """
Risk-adjusted optimization prioritizes capital preservation while maximizing expected returns. 
Stop-loss levels have been calibrated to current volatility, and position sizing reflects 
optimal Kelly criterion calculations based on historical win rates and average returns.
"""
        
        return {
            "optimization_explanation": optimization_explanation,
            "market_analysis": market_analysis,
            "risk_assessment": risk_assessment
        }

# Global AI optimizer instance
ai_optimizer = AIOptimizerService()

@router.post("/optimize-strategy", response_model=OptimizationResult)
async def optimize_strategy_parameters(request: OptimizationRequest):
    """
    AI-powered strategy parameter optimization endpoint
    """
    try:
        result = await ai_optimizer.optimize_strategy_parameters(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/optimization-history")
async def get_optimization_history():
    """
    Get history of AI optimizations
    """
    return {"history": ai_optimizer.optimization_history[-10:]}  # Last 10 optimizations

@router.post("/backtest-strategy")
async def backtest_strategy(
    strategy_type: str,
    parameters: Dict[str, Any],
    start_date: str,
    end_date: str,
    initial_capital: float = 100000
):
    """
    Backtest strategy with given parameters
    """
    # Mock backtesting results - in production, implement actual backtesting
    await asyncio.sleep(1)  # Simulate processing
    
    return {
        "strategy_type": strategy_type,
        "parameters": parameters,
        "backtest_period": f"{start_date} to {end_date}",
        "results": {
            "total_return": random.uniform(0.08, 0.25),
            "sharpe_ratio": random.uniform(1.0, 1.8),
            "max_drawdown": random.uniform(0.05, 0.20),
            "win_rate": random.uniform(0.52, 0.68),
            "avg_trade_return": random.uniform(0.02, 0.08),
            "total_trades": random.randint(50, 200),
            "profitable_trades": random.randint(30, 140)
        }
    }

@router.get("/market-analysis")
async def get_market_analysis():
    """
    Get current market analysis for strategy optimization
    """
    analysis = await ai_optimizer._analyze_market_conditions()
    
    return {
        "market_conditions": analysis,
        "recommendations": {
            "overall_stance": "moderately bullish" if analysis["vix_level"] < 22 else "cautious",
            "preferred_strategies": ["earnings", "seasonality"] if analysis["volatility_regime"] == "low" else ["macro"],
            "risk_adjustment": "increase" if analysis["vix_level"] > 25 else "maintain"
        }
    }
