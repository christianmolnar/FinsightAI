from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.models import Portfolio, Position, Trade
from app.schwab_api import schwab_service
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
# SCHWAB ACCOUNT INTEGRATION - Real Portfolio Data
# =============================================================================

@router.get("/schwab/accounts")
async def get_schwab_accounts():
    """Get all linked Schwab accounts"""
    try:
        if not schwab_service or not schwab_service.is_configured():
            raise HTTPException(
                status_code=503, 
                detail="Schwab API not configured. Please set APP_KEY and APP_SECRET in environment."
            )
        
        # Initialize client if not already done
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(
                    status_code=503,
                    detail="Failed to initialize Schwab client. Please check credentials and authentication."
                )
        
        accounts = schwab_service.get_account_info()
        if accounts is None:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed. Please authenticate with Schwab API first."
            )
        
        return {
            "success": True,
            "accounts": accounts,
            "account_count": len(accounts) if accounts else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching accounts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/schwab/accounts/{account_hash}/positions")
async def get_schwab_account_positions(account_hash: str):
    """Get positions for a specific Schwab account"""
    try:
        if not schwab_service or not schwab_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Schwab API not configured"
            )
        
        # Initialize client if not already done
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(
                    status_code=503,
                    detail="Failed to initialize Schwab client"
                )
        
        # Get account positions
        response = schwab_service.client.account_details(
            accountHash=account_hash,
            fields="positions"
        )
        
        if not response.ok:
            if response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication failed. Please re-authenticate with Schwab API."
                )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Schwab API error: {response.text}"
            )
        
        account_data = response.json()
        positions = account_data.get("securitiesAccount", {}).get("positions", [])
        
        # Transform positions data for our frontend
        formatted_positions = []
        for position in positions:
            instrument = position.get("instrument", {})
            long_qty = position.get("longQuantity", 0)
            short_qty = position.get("shortQuantity", 0)
            net_qty = long_qty - short_qty
            
            if net_qty == 0:  # Skip positions with zero quantity
                continue
            
            market_value = position.get("marketValue", 0)
            avg_price = position.get("averagePrice", 0)
            day_pl = position.get("currentDayProfitLoss", 0)
            
            # Calculate current price from market value and quantity
            current_price = market_value / net_qty if net_qty != 0 else avg_price
            
            # Calculate total P&L
            total_pl = market_value - (avg_price * net_qty)
            
            formatted_position = {
                "symbol": instrument.get("symbol", "N/A"),
                "cusip": instrument.get("cusip", "N/A"),
                "description": instrument.get("description", "N/A"),
                "assetType": instrument.get("assetType", "N/A"),
                "quantity": net_qty,
                "marketValue": market_value,
                "averagePrice": avg_price,
                "currentPrice": current_price,
                "dayPL": day_pl,
                "totalPL": total_pl,
                "dayPLPercent": (day_pl / (avg_price * abs(net_qty))) * 100 if avg_price * net_qty != 0 else 0,
                "totalPLPercent": (total_pl / (avg_price * abs(net_qty))) * 100 if avg_price * net_qty != 0 else 0
            }
            formatted_positions.append(formatted_position)
        
        return {
            "success": True,
            "account_hash": account_hash,
            "positions": formatted_positions,
            "position_count": len(formatted_positions),
            "total_market_value": sum(pos["marketValue"] for pos in formatted_positions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching positions for account {account_hash}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/schwab/accounts/{account_hash}/summary")
async def get_schwab_account_summary(account_hash: str):
    """Get Schwab account summary including balances and totals"""
    try:
        if not schwab_service or not schwab_service.is_configured():
            raise HTTPException(
                status_code=503,
                detail="Schwab API not configured"
            )
        
        # Initialize client if not already done
        if not schwab_service.client:
            if not schwab_service.initialize_client():
                raise HTTPException(
                    status_code=503,
                    detail="Failed to initialize Schwab client"
                )
        
        # Get full account details
        response = schwab_service.client.account_details(
            accountHash=account_hash,
            fields="positions"
        )
        
        if not response.ok:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Schwab API error: {response.text}"
            )
        
        account_data = response.json()
        securities_account = account_data.get("securitiesAccount", {})
        
        # Extract key account information
        summary = {
            "accountId": securities_account.get("accountId", "N/A"),
            "accountHash": account_hash,
            "type": securities_account.get("type", "N/A"),
            "roundTrips": securities_account.get("roundTrips", 0),
            "isDayTrader": securities_account.get("isDayTrader", False),
            "isClosingOnlyRestricted": securities_account.get("isClosingOnlyRestricted", False),
            
            # Current balances
            "currentBalances": securities_account.get("currentBalances", {}),
            "projectedBalances": securities_account.get("projectedBalances", {}),
            
            # Position summary
            "positionCount": len(securities_account.get("positions", [])),
            "totalMarketValue": sum(
                pos.get("marketValue", 0) 
                for pos in securities_account.get("positions", [])
            ),
            "totalDayPL": sum(
                pos.get("currentDayProfitLoss", 0) 
                for pos in securities_account.get("positions", [])
            ),
        }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching account summary for {account_hash}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/schwab/portfolio/overview")
async def get_schwab_portfolio_overview():
    """Get overview of all Schwab accounts and positions"""
    try:
        # First get all accounts
        accounts_response = await get_schwab_accounts()
        accounts = accounts_response["accounts"]
        
        if not accounts:
            return {
                "success": True,
                "message": "No accounts found",
                "total_accounts": 0,
                "total_market_value": 0,
                "accounts": []
            }
        
        portfolio_overview = []
        total_market_value = 0
        total_day_pl = 0
        
        for account in accounts:
            account_hash = account.get("hashValue", "")
            if not account_hash:
                continue
                
            try:
                # Get positions for this account
                positions_response = await get_schwab_account_positions(account_hash)
                positions = positions_response["positions"]
                account_market_value = positions_response["total_market_value"]
                
                # Get account summary
                summary_response = await get_schwab_account_summary(account_hash)
                summary = summary_response["summary"]
                
                account_overview = {
                    "accountNumber": account.get("accountNumber", "N/A"),
                    "accountHash": account_hash,
                    "type": summary.get("type", "N/A"),
                    "marketValue": account_market_value,
                    "dayPL": summary.get("totalDayPL", 0),
                    "positionCount": len(positions),
                    "cashBalance": summary.get("currentBalances", {}).get("cashBalance", 0),
                    "buyingPower": summary.get("currentBalances", {}).get("buyingPower", 0),
                    "isDayTrader": summary.get("isDayTrader", False),
                    "positions": positions  # Include position details
                }
                
                portfolio_overview.append(account_overview)
                total_market_value += account_market_value
                total_day_pl += summary.get("totalDayPL", 0)
                
            except Exception as e:
                logger.warning(f"Could not fetch details for account {account_hash}: {e}")
                continue
        
        return {
            "success": True,
            "total_accounts": len(portfolio_overview),
            "total_market_value": total_market_value,
            "total_day_pl": total_day_pl,
            "day_pl_percent": (total_day_pl / total_market_value * 100) if total_market_value > 0 else 0,
            "accounts": portfolio_overview
        }
        
    except Exception as e:
        logger.error(f"Error creating portfolio overview: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/schwab/positions/all")
async def get_all_schwab_positions():
    """Get all positions across all Schwab accounts"""
    try:
        portfolio_overview = await get_schwab_portfolio_overview()
        
        all_positions = []
        for account in portfolio_overview.get("accounts", []):
            for position in account.get("positions", []):
                # Add account info to each position
                position["accountHash"] = account["accountHash"]
                position["accountNumber"] = account["accountNumber"]
                position["accountType"] = account["type"]
                all_positions.append(position)
        
        # Group positions by symbol across accounts
        symbol_totals = {}
        for pos in all_positions:
            symbol = pos["symbol"]
            if symbol not in symbol_totals:
                symbol_totals[symbol] = {
                    "symbol": symbol,
                    "description": pos["description"],
                    "assetType": pos["assetType"],
                    "totalQuantity": 0,
                    "totalMarketValue": 0,
                    "totalDayPL": 0,
                    "totalPL": 0,
                    "accounts": []
                }
            
            symbol_totals[symbol]["totalQuantity"] += pos["quantity"]
            symbol_totals[symbol]["totalMarketValue"] += pos["marketValue"]
            symbol_totals[symbol]["totalDayPL"] += pos["dayPL"]
            symbol_totals[symbol]["totalPL"] += pos["totalPL"]
            symbol_totals[symbol]["accounts"].append({
                "accountNumber": pos["accountNumber"],
                "quantity": pos["quantity"],
                "marketValue": pos["marketValue"]
            })
        
        # Calculate weighted average prices and percentages
        for symbol_data in symbol_totals.values():
            if symbol_data["totalMarketValue"] > 0:
                symbol_data["averagePrice"] = symbol_data["totalMarketValue"] / symbol_data["totalQuantity"]
                symbol_data["dayPLPercent"] = (symbol_data["totalDayPL"] / symbol_data["totalMarketValue"]) * 100
                symbol_data["totalPLPercent"] = (symbol_data["totalPL"] / symbol_data["totalMarketValue"]) * 100
        
        return {
            "success": True,
            "all_positions": all_positions,
            "consolidated_positions": list(symbol_totals.values()),
            "total_positions": len(all_positions),
            "unique_symbols": len(symbol_totals)
        }
        
    except Exception as e:
        logger.error(f"Error fetching all positions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
