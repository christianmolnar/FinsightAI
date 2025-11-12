from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
import uuid
import yfinance as yf

from database import get_db, User, Portfolio, Position, Transaction, TradeFactor, MarketDataCache

router = APIRouter()

# Pydantic models for API
class PaperTradeRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol to trade")
    action: str = Field(..., description="BUY or SELL")
    quantity: int = Field(..., gt=0, description="Number of shares")
    strategy_used: Optional[str] = Field(None, description="Strategy that triggered this trade")
    ai_confidence: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    target_price: Optional[float] = Field(None, description="Target sell price")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    ai_factors: Optional[Dict[str, Any]] = Field(None, description="Factors that influenced the decision")

class PositionResponse(BaseModel):
    id: str
    symbol: str
    quantity: float
    average_cost: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    purchase_date: datetime
    strategy_used: Optional[str]
    ai_confidence: Optional[float]
    target_price: Optional[float]
    stop_loss: Optional[float]
    days_held: int

class TransactionResponse(BaseModel):
    id: str
    symbol: str
    transaction_type: str
    quantity: float
    price: float
    total_amount: float
    commission: float
    net_amount: float
    strategy_used: Optional[str]
    ai_confidence: Optional[float]
    executed_at: datetime

class PortfolioResponse(BaseModel):
    id: str
    name: str
    portfolio_type: str
    starting_cash: float
    current_cash: float
    total_value: float
    total_return: float
    total_return_percent: float
    positions_value: float
    positions: List[PositionResponse]

class PaperPortfolioService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        try:
            # Try to get from cache first (within last 5 minutes)
            recent_data = self.db.query(MarketDataCache).filter(
                MarketDataCache.symbol == symbol,
                MarketDataCache.timestamp >= datetime.now(timezone.utc).timestamp() - 300  # 5 minutes
            ).first()
            
            if recent_data:
                return float(recent_data.price)
            
            # Fetch fresh data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.history(period="1d", interval="1m")
            
            if info.empty:
                raise ValueError(f"No price data available for {symbol}")
            
            current_price = float(info['Close'].iloc[-1])
            
            # Cache the data
            market_data = MarketDataCache(
                symbol=symbol,
                price=Decimal(str(current_price)),
                volume=int(info['Volume'].iloc[-1]) if not info['Volume'].empty else 0,
                high=Decimal(str(info['High'].iloc[-1])),
                low=Decimal(str(info['Low'].iloc[-1])),
                open=Decimal(str(info['Open'].iloc[-1])),
                timestamp=datetime.now(timezone.utc),
                source="yahoo"
            )
            self.db.add(market_data)
            self.db.commit()
            
            return current_price
            
        except Exception as e:
            # Fallback to a mock price if API fails
            print(f"Error fetching price for {symbol}: {e}")
            return 100.0  # Mock price
    
    def get_paper_portfolio(self, user_id: str = "550e8400-e29b-41d4-a716-446655440000") -> PortfolioResponse:
        """Get the paper portfolio with all positions"""
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.portfolio_type == "paper"
        ).first()
        
        if not portfolio:
            # Create default paper portfolio
            portfolio = Portfolio(
                user_id=user_id,
                portfolio_type="paper",
                name="Paper Trading Portfolio",
                starting_cash=Decimal("10000.00"),
                current_cash=Decimal("10000.00"),
                total_value=Decimal("10000.00")
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
        
        # Get all open positions
        positions = self.db.query(Position).filter(
            Position.portfolio_id == portfolio.id,
            Position.is_open == True
        ).all()
        
        # Update current prices and calculate values
        positions_value = Decimal("0.00")
        position_responses = []
        
        for position in positions:
            current_price = self.get_current_price(position.symbol)
            market_value = Decimal(str(current_price)) * position.quantity
            unrealized_pnl = market_value - position.cost_basis
            unrealized_pnl_percent = (unrealized_pnl / position.cost_basis) * 100 if position.cost_basis > 0 else 0
            
            # Update position in database
            position.current_price = Decimal(str(current_price))
            position.market_value = market_value
            position.unrealized_pnl = unrealized_pnl
            position.unrealized_pnl_percent = unrealized_pnl_percent
            position.days_held = (datetime.now(timezone.utc) - position.purchase_date).days
            
            positions_value += market_value
            
            position_responses.append(PositionResponse(
                id=str(position.id),
                symbol=position.symbol,
                quantity=float(position.quantity),
                average_cost=float(position.average_cost),
                current_price=float(position.current_price),
                market_value=float(position.market_value),
                cost_basis=float(position.cost_basis),
                unrealized_pnl=float(position.unrealized_pnl),
                unrealized_pnl_percent=float(position.unrealized_pnl_percent),
                purchase_date=position.purchase_date,
                strategy_used=position.strategy_used,
                ai_confidence=float(position.ai_confidence) if position.ai_confidence else None,
                target_price=float(position.target_price) if position.target_price else None,
                stop_loss=float(position.stop_loss) if position.stop_loss else None,
                days_held=position.days_held
            ))
        
        # Update portfolio totals
        portfolio.total_value = portfolio.current_cash + positions_value
        portfolio.total_return = portfolio.total_value - portfolio.starting_cash
        portfolio.total_return_percent = (portfolio.total_return / portfolio.starting_cash) * 100
        
        self.db.commit()
        
        return PortfolioResponse(
            id=str(portfolio.id),
            name=portfolio.name,
            portfolio_type=portfolio.portfolio_type,
            starting_cash=float(portfolio.starting_cash),
            current_cash=float(portfolio.current_cash),
            total_value=float(portfolio.total_value),
            total_return=float(portfolio.total_return),
            total_return_percent=float(portfolio.total_return_percent),
            positions_value=float(positions_value),
            positions=position_responses
        )
    
    def execute_paper_trade(self, trade_request: PaperTradeRequest, user_id: str = "550e8400-e29b-41d4-a716-446655440000") -> TransactionResponse:
        """Execute a paper trade"""
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id,
            Portfolio.portfolio_type == "paper"
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Paper portfolio not found")
        
        # Get current market price
        current_price = self.get_current_price(trade_request.symbol)
        commission = Decimal("1.00")  # $1 per trade
        
        if trade_request.action.upper() == "BUY":
            total_cost = Decimal(str(current_price)) * trade_request.quantity + commission
            
            if portfolio.current_cash < total_cost:
                raise HTTPException(status_code=400, detail="Insufficient cash for purchase")
            
            # Check if position exists
            existing_position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio.id,
                Position.symbol == trade_request.symbol,
                Position.is_open == True
            ).first()
            
            if existing_position:
                # Add to existing position
                total_cost_basis = existing_position.cost_basis + (Decimal(str(current_price)) * trade_request.quantity)
                total_quantity = existing_position.quantity + trade_request.quantity
                new_average_cost = total_cost_basis / total_quantity
                
                existing_position.quantity = total_quantity
                existing_position.average_cost = new_average_cost
                existing_position.cost_basis = total_cost_basis
                existing_position.current_price = Decimal(str(current_price))
                existing_position.market_value = Decimal(str(current_price)) * total_quantity
            else:
                # Create new position
                new_position = Position(
                    portfolio_id=portfolio.id,
                    symbol=trade_request.symbol,
                    quantity=trade_request.quantity,
                    average_cost=Decimal(str(current_price)),
                    current_price=Decimal(str(current_price)),
                    cost_basis=Decimal(str(current_price)) * trade_request.quantity,
                    market_value=Decimal(str(current_price)) * trade_request.quantity,
                    purchase_date=datetime.now(timezone.utc),
                    strategy_used=trade_request.strategy_used,
                    ai_confidence=Decimal(str(trade_request.ai_confidence)) if trade_request.ai_confidence else None,
                    target_price=Decimal(str(trade_request.target_price)) if trade_request.target_price else None,
                    stop_loss=Decimal(str(trade_request.stop_loss)) if trade_request.stop_loss else None
                )
                self.db.add(new_position)
            
            # Update portfolio cash
            portfolio.current_cash -= total_cost
            
        elif trade_request.action.upper() == "SELL":
            # Find position to sell
            position = self.db.query(Position).filter(
                Position.portfolio_id == portfolio.id,
                Position.symbol == trade_request.symbol,
                Position.is_open == True
            ).first()
            
            if not position:
                raise HTTPException(status_code=404, detail="Position not found")
            
            if position.quantity < trade_request.quantity:
                raise HTTPException(status_code=400, detail="Insufficient shares to sell")
            
            total_proceeds = (Decimal(str(current_price)) * trade_request.quantity) - commission
            
            if position.quantity == trade_request.quantity:
                # Sell entire position
                position.is_open = False
            else:
                # Partial sell
                position.quantity -= trade_request.quantity
                position.cost_basis = position.average_cost * position.quantity
                position.market_value = position.current_price * position.quantity
            
            # Update portfolio cash
            portfolio.current_cash += total_proceeds
        
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Must be BUY or SELL")
        
        # Create transaction record
        transaction = Transaction(
            portfolio_id=portfolio.id,
            symbol=trade_request.symbol,
            transaction_type=trade_request.action.upper(),
            quantity=trade_request.quantity,
            price=Decimal(str(current_price)),
            total_amount=Decimal(str(current_price)) * trade_request.quantity,
            commission=commission,
            net_amount=Decimal(str(current_price)) * trade_request.quantity + (commission if trade_request.action.upper() == "BUY" else -commission),
            strategy_used=trade_request.strategy_used,
            ai_confidence=Decimal(str(trade_request.ai_confidence)) if trade_request.ai_confidence else None,
            ai_factors=trade_request.ai_factors,
            executed_at=datetime.now(timezone.utc)
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return TransactionResponse(
            id=str(transaction.id),
            symbol=transaction.symbol,
            transaction_type=transaction.transaction_type,
            quantity=float(transaction.quantity),
            price=float(transaction.price),
            total_amount=float(transaction.total_amount),
            commission=float(transaction.commission),
            net_amount=float(transaction.net_amount),
            strategy_used=transaction.strategy_used,
            ai_confidence=float(transaction.ai_confidence) if transaction.ai_confidence else None,
            executed_at=transaction.executed_at
        )

# API endpoints
@router.get("/paper-portfolio", response_model=PortfolioResponse)
async def get_paper_portfolio(db: Session = Depends(get_db)):
    """Get paper portfolio with all positions"""
    service = PaperPortfolioService(db)
    return service.get_paper_portfolio()

@router.post("/paper-portfolio/trade", response_model=TransactionResponse)
async def execute_paper_trade(trade_request: PaperTradeRequest, db: Session = Depends(get_db)):
    """Execute a paper trade"""
    service = PaperPortfolioService(db)
    return service.execute_paper_trade(trade_request)

@router.get("/paper-portfolio/transactions")
async def get_paper_transactions(
    limit: int = 50, 
    offset: int = 0,
    symbol: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get transaction history for paper portfolio"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_type == "paper"
    ).first()
    
    if not portfolio:
        return []
    
    query = db.query(Transaction).filter(Transaction.portfolio_id == portfolio.id)
    
    if symbol:
        query = query.filter(Transaction.symbol == symbol)
    
    transactions = query.order_by(Transaction.executed_at.desc()).offset(offset).limit(limit).all()
    
    return [TransactionResponse(
        id=str(t.id),
        symbol=t.symbol,
        transaction_type=t.transaction_type,
        quantity=float(t.quantity),
        price=float(t.price),
        total_amount=float(t.total_amount),
        commission=float(t.commission),
        net_amount=float(t.net_amount),
        strategy_used=t.strategy_used,
        ai_confidence=float(t.ai_confidence) if t.ai_confidence else None,
        executed_at=t.executed_at
    ) for t in transactions]

@router.get("/paper-portfolio/performance")
async def get_paper_performance(db: Session = Depends(get_db)):
    """Get paper portfolio performance metrics"""
    service = PaperPortfolioService(db)
    portfolio = service.get_paper_portfolio()
    
    # Calculate additional metrics
    transactions = db.query(Transaction).join(Portfolio).filter(
        Portfolio.portfolio_type == "paper"
    ).all()
    
    total_trades = len(transactions)
    buy_trades = len([t for t in transactions if t.transaction_type == "BUY"])
    sell_trades = len([t for t in transactions if t.transaction_type == "SELL"])
    
    return {
        "portfolio_summary": portfolio,
        "performance_metrics": {
            "total_return": portfolio.total_return,
            "total_return_percent": portfolio.total_return_percent,
            "total_trades": total_trades,
            "positions_count": len(portfolio.positions),
            "cash_percent": (portfolio.current_cash / portfolio.total_value) * 100,
            "invested_percent": (portfolio.positions_value / portfolio.total_value) * 100
        }
    }

@router.delete("/paper-portfolio/reset")
async def reset_paper_portfolio(db: Session = Depends(get_db)):
    """Reset paper portfolio to $10,000 cash (development only)"""
    portfolio = db.query(Portfolio).filter(
        Portfolio.portfolio_type == "paper"
    ).first()
    
    if portfolio:
        # Close all positions
        db.query(Position).filter(Position.portfolio_id == portfolio.id).update({"is_open": False})
        
        # Reset portfolio
        portfolio.current_cash = Decimal("10000.00")
        portfolio.total_value = Decimal("10000.00")
        portfolio.total_return = Decimal("0.00")
        portfolio.total_return_percent = Decimal("0.00")
        
        db.commit()
        
        return {"message": "Paper portfolio reset to $10,000"}
    
    return {"message": "Paper portfolio not found"}
