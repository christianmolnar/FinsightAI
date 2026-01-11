from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
from api.queue import router as queue_router
from utils.market_hours import get_market_status
# Commented out optional routers that may not exist in deployment
# from api.ai_optimizer import router as ai_optimizer_router
# from api.paper_trading_db import router as paper_trading_router

app.include_router(portfolio_router)
app.include_router(market_router)
app.include_router(auth_router)
app.include_router(strategy_parameters_router)
app.include_router(research_router)
app.include_router(queue_router)
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
    
    logger.info("✓ Using Alpaca for trading (paper + live)")


@app.get("/")
async def root():
    """Root endpoint with system status"""
    return {
        "message": "FInsightAI Trading Agent",
        "status": "active",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@app.get("/api/market/status")
async def market_status():
    """Get current market status (open/closed)"""
    try:
        status = get_market_status()
        return {
            "success": True,
            **status
        }
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        return {
            "success": False,
            "error": str(e),
            "is_open": False,
            "status": "Unknown"
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


# Helper function to get real stock price using Alpaca API
def get_real_stock_price(symbol: str) -> float | None:
    """Fetch real-time stock price from Alpaca API"""
    try:
        from app.services.alpaca_service import get_alpaca_service
        
        alpaca_service = get_alpaca_service(paper=True)  # Use paper for market data
        quote = alpaca_service.get_quote(symbol)
        
        if quote and 'ask_price' in quote:
            # Return bid/ask midpoint for most accurate price
            if quote.get('bid_price') and quote.get('ask_price'):
                return (float(quote['bid_price']) + float(quote['ask_price'])) / 2
            elif quote.get('ask_price'):
                return float(quote['ask_price'])
        
        logger.warning(f"No price data available for {symbol}")
        return None
        
    except Exception as e:
        logger.warning(f"Could not fetch Alpaca price for {symbol}: {e}")
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
    
    # Get database URL and normalize for psycopg2
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    # psycopg2 doesn't support postgresql+psycopg:// - convert to postgresql://
    db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
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


@app.get("/api/v1/paper/transactions")
async def get_paper_transactions():
    """Get paper trading transaction history from Railway PostgreSQL"""
    try:
        import psycopg2  # type: ignore
        from psycopg2.extras import RealDictCursor  # type: ignore
    except ImportError:
        return {"error": "psycopg2 not installed"}
    
    # Get database URL and normalize for psycopg2
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        
        # Get transactions for default user's paper portfolio
        cur.execute("""
            SELECT t.id, t.transaction_type, t.symbol, t.quantity, t.price, 
                   t.total_amount, t.created_at
            FROM transactions t
            JOIN portfolios p ON t.portfolio_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE u.email = 'default@finsight.ai' AND p.portfolio_type = 'paper'
            ORDER BY t.created_at DESC
            LIMIT 50
        """)
        
        transactions = cur.fetchall()
        cur.close()
        conn.close()
        
        # Format transactions
        result = []
        for txn in transactions:
            result.append({
                'id': str(txn['id']),
                'type': txn['transaction_type'],
                'symbol': txn['symbol'],
                'quantity': float(txn['quantity']),
                'price': float(txn['price']),
                'total': float(txn['total_amount']),
                'timestamp': txn['created_at'].isoformat() if txn['created_at'] else None
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Paper transactions error: {e}")
        return {"error": str(e)}


# Pydantic models for request bodies
class TradeRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "market"


@app.post("/api/v1/paper/trade")
async def paper_trade(trade: TradeRequest):
    """Execute paper trade (buy or sell)"""
    try:
        import psycopg2  # type: ignore
    except ImportError:
        return {"status": "error", "message": "psycopg2 not installed"}
    
    from decimal import Decimal
    
    # Extract values from request
    symbol = trade.symbol
    side = trade.side
    quantity = trade.quantity
    order_type = trade.order_type
    
    # Get real-time price
    price = get_real_stock_price(symbol)
    if price is None:
        return {"status": "error", "message": f"Could not fetch price for {symbol}"}
    
    # Get database URL and normalize for psycopg2
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway')
    # psycopg2 doesn't support postgresql+psycopg:// - convert to postgresql://
    db_url = db_url.replace('postgresql+psycopg://', 'postgresql://')
    
    try:
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
        total_value = Decimal(str(quantity)) * Decimal(str(price))
        
        if side.lower() == "buy":
            if total_value > cash:
                return {"status": "error", "message": "Insufficient funds"}
            
            # Check if position exists
            cur.execute("""
                SELECT quantity, average_cost 
                FROM positions 
                WHERE portfolio_id = %s AND symbol = %s
            """, (portfolio_id, symbol))
            existing_position = cur.fetchone()
            
            if existing_position:
                # Update existing position
                existing_qty, existing_avg = Decimal(str(existing_position[0])), Decimal(str(existing_position[1]))
                new_qty = existing_qty + Decimal(str(quantity))
                new_avg = ((existing_qty * existing_avg) + (Decimal(str(quantity)) * Decimal(str(price)))) / new_qty
                
                cur.execute("""
                    UPDATE positions 
                    SET quantity = %s, average_cost = %s, current_price = %s, market_value = %s * %s
                    WHERE portfolio_id = %s AND symbol = %s
                """, (float(new_qty), float(new_avg), price, float(new_qty), price, portfolio_id, symbol))
            else:
                # Insert new position
                cur.execute("""
                    INSERT INTO positions (portfolio_id, symbol, quantity, average_cost, current_price, market_value)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (portfolio_id, symbol, quantity, price, price, float(total_value)))
            
            # Update cash (decrease)
            cur.execute("""
                UPDATE portfolios SET current_cash = current_cash - %s WHERE id = %s
            """, (float(total_value), portfolio_id))
            
            message = f"Bought {quantity} shares of {symbol} at ${price}"
            
        elif side.lower() == "sell":
            # Check if position exists
            cur.execute("""
                SELECT quantity FROM positions 
                WHERE portfolio_id = %s AND symbol = %s
            """, (portfolio_id, symbol))
            position_result = cur.fetchone()
            
            if position_result is None or position_result[0] < quantity:
                return {"status": "error", "message": "Insufficient shares to sell"}
            
            # Update position
            new_quantity = position_result[0] - quantity
            if new_quantity == 0:
                cur.execute("""
                    DELETE FROM positions WHERE portfolio_id = %s AND symbol = %s
                """, (portfolio_id, symbol))
            else:
                cur.execute("""
                    UPDATE positions 
                    SET quantity = %s, market_value = %s * current_price
                    WHERE portfolio_id = %s AND symbol = %s
                """, (new_quantity, new_quantity, portfolio_id, symbol))
            
            # Update cash (increase)
            cur.execute("""
                UPDATE portfolios SET current_cash = current_cash + %s WHERE id = %s
            """, (float(total_value), portfolio_id))
            
            message = f"Sold {quantity} shares of {symbol} at ${price}"
        else:
            return {"status": "error", "message": "Invalid side. Use 'buy' or 'sell'"}
        
        # Record transaction
        cur.execute("""
            INSERT INTO transactions (portfolio_id, transaction_type, symbol, quantity, price, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (portfolio_id, side.lower(), symbol, quantity, price, float(total_value)))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "message": message,
            "total": float(total_value)
        }
        
    except Exception as e:
        logger.error(f"Paper trade error: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/quotes/{symbol}")
async def get_quote(symbol: str):
    """Get real-time quote for a symbol using Alpaca API"""
    try:
        from app.services.alpaca_service import get_alpaca_service
        
        alpaca_service = get_alpaca_service(paper=True)
        quote = alpaca_service.get_quote(symbol)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}")
        
        # Calculate change from previous close if available
        last_price = float(quote.get('ask_price', 0))
        bid_price = float(quote.get('bid_price', 0))
        
        # Use midpoint for most accurate current price
        current_price = (last_price + bid_price) / 2 if last_price and bid_price else last_price
        
        return {
            "symbol": symbol.upper(),
            "price": current_price,
            "change": 0,  # Would need historical data for this
            "changePercent": 0,  # Would need historical data for this
            "timestamp": time.time(),
            "volume": 0,  # Alpaca quote doesn't include volume in basic quote
            "bid": bid_price,
            "ask": last_price,
            "high": 0,
            "low": 0,
            "open": 0,
            "previousClose": 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
