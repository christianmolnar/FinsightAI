#!/usr/bin/env python3
"""
Quick test: Can we access historical data with free Alpaca tier?
"""
import os
from dotenv import load_dotenv

# Try from backend directory
load_dotenv('/Users/christian/Repos/f.insight.AI Advanced/backend/.env')

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')

print(f"Testing with keys: {API_KEY[:10]}...")

try:
    client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    
    request_params = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=datetime(2024, 1, 1),
        end=datetime(2024, 1, 10)
    )
    
    bars = client.get_stock_bars(request_params)
    
    if bars and bars.df is not None and not bars.df.empty:
        print(f"✅ SUCCESS! Got {len(bars.df)} bars for AAPL")
        print(f"Date range: {bars.df.index[0]} to {bars.df.index[-1]}")
        print("\n✅ FREE TIER WORKS FOR HISTORICAL DATA!")
        print("❌ NO UPGRADE NEEDED - Can use existing code")
    else:
        print("❌ No data returned")
        
except Exception as e:
    error_msg = str(e)
    print(f"❌ Error: {error_msg}")
    
    if "402" in error_msg or "payment" in error_msg.lower():
        print("\n🔴 UPGRADE NEEDED: Free tier doesn't have historical access")
        print("   Recommendation: Alpaca Algo Trader Plus ($99/month)")
    elif "401" in error_msg:
        print("\n❌ Authentication failed - check API keys")
    else:
        print("\n⚠️  Unknown error - may need upgrade")
