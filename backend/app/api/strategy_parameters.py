"""
Strategy Parameters API
CRUD endpoints for managing trading strategy parameters with AI optimization.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
import uuid
from decimal import Decimal
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.strategy_parameters import (
    StrategyParameter,
    StockParameterOverride,
    OptimizationHistory,
    StrategyParameterCreate,
    StrategyParameterUpdate,
    StrategyParameterResponse,
    StockParameterOverrideBase,
    StockParameterOverrideCreate,
    StockParameterOverrideUpdate,
    StockParameterOverrideResponse,
    OptimizationRequest,
    OptimizationResponse,
    StrategyType
)

router = APIRouter(prefix="/api/strategy-parameters", tags=["Strategy Parameters"])


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# TODO: Replace with actual auth when Phase 7 is implemented
def get_current_user_id() -> uuid.UUID:
    """Temporary: return a hardcoded user ID until auth is implemented"""
    # In Phase 7, this will extract user ID from JWT token
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


# =====================
# Parameter CRUD Endpoints
# =====================

@router.post("/", response_model=StrategyParameterResponse, status_code=status.HTTP_201_CREATED)
async def create_parameter(
    parameter: StrategyParameterCreate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Create a new strategy parameter.
    
    - **name**: Internal parameter name (snake_case)
    - **display_name**: Human-readable name
    - **strategy**: Which strategy this parameter belongs to
    - **min_value/max_value**: Acceptable range
    - **default_value/current_value**: Starting values
    - **ai_optimizable**: Whether AI can suggest optimizations
    """
    db_parameter = StrategyParameter(
        **parameter.dict(),
        user_id=user_id
    )
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.get("/", response_model=List[StrategyParameterResponse])
async def list_parameters(
    strategy: Optional[str] = None,
    ai_optimizable: Optional[bool] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    List all strategy parameters for the current user.
    
    - **strategy**: Filter by strategy type (earnings, seasonality, macro, sentiment, ipo)
    - **ai_optimizable**: Filter by AI optimization flag (optional)
    - **is_active**: Filter by active status (default: True)
    """
    query = db.query(StrategyParameter).filter(StrategyParameter.user_id == user_id)
    
    if strategy is not None:
        query = query.filter(StrategyParameter.strategy == strategy.lower())
    if ai_optimizable is not None:
        query = query.filter(StrategyParameter.ai_optimizable == ai_optimizable)
    if is_active is not None:
        query = query.filter(StrategyParameter.is_active == is_active)
    
    parameters = query.order_by(StrategyParameter.strategy, StrategyParameter.category).all()
    return parameters


@router.get("/{parameter_id}", response_model=StrategyParameterResponse)
async def get_parameter(
    parameter_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Get a specific parameter by ID.
    """
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    return parameter


@router.patch("/{parameter_id}", response_model=StrategyParameterResponse)
async def update_parameter(
    parameter_id: uuid.UUID,
    update_data: StrategyParameterUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Update a parameter's configuration.
    
    Only provided fields will be updated.
    """
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(parameter, field, value)
    
    # Validate current_value is still in range
    if 'current_value' in update_dict:
        if parameter.min_value and parameter.current_value < parameter.min_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"current_value must be >= {parameter.min_value}"
            )
        if parameter.max_value and parameter.current_value > parameter.max_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"current_value must be <= {parameter.max_value}"
            )
    
    db.commit()
    db.refresh(parameter)
    return parameter


@router.delete("/{parameter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parameter(
    parameter_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Delete a parameter (soft delete by setting is_active=False).
    """
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    parameter.is_active = False
    db.commit()
    return None


# =====================
# Stock Override Endpoints
# =====================

@router.post("/{parameter_id}/overrides", response_model=StockParameterOverrideResponse, 
             status_code=status.HTTP_201_CREATED)
async def create_stock_override(
    parameter_id: uuid.UUID,
    override: StockParameterOverrideBase,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Create a per-stock override for a parameter.
    
    Example: Set min_eps_growth to 15% for NVDA (more aggressive) vs 10% default.
    """
    # Verify parameter exists and belongs to user
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    # Validate override value is within parameter's min/max
    if parameter.min_value and override.override_value < parameter.min_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"override_value must be >= {parameter.min_value}"
        )
    if parameter.max_value and override.override_value > parameter.max_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"override_value must be <= {parameter.max_value}"
        )
    
    # Check if override already exists
    existing = db.query(StockParameterOverride).filter(
        and_(
            StockParameterOverride.parameter_id == parameter_id,
            StockParameterOverride.symbol == override.symbol.upper(),
            StockParameterOverride.is_active == True
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Override for {override.symbol} already exists"
        )
    
    db_override = StockParameterOverride(
        parameter_id=parameter_id,
        **override.dict()
    )
    db.add(db_override)
    db.commit()
    db.refresh(db_override)
    return db_override


@router.get("/{parameter_id}/overrides", response_model=List[StockParameterOverrideResponse])
async def list_stock_overrides(
    parameter_id: uuid.UUID,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    List all stock overrides for a parameter.
    """
    # Verify parameter exists and belongs to user
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    query = db.query(StockParameterOverride).filter(
        StockParameterOverride.parameter_id == parameter_id
    )
    
    if is_active is not None:
        query = query.filter(StockParameterOverride.is_active == is_active)
    
    overrides = query.order_by(StockParameterOverride.symbol).all()
    return overrides


@router.patch("/overrides/{override_id}", response_model=StockParameterOverrideResponse)
async def update_stock_override(
    override_id: uuid.UUID,
    update_data: StockParameterOverrideUpdate,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Update a stock override.
    """
    override = db.query(StockParameterOverride).join(StrategyParameter).filter(
        and_(
            StockParameterOverride.id == override_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not override:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Override {override_id} not found"
        )
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(override, field, value)
    
    db.commit()
    db.refresh(override)
    return override


@router.delete("/overrides/{override_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock_override(
    override_id: uuid.UUID,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Delete a stock override (soft delete).
    """
    override = db.query(StockParameterOverride).join(StrategyParameter).filter(
        and_(
            StockParameterOverride.id == override_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not override:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Override {override_id} not found"
        )
    
    override.is_active = False
    db.commit()
    return None


# =====================
# AI Optimization Endpoints
# =====================

@router.post("/optimize", response_model=List[OptimizationResponse])
async def optimize_parameters(
    request: OptimizationRequest,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Request AI optimization for parameter(s).
    
    - If **parameter_ids** provided: Optimize specific parameters
    - If **strategy** provided: Optimize all parameters for that strategy
    - If neither: Optimize all AI-optimizable parameters
    
    Returns suggested values with rationale.
    
    NOTE: This is a placeholder. Actual AI optimization logic will be implemented in Phase 5.
    """
    # Build query for parameters to optimize
    query = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.user_id == user_id,
            StrategyParameter.ai_optimizable == True,
            StrategyParameter.is_active == True
        )
    )
    
    if request.parameter_ids:
        query = query.filter(StrategyParameter.id.in_(request.parameter_ids))
    elif request.strategy:
        query = query.filter(StrategyParameter.strategy == request.strategy)
    
    parameters = query.all()
    
    if not parameters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No optimizable parameters found"
        )
    
    # TODO: Phase 5 - Implement actual AI optimization logic
    # For now, return mock suggestions
    suggestions = []
    for param in parameters:
        # Mock: suggest value 10% higher if current is below midpoint
        midpoint = (param.min_value + param.max_value) / 2 if param.min_value and param.max_value else param.current_value
        if param.current_value < midpoint:
            suggested = min(param.current_value * Decimal("1.1"), param.max_value or param.current_value * Decimal("1.1"))
        else:
            suggested = max(param.current_value * Decimal("0.9"), param.min_value or param.current_value * Decimal("0.9"))
        
        suggestions.append(OptimizationResponse(
            parameter_id=param.id,
            parameter_name=param.display_name,
            current_value=param.current_value,
            suggested_value=suggested,
            rationale=f"Mock suggestion: Adjusting {param.name} based on placeholder logic. Real AI optimization coming in Phase 5!",
            expected_improvement=Decimal("0.05"),  # Mock 5% improvement
            confidence=Decimal("0.7")  # Mock 70% confidence
        ))
    
    return suggestions


@router.post("/optimize/{parameter_id}/apply", response_model=StrategyParameterResponse)
async def apply_optimization(
    parameter_id: uuid.UUID,
    suggested_value: Decimal,
    db: Session = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    """
    Apply an AI-suggested optimization to a parameter.
    
    Records the change in optimization_history for performance tracking.
    """
    parameter = db.query(StrategyParameter).filter(
        and_(
            StrategyParameter.id == parameter_id,
            StrategyParameter.user_id == user_id
        )
    ).first()
    
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parameter {parameter_id} not found"
        )
    
    # Validate suggested value
    if parameter.min_value and suggested_value < parameter.min_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"suggested_value must be >= {parameter.min_value}"
        )
    if parameter.max_value and suggested_value > parameter.max_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"suggested_value must be <= {parameter.max_value}"
        )
    
    # Record optimization history
    history = OptimizationHistory(
        parameter_id=parameter_id,
        old_value=parameter.current_value,
        new_value=suggested_value,
        ai_rationale="User approved AI suggestion",
        status="approved",
        approved_by_user=True,
        approved_at=datetime.now(timezone.utc)
    )
    db.add(history)
    
    # Update parameter
    parameter.current_value = suggested_value
    parameter.ai_suggested_value = suggested_value
    parameter.last_optimized_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(parameter)
    return parameter
