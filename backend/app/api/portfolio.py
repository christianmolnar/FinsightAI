from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Portfolio, Position, Trade
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

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
