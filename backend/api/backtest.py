"""
Backtesting API

Endpoints for running backtests and viewing results
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.database import get_db
from services.backtester import get_backtester, BacktestMetrics
from config.backtest_config import enable_debug_mode, disable_debug_mode, BACKTEST_DEBUG


router = APIRouter(prefix="/api/backtest", tags=["backtest"])


# Request/Response Models
class BacktestRequest(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    strategies: Optional[List[str]] = None  # None = all strategies
    confidence_threshold: float = 0.75
    use_ai: bool = True
    initial_capital: float = 10000.0
    position_size: float = 1000.0  # Fixed dollar amount per trade
    max_hold_days: int = 14
    enable_compounding: bool = True  # DEFAULT: Position size grows with portfolio (RECOMMENDED)


class BacktestResponse(BaseModel):
    success: bool
    backtest_id: Optional[str] = None
    metrics: Optional[dict] = None
    trades: Optional[List[dict]] = None
    config: Optional[dict] = None
    error: Optional[str] = None


# Store backtest results in memory (in production, use database)
_backtest_results = {}
_backtest_status = {}


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Run a backtest on historical data
    
    Simulates scanner + AI analyzer over specified date range
    to validate strategy effectiveness
    """
    try:
        # Validate dates
        try:
            start_date = datetime.strptime(request.start_date, '%Y-%m-%d')
            end_date = datetime.strptime(request.end_date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="start_date must be before end_date")
        
        if end_date > datetime.now():
            raise HTTPException(status_code=400, detail="end_date cannot be in the future")
        
        # Validate confidence threshold
        if not 0.0 <= request.confidence_threshold <= 1.0:
            raise HTTPException(status_code=400, detail="confidence_threshold must be between 0.0 and 1.0")
        
        # Generate backtest ID
        backtest_id = f"backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Mark as running
        _backtest_status[backtest_id] = {
            'status': 'running',
            'start_time': datetime.now(),
            'progress': 0
        }
        
        # Run backtest asynchronously
        background_tasks.add_task(
            _run_backtest_task,
            backtest_id=backtest_id,
            db=db,
            request=request,
            start_date=start_date,
            end_date=end_date
        )
        
        return BacktestResponse(
            success=True,
            backtest_id=backtest_id,
            config={
                'start_date': request.start_date,
                'end_date': request.end_date,
                'strategies': request.strategies or ['all'],
                'confidence_threshold': request.confidence_threshold,
                'use_ai': request.use_ai,
                'initial_capital': request.initial_capital,
                'position_size': request.position_size,
                'max_hold_days': request.max_hold_days
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return BacktestResponse(
            success=False,
            error=f"Failed to start backtest: {str(e)}"
        )


async def _run_backtest_task(
    backtest_id: str,
    db: Session,
    request: BacktestRequest,
    start_date: datetime,
    end_date: datetime
):
    """Background task to run backtest"""
    try:
        # Create backtester
        # Handle position sizing mode:
        # - If compounding enabled: Convert dollar amount to percentage
        # - If compounding disabled: Keep as fixed percentage of INITIAL capital
        if request.enable_compounding:
            # Compounding mode: Position size grows with portfolio
            position_size_pct = request.position_size / request.initial_capital
        else:
            # Fixed mode: Position size stays constant relative to INITIAL capital
            # This ensures $3000 position size stays $3000 regardless of portfolio growth
            position_size_pct = request.position_size / request.initial_capital
        
        backtester = get_backtester(
            db=db,
            initial_capital=request.initial_capital,
            position_size_pct=position_size_pct,  # Now using percentage
            max_hold_days=request.max_hold_days,
            enable_compounding=request.enable_compounding  # Pass compounding flag
        )
        
        # Run backtest
        metrics = await backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            strategies=request.strategies,
            confidence_threshold=request.confidence_threshold,
            use_ai=request.use_ai
        )
        
        # Store results
        _backtest_results[backtest_id] = {
            'metrics': metrics.to_dict(),
            'trades': [trade.to_dict() for trade in backtester.trades],
            'config': {
                'start_date': request.start_date,
                'end_date': request.end_date,
                'strategies': request.strategies or ['all'],
                'confidence_threshold': request.confidence_threshold,
                'use_ai': request.use_ai,
                'initial_capital': request.initial_capital,
                'position_size': request.position_size,
                'max_hold_days': request.max_hold_days
            },
            'completed_at': datetime.now().isoformat()
        }
        
        # Update status
        _backtest_status[backtest_id] = {
            'status': 'complete',
            'completed_at': datetime.now()
        }
        
    except Exception as e:
        _backtest_status[backtest_id] = {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now()
        }


@router.get("/status/{backtest_id}")
async def get_backtest_status(backtest_id: str):
    """Get status of a backtest run"""
    if backtest_id not in _backtest_status:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    status = _backtest_status[backtest_id]
    
    return {
        'success': True,
        'backtest_id': backtest_id,
        'status': status['status'],
        'start_time': status.get('start_time').isoformat() if status.get('start_time') else None,
        'completed_at': status.get('completed_at').isoformat() if status.get('completed_at') else None,
        'error': status.get('error')
    }


@router.get("/results/{backtest_id}", response_model=BacktestResponse)
async def get_backtest_results(backtest_id: str):
    """Get results of a completed backtest"""
    if backtest_id not in _backtest_results:
        # Check if it's still running
        if backtest_id in _backtest_status:
            status = _backtest_status[backtest_id]
            if status['status'] == 'running':
                return BacktestResponse(
                    success=False,
                    error="Backtest is still running. Check /status endpoint."
                )
            elif status['status'] == 'failed':
                return BacktestResponse(
                    success=False,
                    error=f"Backtest failed: {status.get('error', 'Unknown error')}"
                )
        
        raise HTTPException(status_code=404, detail="Backtest results not found")
    
    results = _backtest_results[backtest_id]
    
    return BacktestResponse(
        success=True,
        backtest_id=backtest_id,
        metrics=results['metrics'],
        trades=results['trades'],
        config=results['config']
    )


@router.get("/results/{backtest_id}/trades")
async def get_backtest_trades(
    backtest_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Get trades from a backtest (paginated)"""
    if backtest_id not in _backtest_results:
        raise HTTPException(status_code=404, detail="Backtest results not found")
    
    trades = _backtest_results[backtest_id]['trades']
    
    # Paginate
    paginated_trades = trades[offset:offset + limit]
    
    return {
        'success': True,
        'backtest_id': backtest_id,
        'total_trades': len(trades),
        'offset': offset,
        'limit': limit,
        'trades': paginated_trades
    }


@router.get("/list")
async def list_backtests():
    """List all backtest runs"""
    backtests = []
    
    for backtest_id in _backtest_results.keys():
        result = _backtest_results[backtest_id]
        status = _backtest_status.get(backtest_id, {})
        
        backtests.append({
            'backtest_id': backtest_id,
            'status': status.get('status', 'unknown'),
            'config': result['config'],
            'metrics_summary': {
                'total_trades': result['metrics']['summary']['total_trades'],
                'win_rate': result['metrics']['summary']['win_rate'],
                'total_return_pct': result['metrics']['returns']['total_return_pct']
            },
            'completed_at': result['completed_at']
        })
    
    return {
        'success': True,
        'total_backtests': len(backtests),
        'backtests': sorted(backtests, key=lambda x: x['completed_at'], reverse=True)
    }


@router.post("/quick/{period}")
async def run_quick_backtest(
    period: str,  # '30d', '90d', '1y'
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    confidence_threshold: float = 0.75,
    initial_capital: float = 10000.0,  # Accept from frontend
    position_size: float = 1000.0,     # Accept from frontend
    enable_compounding: bool = True    # Accept from frontend
):
    """
    Run a quick backtest with preset time periods
    
    Options:
    - 30d: Last 30 days
    - 90d: Last 90 days
    - 1y: Last year
    
    Now accepts initial_capital and position_size from frontend form!
    """
    # Calculate dates based on period
    end_date = datetime.now()
    
    if period == '30d':
        start_date = end_date - timedelta(days=30)
    elif period == '90d':
        start_date = end_date - timedelta(days=90)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use '30d', '90d', or '1y'")
    
    # Create request with user's parameters
    request = BacktestRequest(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        strategies=None,  # All strategies
        confidence_threshold=confidence_threshold,
        use_ai=True,
        initial_capital=initial_capital,  # Use frontend value
        position_size=position_size,      # Use frontend value
        max_hold_days=14,
        enable_compounding=enable_compounding  # Use frontend value
    )
    
    # Run backtest
    return await run_backtest(request, background_tasks, db)


@router.post("/debug/enable")
async def enable_debug():
    """Enable debug mode for backtesting"""
    enable_debug_mode()
    return {"success": True, "debug_mode": True, "message": "Debug logging enabled"}


@router.post("/debug/disable")
async def disable_debug():
    """Disable debug mode for backtesting"""
    disable_debug_mode()
    return {"success": True, "debug_mode": False, "message": "Debug logging disabled"}


@router.get("/debug/status")
async def get_debug_status():
    """Get current debug mode status"""
    from config.backtest_config import BACKTEST_DEBUG
    return {"success": True, "debug_mode": BACKTEST_DEBUG}
