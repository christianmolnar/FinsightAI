"""
User Preferences API

REST API endpoints for managing user preferences including:
- Auto-refresh settings
- Display preferences
- Theme preferences
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.services.preferences_service import PreferencesService
from sqlalchemy.orm import Session
from app.database import get_db
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/preferences", tags=["preferences"])

# Temporary user ID for testing (same as watchlist)
TEMP_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


# ========================================
# PYDANTIC MODELS
# ========================================

class PreferencesResponse(BaseModel):
    """Response model for user preferences"""
    auto_refresh_enabled: bool
    refresh_interval_watchlist: int
    refresh_interval_portfolio: int
    refresh_interval_orders: int
    default_rows_per_page: int
    theme: str
    
    class Config:
        from_attributes = True


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating preferences (all fields optional)"""
    auto_refresh_enabled: Optional[bool] = None
    refresh_interval_watchlist: Optional[int] = None
    refresh_interval_portfolio: Optional[int] = None
    refresh_interval_orders: Optional[int] = None
    default_rows_per_page: Optional[int] = None
    theme: Optional[str] = None


# ========================================
# API ENDPOINTS
# ========================================

@router.get("/", response_model=PreferencesResponse)
async def get_preferences(db: Session = Depends(get_db)):
    """
    Get user preferences (creates defaults if not exist)
    
    Returns:
        User preferences with all settings
    """
    try:
        service = PreferencesService(db)
        preferences = service.get_or_create_preferences(TEMP_USER_ID)
        
        return PreferencesResponse(
            auto_refresh_enabled=preferences.auto_refresh_enabled,
            refresh_interval_watchlist=preferences.refresh_interval_watchlist,
            refresh_interval_portfolio=preferences.refresh_interval_portfolio,
            refresh_interval_orders=preferences.refresh_interval_orders,
            default_rows_per_page=preferences.default_rows_per_page,
            theme=preferences.theme
        )
        
    except Exception as e:
        logger.error(f"Error fetching preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")


@router.put("/", response_model=PreferencesResponse)
async def update_preferences(
    updates: UpdatePreferencesRequest,
    db: Session = Depends(get_db)
):
    """
    Update user preferences (partial updates supported)
    
    Args:
        updates: Preference fields to update (only provided fields are updated)
        
    Returns:
        Updated preferences
    """
    try:
        service = PreferencesService(db)
        
        # Build update dict from provided fields only
        update_dict = {}
        if updates.auto_refresh_enabled is not None:
            update_dict['auto_refresh_enabled'] = updates.auto_refresh_enabled
        if updates.refresh_interval_watchlist is not None:
            update_dict['refresh_interval_watchlist'] = updates.refresh_interval_watchlist
        if updates.refresh_interval_portfolio is not None:
            update_dict['refresh_interval_portfolio'] = updates.refresh_interval_portfolio
        if updates.refresh_interval_orders is not None:
            update_dict['refresh_interval_orders'] = updates.refresh_interval_orders
        if updates.default_rows_per_page is not None:
            update_dict['default_rows_per_page'] = updates.default_rows_per_page
        if updates.theme is not None:
            update_dict['theme'] = updates.theme
        
        # Update preferences
        preferences = service.update_preferences(TEMP_USER_ID, update_dict)
        
        return PreferencesResponse(
            auto_refresh_enabled=preferences.auto_refresh_enabled,
            refresh_interval_watchlist=preferences.refresh_interval_watchlist,
            refresh_interval_portfolio=preferences.refresh_interval_portfolio,
            refresh_interval_orders=preferences.refresh_interval_orders,
            default_rows_per_page=preferences.default_rows_per_page,
            theme=preferences.theme
        )
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.post("/reset", response_model=PreferencesResponse)
async def reset_preferences(db: Session = Depends(get_db)):
    """
    Reset user preferences to defaults
    
    Returns:
        Reset preferences with default values
    """
    try:
        service = PreferencesService(db)
        preferences = service.reset_to_defaults(TEMP_USER_ID)
        
        return PreferencesResponse(
            auto_refresh_enabled=preferences.auto_refresh_enabled,
            refresh_interval_watchlist=preferences.refresh_interval_watchlist,
            refresh_interval_portfolio=preferences.refresh_interval_portfolio,
            refresh_interval_orders=preferences.refresh_interval_orders,
            default_rows_per_page=preferences.default_rows_per_page,
            theme=preferences.theme
        )
        
    except Exception as e:
        logger.error(f"Error resetting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting preferences: {str(e)}")
