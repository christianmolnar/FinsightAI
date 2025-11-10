from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://christian@localhost:5432/finsight")

try:
    engine = create_engine(DATABASE_URL)
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    engine = None


# Import routers
from app.api.portfolio import router as portfolio_router
from app.api.market import router as market_router
from app.api.auth import router as auth_router
app.include_router(portfolio_router)
app.include_router(market_router)
app.include_router(auth_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        from app.database import create_tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")


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
    """Get real-time market data for a symbol"""
    # Placeholder implementation
    return {
        "symbol": symbol.upper(),
        "price": 150.25,
        "change": 2.15,
        "change_percent": 1.45,
        "volume": 45678900,
        "high": 152.30,
        "low": 148.90,
        "open": 149.50,
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
