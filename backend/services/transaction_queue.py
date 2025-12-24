"""
Transaction Queue Service
Manages pending trades, auto-execution, and queue operations
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from uuid import UUID
import psycopg2
from psycopg2.extras import RealDictCursor
import json

logger = logging.getLogger(__name__)


class TransactionQueueService:
    """Service for managing transaction queue (pending trades)"""
    
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "").replace('postgresql+psycopg://', 'postgresql://')
    
    def _get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def create_pending_transaction(
        self,
        portfolio_id: str,
        transaction_type: str,
        symbol: str,
        quantity: int,
        proposed_price: float,
        confidence_score: int,
        ai_reasoning: Dict[str, Any],
        risk_factors: List[str] = None,
        catalysts: List[str] = None,
        stop_loss: Optional[float] = None,
        profit_target: Optional[float] = None,
        reason_for_trade: Optional[str] = None,
        auto_execute: bool = False,
        scheduled_minutes: int = 60,
        created_by: str = "user"
    ) -> Dict[str, Any]:
        """
        Create a new pending transaction in the queue
        
        Args:
            portfolio_id: Portfolio UUID
            transaction_type: 'buy' or 'sell'
            symbol: Stock symbol
            quantity: Number of shares
            proposed_price: Proposed execution price
            confidence_score: AI confidence (0-100)
            ai_reasoning: JSONB with OpenAI and Claude recommendations
            risk_factors: List of identified risks
            catalysts: List of positive catalysts
            stop_loss: Optional stop loss price
            profit_target: Optional profit target price
            reason_for_trade: User's reason for trade
            auto_execute: Whether to auto-execute
            scheduled_minutes: Minutes until auto-execution (default 60)
            created_by: 'user' or 'ai_agent'
        
        Returns:
            Dict with created transaction details
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Calculate scheduled time if auto_execute
            scheduled_time = None
            expires_at = None
            if auto_execute:
                scheduled_time = datetime.now() + timedelta(minutes=scheduled_minutes)
                expires_at = scheduled_time + timedelta(hours=1)  # Expire 1 hour after scheduled
            else:
                expires_at = datetime.now() + timedelta(days=7)  # Expire in 7 days if not acted upon
            
            query = """
                INSERT INTO pending_transactions (
                    portfolio_id, transaction_type, symbol, quantity, proposed_price,
                    confidence_score, ai_reasoning, risk_factors, catalysts,
                    stop_loss, profit_target, reason_for_trade,
                    auto_execute, scheduled_time, expires_at, created_by, status
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, 'pending'
                )
                RETURNING *
            """
            
            cur.execute(query, (
                portfolio_id, transaction_type, symbol, quantity, proposed_price,
                confidence_score, json.dumps(ai_reasoning), risk_factors or [], catalysts or [],
                stop_loss, profit_target, reason_for_trade,
                auto_execute, scheduled_time, expires_at, created_by
            ))
            
            result = dict(cur.fetchone())
            conn.commit()
            
            logger.info(f"Created pending transaction: {result['id']} - {transaction_type} {quantity} {symbol}")
            
            cur.close()
            conn.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating pending transaction: {e}")
            raise
    
    def list_pending_transactions(
        self,
        portfolio_id: str,
        status: Optional[str] = None,
        transaction_type: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List pending transactions with optional filters
        
        Args:
            portfolio_id: Portfolio UUID
            status: Filter by status (pending, approved, rejected, etc.)
            transaction_type: Filter by type ('buy' or 'sell')
            symbol: Filter by stock symbol
            limit: Maximum number of results
        
        Returns:
            List of pending transactions
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT * FROM pending_transactions
                WHERE portfolio_id = %s
            """
            params = [portfolio_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            if transaction_type:
                query += " AND transaction_type = %s"
                params.append(transaction_type)
            
            if symbol:
                query += " AND symbol = %s"
                params.append(symbol)
            
            query += " ORDER BY confidence_score DESC, created_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            results = [dict(row) for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error listing pending transactions: {e}")
            raise
    
    def approve_transaction(self, transaction_id: str, user_notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve a pending transaction and execute it
        
        Args:
            transaction_id: Transaction UUID
            user_notes: Optional notes from user
        
        Returns:
            Dict with execution result
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get transaction details
            cur.execute("SELECT * FROM pending_transactions WHERE id = %s", (transaction_id,))
            transaction = dict(cur.fetchone())
            
            if transaction['status'] != 'pending':
                raise ValueError(f"Transaction {transaction_id} is not pending (status: {transaction['status']})")
            
            # Execute the trade
            from backend.services.paper_trading import PaperTradingService
            trading_service = PaperTradingService()
            
            trade_result = trading_service.execute_trade(
                portfolio_id=transaction['portfolio_id'],
                symbol=transaction['symbol'],
                quantity=transaction['quantity'],
                trade_type=transaction['transaction_type'],
                price=transaction['proposed_price']  # Use proposed price for paper trading
            )
            
            # Update pending transaction status
            update_query = """
                UPDATE pending_transactions
                SET status = 'executed',
                    executed_at = NOW(),
                    execution_price = %s,
                    execution_notes = %s,
                    user_notes = %s
                WHERE id = %s
                RETURNING *
            """
            
            cur.execute(update_query, (
                transaction['proposed_price'],
                f"Trade executed successfully: {trade_result.get('message', '')}",
                user_notes,
                transaction_id
            ))
            
            result = dict(cur.fetchone())
            conn.commit()
            
            logger.info(f"Approved and executed transaction: {transaction_id}")
            
            cur.close()
            conn.close()
            
            return {
                "success": True,
                "transaction": result,
                "trade_result": trade_result
            }
            
        except Exception as e:
            logger.error(f"Error approving transaction: {e}")
            if conn:
                conn.rollback()
            raise
    
    def reject_transaction(self, transaction_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Reject a pending transaction
        
        Args:
            transaction_id: Transaction UUID
            reason: Reason for rejection
        
        Returns:
            Dict with rejection result
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                UPDATE pending_transactions
                SET status = 'rejected',
                    user_notes = %s
                WHERE id = %s AND status = 'pending'
                RETURNING *
            """
            
            cur.execute(query, (reason, transaction_id))
            result = cur.fetchone()
            
            if not result:
                raise ValueError(f"Transaction {transaction_id} not found or not pending")
            
            result = dict(result)
            conn.commit()
            
            logger.info(f"Rejected transaction: {transaction_id}")
            
            cur.close()
            conn.close()
            
            return {
                "success": True,
                "transaction": result
            }
            
        except Exception as e:
            logger.error(f"Error rejecting transaction: {e}")
            raise
    
    def modify_transaction(
        self,
        transaction_id: str,
        quantity: Optional[int] = None,
        proposed_price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        profit_target: Optional[float] = None,
        user_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify a pending transaction
        
        Args:
            transaction_id: Transaction UUID
            quantity: New quantity (optional)
            proposed_price: New proposed price (optional)
            stop_loss: New stop loss (optional)
            profit_target: New profit target (optional)
            user_notes: User notes about modification
        
        Returns:
            Dict with modified transaction
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            updates = []
            params = []
            
            if quantity is not None:
                updates.append("quantity = %s")
                params.append(quantity)
            
            if proposed_price is not None:
                updates.append("proposed_price = %s")
                params.append(proposed_price)
            
            if stop_loss is not None:
                updates.append("stop_loss = %s")
                params.append(stop_loss)
            
            if profit_target is not None:
                updates.append("profit_target = %s")
                params.append(profit_target)
            
            if user_notes is not None:
                updates.append("user_notes = %s")
                params.append(user_notes)
            
            if not updates:
                raise ValueError("No modifications provided")
            
            query = f"""
                UPDATE pending_transactions
                SET {', '.join(updates)}
                WHERE id = %s AND status = 'pending'
                RETURNING *
            """
            params.append(transaction_id)
            
            cur.execute(query, params)
            result = cur.fetchone()
            
            if not result:
                raise ValueError(f"Transaction {transaction_id} not found or not pending")
            
            result = dict(result)
            conn.commit()
            
            logger.info(f"Modified transaction: {transaction_id}")
            
            cur.close()
            conn.close()
            
            return {
                "success": True,
                "transaction": result
            }
            
        except Exception as e:
            logger.error(f"Error modifying transaction: {e}")
            raise
    
    def process_auto_execute_queue(self) -> Dict[str, Any]:
        """
        Process transactions scheduled for auto-execution
        This should be called periodically (e.g., every minute via cron/scheduler)
        
        Returns:
            Dict with execution summary
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Find transactions ready for auto-execution
            query = """
                SELECT * FROM pending_transactions
                WHERE status = 'pending'
                AND auto_execute = true
                AND scheduled_time <= NOW()
                ORDER BY scheduled_time ASC
            """
            
            cur.execute(query)
            ready_transactions = [dict(row) for row in cur.fetchall()]
            
            executed = []
            failed = []
            
            for transaction in ready_transactions:
                try:
                    result = self.approve_transaction(
                        transaction['id'],
                        user_notes="Auto-executed by system"
                    )
                    executed.append(result)
                    logger.info(f"Auto-executed: {transaction['id']}")
                except Exception as e:
                    logger.error(f"Failed to auto-execute {transaction['id']}: {e}")
                    failed.append({
                        "transaction_id": transaction['id'],
                        "error": str(e)
                    })
            
            cur.close()
            conn.close()
            
            return {
                "processed": len(ready_transactions),
                "executed": len(executed),
                "failed": len(failed),
                "details": {
                    "executed": executed,
                    "failed": failed
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing auto-execute queue: {e}")
            raise
    
    def expire_old_transactions(self, days_old: int = 7) -> Dict[str, Any]:
        """
        Expire transactions that haven't been acted upon
        
        Args:
            days_old: Expire transactions older than this many days
        
        Returns:
            Dict with expiration summary
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                UPDATE pending_transactions
                SET status = 'expired',
                    execution_notes = 'Automatically expired due to inactivity'
                WHERE status = 'pending'
                AND (expires_at <= NOW() OR created_at < NOW() - INTERVAL '%s days')
                RETURNING id, symbol, created_at
            """
            
            cur.execute(query, (days_old,))
            expired = [dict(row) for row in cur.fetchall()]
            
            conn.commit()
            
            logger.info(f"Expired {len(expired)} old transactions")
            
            cur.close()
            conn.close()
            
            return {
                "expired_count": len(expired),
                "transactions": expired
            }
            
        except Exception as e:
            logger.error(f"Error expiring transactions: {e}")
            raise
    
    def get_queue_stats(self, portfolio_id: str) -> Dict[str, Any]:
        """
        Get statistics about the transaction queue
        
        Args:
            portfolio_id: Portfolio UUID
        
        Returns:
            Dict with queue statistics
        """
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT 
                    status,
                    transaction_type,
                    COUNT(*) as count,
                    AVG(confidence_score) as avg_confidence,
                    SUM(quantity * proposed_price) as total_value
                FROM pending_transactions
                WHERE portfolio_id = %s
                GROUP BY status, transaction_type
            """
            
            cur.execute(query, (portfolio_id,))
            stats = [dict(row) for row in cur.fetchall()]
            
            cur.close()
            conn.close()
            
            return {
                "portfolio_id": portfolio_id,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {e}")
            raise
