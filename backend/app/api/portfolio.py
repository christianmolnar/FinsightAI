from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Portfolio, Position, Trade
from app.services.alpaca_service import get_alpaca_service
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


class PositionResponse(BaseModel):
    symbol: str
    shares: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float


class PerformanceResponse(BaseModel):
    daily_pnl: float
    daily_pnl_percent: float
    total_pnl: float
    total_pnl_percent: float


class PortfolioResponse(BaseModel):
    total_value: float
    cash_balance: float
    invested_value: float
    positions: List[PositionResponse]
    performance: PerformanceResponse


class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    total_amount: float
    status: str
    strategy: Optional[str]
    confidence_score: Optional[float]
    executed_at: Optional[datetime]
    created_at: datetime


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(db: Session = Depends(get_db)):
    """Get current portfolio status"""
    
    # Get or create default portfolio
    portfolio = db.query(Portfolio).first()
    if not portfolio:
        # Create default portfolio if none exists
        portfolio = Portfolio(
            total_value=100000.00,
            cash_balance=50000.00,
            invested_value=50000.00,
            total_pnl=0.0,
            daily_pnl=0.0
        )
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
    
    # Get positions
    positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
    
    position_responses = []
    for pos in positions:
        position_responses.append(PositionResponse(
            symbol=pos.symbol,
            shares=float(pos.shares),
            avg_cost=float(pos.avg_cost),
            current_price=float(pos.current_price),
            market_value=float(pos.market_value),
            unrealized_pnl=float(pos.unrealized_pnl)
        ))
    
    # Calculate performance percentages
    total_value = float(portfolio.total_value)
    daily_pnl_percent = (float(portfolio.daily_pnl) / total_value * 100) if total_value > 0 else 0
    total_pnl_percent = (float(portfolio.total_pnl) / total_value * 100) if total_value > 0 else 0
    
    performance = PerformanceResponse(
        daily_pnl=float(portfolio.daily_pnl),
        daily_pnl_percent=daily_pnl_percent,
        total_pnl=float(portfolio.total_pnl),
        total_pnl_percent=total_pnl_percent
    )
    
    return PortfolioResponse(
        total_value=total_value,
        cash_balance=float(portfolio.cash_balance),
        invested_value=float(portfolio.invested_value),
        positions=position_responses,
        performance=performance
    )


@router.get("/portfolios")
async def list_portfolios(db: Session = Depends(get_db)):
    """List all portfolios"""
    try:
        # Use raw SQL since the Portfolio model may not match schema
        result = db.execute(text("""
            SELECT 
                id, 
                name, 
                portfolio_type,
                total_value,
                current_cash
            FROM portfolios
            ORDER BY created_at DESC
        """))
        
        portfolios = []
        for row in result:
            portfolios.append({
                "id": str(row[0]),
                "name": row[1],
                "portfolio_type": row[2],
                "total_value": float(row[3]) if row[3] else 0.0,
                "cash_balance": float(row[4]) if row[4] else 0.0
            })
        
        return portfolios
    except Exception as e:
        logger.error(f"Error listing portfolios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent trading activity"""
    
    trades = db.query(Trade).order_by(Trade.created_at.desc()).limit(limit).all()
    
    trade_responses = []
    for trade in trades:
        trade_responses.append(TradeResponse(
            id=trade.id,
            symbol=trade.symbol,
            side=trade.side.value,
            quantity=float(trade.quantity),
            price=float(trade.price),
            total_amount=float(trade.total_amount),
            status=trade.status.value,
            strategy=trade.strategy.value if trade.strategy else None,
            confidence_score=trade.confidence_score,
            executed_at=trade.executed_at,
            created_at=trade.created_at
        ))
    
    return trade_responses


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(db: Session = Depends(get_db)):
    """Get all current positions"""
    
    positions = db.query(Position).all()
    
    position_responses = []
    for pos in positions:
        position_responses.append(PositionResponse(
            symbol=pos.symbol,
            shares=float(pos.shares),
            avg_cost=float(pos.avg_cost),
            current_price=float(pos.current_price),
            market_value=float(pos.market_value),
            unrealized_pnl=float(pos.unrealized_pnl)
        ))
    
    return position_responses


@router.get("/positions/{symbol}", response_model=PositionResponse)
async def get_position(symbol: str, db: Session = Depends(get_db)):
    """Get position for specific symbol"""
    
    position = db.query(Position).filter(Position.symbol == symbol.upper()).first()
    
    if not position:
        raise HTTPException(status_code=404, detail=f"Position not found for symbol {symbol}")
    
    return PositionResponse(
        symbol=position.symbol,
        shares=float(position.shares),
        avg_cost=float(position.avg_cost),
        current_price=float(position.current_price),
        market_value=float(position.market_value),
        unrealized_pnl=float(position.unrealized_pnl)
    )


# =============================================================================
# ALPACA ACCOUNT INTEGRATION - Real Portfolio Data
# =============================================================================

@router.get("/alpaca/paper/account")
async def get_alpaca_paper_account():
    """Get Alpaca paper trading account information"""
    try:
        alpaca = get_alpaca_service(paper=True)
        account = alpaca.get_account()
        
        return {
            "success": True,
            "account": account
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca paper account: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/live/account")
async def get_alpaca_live_account():
    """Get Alpaca live trading account information"""
    try:
        alpaca = get_alpaca_service(paper=False)
        account = alpaca.get_account()
        
        return {
            "success": True,
            "account": account
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca live account: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/account")
async def get_alpaca_account():
    """Get Alpaca account information (defaults to paper for backwards compatibility)"""
    try:
        alpaca = get_alpaca_service(paper=True)
        account = alpaca.get_account()
        
        return {
            "success": True,
            "account": account
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca account: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/paper/positions")
async def get_alpaca_paper_positions():
    """Get all Alpaca paper trading positions"""
    try:
        alpaca = get_alpaca_service(paper=True)
        positions = alpaca.get_positions()
        
        # Calculate totals
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        
        return {
            "success": True,
            "positions": positions,
            "position_count": len(positions),
            "total_market_value": total_market_value,
            "total_unrealized_pl": total_pl,
            "total_unrealized_pl_percent": (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca paper positions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/live/positions")
async def get_alpaca_live_positions():
    """Get all Alpaca live trading positions"""
    try:
        alpaca = get_alpaca_service(paper=False)
        positions = alpaca.get_positions()
        
        # Calculate totals
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        
        return {
            "success": True,
            "positions": positions,
            "position_count": len(positions),
            "total_market_value": total_market_value,
            "total_unrealized_pl": total_pl,
            "total_unrealized_pl_percent": (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca live positions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/positions")
async def get_alpaca_positions():
    """Get all Alpaca positions (defaults to paper for backwards compatibility)"""
    try:
        alpaca = get_alpaca_service(paper=True)
        positions = alpaca.get_positions()
        
        # Calculate totals
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        
        return {
            "success": True,
            "positions": positions,
            "position_count": len(positions),
            "total_market_value": total_market_value,
            "total_unrealized_pl": total_pl,
            "total_unrealized_pl_percent": (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca positions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/positions/{symbol}")
async def get_alpaca_position(symbol: str):
    """Get position for a specific symbol"""
    try:
        alpaca = get_alpaca_service()
        position = alpaca.get_position(symbol.upper())
        
        if not position:
            raise HTTPException(status_code=404, detail=f"Position not found for symbol {symbol}")
        
        return {
            "success": True,
            "position": position
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching position for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/paper/portfolio")
async def get_alpaca_paper_portfolio():
    """Get complete Alpaca paper trading portfolio overview"""
    try:
        alpaca = get_alpaca_service(paper=True)
        
        # Get account info
        account = alpaca.get_account()
        
        # Get all positions
        positions = alpaca.get_positions()
        
        # Calculate metrics
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        total_pl_percent = (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        
        return {
            "success": True,
            "account": {
                "id": account["id"],
                "status": account["status"],
                "cash": account["cash"],
                "portfolio_value": account["portfolio_value"],
                "buying_power": account["buying_power"],
                "equity": account["equity"],
                "pattern_day_trader": account["pattern_day_trader"]
            },
            "positions": positions,
            "metrics": {
                "position_count": len(positions),
                "total_market_value": total_market_value,
                "total_unrealized_pl": total_pl,
                "total_unrealized_pl_percent": total_pl_percent,
                "cash_balance": account["cash"],
                "total_portfolio_value": account["portfolio_value"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca paper portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/live/portfolio")
async def get_alpaca_live_portfolio():
    """Get complete Alpaca live trading portfolio overview"""
    try:
        alpaca = get_alpaca_service(paper=False)
        
        # Get account info
        account = alpaca.get_account()
        
        # Get all positions
        positions = alpaca.get_positions()
        
        # Calculate metrics
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        total_pl_percent = (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        
        return {
            "success": True,
            "account": {
                "id": account["id"],
                "status": account["status"],
                "cash": account["cash"],
                "portfolio_value": account["portfolio_value"],
                "buying_power": account["buying_power"],
                "equity": account["equity"],
                "pattern_day_trader": account["pattern_day_trader"]
            },
            "positions": positions,
            "metrics": {
                "position_count": len(positions),
                "total_market_value": total_market_value,
                "total_unrealized_pl": total_pl,
                "total_unrealized_pl_percent": total_pl_percent,
                "cash_balance": account["cash"],
                "total_portfolio_value": account["portfolio_value"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca live portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/paper/orders")
async def get_alpaca_paper_orders():
    """Get pending orders from Alpaca paper trading account"""
    try:
        alpaca = get_alpaca_service(paper=True)
        orders = alpaca.get_orders(status="open")
        
        return {
            "success": True,
            "orders": orders
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca paper orders: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/live/orders")
async def get_alpaca_live_orders():
    """Get pending orders from Alpaca live trading account"""
    try:
        alpaca = get_alpaca_service(paper=False)
        orders = alpaca.get_orders(status="open")
        
        return {
            "success": True,
            "orders": orders
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca live orders: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/alpaca/portfolio")
async def get_alpaca_portfolio():
    """Get complete Alpaca portfolio overview (defaults to paper for backwards compatibility)"""
    try:
        alpaca = get_alpaca_service(paper=True)
        
        # Get account info
        account = alpaca.get_account()
        
        # Get all positions
        positions = alpaca.get_positions()
        
        # Calculate metrics
        total_market_value = sum(pos["market_value"] for pos in positions)
        total_pl = sum(pos["unrealized_pl"] for pos in positions)
        total_pl_percent = (total_pl / total_market_value * 100) if total_market_value > 0 else 0
        
        return {
            "success": True,
            "account": {
                "id": account["id"],
                "status": account["status"],
                "cash": account["cash"],
                "portfolio_value": account["portfolio_value"],
                "buying_power": account["buying_power"],
                "equity": account["equity"],
                "pattern_day_trader": account["pattern_day_trader"]
            },
            "positions": positions,
            "metrics": {
                "position_count": len(positions),
                "total_market_value": total_market_value,
                "total_unrealized_pl": total_pl,
                "total_unrealized_pl_percent": total_pl_percent,
                "cash_balance": account["cash"],
                "total_portfolio_value": account["portfolio_value"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching Alpaca portfolio: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Trade execution request model
class TradeRequest(BaseModel):
    symbol: str
    quantity: int
    side: str  # "buy" or "sell"
    type: str = "market"  # "market" or "limit"
    limit_price: Optional[float] = None


@router.post("/alpaca/paper/trade")
async def execute_paper_trade(trade: TradeRequest):
    """Execute a trade on Alpaca paper trading account"""
    try:
        alpaca = get_alpaca_service(paper=True)
        
        # Validate inputs
        if trade.side.lower() not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Side must be 'buy' or 'sell'")
        
        if trade.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        # Execute trade
        if trade.type.lower() == "market":
            order = alpaca.place_market_order(
                symbol=trade.symbol.upper(),
                qty=trade.quantity,
                side=trade.side.lower()
            )
        elif trade.type.lower() == "limit":
            if not trade.limit_price:
                raise HTTPException(status_code=400, detail="Limit price required for limit orders")
            order = alpaca.place_limit_order(
                symbol=trade.symbol.upper(),
                qty=trade.quantity,
                side=trade.side.lower(),
                limit_price=trade.limit_price
            )
        else:
            raise HTTPException(status_code=400, detail="Order type must be 'market' or 'limit'")
        
        return {
            "success": True,
            "order": {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "side": order["side"],
                "type": order["type"],
                "status": order["status"],
                "filled_qty": order.get("filled_qty", 0),
                "filled_avg_price": order.get("filled_avg_price"),
                "submitted_at": order.get("submitted_at"),
                "filled_at": order.get("filled_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing paper trade: {e}")
        raise HTTPException(status_code=500, detail=f"Trade execution failed: {str(e)}")


@router.post("/alpaca/live/trade")
async def execute_live_trade(trade: TradeRequest):
    """Execute a trade on Alpaca LIVE trading account"""
    try:
        alpaca = get_alpaca_service(paper=False)
        
        # Validate inputs
        if trade.side.lower() not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Side must be 'buy' or 'sell'")
        
        if trade.quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        # Execute trade
        if trade.type.lower() == "market":
            order = alpaca.place_market_order(
                symbol=trade.symbol.upper(),
                qty=trade.quantity,
                side=trade.side.lower()
            )
        elif trade.type.lower() == "limit":
            if not trade.limit_price:
                raise HTTPException(status_code=400, detail="Limit price required for limit orders")
            order = alpaca.place_limit_order(
                symbol=trade.symbol.upper(),
                qty=trade.quantity,
                side=trade.side.lower(),
                limit_price=trade.limit_price
            )
        else:
            raise HTTPException(status_code=400, detail="Order type must be 'market' or 'limit'")
        
        return {
            "success": True,
            "order": {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "side": order["side"],
                "type": order["type"],
                "status": order["status"],
                "filled_qty": order.get("filled_qty", 0),
                "filled_avg_price": order.get("filled_avg_price"),
                "submitted_at": order.get("submitted_at"),
                "filled_at": order.get("filled_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing live trade: {e}")
        raise HTTPException(status_code=500, detail=f"Trade execution failed: {str(e)}")
