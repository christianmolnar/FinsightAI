from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database components from app.database
from app.database import engine, get_db, check_connection

# Create FastAPI app
app = FastAPI(
    title="FInsightAI Trading Agent",
    description="Autonomous trading agent with real-time market analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import routers
from app.api.portfolio import router as portfolio_router
from app.api.market import router as market_router
from app.api.auth import router as auth_router
from app.api.strategy_parameters import router as strategy_parameters_router
from api.research import router as research_router
# Commented out optional routers that may not exist in deployment
# from api.ai_optimizer import router as ai_optimizer_router
# from api.paper_trading_db import router as paper_trading_router

app.include_router(portfolio_router)
app.include_router(market_router)
app.include_router(auth_router)
app.include_router(strategy_parameters_router)
app.include_router(research_router)
# app.include_router(ai_optimizer_router, prefix="/api/v1/ai", tags=["AI Optimization"])
# app.include_router(paper_trading_router, prefix="/api/v1", tags=["Paper Trading"])

# Paper trading endpoints are defined directly in this file below


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting FInsightAI Trading Agent...")
    
    # Check database connection
    if check_connection():
        logger.info("✓ Database connection successful")
    else:
        logger.warning("⚠ Database connection failed - some features may not work")
    
    # Import models to register them with SQLAlchemy
    try:
        from app import models
        logger.info("✓ Models loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load models: {e}")


@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "FInsightAI Trading Agent",
        "status": "active",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {}
    }
    
    # Check database connection
    try:
        if engine:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                health_status["services"]["database"] = "connected"
        else:
            health_status["services"]["database"] = "disconnected"
            health_status["status"] = "degraded"
    except SQLAlchemyError as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["services"]["database"] = f"unknown error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Add other service checks here later
    health_status["services"]["trading_engine"] = "not_implemented"
    health_status["services"]["market_data"] = "not_implemented"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@app.get("/api/v1/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Get real-time market data for a symbol using Yahoo Finance"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.history(period="1d", interval="1m")
        
        if info.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        current_price = float(info['Close'].iloc[-1])
        open_price = float(info['Open'].iloc[0])
        high_price = float(info['High'].max())
        low_price = float(info['Low'].min())
        volume = int(info['Volume'].sum())
        
        change = current_price - open_price
        change_percent = (change / open_price) * 100 if open_price > 0 else 0
        
        return {
            "symbol": symbol.upper(),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "open": round(open_price, 2),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


# Helper function to get real stock price
def get_real_stock_price(symbol: str) -> float | None:
    """Fetch real-time stock price from Yahoo Finance with timeout"""
    try:
        import yfinance as yf
        from datetime import datetime
        import pytz
        
        # Check if market is open (basic check)
        now = datetime.now(pytz.timezone('US/Eastern'))
        if now.weekday() >= 5:  # Weekend
            return None
        if now.hour < 9 or (now.hour == 9 and now.minute < 30) or now.hour >= 16:  # Outside market hours
            return None
            
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d", interval="1m")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except Exception as e:
        logger.warning(f"Could not fetch real price for {symbol}: {e}")
    # Fallback to stored price
    return None


# Paper Trading Routes (Railway PostgreSQL)
@app.get("/api/v1/paper/portfolio")
async def get_paper_portfolio():
    """Get paper trading portfolio from Railway PostgreSQL with real-time prices"""
    try:
        import psycopg2  # type: ignore
        from psycopg2.extras import RealDictCursor  # type: ignore
    except ImportError:
        return {"error": "psycopg2 not installed"}
    
    from decimal import Decimal
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Get default user portfolio
        cur.execute("""
            SELECT p.id, p.current_cash, p.total_value
            FROM portfolios p
            JOIN users u ON p.user_id = u.id
            WHERE u.email = 'default@finsight.ai' AND p.portfolio_type = 'paper'
            LIMIT 1
        """)
        portfolio = cur.fetchone()
        
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        # Type-safe dictionary access with RealDictCursor
        portfolio_id: int = portfolio['id']  # type: ignore
        
        # Get positions
        cur.execute("""
            SELECT symbol, quantity, average_cost as avg_price,
                   current_price, market_value, unrealized_pnl
            FROM positions
            WHERE portfolio_id = %s
        """, (portfolio_id,))
        
        positions = {}
        total_market_value = Decimal('0')
        
        for pos in cur.fetchall():
            symbol: str = pos['symbol']  # type: ignore
            quantity = float(pos['quantity'])  # type: ignore
            avg_price = float(pos['avg_price'])  # type: ignore
            
            # Get real-time price
            real_price = get_real_stock_price(symbol)
            current_price = real_price if real_price else float(pos['current_price'])  # type: ignore
            
            # Calculate values with real price
            market_value = quantity * current_price
            unrealized_pnl = market_value - (quantity * avg_price)
            
            positions[symbol] = {
                'quantity': quantity,
                'avg_price': avg_price,
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl
            }
            
            total_market_value += Decimal(str(market_value))
        
        cash_balance = float(portfolio['current_cash'])  # type: ignore
        total_value = cash_balance + float(total_market_value)
        
        cur.close()
        conn.close()
        
        return {
            "cash_balance": cash_balance,
            "positions": positions,
            "total_value": total_value,
            "realized_pnl": 0.0
        }
        
    except Exception as e:
        logger.error(f"Paper portfolio error: {e}")
        return {"error": str(e)}


@app.post("/api/v1/paper/trade/buy")
async def paper_buy(symbol: str, quantity: float, price: float | None = None):
    """Execute paper buy trade with optional real-time pricing"""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        return {"status": "error", "message": "psycopg2 not installed"}
    
    from decimal import Decimal
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    
    try:
        # Get real price if not provided
        if price is None:
            real_price = get_real_stock_price(symbol)
            if real_price is None:
                return {"status": "error", "message": f"Could not fetch price for {symbol}"}
            price = real_price
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Get portfolio
        cur.execute("""
            SELECT p.id, p.current_cash
            FROM portfolios p
            JOIN users u ON p.user_id = u.id
            WHERE u.email = 'default@finsight.ai' AND p.portfolio_type = 'paper'
        """)
        result = cur.fetchone()
        
        if result is None:
            return {"status": "error", "message": "Portfolio not found"}
        
        portfolio_id, cash = result[0], Decimal(str(result[1]))
        
        cost = Decimal(str(quantity)) * Decimal(str(price))
        
        if cost > cash:
            return {"status": "error", "message": "Insufficient funds"}
        
        # Update/create position
        cur.execute("""
            INSERT INTO positions (portfolio_id, symbol, quantity, average_cost, current_price, market_value)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (portfolio_id, symbol) 
            DO UPDATE SET 
                quantity = positions.quantity + EXCLUDED.quantity,
                average_cost = ((positions.quantity * positions.average_cost) + (EXCLUDED.quantity * EXCLUDED.average_cost)) / (positions.quantity + EXCLUDED.quantity),
                market_value = (positions.quantity + EXCLUDED.quantity) * EXCLUDED.current_price
        """, (portfolio_id, symbol, quantity, price, price, float(cost)))
        
        # Update cash
        cur.execute("""
            UPDATE portfolios SET current_cash = current_cash - %s WHERE id = %s
        """, (float(cost), portfolio_id))
        
        # Record transaction
        cur.execute("""
            INSERT INTO transactions (portfolio_id, transaction_type, symbol, quantity, price, total_amount)
            VALUES (%s, 'buy', %s, %s, %s, %s)
        """, (portfolio_id, symbol, quantity, price, float(cost)))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Bought {quantity} shares of {symbol} at ${price}",
            "cost": float(cost)
        }
        
    except Exception as e:
        logger.error(f"Paper buy error: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/paper/reset")
async def paper_reset():
    """Reset paper portfolio to $10,000"""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        return {"status": "error", "message": "psycopg2 not installed"}
    
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT p.id FROM portfolios p
            JOIN users u ON p.user_id = u.id
            WHERE u.email = 'default@finsight.ai' AND p.portfolio_type = 'paper'
        """)
        result = cur.fetchone()
        
        if result is None:
            return {"status": "error", "message": "Portfolio not found"}
        
        portfolio_id = result[0]
        
        cur.execute("DELETE FROM positions WHERE portfolio_id = %s", (portfolio_id,))
        cur.execute("DELETE FROM transactions WHERE portfolio_id = %s", (portfolio_id,))
        cur.execute("""
            UPDATE portfolios 
            SET current_cash = 10000.00, total_value = 10000.00 
            WHERE id = %s
        """, (portfolio_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {"status": "success", "message": "Portfolio reset to $10,000"}
        
    except Exception as e:
        logger.error(f"Paper reset error: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
