"""
Agent Configuration API

Endpoints for managing autonomous agent settings.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel, Field
import logging

from app.database import get_db
from app.models.agent_config import AgentConfig

router = APIRouter(prefix="/api/agent", tags=["agent"])
logger = logging.getLogger(__name__)


class AgentConfigUpdate(BaseModel):
    """Request model for updating agent configuration"""
    enabled: bool | None = None
    enabled_strategies: List[str] | None = Field(None, example=["technical_breakout", "earnings_play"])
    confidence_threshold: float | None = Field(None, ge=0.0, le=1.0)
    max_opportunities_per_scan: int | None = Field(None, ge=1, le=20)
    scan_frequency_minutes: int | None = Field(None, ge=5, le=60)
    max_positions: int | None = Field(None, ge=1, le=50)
    max_position_size: float | None = Field(None, ge=100.0)
    default_position_shares: int | None = Field(None, ge=1)
    max_portfolio_risk: float | None = Field(None, ge=0.01, le=0.10)
    require_stop_loss: bool | None = None
    auto_execute_enabled: bool | None = None
    auto_execute_threshold: float | None = Field(None, ge=0.0, le=1.0)
    auto_execute_max_per_day: int | None = Field(None, ge=0, le=20)


@router.get("/config")
async def get_config(db: Session = Depends(get_db)) -> Dict:
    """
    Get current agent configuration
    
    Returns:
        Dict with agent settings
    """
    try:
        # Get or create default config
        config = db.query(AgentConfig).filter(AgentConfig.user_id == "default").first()
        
        if not config:
            # Create default configuration
            config = AgentConfig(user_id="default")
            db.add(config)
            db.commit()
            db.refresh(config)
            logger.info("Created default agent configuration")
        
        return {
            "success": True,
            "config": config.to_dict()
        }
    
    except Exception as e:
        logger.error(f"Error fetching agent config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch config: {str(e)}")


@router.put("/config")
async def update_config(
    updates: AgentConfigUpdate,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Update agent configuration
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Args:
        updates: Configuration updates
        
    Returns:
        Dict with updated configuration
    """
    try:
        # Get or create config
        config = db.query(AgentConfig).filter(AgentConfig.user_id == "default").first()
        
        if not config:
            config = AgentConfig(user_id="default")
            db.add(config)
        
        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        db.commit()
        db.refresh(config)
        
        logger.info(f"Updated agent config: {list(update_data.keys())}")
        
        return {
            "success": True,
            "message": "Configuration updated",
            "config": config.to_dict()
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating agent config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.post("/enable")
async def enable_agent(db: Session = Depends(get_db)) -> Dict:
    """
    Enable autonomous agent
    
    Returns:
        Dict with success message
    """
    try:
        config = db.query(AgentConfig).filter(AgentConfig.user_id == "default").first()
        
        if not config:
            config = AgentConfig(user_id="default", enabled=True)
            db.add(config)
        else:
            config.enabled = True
        
        db.commit()
        logger.info("✅ Autonomous agent ENABLED")
        
        return {
            "success": True,
            "message": "Agent enabled",
            "enabled": True
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error enabling agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enable agent: {str(e)}")


@router.post("/disable")
async def disable_agent(db: Session = Depends(get_db)) -> Dict:
    """
    Disable autonomous agent
    
    Returns:
        Dict with success message
    """
    try:
        config = db.query(AgentConfig).filter(AgentConfig.user_id == "default").first()
        
        if not config:
            # Already disabled (no config exists yet)
            return {
                "success": True,
                "message": "Agent already disabled",
                "enabled": False
            }
        
        config.enabled = False
        db.commit()
        logger.info("⏸️ Autonomous agent DISABLED")
        
        return {
            "success": True,
            "message": "Agent disabled",
            "enabled": False
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error disabling agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disable agent: {str(e)}")


@router.get("/status")
async def get_agent_status(db: Session = Depends(get_db)) -> Dict:
    """
    Get comprehensive agent status
    
    Returns:
        Dict with agent status, config summary, and recent activity
    """
    try:
        # Get config
        config = db.query(AgentConfig).filter(AgentConfig.user_id == "default").first()
        
        if not config:
            return {
                "success": True,
                "enabled": False,
                "message": "Agent not configured yet",
                "config_summary": None
            }
        
        # Get recent proposals created by agent
        # TODO: Implement TradeProposal model and query
        # from app.models import TradeProposal
        # recent_proposals = db.query(TradeProposal).filter(
        #     TradeProposal.source == "autonomous_scanner"
        # ).order_by(TradeProposal.created_at.desc()).limit(10).all()
        recent_proposals = []  # Temporary placeholder
        
        return {
            "success": True,
            "enabled": config.enabled,
            "config_summary": {
                "confidence_threshold": f"{config.confidence_threshold:.0%}",
                "enabled_strategies": config.enabled_strategies,
                "max_positions": config.max_positions,
                "auto_execute": config.auto_execute_enabled,
                "scan_frequency": f"{config.scan_frequency_minutes} minutes"
            },
            "recent_activity": {
                "proposals_created": len(recent_proposals),
                "latest_proposals": [
                    {
                        "symbol": p.symbol,
                        "score": p.final_score,
                        "confidence": f"{p.ai_confidence:.0%}",
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in recent_proposals[:5]
                ]
            }
        }
    
    except Exception as e:
        logger.error(f"Error fetching agent status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch status: {str(e)}")
