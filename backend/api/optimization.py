"""
API endpoints for optimization run management.

Provides endpoints to:
- List saved optimization runs
- Get optimization run details
- Apply optimization to Strategy Config
- Compare optimization runs
- Mark runs as favorites
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db, StrategyConfig
from models.optimization_run import OptimizationRun, StrategyConfigSnapshot
from auth import get_current_user

router = APIRouter(prefix="/api/optimization", tags=["optimization"])


# Request/Response Models
class OptimizationRunSummary(BaseModel):
    id: str
    name: Optional[str]
    created_at: str
    start_date: str
    end_date: str
    initial_return_pct: float
    best_return_pct: float
    total_improvement: float
    total_iterations: int
    converged: bool
    is_applied: bool
    is_favorite: bool
    
    class Config:
        from_attributes = True


class ApplyOptimizationRequest(BaseModel):
    optimization_run_id: str
    apply_to_strategies: Optional[List[str]] = None  # Which strategies to update


@router.get("/runs", response_model=List[OptimizationRunSummary])
async def list_optimization_runs(
    user_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all optimization runs for the user.
    
    Returns summaries sorted by created_at descending (newest first).
    """
    query = db.query(OptimizationRun)
    
    if user_id:
        query = query.filter(OptimizationRun.user_id == user_id)
    
    runs = query.order_by(OptimizationRun.created_at.desc()).limit(limit).all()
    
    return [
        OptimizationRunSummary(
            id=run.id,
            name=run.name or f"Optimization {run.created_at.strftime('%Y-%m-%d %H:%M')}",
            created_at=run.created_at.isoformat(),
            start_date=run.start_date,
            end_date=run.end_date,
            initial_return_pct=run.initial_return_pct,
            best_return_pct=run.best_return_pct,
            total_improvement=run.total_improvement,
            total_iterations=run.total_iterations,
            converged=run.converged,
            is_applied=run.is_applied,
            is_favorite=run.is_favorite
        )
        for run in runs
    ]


@router.get("/runs/{run_id}")
async def get_optimization_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get full details of an optimization run including all iterations."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    
    return {
        'success': True,
        'run': run.to_dict()
    }


@router.post("/apply")
async def apply_optimization_to_config(
    request: ApplyOptimizationRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Apply an optimization run's best configuration to Strategy Config.
    
    Creates a StrategyConfigSnapshot for provenance tracking.
    Updates StrategyConfig with optimized parameters.
    """
    # Get optimization run
    run = db.query(OptimizationRun).filter(
        OptimizationRun.id == request.optimization_run_id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    
    # Get user's current strategy config
    user_id = current_user.get('sub') or current_user.get('user_id')
    
    strategy_config = db.query(StrategyConfig).filter(
        StrategyConfig.user_id == user_id
    ).first()
    
    if not strategy_config:
        raise HTTPException(status_code=404, detail="Strategy config not found")
    
    # Build changes list for provenance
    changes = []
    best_config = run.best_config
    
    # Map optimization params to strategy config
    param_mappings = {
        'confidence_threshold': 'confidence_threshold',
        'position_size': 'position_size_pct',
        'max_hold_days': 'max_hold_days',
        'enable_compounding': 'enable_compounding'
    }
    
    current_config = strategy_config.config or {}
    
    for opt_param, config_param in param_mappings.items():
        if opt_param in best_config:
            old_value = current_config.get(config_param)
            new_value = best_config[opt_param]
            
            if old_value != new_value:
                changes.append({
                    'parameter': config_param,
                    'old_value': old_value,
                    'new_value': new_value,
                    'reason': f'AI Optimization improved return by {run.total_improvement:.2f}%'
                })
                
                current_config[config_param] = new_value
    
    # Update strategy config
    strategy_config.config = current_config
    strategy_config.updated_at = datetime.utcnow()
    
    # Create snapshot for provenance
    snapshot = StrategyConfigSnapshot(
        user_id=user_id,
        source='optimization',
        source_id=run.id,
        config=current_config,
        changes=changes,
        is_active=True
    )
    
    # Mark old snapshots as inactive
    db.query(StrategyConfigSnapshot).filter(
        StrategyConfigSnapshot.user_id == user_id,
        StrategyConfigSnapshot.is_active == True
    ).update({'is_active': False})
    
    # Mark optimization as applied
    run.is_applied = True
    run.applied_at = datetime.utcnow()
    
    db.add(snapshot)
    db.commit()
    db.refresh(strategy_config)
    db.refresh(snapshot)
    
    return {
        'success': True,
        'message': f'Applied {len(changes)} optimized parameters to Strategy Config',
        'changes': changes,
        'snapshot_id': snapshot.id
    }


@router.post("/runs/{run_id}/favorite")
async def toggle_favorite(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Toggle favorite status for an optimization run."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    
    run.is_favorite = not run.is_favorite
    db.commit()
    
    return {
        'success': True,
        'is_favorite': run.is_favorite
    }


@router.post("/runs/{run_id}/name")
async def update_run_name(
    run_id: str,
    name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update the name/description of an optimization run."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    
    run.name = name
    db.commit()
    
    return {
        'success': True,
        'name': name
    }


@router.delete("/runs/{run_id}")
async def delete_optimization_run(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete an optimization run."""
    run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Optimization run not found")
    
    db.delete(run)
    db.commit()
    
    return {
        'success': True,
        'message': 'Optimization run deleted'
    }


@router.get("/config/history")
async def get_config_history(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get history of Strategy Config changes.
    
    Shows provenance: what changed, when, and why.
    """
    user_id = current_user.get('sub') or current_user.get('user_id')
    
    snapshots = db.query(StrategyConfigSnapshot).filter(
        StrategyConfigSnapshot.user_id == user_id
    ).order_by(StrategyConfigSnapshot.created_at.desc()).limit(limit).all()
    
    return {
        'success': True,
        'history': [snapshot.to_dict() for snapshot in snapshots]
    }
