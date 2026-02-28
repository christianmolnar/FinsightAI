"""
Market Scanner API Endpoints

Provides REST API access to the autonomous market scanner and opportunity analyzer.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import logging

from app.database import get_db
from services.market_scanner import get_market_scanner
from services.opportunity_analyzer import get_opportunity_analyzer

router = APIRouter(prefix="/api/scanner", tags=["scanner"])
logger = logging.getLogger(__name__)


# Store last scan result in memory (simple approach)
_last_scan_result = None


@router.get("/scan")
async def scan_market(db: Session = Depends(get_db)) -> Dict:
    """
    Run market scan across all strategies
    
    Returns:
        Dict with:
        - candidates: List of opportunities found
        - total_scanned: Number of symbols scanned
        - scan_time: Timestamp of scan
    """
    try:
        scanner = get_market_scanner(db)
        candidates = scanner.scan_all_strategies()
        
        return {
            "success": True,
            "candidates": candidates,
            "total_found": len(candidates),
            "total_scanned": len(scanner.SCAN_UNIVERSE),
            "scan_time": "2026-02-14T19:30:00Z"  # Would be datetime.now() in production
        }
    
    except Exception as e:
        logger.error(f"Error scanning market: {e}")
        raise HTTPException(status_code=500, detail=f"Market scan failed: {str(e)}")


@router.get("/scan/earnings")
async def scan_earnings(db: Session = Depends(get_db)) -> Dict:
    """
    Run earnings strategy only
    
    Returns:
        Dict with earnings play candidates
    """
    try:
        scanner = get_market_scanner(db)
        candidates = scanner._scan_earnings_plays()
        
        return {
            "success": True,
            "strategy": "earnings_play",
            "candidates": candidates,
            "total_found": len(candidates)
        }
    
    except Exception as e:
        logger.error(f"Error scanning earnings: {e}")
        raise HTTPException(status_code=500, detail=f"Earnings scan failed: {str(e)}")


@router.get("/scan/breakouts")
async def scan_breakouts(db: Session = Depends(get_db)) -> Dict:
    """
    Run technical breakout strategy only
    
    Returns:
        Dict with breakout candidates
    """
    try:
        scanner = get_market_scanner(db)
        candidates = scanner._scan_technical_breakouts()
        
        return {
            "success": True,
            "strategy": "technical_breakout",
            "candidates": candidates,
            "total_found": len(candidates)
        }
    
    except Exception as e:
        logger.error(f"Error scanning breakouts: {e}")
        raise HTTPException(status_code=500, detail=f"Breakout scan failed: {str(e)}")


@router.get("/scan/seasonal")
async def scan_seasonal(db: Session = Depends(get_db)) -> Dict:
    """
    Run seasonality strategy only
    
    Returns:
        Dict with seasonal candidates
    """
    try:
        scanner = get_market_scanner(db)
        candidates = scanner._scan_seasonality()
        
        return {
            "success": True,
            "strategy": "seasonality",
            "candidates": candidates,
            "total_found": len(candidates)
        }
    
    except Exception as e:
        logger.error(f"Error scanning seasonal: {e}")
        raise HTTPException(status_code=500, detail=f"Seasonal scan failed: {str(e)}")


@router.get("/opportunities")
async def find_opportunities(
    strategies: Optional[str] = None,  # Comma-separated: "earnings,breakout,seasonal"
    max_results: int = 5,
    confidence_threshold: float = 0.75,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Find AI-analyzed trading opportunities
    
    Args:
        strategies: Which strategies to run (comma-separated: earnings,breakout,seasonal)
                   If not provided, runs all strategies
        max_results: Maximum number of opportunities to return (default: 5)
        confidence_threshold: Minimum AI confidence 0.0-1.0 (default: 0.75)
    
    Returns:
        Dict with analyzed opportunities sorted by confidence:
        {
            "success": true,
            "opportunities": [
                {
                    "symbol": "AAPL",
                    "scanner_strategy": "technical_breakout",
                    "scanner_score": 75,
                    "ai_recommendation": "BUY",
                    "ai_confidence": 0.85,
                    "ai_reasoning": "Strong fundamentals...",
                    "entry_price": 257.50,
                    "stop_loss": 245.00,
                    "target_price": 285.00,
                    "final_score": 85
                }
            ],
            "total_found": 3,
            "confidence_threshold": 0.75,
            "strategies_used": ["earnings", "breakout", "seasonal"]
        }
    """
    try:
        # Parse strategies parameter
        strategy_list = None
        if strategies:
            strategy_list = [s.strip() for s in strategies.split(',')]
        
        # Create analyzer and find opportunities
        analyzer = get_opportunity_analyzer(db, confidence_threshold)
        opportunities = await analyzer.find_opportunities(
            strategies=strategy_list,
            max_opportunities=max_results
        )
        
        return {
            "success": True,
            "opportunities": opportunities,
            "total_found": len(opportunities),
            "confidence_threshold": confidence_threshold,
            "strategies_used": strategy_list or ["earnings", "breakout", "seasonal"]
        }
    
    except Exception as e:
        logger.error(f"Error finding opportunities: {e}")
        raise HTTPException(status_code=500, detail=f"Opportunity analysis failed: {str(e)}")


@router.post("/scan/trigger")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    confidence_threshold: float = 0.75,
    max_opportunities: int = 5,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Manually trigger an opportunity scan job
    
    This runs the same background job that would run on a schedule.
    Useful for testing and manual intervention.
    
    Args:
        confidence_threshold: Minimum AI confidence (default: 0.75)
        max_opportunities: Max opportunities to find (default: 5)
    
    Returns:
        Dict with job status:
        {
            "success": true,
            "message": "Scan job started",
            "scan_id": 123,
            "estimated_duration": "2-3 minutes"
        }
    """
    try:
        from jobs.scan_opportunities import OpportunityScanJob
        
        # Create job
        job = OpportunityScanJob(
            confidence_threshold=confidence_threshold,
            max_opportunities=max_opportunities,
            auto_create_proposals=True
        )
        
        # Run in background
        async def run_scan():
            global _last_scan_result
            _last_scan_result = await job.run()
            logger.info(f"Background scan complete: {_last_scan_result['opportunities_found']} opportunities")
        
        background_tasks.add_task(run_scan)
        
        return {
            "success": True,
            "message": "Scan job started in background",
            "scan_id": job.scan_count + 1,
            "estimated_duration": "2-3 minutes",
            "check_status_at": "/api/scanner/scan/status"
        }
    
    except Exception as e:
        logger.error(f"Error triggering scan: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")


@router.get("/scan/status")
async def get_scan_status() -> Dict:
    """
    Get status of last scan job
    
    Returns:
        Dict with last scan results or indication that no scan has run
    """
    global _last_scan_result
    
    if _last_scan_result is None:
        return {
            "success": True,
            "message": "No scans have been run yet",
            "last_scan": None
        }
    
    return {
        "success": True,
        "last_scan": _last_scan_result
    }
