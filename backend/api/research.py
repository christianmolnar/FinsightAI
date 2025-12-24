"""
Research API Endpoints
Provides stock research with AI recommendations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from services.ai_models import get_ai_service, Recommendation
from services.stock_researcher import get_researcher

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])


class AIModelResult(BaseModel):
    """Single AI model's recommendation"""
    model_config = {"protected_namespaces": ()}  # Allow model_name field
    
    model_name: str
    recommendation: str
    reasoning: str
    confidence: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None


class ResearchResponse(BaseModel):
    """Complete stock research response"""
    symbol: str
    consensus: str
    confidence: float
    agreement: bool
    models: List[AIModelResult]
    fundamental: Dict
    technical: Dict
    news: List[Dict]
    timestamp: str


@router.post("/stock/{symbol}", response_model=ResearchResponse)
async def research_stock(symbol: str):
    """
    Perform comprehensive stock research with AI recommendation.
    
    Process:
    1. Gather fundamental, technical, and news data
    2. Feed data to dual AI models (OpenAI + Claude)
    3. Return consensus recommendation with reasoning
    
    Returns:
        ResearchResponse with BUY/WAIT/AVOID recommendation
    """
    try:
        symbol = symbol.upper()
        logger.info(f"🔍 Starting research for {symbol}")
        
        # Get research data
        researcher = get_researcher()
        research = await researcher.research_stock(symbol)
        
        # Validate we got data
        if not research.get('fundamental') and not research.get('technical'):
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch data for symbol {symbol}. Please verify the ticker is valid."
            )
        
        # Get AI recommendations
        ai_service = get_ai_service()
        consensus = await ai_service.get_stock_recommendation(
            symbol=symbol,
            fundamental_data=research['fundamental'],
            technical_data=research['technical'],
            news_data=research['news']
        )
        
        # Format response
        response = ResearchResponse(
            symbol=symbol,
            consensus=consensus.consensus.value,
            confidence=round(consensus.confidence, 2),
            agreement=consensus.agreement,
            models=[
                AIModelResult(
                    model_name=model.model_name,
                    recommendation=model.recommendation.value,
                    reasoning=model.reasoning,
                    confidence=round(model.confidence, 2),
                    entry_price=model.entry_price,
                    stop_loss=model.stop_loss,
                    target_price=model.target_price
                )
                for model in consensus.models
            ],
            fundamental=research['fundamental'],
            technical=research['technical'],
            news=research['news'],
            timestamp=research['timestamp']
        )
        
        logger.info(f"✅ Research complete for {symbol}: {consensus.consensus.value} (confidence: {consensus.confidence:.0%})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Research failed for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "research",
        "ai_models": ["OpenAI GPT-4", "Anthropic Claude"],
        "data_sources": ["yfinance"]
    }
