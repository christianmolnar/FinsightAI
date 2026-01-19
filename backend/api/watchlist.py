"""
User Watchlist API Endpoints
Provides REST API for managing user watchlists
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
import logging

from app.database import get_db
from services.watchlist_service import WatchlistService
from app.services.alpaca_service import AlpacaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])


# Pydantic models for request/response
class WatchlistItemResponse(BaseModel):
    """Response model for watchlist item"""
    id: int
    user_id: str
    symbol: str
    added_at: str  # Changed from created_at to match database column
    
    class Config:
        from_attributes = True


class AddToWatchlistRequest(BaseModel):
    """Request model for adding symbol to watchlist"""
    symbol: str
    # Removed notes - column doesn't exist in database


# Dependency injection for watchlist service
# TODO: Re-enable authentication in Phase 7
def get_watchlist_service(db: Session = Depends(get_db)) -> tuple[WatchlistService, UUID]:
    """
    Get watchlist service instance with temporary user_id
    
    Returns:
        Tuple of (WatchlistService, user_id)
    """
    alpaca_service = AlpacaService()
    watchlist_service = WatchlistService(db, alpaca_service)
    # Temporary default user until Phase 7 (Authentication)
    user_id = UUID("00000000-0000-0000-0000-000000000001")
    return watchlist_service, user_id


@router.get("/", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    service_tuple = Depends(get_watchlist_service)
):
    """
    Get user's watchlist
    
    Returns:
        List of watchlist items
    """
    try:
        service, user_id = service_tuple
        items = service.get_user_watchlist(user_id)
        
        # Convert SQLAlchemy objects to response models
        return [
            WatchlistItemResponse(
                id=item.id,
                user_id=str(item.user_id),
                symbol=item.symbol,
                added_at=item.added_at.isoformat()  # Changed from created_at
            )
            for item in items
        ]
        
    except Exception as e:
        logger.error(f"Error getting watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    request: AddToWatchlistRequest,
    service_tuple = Depends(get_watchlist_service)
):
    """
    Add symbol to watchlist
    
    Args:
        request: AddToWatchlistRequest with symbol
        
    Returns:
        Created watchlist item
    """
    try:
        service, user_id = service_tuple
        item = service.add_to_watchlist(
            user_id=user_id,
            symbol=request.symbol.upper()
            # Removed notes parameter - doesn't exist in database
        )
        
        if not item:
            raise HTTPException(
                status_code=400,
                detail=f"Symbol {request.symbol} already in watchlist"
            )
        
        return WatchlistItemResponse(
            id=item.id,
            user_id=str(item.user_id),
            symbol=item.symbol,
            added_at=item.added_at.isoformat()  # Changed from created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    service_tuple = Depends(get_watchlist_service)
):
    """
    Remove symbol from watchlist
    
    Args:
        symbol: Stock symbol to remove
        
    Returns:
        Success message
    """
    try:
        service, user_id = service_tuple
        success = service.remove_from_watchlist(user_id, symbol.upper())
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Symbol {symbol} not found in watchlist"
            )
        
        return {"message": f"Symbol {symbol} removed from watchlist"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# REMOVED: PUT /{symbol}/notes endpoint - notes column doesn't exist in database schema


@router.post("/sync/from-alpaca", response_model=List[WatchlistItemResponse])
async def sync_from_alpaca(
    service_tuple = Depends(get_watchlist_service)
):
    """
    Sync watchlist FROM Alpaca TO local database
    
    Returns:
        Updated watchlist items
    """
    try:
        service, user_id = service_tuple
        items = service.sync_from_alpaca(user_id)
        
        return [
            WatchlistItemResponse(
                id=item.id,
                user_id=str(item.user_id),
                symbol=item.symbol,
                notes=item.notes,
                created_at=item.created_at.isoformat()
            )
            for item in items
        ]
        
    except Exception as e:
        logger.error(f"Error syncing from Alpaca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/to-alpaca")
async def sync_to_alpaca(
    service_tuple = Depends(get_watchlist_service)
):
    """
    Sync watchlist FROM local database TO Alpaca
    
    Returns:
        Success message
    """
    try:
        service, user_id = service_tuple
        success = service.sync_to_alpaca(user_id)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to sync watchlist to Alpaca"
            )
        
        return {"message": "Watchlist synced to Alpaca successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing to Alpaca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
