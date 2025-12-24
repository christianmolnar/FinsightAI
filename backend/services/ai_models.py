"""
Dual AI Model Service - OpenAI GPT-4 + Anthropic Claude
Provides stock research recommendations with consensus logic.
"""
import os
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class Recommendation(str, Enum):
    """Stock recommendation types"""
    BUY = "BUY"
    WAIT = "WAIT"
    AVOID = "AVOID"


class AIModelResponse:
    """Response from a single AI model"""
    def __init__(
        self,
        model_name: str,
        recommendation: Recommendation,
        reasoning: str,
        confidence: float,
        entry_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        target_price: Optional[float] = None
    ):
        self.model_name = model_name
        self.recommendation = recommendation
        self.reasoning = reasoning
        self.confidence = confidence  # 0.0 to 1.0
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.target_price = target_price


class ConsensusResponse:
    """Combined response from multiple AI models"""
    def __init__(
        self,
        consensus: Recommendation,
        models: List[AIModelResponse],
        agreement: bool,
        confidence: float
    ):
        self.consensus = consensus
        self.models = models
        self.agreement = agreement  # True if all models agree
        self.confidence = confidence  # Average confidence when agreed, lower when disagreed


class DualAIService:
    """
    Coordinates OpenAI GPT-4 and Anthropic Claude for stock research.
    Returns consensus recommendations with reasoning from both models.
    """
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.openai_key:
            logger.warning("⚠️ OPENAI_API_KEY not set - OpenAI calls will fail")
        if not self.anthropic_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY not set - Anthropic calls will fail")
    
    async def get_stock_recommendation(
        self,
        symbol: str,
        fundamental_data: Dict,
        technical_data: Dict,
        news_data: List[Dict]
    ) -> ConsensusResponse:
        """
        Get stock recommendation from both AI models and return consensus.
        
        Args:
            symbol: Stock ticker symbol
            fundamental_data: P/E ratio, EPS, margins, etc.
            technical_data: RSI, MACD, moving averages, etc.
            news_data: Recent news articles with sentiment
            
        Returns:
            ConsensusResponse with recommendations from both models
        """
        # Build research context for AI models
        context = self._build_research_context(
            symbol, fundamental_data, technical_data, news_data
        )
        
        # Get recommendations from both models in parallel
        openai_response = await self._call_openai(symbol, context)
        anthropic_response = await self._call_anthropic(symbol, context)
        
        # Calculate consensus
        consensus = self._calculate_consensus(openai_response, anthropic_response)
        
        return consensus
    
    def _build_research_context(
        self,
        symbol: str,
        fundamental_data: Dict,
        technical_data: Dict,
        news_data: List[Dict]
    ) -> str:
        """Build formatted research context for AI models"""
        context = f"""
Stock Symbol: {symbol}

FUNDAMENTAL ANALYSIS:
- P/E Ratio: {fundamental_data.get('pe_ratio', 'N/A')}
- EPS: ${fundamental_data.get('eps', 'N/A')}
- Profit Margin: {fundamental_data.get('profit_margin', 'N/A')}%
- Revenue Growth: {fundamental_data.get('revenue_growth', 'N/A')}%
- Debt to Equity: {fundamental_data.get('debt_to_equity', 'N/A')}

TECHNICAL ANALYSIS:
- RSI (14): {technical_data.get('rsi', 'N/A')}
- MACD: {technical_data.get('macd', 'N/A')}
- 50-Day MA: ${technical_data.get('ma_50', 'N/A')}
- 200-Day MA: ${technical_data.get('ma_200', 'N/A')}
- Current Price: ${technical_data.get('current_price', 'N/A')}

RECENT NEWS:
"""
        for news in news_data[:5]:  # Top 5 news items
            context += f"- {news.get('title', '')} (Sentiment: {news.get('sentiment', 'neutral')})\n"
        
        context += """

Based on this data, provide:
1. Recommendation (BUY, WAIT, or AVOID)
2. Your reasoning (2-3 sentences)
3. Confidence level (0-100%)
4. If BUY: Entry price, stop loss, and target price
"""
        return context
    
    async def _call_openai(self, symbol: str, context: str) -> AIModelResponse:
        """Call OpenAI GPT-4 API"""
        # TODO: Implement actual OpenAI API call
        # For now, return mock response
        logger.info(f"🤖 Calling OpenAI GPT-4 for {symbol}")
        
        return AIModelResponse(
            model_name="OpenAI GPT-4",
            recommendation=Recommendation.BUY,
            reasoning="Strong fundamentals with P/E below sector average. Technical indicators show bullish momentum.",
            confidence=0.85,
            entry_price=150.00,
            stop_loss=142.50,
            target_price=165.00
        )
    
    async def _call_anthropic(self, symbol: str, context: str) -> AIModelResponse:
        """Call Anthropic Claude API"""
        # TODO: Implement actual Anthropic API call
        # For now, return mock response
        logger.info(f"🤖 Calling Anthropic Claude for {symbol}")
        
        return AIModelResponse(
            model_name="Anthropic Claude",
            recommendation=Recommendation.WAIT,
            reasoning="While fundamentals are solid, RSI shows overbought conditions. Wait for pullback.",
            confidence=0.75,
            entry_price=145.00,
            stop_loss=138.00,
            target_price=160.00
        )
    
    def _calculate_consensus(
        self,
        openai: AIModelResponse,
        anthropic: AIModelResponse
    ) -> ConsensusResponse:
        """
        Calculate consensus between two AI model responses.
        If they agree: return consensus with high confidence.
        If they disagree: return WAIT with reasoning from both.
        """
        models = [openai, anthropic]
        agreement = openai.recommendation == anthropic.recommendation
        
        if agreement:
            # Both models agree - return consensus
            avg_confidence = (openai.confidence + anthropic.confidence) / 2
            logger.info(f"✅ Models agree: {openai.recommendation.value} (confidence: {avg_confidence:.0%})")
            
            return ConsensusResponse(
                consensus=openai.recommendation,
                models=models,
                agreement=True,
                confidence=avg_confidence
            )
        else:
            # Models disagree - return WAIT as safe default
            logger.warning(f"⚠️ Models disagree: {openai.recommendation.value} vs {anthropic.recommendation.value}")
            
            # Lower confidence when models disagree
            avg_confidence = (openai.confidence + anthropic.confidence) / 2 * 0.7
            
            return ConsensusResponse(
                consensus=Recommendation.WAIT,
                models=models,
                agreement=False,
                confidence=avg_confidence
            )


# Singleton instance
_ai_service: Optional[DualAIService] = None


def get_ai_service() -> DualAIService:
    """Get or create singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = DualAIService()
        logger.info("✅ Dual AI Service initialized")
    return _ai_service
