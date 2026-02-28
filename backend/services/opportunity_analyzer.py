"""
Opportunity Analyzer

Analyzes scanner candidates using AI to determine high-quality trading opportunities.
Integrates MarketScanner findings with StockResearcher and DualAIService.
"""

import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from services.market_scanner import get_market_scanner
from services.stock_researcher import get_researcher
from services.ai_models import get_ai_service, Recommendation

logger = logging.getLogger(__name__)


class OpportunityAnalyzer:
    """
    Analyzes scanner candidates with AI to find high-quality opportunities.
    
    Flow:
    1. Scanner finds candidates (technical, earnings, seasonal)
    2. Researcher gathers comprehensive data for each
    3. AI models analyze and make recommendations
    4. Filter by confidence threshold
    5. Return scored opportunities ready for trading
    """
    
    def __init__(self, db: Session, confidence_threshold: float = 0.75):
        """
        Initialize analyzer
        
        Args:
            db: Database session
            confidence_threshold: Minimum AI confidence (0.0-1.0) to recommend
        """
        self.db = db
        self.scanner = get_market_scanner(db)
        self.researcher = get_researcher()
        self.ai_service = get_ai_service()
        self.confidence_threshold = confidence_threshold
        
        logger.info(f"OpportunityAnalyzer initialized (threshold={confidence_threshold})")
    
    async def find_opportunities(
        self,
        strategies: Optional[List[str]] = None,
        max_opportunities: int = 5
    ) -> List[Dict]:
        """
        Find and analyze trading opportunities
        
        Args:
            strategies: Which strategies to run ['earnings', 'breakout', 'seasonal']
                       If None, runs all strategies
            max_opportunities: Maximum number of opportunities to return
            
        Returns:
            List of opportunity dicts sorted by confidence (highest first):
            {
                'symbol': 'AAPL',
                'scanner_strategy': 'technical_breakout',
                'scanner_score': 75,
                'scanner_reason': 'Breaking above 52-week high...',
                'ai_recommendation': 'BUY',
                'ai_confidence': 0.85,
                'ai_reasoning': 'Strong fundamentals with technical breakout...',
                'entry_price': 257.50,
                'stop_loss': 245.00,
                'target_price': 285.00,
                'current_price': 257.06,
                'volume': 50000000,
                'final_score': 85  # Combined scanner + AI score
            }
        """
        logger.info(f"🔍 Finding opportunities (strategies={strategies}, max={max_opportunities})")
        
        # Step 1: Get scanner candidates
        candidates = await self._get_scanner_candidates(strategies)
        
        if not candidates:
            logger.info("No scanner candidates found")
            return []
        
        logger.info(f"📊 Scanner found {len(candidates)} candidates")
        
        # Step 2: Analyze each candidate with AI
        opportunities = []
        for candidate in candidates:
            try:
                opportunity = await self._analyze_candidate(candidate)
                
                # Filter by confidence threshold
                if opportunity and opportunity['ai_confidence'] >= self.confidence_threshold:
                    opportunities.append(opportunity)
                    logger.info(
                        f"✅ {opportunity['symbol']}: "
                        f"{opportunity['ai_recommendation']} "
                        f"({opportunity['ai_confidence']:.0%} confidence)"
                    )
                else:
                    if opportunity:
                        logger.debug(
                            f"⏭️ {candidate['symbol']}: Below threshold "
                            f"({opportunity['ai_confidence']:.0%} < {self.confidence_threshold:.0%})"
                        )
            
            except Exception as e:
                logger.error(f"❌ Error analyzing {candidate['symbol']}: {e}")
                continue
        
        # Step 3: Sort by final score (highest first) and limit
        opportunities.sort(key=lambda x: x['final_score'], reverse=True)
        opportunities = opportunities[:max_opportunities]
        
        logger.info(f"🎯 Found {len(opportunities)} high-quality opportunities")
        return opportunities
    
    async def _get_scanner_candidates(self, strategies: Optional[List[str]]) -> List[Dict]:
        """Get candidates from market scanner"""
        if not strategies:
            # Run all strategies
            return self.scanner.scan_all_strategies()
        
        # Run specific strategies
        candidates = []
        
        if 'earnings' in strategies:
            candidates.extend(self.scanner._scan_earnings_plays())
        
        if 'breakout' in strategies:
            candidates.extend(self.scanner._scan_technical_breakouts())
        
        if 'seasonal' in strategies:
            candidates.extend(self.scanner._scan_seasonality())
        
        # Deduplicate
        return self.scanner._deduplicate_candidates(candidates)
    
    async def _analyze_candidate(self, candidate: Dict) -> Optional[Dict]:
        """
        Analyze a single scanner candidate with AI
        
        Args:
            candidate: Scanner result with symbol, strategy, score, reason
            
        Returns:
            Full opportunity dict with AI analysis, or None if analysis fails
        """
        symbol = candidate['symbol']
        
        logger.debug(f"🔬 Analyzing {symbol} ({candidate['strategy']})...")
        
        # Step 1: Gather comprehensive research data
        research = await self.researcher.research_stock(symbol)
        
        if not research:
            logger.warning(f"⚠️ No research data for {symbol}")
            return None
        
        # Step 2: Get AI recommendation
        ai_response = await self.ai_service.get_stock_recommendation(
            symbol=symbol,
            fundamental_data=research.get('fundamental', {}),
            technical_data=research.get('technical', {}),
            news_data=research.get('news', [])
        )
        
        # Step 3: Combine scanner + AI analysis
        opportunity = {
            # Scanner data
            'symbol': symbol,
            'scanner_strategy': candidate['strategy'],
            'scanner_score': candidate['score'],
            'scanner_reason': candidate['reason'],
            
            # AI analysis
            'ai_recommendation': ai_response.consensus.value,
            'ai_confidence': ai_response.confidence,
            'ai_reasoning': self._format_ai_reasoning(ai_response),
            'ai_models_agree': ai_response.agreement,
            
            # Trading parameters (from AI)
            'entry_price': self._get_entry_price(ai_response),
            'stop_loss': self._get_stop_loss(ai_response),
            'target_price': self._get_target_price(ai_response),
            
            # Market data
            'current_price': research.get('technical', {}).get('current_price'),
            'volume': research.get('technical', {}).get('volume_current'),
            
            # Combined score (70% AI confidence, 30% scanner score)
            'final_score': self._calculate_final_score(candidate['score'], ai_response.confidence),
            
            # Metadata
            'analyzed_at': research.get('timestamp')
        }
        
        return opportunity
    
    def _format_ai_reasoning(self, ai_response) -> str:
        """Format AI reasoning from both models"""
        if ai_response.agreement:
            # Both models agree - use first model's reasoning
            return ai_response.models[0].reasoning
        else:
            # Models disagree - show both perspectives
            reasonings = []
            for model in ai_response.models:
                reasonings.append(f"{model.model_name}: {model.reasoning}")
            return " | ".join(reasonings)
    
    def _get_entry_price(self, ai_response) -> Optional[float]:
        """Extract entry price from AI response"""
        # Use first model's entry price if available
        for model in ai_response.models:
            if model.entry_price:
                return model.entry_price
        return None
    
    def _get_stop_loss(self, ai_response) -> Optional[float]:
        """Extract stop loss from AI response"""
        for model in ai_response.models:
            if model.stop_loss:
                return model.stop_loss
        return None
    
    def _get_target_price(self, ai_response) -> Optional[float]:
        """Extract target price from AI response"""
        for model in ai_response.models:
            if model.target_price:
                return model.target_price
        return None
    
    def _calculate_final_score(self, scanner_score: int, ai_confidence: float) -> int:
        """
        Calculate final opportunity score
        
        Weights:
        - 70% AI confidence (0-100)
        - 30% Scanner score (0-100)
        
        Returns:
            Score from 0-100
        """
        ai_score = ai_confidence * 100  # Convert 0.0-1.0 to 0-100
        final = (ai_score * 0.7) + (scanner_score * 0.3)
        return int(round(final))


# Singleton instance
_analyzer: Optional[OpportunityAnalyzer] = None


def get_opportunity_analyzer(
    db: Session,
    confidence_threshold: float = 0.75
) -> OpportunityAnalyzer:
    """
    Get or create OpportunityAnalyzer singleton
    
    Args:
        db: Database session
        confidence_threshold: Minimum AI confidence to recommend (0.0-1.0)
    
    Returns:
        OpportunityAnalyzer instance
    """
    global _analyzer
    if _analyzer is None:
        _analyzer = OpportunityAnalyzer(db, confidence_threshold)
        logger.info("✅ Opportunity Analyzer initialized")
    return _analyzer
