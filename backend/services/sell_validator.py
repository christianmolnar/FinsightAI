"""
Sell Validation Service
Validates sell decisions using AI analysis and tax implications
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from services.ai_models import get_ai_service
from services.stock_researcher import get_researcher

logger = logging.getLogger(__name__)


class SellReason(Enum):
    """Reasons for selling a position"""
    PROFIT_TARGET = "profit_target"
    OVERVALUED = "overvalued"
    BAD_NEWS = "bad_news"
    STOP_LOSS = "stop_loss"
    REBALANCE = "rebalance"
    NEED_CASH = "need_cash"
    BETTER_OPPORTUNITY = "better_opportunity"
    OTHER = "other"


class SellValidation(Enum):
    """AI validation result"""
    AGREE = "AGREE"
    WAIT = "WAIT"
    DISAGREE = "DISAGREE"


class SellValidationResult:
    """Complete sell validation result"""
    def __init__(
        self,
        symbol: str,
        validation: SellValidation,
        reasoning: str,
        confidence: float,
        agreement: bool,
        openai_recommendation: str,
        claude_recommendation: str,
        tax_implications: Dict,
        alternatives: List[str]
    ):
        self.symbol = symbol
        self.validation = validation
        self.reasoning = reasoning
        self.confidence = confidence
        self.agreement = agreement
        self.openai_recommendation = openai_recommendation
        self.claude_recommendation = claude_recommendation
        self.tax_implications = tax_implications
        self.alternatives = alternatives


class SellValidator:
    """Validates sell decisions with AI and tax analysis"""
    
    def __init__(self):
        self.ai_service = get_ai_service()
        self.researcher = get_researcher()
    
    async def validate_sell(
        self,
        symbol: str,
        position_data: Dict,
        user_reason: SellReason,
        custom_reason: Optional[str] = None
    ) -> SellValidationResult:
        """
        Validate a sell decision
        
        Args:
            symbol: Stock symbol
            position_data: Dict with quantity, avg_price, current_price, purchase_date
            user_reason: SellReason enum
            custom_reason: Optional custom reason text
        
        Returns:
            SellValidationResult with AI validation and tax analysis
        """
        logger.info(f"🔍 Validating sell decision for {symbol}")
        
        # Calculate tax implications
        tax_data = self._calculate_tax_implications(position_data)
        
        # Get current market data
        research = await self.researcher.research_stock(symbol)
        
        # Build validation context
        context = self._build_validation_context(
            symbol=symbol,
            position_data=position_data,
            user_reason=user_reason,
            custom_reason=custom_reason,
            tax_data=tax_data,
            market_data=research
        )
        
        # Get AI recommendations
        consensus = await self.ai_service.get_stock_recommendation(
            symbol=symbol,
            fundamental_data=research['fundamental'],
            technical_data=research['technical'],
            news_data=research['news']
        )
        
        # Determine validation result
        openai_rec = consensus.models[0].recommendation.value if len(consensus.models) > 0 else "UNKNOWN"
        claude_rec = consensus.models[1].recommendation.value if len(consensus.models) > 1 else "UNKNOWN"
        
        # Determine if we agree with the sell
        validation = self._determine_validation(
            user_reason=user_reason,
            openai_rec=openai_rec,
            claude_rec=claude_rec,
            tax_data=tax_data,
            position_data=position_data
        )
        
        # Generate alternatives
        alternatives = self._generate_alternatives(
            validation=validation,
            tax_data=tax_data,
            position_data=position_data
        )
        
        result = SellValidationResult(
            symbol=symbol,
            validation=validation,
            reasoning=f"AI consensus analysis based on market data and tax implications",
            confidence=consensus.confidence,
            agreement=consensus.agreement,
            openai_recommendation=openai_rec,
            claude_recommendation=claude_rec,
            tax_implications=tax_data,
            alternatives=alternatives
        )
        
        logger.info(f"✅ Validation complete for {symbol}: {validation.value}")
        return result
    
    def _calculate_tax_implications(self, position_data: Dict) -> Dict:
        """Calculate tax implications of selling"""
        # Parse purchase date and make timezone-aware if needed
        purchase_date_str = position_data['purchase_date'].replace('Z', '+00:00')
        purchase_date = datetime.fromisoformat(purchase_date_str)
        
        # Make purchase_date timezone-naive for comparison
        if purchase_date.tzinfo is not None:
            purchase_date = purchase_date.replace(tzinfo=None)
        
        holding_period = (datetime.now() - purchase_date).days
        
        # Calculate gain/loss
        quantity = position_data['quantity']
        avg_price = position_data['avg_price']
        current_price = position_data['current_price']
        
        cost_basis = quantity * avg_price
        current_value = quantity * current_price
        gain_loss = current_value - cost_basis
        
        # Determine tax treatment
        is_long_term = holding_period > 365
        
        if is_long_term:
            tax_rate = 0.15  # Long-term capital gains (simplified)
            tax_type = "Long-term capital gains"
        else:
            tax_rate = 0.24  # Short-term (ordinary income, simplified)
            tax_type = "Short-term capital gains"
        
        estimated_tax = max(0, gain_loss * tax_rate)
        proceeds_after_tax = current_value - estimated_tax
        
        days_until_long_term = max(0, 366 - holding_period)
        
        return {
            'holding_period_days': holding_period,
            'is_long_term': is_long_term,
            'tax_type': tax_type,
            'tax_rate': tax_rate,
            'estimated_tax': round(estimated_tax, 2),
            'proceeds_after_tax': round(proceeds_after_tax, 2),
            'days_until_long_term': days_until_long_term
        }
    
    def _build_validation_context(
        self,
        symbol: str,
        position_data: Dict,
        user_reason: SellReason,
        custom_reason: Optional[str],
        tax_data: Dict,
        market_data: Dict
    ) -> str:
        """Build context for AI validation"""
        reason_text = user_reason.value.replace('_', ' ').title()
        if custom_reason:
            reason_text += f": {custom_reason}"
        
        context = f"""
USER SELL DECISION TO VALIDATE:
Symbol: {symbol}
Reason: {reason_text}
Position: {position_data['quantity']} shares @ ${position_data['avg_price']:.2f}
Current Price: ${position_data['current_price']:.2f}
Holding Period: {tax_data['holding_period_days']} days
Tax Treatment: {tax_data['tax_type']} ({tax_data['tax_rate']*100:.0f}% rate)
Days Until Long-Term: {tax_data['days_until_long_term']}

VALIDATION TASK:
Analyze whether this sell decision is optimal given:
1. Current market conditions and stock fundamentals
2. Tax implications (short-term vs long-term)
3. User's stated reason for selling
4. Alternative strategies (hold, partial sell, etc.)

Provide recommendation: AGREE (good time to sell), WAIT (consider waiting), or DISAGREE (should hold).
"""
        return context
    
    def _determine_validation(
        self,
        user_reason: SellReason,
        openai_rec: str,
        claude_rec: str,
        tax_data: Dict,
        position_data: Dict
    ) -> SellValidation:
        """Determine validation result"""
        
        # If both AIs say SELL, we AGREE
        if "SELL" in openai_rec.upper() and "SELL" in claude_rec.upper():
            return SellValidation.AGREE
        
        # If both say BUY/HOLD, we DISAGREE
        if ("BUY" in openai_rec.upper() or "HOLD" in openai_rec.upper()) and \
           ("BUY" in claude_rec.upper() or "HOLD" in claude_rec.upper()):
            
            # Unless it's a stop-loss situation
            if user_reason == SellReason.STOP_LOSS:
                return SellValidation.AGREE
            
            # Or close to long-term tax treatment
            if tax_data['days_until_long_term'] <= 30:
                return SellValidation.WAIT
            
            return SellValidation.DISAGREE
        
        # Mixed signals - check tax situation
        if not tax_data['is_long_term'] and tax_data['days_until_long_term'] <= 60:
            return SellValidation.WAIT
        
        return SellValidation.WAIT
    
    def _generate_alternatives(
        self,
        validation: SellValidation,
        tax_data: Dict,
        position_data: Dict
    ) -> List[str]:
        """Generate alternative recommendations"""
        alternatives = []
        
        if validation == SellValidation.WAIT:
            if not tax_data['is_long_term']:
                alternatives.append(
                    f"Wait {tax_data['days_until_long_term']} days for long-term capital gains treatment "
                    f"(save {(tax_data['tax_rate'] - 0.15) * 100:.0f}% in taxes)"
                )
        
        if validation == SellValidation.DISAGREE:
            alternatives.append("Hold position - fundamentals remain strong")
            alternatives.append(f"Set stop-loss at {position_data['current_price'] * 0.95:.2f} (-5%)")
            alternatives.append("Consider selling covered calls to generate income while holding")
        
        if validation == SellValidation.AGREE:
            alternatives.append("Execute full sale at current market price")
            alternatives.append(f"Consider partial sale (50%) to lock in gains while maintaining exposure")
        
        # Always include rebalancing option
        alternatives.append("Rebalance into diversified positions to reduce concentration risk")
        
        return alternatives


# Singleton instance
_validator_instance = None

def get_sell_validator() -> SellValidator:
    """Get singleton sell validator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = SellValidator()
    return _validator_instance
