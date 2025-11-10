"""
Schwab API integration service for real-time market data
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import json

import schwabdev
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models import MarketData, TradingSignal, NewsEvent
from app.database import get_db

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchwabAPIService:
    """
    Service for integrating with Charles Schwab API
    Provides automatic token management and real-time market data
    """
    
    def __init__(self):
        """Initialize the Schwab API client with automatic token management"""
        
        # Get credentials from environment
        self.app_key = os.getenv('APP_KEY')
        self.app_secret = os.getenv('APP_SECRET')
        self.callback_url = os.getenv('CALLBACK_URL', 'https://127.0.0.1')
        
        if not self.app_key or not self.app_secret:
            raise ValueError(
                "Missing Schwab API credentials. Please set APP_KEY and APP_SECRET in your .env file.\n"
                "Get these from https://beta-developer.schwab.com/"
            )
        
        if len(self.app_key) not in (32, 48) or len(self.app_secret) not in (16, 64):
            raise ValueError(
                f"Invalid credential lengths. APP_KEY should be 32 chars, APP_SECRET should be 16 chars.\n"
                f"Current lengths: APP_KEY={len(self.app_key)}, APP_SECRET={len(self.app_secret)}"
            )
        
        # Initialize client with automatic callback capture
        self.client = None
        self.streamer = None
        
    def initialize_client(self):
        """Initialize the Schwab client (call this after setting up credentials)"""
        try:
            # Create client with automatic callback capture for easier authentication
            self.client = schwabdev.Client(
                app_key=self.app_key,
                app_secret=self.app_secret,
                callback_url=self.callback_url,
                tokens_file="tokens.json",
                timeout=30,
                capture_callback=True,  # Automatically captures OAuth callback
                use_session=True
            )
            
            self.streamer = self.client.stream
            logger.info("✅ Schwab API client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Schwab client: {e}")
            logger.info(
                "📋 Setup checklist:\n"
                "1. Create account at https://beta-developer.schwab.com/\n"
                "2. Create an individual developer app\n"
                "3. Add both APIs: 'Accounts and Trading Production' and 'Market Data Production'\n"
                "4. Wait for app status to be 'Ready for Use' (not just 'Approved - Pending')\n"
                "5. Enable TOS (Thinkorswim) for your Schwab account\n"
                "6. Add your APP_KEY and APP_SECRET to the .env file"
            )
            return False
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get linked account information"""
        if not self.client:
            logger.error("Client not initialized. Call initialize_client() first.")
            return None
            
        try:
            response = self.client.account_linked()
            if response.ok:
                accounts = response.json()
                logger.info(f"📊 Found {len(accounts)} linked accounts")
                return accounts
            else:
                logger.error(f"Failed to get accounts: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_real_time_quotes(self, symbols: List[str]) -> Optional[Dict[str, Any]]:
        """Get real-time quotes for given symbols"""
        if not self.client:
            logger.error("Client not initialized. Call initialize_client() first.")
            return None
            
        try:
            # Convert list to comma-separated string if needed
            symbol_string = ",".join(symbols) if isinstance(symbols, list) else symbols
            
            response = self.client.quotes(symbols=symbol_string)
            if response.ok:
                quotes = response.json()
                logger.info(f"📈 Retrieved quotes for {len(quotes)} symbols")
                return quotes
            else:
                logger.error(f"Failed to get quotes: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting quotes: {e}")
            return None
    
    def start_real_time_stream(self, symbols: List[str], callback_func=None):
        """Start real-time data streaming for given symbols"""
        if not self.client or not self.streamer:
            logger.error("Client/streamer not initialized. Call initialize_client() first.")
            return False
            
        try:
            # Define default response handler if none provided
            def default_handler(message):
                """Default handler that saves data to database"""
                try:
                    data = json.loads(message) if isinstance(message, str) else message
                    logger.info(f"📊 Received streaming data: {data}")
                    
                    # Here you would save to your database
                    # self.save_market_data_to_db(data)
                    
                except Exception as e:
                    logger.error(f"Error handling stream data: {e}")
            
            handler = callback_func or default_handler
            
            # Start the streamer
            self.streamer.start(handler)
            
            # Subscribe to level 1 equity data (real-time quotes)
            symbol_string = ",".join(symbols) if isinstance(symbols, list) else symbols
            stream_request = self.streamer.level_one_equities(
                keys=symbol_string,
                fields="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"
            )
            
            self.streamer.send(stream_request)
            logger.info(f"🔄 Started real-time streaming for symbols: {symbols}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return False
    
    def stop_stream(self):
        """Stop the real-time data stream"""
        if self.streamer:
            try:
                self.streamer.stop()
                logger.info("⏹️ Stopped real-time streaming")
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
    
    def get_market_data_history(self, symbol: str, period_type: str = "day", period: int = 1) -> Optional[Dict[str, Any]]:
        """Get historical market data"""
        if not self.client:
            logger.error("Client not initialized. Call initialize_client() first.")
            return None
            
        try:
            response = self.client.price_history(
                symbol=symbol,
                periodType=period_type,
                period=period,
                frequencyType="minute",
                frequency=1
            )
            
            if response.ok:
                data = response.json()
                logger.info(f"📊 Retrieved historical data for {symbol}")
                return data
            else:
                logger.error(f"Failed to get historical data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None
    
    def save_market_data_to_db(self, market_data: Dict[str, Any]):
        """Save market data to the database"""
        try:
            db = next(get_db())
            
            # Extract relevant data from the market response
            # This will depend on the exact structure of Schwab's streaming data
            
            # Example structure (adjust based on actual Schwab response format):
            if 'content' in market_data:
                for item in market_data['content']:
                    if 'key' in item and 'content' in item:
                        symbol = item['key']
                        data = item['content']
                        
                        market_entry = MarketData(
                            symbol=symbol,
                            price=float(data.get('last_price', 0)),
                            volume=int(data.get('volume', 0)),
                            timestamp=datetime.now(timezone.utc),
                            open_price=float(data.get('open_price', 0)),
                            high_price=float(data.get('high_price', 0)),
                            low_price=float(data.get('low_price', 0)),
                            close_price=float(data.get('last_price', 0))
                        )
                        
                        db.add(market_entry)
            
            db.commit()
            logger.info("💾 Saved market data to database")
            
        except Exception as e:
            logger.error(f"Error saving market data to database: {e}")
        finally:
            db.close()


# Global service instance
schwab_service = SchwabAPIService()


def test_schwab_connection():
    """Test the Schwab API connection and basic functionality"""
    logger.info("🧪 Testing Schwab API connection...")
    
    if not schwab_service.initialize_client():
        return False
    
    # Test account access
    accounts = schwab_service.get_account_info()
    if not accounts:
        return False
    
    # Test quotes
    test_symbols = ["AAPL", "MSFT", "TSLA"]
    quotes = schwab_service.get_real_time_quotes(test_symbols)
    if not quotes:
        return False
    
    logger.info("✅ All Schwab API tests passed!")
    return True


if __name__ == "__main__":
    # Run connection test
    test_schwab_connection()
