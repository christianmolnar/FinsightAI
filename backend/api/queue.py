"""
Transaction Queue API Endpoints
Routes for managing pending trades
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.transaction_queue import TransactionQueueService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/queue", tags=["Transaction Queue"])


# Pydantic models for request/response validation
class CreateTransactionRequest(BaseModel):
    portfolio_id: str = Field(..., description="Portfolio UUID")
    transaction_type: str = Field(..., pattern="^(buy|sell)$", description="Transaction type")
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    quantity: int = Field(..., gt=0, description="Number of shares")
    proposed_price: float = Field(..., gt=0, description="Proposed price per share")
    confidence_score: int = Field(..., ge=0, le=100, description="AI confidence score")
    ai_reasoning: Dict[str, Any] = Field(..., description="AI analysis with OpenAI and Claude recommendations")
    risk_factors: Optional[List[str]] = Field(None, description="List of identified risks")
    catalysts: Optional[List[str]] = Field(None, description="List of positive catalysts")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    profit_target: Optional[float] = Field(None, gt=0, description="Profit target price")
    reason_for_trade: Optional[str] = Field(None, description="User's reason for trade")
    auto_execute: bool = Field(False, description="Whether to auto-execute")
    scheduled_minutes: int = Field(60, ge=1, le=1440, description="Minutes until auto-execution")
    created_by: str = Field("user", pattern="^(user|ai_agent)$", description="Creator")


class ModifyTransactionRequest(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, description="New quantity")
    proposed_price: Optional[float] = Field(None, gt=0, description="New proposed price")
    stop_loss: Optional[float] = Field(None, gt=0, description="New stop loss")
    profit_target: Optional[float] = Field(None, gt=0, description="New profit target")
    user_notes: Optional[str] = Field(None, description="Modification notes")


class ActionRequest(BaseModel):
    user_notes: Optional[str] = Field(None, description="User notes")
    reason: Optional[str] = Field(None, description="Reason for action")


@router.post("/pending")
async def create_pending_transaction(request: CreateTransactionRequest):
    """
    Create a new pending transaction in the queue
    
    This endpoint is called when:
    - User completes research and clicks "Create Trade Proposal"
    - AI agent autonomously identifies an opportunity
    
    Returns the created transaction with ID and status
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.create_pending_transaction(
            portfolio_id=request.portfolio_id,
            transaction_type=request.transaction_type,
            symbol=request.symbol,
            quantity=request.quantity,
            proposed_price=request.proposed_price,
            confidence_score=request.confidence_score,
            ai_reasoning=request.ai_reasoning,
            risk_factors=request.risk_factors,
            catalysts=request.catalysts,
            stop_loss=request.stop_loss,
            profit_target=request.profit_target,
            reason_for_trade=request.reason_for_trade,
            auto_execute=request.auto_execute,
            scheduled_minutes=request.scheduled_minutes,
            created_by=request.created_by
        )
        
        return {
            "success": True,
            "message": f"Created pending {request.transaction_type} order for {request.symbol}",
            "transaction": result
        }
        
    except Exception as e:
        logger.error(f"Error creating pending transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create pending transaction: {str(e)}"
        )


@router.get("/pending")
async def list_pending_transactions(
    portfolio_id: Optional[str] = None,
    status: Optional[str] = None,
    transaction_type: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50
):
    """
    List pending transactions with optional filters
    
    Query params:
    - portfolio_id: Optional - Portfolio UUID (if not provided, returns from all portfolios)
    - status: Optional - Filter by status (pending, approved, rejected, executed, expired)
    - transaction_type: Optional - Filter by type (buy, sell)
    - symbol: Optional - Filter by stock symbol
    - limit: Optional - Max results (default 50)
    
    Returns list of transactions ordered by confidence score and date
    """
    try:
        queue_service = TransactionQueueService()
        
        transactions = queue_service.list_pending_transactions(
            portfolio_id=portfolio_id or "",  # Empty string means all portfolios
            status=status,
            transaction_type=transaction_type,
            symbol=symbol,
            limit=limit
        )
        
        return {
            "success": True,
            "count": len(transactions),
            "transactions": transactions
        }
        
    except Exception as e:
        logger.error(f"Error listing pending transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list pending transactions: {str(e)}"
        )


@router.get("/pending/{transaction_id}")
async def get_transaction_details(transaction_id: str):
    """
    Get details of a specific pending transaction
    
    Returns full transaction details including AI reasoning
    """
    try:
        queue_service = TransactionQueueService()
        
        # Get all transactions and filter by ID (could optimize with specific query)
        transactions = queue_service.list_pending_transactions(
            portfolio_id="",  # Will need portfolio_id in real implementation
            limit=1000
        )
        
        transaction = next((t for t in transactions if str(t['id']) == transaction_id), None)
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction {transaction_id} not found"
            )
        
        return {
            "success": True,
            "transaction": transaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction details: {str(e)}"
        )


@router.put("/pending/{transaction_id}/approve")
async def approve_transaction(transaction_id: str, request: ActionRequest):
    """
    Approve a pending transaction and execute it immediately
    
    This will:
    1. Execute the trade (paper trading)
    2. Update transaction status to 'executed'
    3. Record execution details
    
    Returns execution result
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.approve_transaction(
            transaction_id=transaction_id,
            user_notes=request.user_notes
        )
        
        return {
            "success": True,
            "message": "Transaction approved and executed",
            **result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error approving transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve transaction: {str(e)}"
        )


@router.put("/pending/{transaction_id}/reject")
async def reject_transaction(transaction_id: str, request: ActionRequest):
    """
    Reject a pending transaction
    
    This will:
    1. Update transaction status to 'rejected'
    2. Remove from active queue
    3. Record rejection reason
    
    Returns rejection confirmation
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.reject_transaction(
            transaction_id=transaction_id,
            reason=request.reason
        )
        
        return {
            "success": True,
            "message": "Transaction rejected",
            **result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rejecting transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject transaction: {str(e)}"
        )


@router.put("/pending/{transaction_id}/modify")
async def modify_transaction(transaction_id: str, request: ModifyTransactionRequest):
    """
    Modify a pending transaction
    
    Allows changing:
    - Quantity
    - Proposed price
    - Stop loss
    - Profit target
    
    Only works for transactions with status='pending'
    
    Returns updated transaction
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.modify_transaction(
            transaction_id=transaction_id,
            quantity=request.quantity,
            proposed_price=request.proposed_price,
            stop_loss=request.stop_loss,
            profit_target=request.profit_target,
            user_notes=request.user_notes
        )
        
        return {
            "success": True,
            "message": "Transaction modified",
            **result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error modifying transaction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify transaction: {str(e)}"
        )


@router.get("/stats")
async def get_queue_stats(portfolio_id: str):
    """
    Get statistics about the transaction queue
    
    Returns:
    - Count by status
    - Count by transaction type
    - Average confidence scores
    - Total values
    
    Useful for dashboard displays
    """
    try:
        queue_service = TransactionQueueService()
        
        stats = queue_service.get_queue_stats(portfolio_id=portfolio_id)
        
        return {
            "success": True,
            **stats
        }
        
    except Exception as e:
        logger.error(f"Error getting queue stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get queue stats: {str(e)}"
        )


@router.post("/process-auto-execute")
async def process_auto_execute():
    """
    Manually trigger auto-execution processing
    
    This endpoint should be called by a scheduler (cron job) every minute
    to process transactions scheduled for auto-execution
    
    In production, use a proper task scheduler like Celery or APScheduler
    
    Returns summary of processed transactions
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.process_auto_execute_queue()
        
        return {
            "success": True,
            "message": f"Processed {result['processed']} transactions",
            **result
        }
        
    except Exception as e:
        logger.error(f"Error processing auto-execute queue: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process auto-execute queue: {str(e)}"
        )


@router.post("/expire-old")
async def expire_old_transactions(days_old: int = 7):
    """
    Expire old pending transactions
    
    Transactions that haven't been acted upon after N days are automatically expired
    
    Query params:
    - days_old: Number of days (default 7)
    
    Returns summary of expired transactions
    """
    try:
        queue_service = TransactionQueueService()
        
        result = queue_service.expire_old_transactions(days_old=days_old)
        
        return {
            "success": True,
            "message": f"Expired {result['expired_count']} old transactions",
            **result
        }
        
    except Exception as e:
        logger.error(f"Error expiring transactions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to expire transactions: {str(e)}"
        )
