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
from services.market_scanner import get_market_scanner
from app.models.trade_proposal import TradeProposal
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
        ai_score_threshold: int = 60,
        max_opportunities: int = 5,
        auto_create_proposals: bool = True
    ):
        """
        Initialize scan job

        Args:
            ai_score_threshold: Minimum AI score 0–100 for a signal to pass
            max_opportunities: Max signals to act on per scan
            auto_create_proposals: If True, auto-create proposals in DB
        """
        self.ai_score_threshold = ai_score_threshold
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
        logger.info(f"   AI threshold: {self.ai_score_threshold}/100, Max: {self.max_opportunities}")
        
        db = SessionLocal()
        
        try:
            # Step 1: Find opportunities via unified signal engine + AI gate
            scanner = get_market_scanner(db)
            opportunities = scanner.scan_all_strategies(
                ai_gated=True,
                ai_score_threshold=self.ai_score_threshold,
            )
            # Sort by score descending, cap at max
            opportunities = sorted(opportunities, key=lambda x: x.get('score', 0), reverse=True)
            opportunities = opportunities[:self.max_opportunities]
            
            logger.info(f"📊 Found {len(opportunities)} opportunities")
            self.total_opportunities_found += len(opportunities)
            
            # Step 2: Create proposals for high-confidence opportunities
            proposals_created = 0
            if self.auto_create_proposals and opportunities:
                proposals_created = await self._create_proposals(db, opportunities)
                self.total_proposals_created += proposals_created
                logger.info(f"✅ Created {proposals_created} trade proposals")
            
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
        Persist AI-approved signals as TradeProposal rows.
        Skips symbols that already have a pending proposal.
        """
        created = 0
        for opp in opportunities:
            try:
                existing = db.query(TradeProposal).filter(
                    TradeProposal.symbol == opp['symbol'],
                    TradeProposal.status == 'pending'
                ).first()
                if existing:
                    logger.debug(f"⏭️ {opp['symbol']}: pending proposal already exists")
                    continue

                exit_params = opp.get('exit_params', {})
                proposal = TradeProposal(
                    symbol=opp['symbol'],
                    strategy=opp.get('strategy', 'unknown'),
                    score=opp.get('score', 0),
                    ai_score=opp.get('ai_score'),
                    ai_reasoning=opp.get('ai_reasoning'),
                    entry_price=opp.get('current_price') or opp.get('price'),
                    profit_target_pct=exit_params.get('profit_target'),
                    stop_loss_pct=exit_params.get('stop_loss'),
                    max_portfolio_weight=exit_params.get('max_portfolio_weight'),
                    signal_metadata=opp.get('signal_metadata'),
                    params_used=opp.get('params_used'),
                    status='pending',
                    source='autonomous_scanner',
                )
                db.add(proposal)
                db.commit()
                created += 1
                logger.info(
                    f"📝 Proposal created: {opp['symbol']} | {opp.get('strategy')} "
                    f"| score={opp.get('score')} ai={opp.get('ai_score')}"
                )
            except SQLAlchemyError as e:
                logger.error(f"❌ DB error creating proposal for {opp['symbol']}: {e}")
                db.rollback()
        return created
    
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
        ai_score_threshold=60,       # 60/100 AI score minimum
        max_opportunities=5,
        auto_create_proposals=True
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
                f"  {i}. {opp['symbol']}: {opp.get('strategy')} "
                f"(score: {opp.get('score')}, ai: {opp.get('ai_score')})"
            )
    
    logger.info("=" * 60)
    
    return result


if __name__ == "__main__":
    # Run the job
    asyncio.run(main())
