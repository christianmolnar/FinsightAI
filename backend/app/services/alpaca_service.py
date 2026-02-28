"""
Alpaca Trading Service

Handles all interactions with the Alpaca API.
Provides methods for:
- Account management
- Position tracking
- Order placement
- Market data retrieval
"""

import os
from typing import List, Dict, Optional
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
from dotenv import load_dotenv
import logging
from pathlib import Path

# Load .env from project root (one level up from backend/)
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger(__name__)


class AlpacaService:
    """Service for interacting with Alpaca API"""
    
    def __init__(self, paper: bool = True):
        """
        Initialize Alpaca clients
        
        Args:
            paper: If True, use paper trading account. If False, use live account.
        """
        self.paper = paper
        
        # Load correct credentials based on paper vs live
        if paper:
            self.api_key = os.getenv("ALPACA_PAPER_API_KEY_ID")
            self.secret_key = os.getenv("ALPACA_PAPER_API_SECRET_KEY")
            key_type = "paper"
        else:
            self.api_key = os.getenv("ALPACA_LIVE_API_KEY_ID")
            self.secret_key = os.getenv("ALPACA_LIVE_API_SECRET_KEY")
            key_type = "live"
        
        if not self.api_key or not self.secret_key:
            raise ValueError(
                f"Alpaca {key_type} trading API credentials not found. "
                f"Set ALPACA_{key_type.upper()}_API_KEY_ID and ALPACA_{key_type.upper()}_API_SECRET_KEY in .env"
            )
        
        # Trading client (for account, positions, orders)
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=self.paper
        )
        
        # Market data client (for quotes, bars, etc.)
        self.market_data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
        
        logger.info(f"AlpacaService initialized (paper={self.paper})")
    
    # ========================================
    # ACCOUNT METHODS
    # ========================================
    
    def get_account(self) -> Dict:
        """
        Get account information
        
        Returns:
            Dict with account details including:
            - id: Account ID
            - cash: Available cash
            - portfolio_value: Total portfolio value
            - buying_power: Buying power
            - pattern_day_trader: PDT status
        """
        try:
            account = self.trading_client.get_account()
            
            # Use getattr for safe attribute access (Alpaca returns RawData objects)
            return {
                "id": getattr(account, 'id', None),
                "account_number": getattr(account, 'account_number', None),
                "status": getattr(account, 'status', None),
                "currency": getattr(account, 'currency', 'USD'),
                "cash": float(getattr(account, 'cash', 0)),
                "portfolio_value": float(getattr(account, 'portfolio_value', 0)),
                "buying_power": float(getattr(account, 'buying_power', 0)),
                "equity": float(getattr(account, 'equity', 0)),
                "last_equity": float(getattr(account, 'last_equity', 0)),
                "pattern_day_trader": getattr(account, 'pattern_day_trader', False),
                "trading_blocked": getattr(account, 'trading_blocked', False),
                "transfers_blocked": getattr(account, 'transfers_blocked', False),
                "account_blocked": getattr(account, 'account_blocked', False),
                "created_at": getattr(account, 'created_at', None).isoformat() if getattr(account, 'created_at', None) else None,
            }
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
    
    # ========================================
    # POSITION METHODS
    # ========================================
    
    def get_positions(self) -> List[Dict]:
        """
        Get all positions
        
        Returns:
            List of position dicts with:
            - symbol: Stock symbol
            - qty: Number of shares
            - avg_entry_price: Average entry price
            - current_price: Current market price
            - market_value: Current market value
            - cost_basis: Total cost basis
            - unrealized_pl: Unrealized profit/loss ($)
            - unrealized_plpc: Unrealized profit/loss (%)
        """
        try:
            positions = self.trading_client.get_all_positions()
            
            # Use getattr for safe attribute access (Alpaca returns RawData objects)
            return [
                {
                    "symbol": getattr(pos, 'symbol', ''),
                    "qty": float(getattr(pos, 'qty', 0)),
                    "avg_entry_price": float(getattr(pos, 'avg_entry_price', 0)),
                    "current_price": float(getattr(pos, 'current_price', 0)),
                    "market_value": float(getattr(pos, 'market_value', 0)),
                    "cost_basis": float(getattr(pos, 'cost_basis', 0)),
                    "unrealized_pl": float(getattr(pos, 'unrealized_pl', 0)),
                    "unrealized_plpc": float(getattr(pos, 'unrealized_plpc', 0)),
                    "side": getattr(pos, 'side', None),
                    "exchange": getattr(pos, 'exchange', None),
                    "asset_id": getattr(pos, 'asset_id', None),
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get a specific position
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Position dict or None if position doesn't exist
        """
        try:
            pos = self.trading_client.get_open_position(symbol)
            
            # Use getattr for safe attribute access (Alpaca returns RawData objects)
            return {
                "symbol": getattr(pos, 'symbol', symbol),
                "qty": float(getattr(pos, 'qty', 0)),
                "avg_entry_price": float(getattr(pos, 'avg_entry_price', 0)),
                "current_price": float(getattr(pos, 'current_price', 0)),
                "market_value": float(getattr(pos, 'market_value', 0)),
                "cost_basis": float(getattr(pos, 'cost_basis', 0)),
                "unrealized_pl": float(getattr(pos, 'unrealized_pl', 0)),
                "unrealized_plpc": float(getattr(pos, 'unrealized_plpc', 0)),
                "side": getattr(pos, 'side', None),
                "exchange": getattr(pos, 'exchange', None),
                "asset_id": getattr(pos, 'asset_id', None),
            }
        except Exception as e:
            if "position does not exist" in str(e).lower():
                return None
            logger.error(f"Error fetching position for {symbol}: {e}")
            raise
    
    # ========================================
    # ORDER METHODS
    # ========================================
    
    def place_market_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        time_in_force: str = "day"
    ) -> Dict:
        """
        Place a market order
        
        Args:
            symbol: Stock symbol
            qty: Number of shares (can be fractional)
            side: 'buy' or 'sell'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
            
        Returns:
            Order dict with order details
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce[time_in_force.upper()]
            
            market_order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=tif
            )
            
            order = self.trading_client.submit_order(market_order_data)
            
            return self._format_order(order)
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise
    
    def place_limit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        limit_price: float,
        time_in_force: str = "day"
    ) -> Dict:
        """
        Place a limit order
        
        Args:
            symbol: Stock symbol
            qty: Number of shares (can be fractional)
            side: 'buy' or 'sell'
            limit_price: Limit price
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
            
        Returns:
            Order dict with order details
        """
        try:
            order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
            tif = TimeInForce[time_in_force.upper()]
            
            limit_order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                limit_price=limit_price,
                time_in_force=tif
            )
            
            order = self.trading_client.submit_order(limit_order_data)
            
            return self._format_order(order)
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise
    
    def get_orders(self, status: str = "open") -> List[Dict]:
        """
        Get orders
        
        Args:
            status: Order status filter ('open', 'closed', 'all')
            
        Returns:
            List of order dicts
        """
        try:
            if status == "open":
                orders = self.trading_client.get_orders()
            else:
                # Get all orders (closed + open)
                orders = self.trading_client.get_orders(status="all")
                
            return [self._format_order(order) for order in orders]
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            
        Returns:
            True if successful
        """
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"Cancelled order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            raise
    
    def _format_order(self, order) -> Dict:
        """Format Alpaca order object to dict"""
        return {
            "id": order.id,
            "client_order_id": order.client_order_id,
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "side": order.side.value,
            "type": order.type.value,
            "time_in_force": order.time_in_force.value,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "status": order.status.value,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "expired_at": order.expired_at.isoformat() if order.expired_at else None,
            "canceled_at": order.canceled_at.isoformat() if order.canceled_at else None,
        }
    
    # ========================================
    # MARKET DATA METHODS
    # ========================================
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Get latest quote for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Quote dict with bid/ask prices
        """
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = self.market_data_client.get_stock_latest_quote(request_params)
            quote = quotes[symbol]
            
            return {
                "symbol": symbol,
                "bid_price": float(quote.bid_price),
                "bid_size": int(quote.bid_size),
                "ask_price": float(quote.ask_price),
                "ask_size": int(quote.ask_size),
                "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            raise
    
    def get_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get latest quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dict mapping symbol to quote dict
        """
        try:
            request_params = StockLatestQuoteRequest(symbol_or_symbols=symbols)
            quotes = self.market_data_client.get_stock_latest_quote(request_params)
            
            return {
                symbol: {
                    "symbol": symbol,
                    "bid_price": float(quote.bid_price),
                    "bid_size": int(quote.bid_size),
                    "ask_price": float(quote.ask_price),
                    "ask_size": int(quote.ask_size),
                    "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
                }
                for symbol, quote in quotes.items()
            }
        except Exception as e:
            logger.error(f"Error fetching quotes: {e}")
            raise


# Singleton instances
_alpaca_paper_service = None
_alpaca_live_service = None


def get_alpaca_service(paper: bool = True) -> AlpacaService:
    """
    Get or create AlpacaService singleton
    
    Args:
        paper: If True, return paper trading service. If False, return live service.
    
    Returns:
        AlpacaService instance
    """
    global _alpaca_paper_service, _alpaca_live_service
    
    if paper:
        if _alpaca_paper_service is None:
            _alpaca_paper_service = AlpacaService(paper=True)
        return _alpaca_paper_service
    else:
        if _alpaca_live_service is None:
            _alpaca_live_service = AlpacaService(paper=False)
        return _alpaca_live_service
