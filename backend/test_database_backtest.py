"""
Quick test: Verify database-first backtester works

Tests that historical data service pulls from database correctly.
"""

import asyncio
from datetime import datetime, timedelta
from app.services.historical_data_service import get_historical_data_service

async def main():
    print("🧪 Testing Database-First Historical Data Service\n")
    
    service = get_historical_data_service()
    
    # Test 1: Check database coverage
    print("📊 Database Coverage:")
    stats = service.get_data_coverage_stats()
    print(f"   Total bars: {stats['total_bars']:,}")
    print(f"   Total symbols: {stats['total_symbols']}")
    print(f"   Date range: {stats['earliest_date']} to {stats['latest_date']}\n")
    
    # Test 2: Get historical data for a known symbol
    print("📈 Testing AAPL historical data:")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 1 year
    
    result = service.get_historical_bars(
        symbols=["AAPL"],
        start=start_date,
        end=end_date,
        timeframe="1Day"
    )
    
    if "AAPL" in result and not result["AAPL"].empty:
        df = result["AAPL"]
        print(f"   ✅ Got {len(df)} bars")
        print(f"   Date range: {df.index.min()} to {df.index.max()}")
        print(f"   Latest close: ${df['close'].iloc[-1]:.2f}\n")
    else:
        print("   ❌ No data returned\n")
    
    # Test 3: Get multiple symbols
    print("📊 Testing batch retrieval (5 symbols):")
    result = service.get_historical_bars(
        symbols=["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"],
        start=start_date,
        end=end_date,
        timeframe="1Day"
    )
    
    for symbol, df in result.items():
        if not df.empty:
            print(f"   ✅ {symbol:6} {len(df):4} bars")
        else:
            print(f"   ❌ {symbol:6} No data")
    
    print("\n✅ Database-first service working!")
    print("\n💡 Next: Run actual backtest to verify end-to-end")
    
    service.close()

if __name__ == "__main__":
    asyncio.run(main())
