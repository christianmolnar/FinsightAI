"""
Research API Endpoints
Provides stock research with AI recommendations.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
from datetime import datetime

from services.ai_models import get_ai_service, Recommendation
from services.stock_researcher import get_researcher
from services.sell_validator import get_sell_validator, SellReason

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


class PositionData(BaseModel):
    """Position data for sell validation"""
    quantity: float
    avg_price: float
    current_price: float
    purchase_date: str  # ISO format


class SellValidationRequest(BaseModel):
    """Request for sell validation"""
    position: PositionData
    reason: str  # SellReason enum value
    custom_reason: Optional[str] = None


class TaxImplications(BaseModel):
    """Tax implications of selling"""
    holding_period_days: int
    is_long_term: bool
    tax_type: str
    tax_rate: float
    estimated_tax: float
    proceeds_after_tax: float
    days_until_long_term: int


class SellValidationResponse(BaseModel):
    """Sell validation response"""
    symbol: str
    validation: str  # AGREE, WAIT, or DISAGREE
    reasoning: str
    confidence: float
    agreement: bool
    openai_recommendation: str
    claude_recommendation: str
    tax_implications: TaxImplications
    alternatives: List[str]
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


@router.post("/sell-validation/{symbol}", response_model=SellValidationResponse)
async def validate_sell(symbol: str, request: SellValidationRequest):
    """Validate a sell decision with AI"""
    try:
        validator = get_sell_validator()
        
        # Convert position data to dict
        position_data = {
            'quantity': request.position.quantity,
            'avg_price': request.position.avg_price,
            'current_price': request.position.current_price,
            'purchase_date': request.position.purchase_date
        }
        
        # Parse reason
        reason = SellReason(request.reason)
        
        # Get validation
        result = await validator.validate_sell(
            symbol=symbol,
            position_data=position_data,
            user_reason=reason,
            custom_reason=request.custom_reason
        )
        
        return SellValidationResponse(
            symbol=result.symbol,
            validation=result.validation.value,
            reasoning=result.reasoning,
            confidence=result.confidence,
            agreement=result.agreement,
            openai_recommendation=result.openai_recommendation,
            claude_recommendation=result.claude_recommendation,
            tax_implications=TaxImplications(**result.tax_implications),
            alternatives=result.alternatives,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Sell validation failed for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Sell validation failed: {str(e)}"
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
