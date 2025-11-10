"""
Market data API endpoints for the trading platform
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.models import MarketData, TradingSignal
from app.schwab_api import schwab_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/test-connection")
async def test_schwab_connection():
    """Test the Schwab API connection"""
    try:
        if not schwab_service:
            return {
                "status": "unavailable",
                "message": "Schwab API service not initialized. Please configure APP_KEY and APP_SECRET in .env file.",
                "connection_time": datetime.utcnow().isoformat()
            }
        
        if not schwab_service.initialize_client():
            raise HTTPException(status_code=503, detail="Failed to initialize Schwab API client")
        
        accounts = schwab_service.get_account_info()
        if not accounts:
            raise HTTPException(status_code=503, detail="Failed to connect to Schwab API")
        
        return {
            "status": "success",
            "message": "Successfully connected to Schwab API",
            "accounts_found": len(accounts),
            "connection_time": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Schwab API connection failed: {str(e)}")


@router.get("/quotes/{symbols}")
async def get_real_time_quotes(symbols: str):
    """Get real-time quotes for given symbols (comma-separated)"""
    try:
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(status_code=503, detail="Schwab API not available")
        
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        quotes = schwab_service.get_real_time_quotes(symbol_list)
        
        if not quotes:
            raise HTTPException(status_code=404, detail="Failed to get quotes")
        
        return {
            "status": "success",
            "symbols": symbol_list,
            "quotes": quotes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting quotes: {str(e)}")


@router.get("/history/{symbol}")
async def get_market_history(
    symbol: str,
    period_type: str = "day",
    period: int = 1,
    db: Session = Depends(get_db)
):
    """Get historical market data for a symbol"""
    try:
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(status_code=503, detail="Schwab API not available")
        
        # Get data from Schwab API
        historical_data = schwab_service.get_market_data_history(
            symbol=symbol.upper(),
            period_type=period_type,
            period=period
        )
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="Failed to get historical data")
        
        # Also get any stored data from our database
        stored_data = db.query(MarketData).filter(
            MarketData.symbol == symbol.upper()
        ).order_by(MarketData.timestamp.desc()).limit(100).all()
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "historical_data": historical_data,
            "stored_data": [
                {
                    "timestamp": data.timestamp.isoformat(),
                    "price": float(data.price),
                    "volume": data.volume,
                    "open": float(data.open_price),
                    "high": float(data.high_price),
                    "low": float(data.low_price),
                    "close": float(data.close_price)
                } for data in stored_data
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting historical data: {str(e)}")


@router.post("/stream/start")
async def start_market_stream(
    symbols: List[str],
    background_tasks: BackgroundTasks
):
    """Start real-time market data streaming"""
    try:
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(status_code=503, detail="Schwab API not available")
        
        # Convert symbols to uppercase
        symbols = [s.upper() for s in symbols]
        
        # Start streaming in background
        def stream_handler(message):
            """Custom handler that saves data to database"""
            try:
                schwab_service.save_market_data_to_db(message)
            except Exception as e:
                print(f"Error saving stream data: {e}")
        
        success = schwab_service.start_real_time_stream(symbols, stream_handler)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start streaming")
        
        return {
            "status": "success",
            "message": f"Started real-time streaming for {len(symbols)} symbols",
            "symbols": symbols,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting stream: {str(e)}")


@router.post("/stream/stop")
async def stop_market_stream():
    """Stop real-time market data streaming"""
    try:
        schwab_service.stop_stream()
        return {
            "status": "success",
            "message": "Stopped market data streaming",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping stream: {str(e)}")


@router.get("/data/recent/{symbol}")
async def get_recent_market_data(
    symbol: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get recent market data from our database for a specific symbol"""
    try:
        since_time = datetime.utcnow() - timedelta(hours=hours)
        
        data = db.query(MarketData).filter(
            MarketData.symbol == symbol.upper(),
            MarketData.timestamp >= since_time
        ).order_by(MarketData.timestamp.desc()).all()
        
        return {
            "status": "success",
            "symbol": symbol.upper(),
            "hours": hours,
            "count": len(data),
            "data": [
                {
                    "id": d.id,
                    "timestamp": d.timestamp.isoformat(),
                    "price": float(d.price),
                    "volume": d.volume,
                    "open": float(d.open_price),
                    "high": float(d.high_price),
                    "low": float(d.low_price),
                    "close": float(d.close_price)
                } for d in data
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recent data: {str(e)}")


@router.get("/accounts")
async def get_schwab_accounts():
    """Get linked Schwab account information"""
    try:
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(status_code=503, detail="Schwab API not available")
        
        accounts = schwab_service.get_account_info()
        if not accounts:
            raise HTTPException(status_code=404, detail="No accounts found")
        
        return {
            "status": "success",
            "accounts": accounts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting accounts: {str(e)}")


@router.get("/signals/recent")
async def get_recent_signals(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent trading signals from the database"""
    try:
        signals = db.query(TradingSignal).order_by(
            TradingSignal.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "status": "success",
            "count": len(signals),
            "signals": [
                {
                    "id": s.id,
                    "symbol": s.symbol,
                    "signal_type": s.signal_type,
                    "strength": float(s.strength),
                    "price": float(s.price),
                    "timestamp": s.timestamp.isoformat(),
                    "metadata": s.metadata
                } for s in signals
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting signals: {str(e)}")
