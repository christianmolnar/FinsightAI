"""
Paper Trading API - Railway PostgreSQL Version
Replaces JSON storage with database
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from decimal import Decimal

router = APIRouter()

# Database connection
def get_db_connection():
    """Get PostgreSQL connection from Railway"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

# Request/Response models
class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    price: float

class PortfolioResponse(BaseModel):
    cash_balance: float
    positions: Dict[str, Dict]
    total_value: float
    realized_pnl: float

# Helper: Get default portfolio
def get_default_portfolio():
    """Get or create the default paper portfolio"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get default user
        cur.execute("SELECT id FROM users WHERE email = 'default@finsight.ai' LIMIT 1")
        user = cur.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Default user not found")
        user_id = user['id']
        
        # Get paper portfolio
        cur.execute("""
            SELECT id, current_cash, total_value
            FROM portfolios
            WHERE user_id = %s AND portfolio_type = 'paper'
            LIMIT 1
        """, (user_id,))
        
        portfolio = cur.fetchone()
        if not portfolio:
            raise HTTPException(status_code=404, detail="Paper portfolio not found")
        
        return dict(portfolio), conn, cur
        
    except Exception as e:
        conn.close()
        raise e

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    """Get current paper portfolio"""
    try:
        portfolio, conn, cur = get_default_portfolio()
        portfolio_id = portfolio['id']
        
        # Get positions
        cur.execute("""
            SELECT symbol, quantity, average_cost as avg_price, 
                   current_price, market_value, unrealized_pnl
            FROM positions
            WHERE portfolio_id = %s
        """, (portfolio_id,))
        
        positions = {}
        total_position_value = Decimal('0')
        
        for pos in cur.fetchall():
            symbol = pos['symbol']
            positions[symbol] = {
                'quantity': float(pos['quantity']),
                'avg_price': float(pos['avg_price']),
                'current_price': float(pos['current_price']),
                'market_value': float(pos['market_value']),
                'unrealized_pnl': float(pos['unrealized_pnl'])
            }
            total_position_value += Decimal(str(pos['market_value']))
        
        cash_balance = float(portfolio['current_cash'])
        total_value = cash_balance + float(total_position_value)
        
        # Calculate realized P&L from transactions
        cur.execute("""
            SELECT COALESCE(SUM(
                CASE 
                    WHEN transaction_type = 'sell' THEN total_amount
                    WHEN transaction_type = 'buy' THEN -total_amount
                END
            ), 0) as realized_pnl
            FROM transactions
            WHERE portfolio_id = %s
        """, (portfolio_id,))
        
        realized_pnl = float(cur.fetchone()['realized_pnl'])
        
        cur.close()
        conn.close()
        
        return PortfolioResponse(
            cash_balance=cash_balance,
            positions=positions,
            total_value=total_value,
            realized_pnl=realized_pnl
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/buy")
async def buy_stock(trade: TradeRequest):
    """Execute a paper buy trade"""
    try:
        portfolio, conn, cur = get_default_portfolio()
        portfolio_id = portfolio['id']
        cash_balance = Decimal(str(portfolio['current_cash']))
        
        # Calculate cost
        cost = Decimal(str(trade.quantity)) * Decimal(str(trade.price))
        
        # Check sufficient funds
        if cost > cash_balance:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Check if position exists
        cur.execute("""
            SELECT id, quantity, average_cost
            FROM positions
            WHERE portfolio_id = %s AND symbol = %s
        """, (portfolio_id, trade.symbol))
        
        existing_position = cur.fetchone()
        
        if existing_position:
            # Update existing position
            old_qty = Decimal(str(existing_position['quantity']))
            old_avg = Decimal(str(existing_position['average_cost']))
            new_qty = old_qty + Decimal(str(trade.quantity))
            new_avg = ((old_qty * old_avg) + cost) / new_qty
            new_market_value = new_qty * Decimal(str(trade.price))
            
            cur.execute("""
                UPDATE positions
                SET quantity = %s,
                    average_cost = %s,
                    current_price = %s,
                    market_value = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (
                float(new_qty),
                float(new_avg),
                trade.price,
                float(new_market_value),
                existing_position['id']
            ))
        else:
            # Create new position
            market_value = cost
            cur.execute("""
                INSERT INTO positions (
                    portfolio_id, symbol, quantity,
                    average_cost, current_price, market_value
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                portfolio_id,
                trade.symbol,
                trade.quantity,
                trade.price,
                trade.price,
                float(market_value)
            ))
        
        # Record transaction
        cur.execute("""
            INSERT INTO transactions (
                portfolio_id, transaction_type, symbol,
                quantity, price, total_amount
            )
            VALUES (%s, 'buy', %s, %s, %s, %s)
        """, (portfolio_id, trade.symbol, trade.quantity, trade.price, float(cost)))
        
        # Update portfolio cash
        new_cash = cash_balance - cost
        cur.execute("""
            UPDATE portfolios
            SET current_cash = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (float(new_cash), portfolio_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Bought {trade.quantity} shares of {trade.symbol} at ${trade.price}",
            "cost": float(cost),
            "new_cash_balance": float(new_cash)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade/sell")
async def sell_stock(trade: TradeRequest):
    """Execute a paper sell trade"""
    try:
        portfolio, conn, cur = get_default_portfolio()
        portfolio_id = portfolio['id']
        cash_balance = Decimal(str(portfolio['current_cash']))
        
        # Check position exists
        cur.execute("""
            SELECT id, quantity, average_cost
            FROM positions
            WHERE portfolio_id = %s AND symbol = %s
        """, (portfolio_id, trade.symbol))
        
        position = cur.fetchone()
        if not position:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"No position in {trade.symbol}")
        
        current_qty = Decimal(str(position['quantity']))
        if Decimal(str(trade.quantity)) > current_qty:
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Insufficient shares")
        
        # Calculate proceeds
        proceeds = Decimal(str(trade.quantity)) * Decimal(str(trade.price))
        
        # Update or delete position
        new_qty = current_qty - Decimal(str(trade.quantity))
        if new_qty > 0:
            new_market_value = new_qty * Decimal(str(trade.price))
            cur.execute("""
                UPDATE positions
                SET quantity = %s,
                    current_price = %s,
                    market_value = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (float(new_qty), trade.price, float(new_market_value), position['id']))
        else:
            cur.execute("DELETE FROM positions WHERE id = %s", (position['id'],))
        
        # Record transaction
        cur.execute("""
            INSERT INTO transactions (
                portfolio_id, transaction_type, symbol,
                quantity, price, total_amount
            )
            VALUES (%s, 'sell', %s, %s, %s, %s)
        """, (portfolio_id, trade.symbol, trade.quantity, trade.price, float(proceeds)))
        
        # Update portfolio cash
        new_cash = cash_balance + proceeds
        cur.execute("""
            UPDATE portfolios
            SET current_cash = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (float(new_cash), portfolio_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Sold {trade.quantity} shares of {trade.symbol} at ${trade.price}",
            "proceeds": float(proceeds),
            "new_cash_balance": float(new_cash)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_portfolio():
    """Reset paper portfolio to $10,000"""
    try:
        portfolio, conn, cur = get_default_portfolio()
        portfolio_id = portfolio['id']
        
        # Delete all positions
        cur.execute("DELETE FROM positions WHERE portfolio_id = %s", (portfolio_id,))
        
        # Delete all transactions
        cur.execute("DELETE FROM transactions WHERE portfolio_id = %s", (portfolio_id,))
        
        # Reset cash
        cur.execute("""
            UPDATE portfolios
            SET current_cash = 10000.00,
                total_value = 10000.00,
                updated_at = NOW()
            WHERE id = %s
        """, (portfolio_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Portfolio reset to $10,000"
        }
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
