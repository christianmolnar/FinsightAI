"""
Strategy Variants API

CRUD endpoints for StrategyVariant records.
Variants are named, versioned strategy configs created by the optimizer or user.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.database import get_db
from app.models.strategy_variant import StrategyVariant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/strategy-variants", tags=["strategy_variants"])


# ── Request/Response Models ───────────────────────────────────────────────────

class CreateVariantRequest(BaseModel):
    name: str
    description: Optional[str] = None
    source: str = "manual"          # manual | optimization | ai_discovery
    source_id: Optional[str] = None
    parent_variant_id: Optional[str] = None
    config: dict
    ai_summary: Optional[str] = None
    ai_proposed_changes: Optional[dict] = None
    user_id: Optional[str] = "default"


class UpdateVariantRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    ai_summary: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def list_variants(
    user_id: str = "default",
    include_archived: bool = False,
    source: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all strategy variants, newest first."""
    query = db.query(StrategyVariant).filter(StrategyVariant.user_id == user_id)
    if not include_archived:
        query = query.filter(StrategyVariant.is_archived == False)
    if source:
        query = query.filter(StrategyVariant.source == source)
    variants = query.order_by(StrategyVariant.created_at.desc()).all()
    return {"variants": [v.to_dict() for v in variants]}


@router.get("/{variant_id}")
def get_variant(variant_id: str, db: Session = Depends(get_db)):
    """Get a single variant by ID."""
    variant = db.query(StrategyVariant).filter(StrategyVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant.to_dict()


@router.post("")
def create_variant(request: CreateVariantRequest, db: Session = Depends(get_db)):
    """Create a new strategy variant manually."""
    # Determine version: count existing variants with same name
    existing_count = db.query(StrategyVariant).filter(
        StrategyVariant.name == request.name,
        StrategyVariant.user_id == request.user_id
    ).count()

    variant = StrategyVariant(
        name=request.name,
        description=request.description,
        user_id=request.user_id,
        source=request.source,
        source_id=request.source_id,
        parent_variant_id=request.parent_variant_id,
        version=existing_count + 1,
        config=request.config,
        ai_summary=request.ai_summary,
        ai_proposed_changes=request.ai_proposed_changes,
    )
    db.add(variant)
    db.commit()
    db.refresh(variant)
    logger.info(f"Created strategy variant '{request.name}' v{variant.version}")
    return variant.to_dict()


@router.patch("/{variant_id}")
def update_variant(variant_id: str, request: UpdateVariantRequest, db: Session = Depends(get_db)):
    """Update mutable fields on a variant (name, favorite, archived, etc.)."""
    variant = db.query(StrategyVariant).filter(StrategyVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    if request.name is not None:
        variant.name = request.name
    if request.description is not None:
        variant.description = request.description
    if request.is_favorite is not None:
        variant.is_favorite = request.is_favorite
    if request.is_archived is not None:
        variant.is_archived = request.is_archived
    if request.ai_summary is not None:
        variant.ai_summary = request.ai_summary
    db.commit()
    db.refresh(variant)
    return variant.to_dict()


@router.post("/{variant_id}/promote")
def promote_variant(variant_id: str, user_id: str = "default", db: Session = Depends(get_db)):
    """
    Promote a variant to the active config.
    Clears is_active on all other variants for this user, sets it on this one.
    """
    variant = db.query(StrategyVariant).filter(StrategyVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Deactivate all others for this user
    db.query(StrategyVariant).filter(
        StrategyVariant.user_id == user_id,
        StrategyVariant.is_active == True
    ).update({"is_active": False})

    variant.is_active = True
    db.commit()
    db.refresh(variant)
    logger.info(f"Promoted variant '{variant.name}' v{variant.version} to active config")
    return {"success": True, "active_variant": variant.to_dict()}


@router.delete("/{variant_id}")
def archive_variant(variant_id: str, db: Session = Depends(get_db)):
    """Soft-delete (archive) a variant."""
    variant = db.query(StrategyVariant).filter(StrategyVariant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    if variant.is_active:
        raise HTTPException(status_code=400, detail="Cannot archive the active variant")
    variant.is_archived = True
    db.commit()
    return {"success": True, "id": variant_id}
