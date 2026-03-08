"""
Automated Opportunity Scanner Job

Runs periodically (every 15 minutes) to:
1. Scan market for opportunities
2. Analyze with AI
3. Create proposals for high-confidence opportunities
4. Log results

Designed to run as a background job via cron or Railway scheduler.
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from typing import List, Dict

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from services.opportunity_analyzer import get_opportunity_analyzer
from services.alert_service import get_alert_service
from app.models import TradeProposal
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OpportunityScanJob:
    """
    Background job that scans for opportunities and creates trade proposals
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.75,
        max_opportunities: int = 5,
        auto_create_proposals: bool = True
    ):
        """
        Initialize scan job
        
        Args:
            confidence_threshold: Minimum AI confidence (0.0-1.0)
            max_opportunities: Max opportunities to find per scan
            auto_create_proposals: If True, auto-create proposals in DB
        """
        self.confidence_threshold = confidence_threshold
        self.max_opportunities = max_opportunities
        self.auto_create_proposals = auto_create_proposals
        
        self.scan_count = 0
        self.total_opportunities_found = 0
        self.total_proposals_created = 0
    
    async def run(self) -> Dict:
        """
        Run opportunity scan
        
        Returns:
            Dict with scan results:
            {
                'scan_id': 123,
                'timestamp': '2026-02-15T10:30:00Z',
                'opportunities_found': 3,
                'proposals_created': 2,
                'duration_seconds': 45.3,
                'status': 'success'
            }
        """
        start_time = datetime.now()
        self.scan_count += 1
        scan_id = self.scan_count
        
        logger.info(f"🔍 Starting opportunity scan #{scan_id}")
        logger.info(f"   Threshold: {self.confidence_threshold:.0%}, Max: {self.max_opportunities}")
        
        db = SessionLocal()
        
        try:
            # Step 1: Find opportunities
            analyzer = get_opportunity_analyzer(db, self.confidence_threshold)
            opportunities = await analyzer.find_opportunities(
                strategies=None,  # All strategies
                max_opportunities=self.max_opportunities
            )
            
            logger.info(f"📊 Found {len(opportunities)} opportunities")
            self.total_opportunities_found += len(opportunities)
            
            # Step 2: Create proposals for high-confidence opportunities
            proposals_created = 0
            if self.auto_create_proposals and opportunities:
                proposals_created = await self._create_proposals(db, opportunities)
                self.total_proposals_created += proposals_created
                logger.info(f"✅ Created {proposals_created} trade proposals")
                
                # Step 2.5: Send alert if opportunities found
                if opportunities:
                    alert_service = get_alert_service()
                    top_opp = opportunities[0]  # Highest confidence
                    alert_service.send_opportunity_alert(
                        symbol=top_opp['symbol'],
                        strategy=top_opp['strategy'],
                        confidence=top_opp['confidence'],
                        reasoning=top_opp.get('reasoning', 'No reasoning provided'),
                        count=len(opportunities)
                    )
            
            # Step 3: Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Step 4: Build result
            result = {
                'scan_id': scan_id,
                'timestamp': start_time.isoformat(),
                'opportunities_found': len(opportunities),
                'proposals_created': proposals_created,
                'duration_seconds': round(duration, 1),
                'status': 'success',
                'opportunities': opportunities
            }
            
            logger.info(f"✅ Scan #{scan_id} complete in {duration:.1f}s")
            return result
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Scan #{scan_id} failed: {e}")
            
            return {
                'scan_id': scan_id,
                'timestamp': start_time.isoformat(),
                'opportunities_found': 0,
                'proposals_created': 0,
                'duration_seconds': round(duration, 1),
                'status': 'error',
                'error': str(e)
            }
        
        finally:
            db.close()
    
    async def _create_proposals(self, db, opportunities: List[Dict]) -> int:
        """
        Create trade proposals for opportunities
        
        Args:
            db: Database session
            opportunities: List of opportunity dicts
            
        Returns:
            Number of proposals created
        """
        created = 0
        
        for opp in opportunities:
            try:
                # Check if proposal already exists for this symbol
                existing = db.query(TradeProposal).filter(
                    TradeProposal.symbol == opp['symbol'],
                    TradeProposal.status == 'pending'
                ).first()
                
                if existing:
                    logger.debug(f"⏭️ {opp['symbol']}: Proposal already exists")
                    continue
                
                # Create new proposal
                proposal = TradeProposal(
                    symbol=opp['symbol'],
                    action='BUY',  # Opportunities are buy recommendations
                    quantity=self._calculate_quantity(opp),
                    entry_price=opp.get('entry_price'),
                    stop_loss=opp.get('stop_loss'),
                    target_price=opp.get('target_price'),
                    ai_confidence=opp['ai_confidence'],
                    ai_reasoning=opp['ai_reasoning'],
                    scanner_strategy=opp['scanner_strategy'],
                    final_score=opp['final_score'],
                    status='pending',
                    source='autonomous_scanner'
                )
                
                db.add(proposal)
                db.commit()
                
                created += 1
                logger.info(
                    f"📝 Created proposal: {opp['symbol']} @ ${opp.get('entry_price')} "
                    f"(score: {opp['final_score']})"
                )
            
            except SQLAlchemyError as e:
                logger.error(f"❌ Error creating proposal for {opp['symbol']}: {e}")
                db.rollback()
                continue
        
        return created
    
    def _calculate_quantity(self, opportunity: Dict) -> int:
        """
        Calculate position size based on opportunity
        
        For now, returns fixed quantity.
        TODO: Implement Kelly Criterion or risk-based position sizing
        
        Args:
            opportunity: Opportunity dict with prices and confidence
            
        Returns:
            Number of shares to buy
        """
        # Simple fixed position size for now
        # In future: calculate based on:
        # - Account size
        # - Risk tolerance (stop loss distance)
        # - AI confidence
        # - Portfolio diversification
        return 10  # Fixed 10 shares per position
    
    def get_stats(self) -> Dict:
        """Get job statistics"""
        return {
            'total_scans': self.scan_count,
            'total_opportunities_found': self.total_opportunities_found,
            'total_proposals_created': self.total_proposals_created,
            'avg_opportunities_per_scan': (
                self.total_opportunities_found / self.scan_count
                if self.scan_count > 0 else 0
            )
        }


async def main():
    """
    Main entry point for scheduled job
    
    Usage:
        python3 jobs/scan_opportunities.py
    
    For cron:
        */15 * * * * cd /path/to/backend && python3 jobs/scan_opportunities.py >> logs/scanner.log 2>&1
    """
    logger.info("=" * 60)
    logger.info("AUTOMATED OPPORTUNITY SCANNER")
    logger.info("=" * 60)
    
    # Create and run job
    job = OpportunityScanJob(
        confidence_threshold=0.75,  # 75% AI confidence minimum
        max_opportunities=5,         # Find up to 5 opportunities
        auto_create_proposals=True   # Auto-create proposals in DB
    )
    
    result = await job.run()
    
    # Log summary
    logger.info("")
    logger.info("SCAN SUMMARY:")
    logger.info(f"  Status: {result['status']}")
    logger.info(f"  Opportunities Found: {result['opportunities_found']}")
    logger.info(f"  Proposals Created: {result['proposals_created']}")
    logger.info(f"  Duration: {result['duration_seconds']}s")
    
    if result['status'] == 'success' and result['opportunities_found'] > 0:
        logger.info("")
        logger.info("TOP OPPORTUNITIES:")
        for i, opp in enumerate(result['opportunities'][:3], 1):
            logger.info(
                f"  {i}. {opp['symbol']}: {opp['ai_recommendation']} "
                f"({opp['ai_confidence']:.0%} confidence, score: {opp['final_score']})"
            )
    
    logger.info("=" * 60)
    
    return result


if __name__ == "__main__":
    # Run the job
    asyncio.run(main())
