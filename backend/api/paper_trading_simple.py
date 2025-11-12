"""
Simple Paper Trading API - No Database Required
Provides basic endpoints for paper trading functionality
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import time
import os

router = APIRouter()

# Simple in-memory storage for development
PORTFOLIOS_FILE = "paper_portfolios.json"

def load_portfolios():
    if os.path.exists(PORTFOLIOS_FILE):
        with open(PORTFOLIOS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_portfolios(portfolios):
    with open(PORTFOLIOS_FILE, 'w') as f:
        json.dump(portfolios, f, indent=2)

# Pydantic models
class TradeRequest(BaseModel):
    symbol: str
    side: str  # "buy" or "sell"
    quantity: float
    order_type: str = "market"

class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    market_value: float
    unrealized_pnl: float

class Portfolio(BaseModel):
    id: str
    name: str
    cash_balance: float
    total_value: float
    positions: List[Position]
    unrealized_pnl: float
    realized_pnl: float

# Mock price data - in production this would come from market data API
MOCK_PRICES = {
    "AAPL": 175.50,
    "MSFT": 365.80,
    "GOOGL": 142.25,
    "AMZN": 155.90,
    "TSLA": 245.30,
    "NVDA": 485.20,
    "SPY": 425.15,
    "QQQ": 385.45
}

def get_current_price(symbol: str) -> float:
    """Get current price for a symbol (mock implementation)"""
    return MOCK_PRICES.get(symbol.upper(), 100.0)  # Default to $100 if not found

@router.get("/paper/portfolio", response_model=Portfolio)
async def get_paper_portfolio():
    """Get the paper trading portfolio"""
    portfolios = load_portfolios()
    
    # Create default portfolio if it doesn't exist
    if "default" not in portfolios:
        portfolios["default"] = {
            "id": "default",
            "name": "Paper Portfolio",
            "cash_balance": 10000.0,
            "positions": {},
            "realized_pnl": 0.0
        }
        save_portfolios(portfolios)
    
    portfolio_data = portfolios["default"]
    
    # Calculate positions with current market values
    positions = []
    total_market_value = 0.0
    total_unrealized_pnl = 0.0
    
    for symbol, position_data in portfolio_data.get("positions", {}).items():
        if position_data["quantity"] > 0:
            current_price = get_current_price(symbol)
            market_value = position_data["quantity"] * current_price
            unrealized_pnl = (current_price - position_data["avg_price"]) * position_data["quantity"]
            
            positions.append(Position(
                symbol=symbol,
                quantity=position_data["quantity"],
                avg_price=position_data["avg_price"],
                market_value=market_value,
                unrealized_pnl=unrealized_pnl
            ))
            
            total_market_value += market_value
            total_unrealized_pnl += unrealized_pnl
    
    return Portfolio(
        id=portfolio_data["id"],
        name=portfolio_data["name"],
        cash_balance=portfolio_data["cash_balance"],
        total_value=portfolio_data["cash_balance"] + total_market_value,
        positions=positions,
        unrealized_pnl=total_unrealized_pnl,
        realized_pnl=portfolio_data.get("realized_pnl", 0.0)
    )

@router.post("/paper/trade")
async def execute_trade(trade: TradeRequest):
    """Execute a paper trade"""
    portfolios = load_portfolios()
    
    if "default" not in portfolios:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    portfolio = portfolios["default"]
    current_price = get_current_price(trade.symbol)
    trade_value = trade.quantity * current_price
    
    if trade.side.lower() == "buy":
        # Check if we have enough cash
        if trade_value > portfolio["cash_balance"]:
            raise HTTPException(status_code=400, detail="Insufficient cash balance")
        
        # Update cash balance
        portfolio["cash_balance"] -= trade_value
        
        # Update position
        if "positions" not in portfolio:
            portfolio["positions"] = {}
        
        if trade.symbol not in portfolio["positions"]:
            portfolio["positions"][trade.symbol] = {
                "quantity": 0.0,
                "avg_price": 0.0,
                "total_cost": 0.0
            }
        
        position = portfolio["positions"][trade.symbol]
        new_total_cost = position.get("total_cost", 0.0) + trade_value
        new_quantity = position["quantity"] + trade.quantity
        
        portfolio["positions"][trade.symbol] = {
            "quantity": new_quantity,
            "avg_price": new_total_cost / new_quantity,
            "total_cost": new_total_cost
        }
        
    elif trade.side.lower() == "sell":
        # Check if we have enough shares
        if "positions" not in portfolio or trade.symbol not in portfolio["positions"]:
            raise HTTPException(status_code=400, detail="No position to sell")
        
        position = portfolio["positions"][trade.symbol]
        if position["quantity"] < trade.quantity:
            raise HTTPException(status_code=400, detail="Insufficient shares to sell")
        
        # Calculate realized P&L
        realized_pnl = (current_price - position["avg_price"]) * trade.quantity
        portfolio["realized_pnl"] = portfolio.get("realized_pnl", 0.0) + realized_pnl
        
        # Update cash balance
        portfolio["cash_balance"] += trade_value
        
        # Update position
        position["quantity"] -= trade.quantity
        position["total_cost"] -= position["avg_price"] * trade.quantity
        
        # Remove position if quantity is zero
        if position["quantity"] <= 0:
            del portfolio["positions"][trade.symbol]
    
    else:
        raise HTTPException(status_code=400, detail="Invalid trade side. Use 'buy' or 'sell'")
    
    save_portfolios(portfolios)
    
    return {
        "message": f"Successfully {trade.side} {trade.quantity} shares of {trade.symbol} at ${current_price:.2f}",
        "trade_value": trade_value,
        "remaining_cash": portfolio["cash_balance"]
    }

@router.get("/paper/prices/{symbol}")
async def get_stock_price(symbol: str):
    """Get current price for a stock symbol"""
    price = get_current_price(symbol)
    return {
        "symbol": symbol.upper(),
        "price": price,
        "timestamp": int(time.time())
    }

@router.post("/paper/reset")
async def reset_portfolio():
    """Reset portfolio to initial state"""
    portfolios = load_portfolios()
    portfolios["default"] = {
        "id": "default",
        "name": "Paper Portfolio",
        "cash_balance": 10000.0,
        "positions": {},
        "realized_pnl": 0.0
    }
    save_portfolios(portfolios)
    
    return {"message": "Portfolio reset to $10,000 cash"}
