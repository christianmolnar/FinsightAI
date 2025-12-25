"""
Market data API endpoints for the trading platform
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import MarketData, TradingSignal
from app.services.alpaca_service import get_alpaca_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/test-connection")
async def test_alpaca_connection():
    """Test the Alpaca API connection"""
    try:
        alpaca = get_alpaca_service()
        account = alpaca.get_account()
        
        return {
            "status": "success",
            "message": "Successfully connected to Alpaca API",
            "account_id": account["id"],
            "portfolio_value": account["portfolio_value"],
            "connection_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Alpaca API connection failed: {str(e)}")


@router.get("/quotes/{symbols}")
async def get_real_time_quotes(symbols: str):
    """Get real-time quotes for given symbols (comma-separated)"""
    try:
        alpaca = get_alpaca_service()
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        if len(symbol_list) == 1:
            quote = alpaca.get_quote(symbol_list[0])
            quotes = {symbol_list[0]: quote}
        else:
            quotes = alpaca.get_quotes(symbol_list)
        
        return {
            "status": "success",
            "symbols": symbol_list,
            "quotes": quotes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quotes: {str(e)}")


# Historical data and streaming endpoints - TODO: Implement with Alpaca
# These require Alpaca's historical data API which works differently

# @router.get("/history/{symbol}")
# async def get_market_history(...):
#     """Get historical market data for a symbol"""
#     # TODO: Implement with Alpaca StockHistoricalDataClient

# @router.post("/stream/start")
# async def start_market_stream(...):
#     """Start real-time market data streaming"""
#     # TODO: Implement with Alpaca WebSocket streaming

# @router.post("/stream/stop")
# async def stop_market_stream():
#     """Stop real-time market data streaming"""
#     # TODO: Implement with Alpaca WebSocket


# Database-dependent endpoints - TODO: Fix models or remove
# @router.get("/data/recent/{symbol}")
# @router.get("/signals/recent")
