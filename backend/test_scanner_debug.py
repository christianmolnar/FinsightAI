"""Debug test to see what the scanner finds"""

import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from services.backtester import Backtester
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

async def main():
    print("🔍 Testing what the scanner finds...\n")
    
    db = SessionLocal()
    
    # Test just 1 week
    end_date = datetime(2026, 3, 1)
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing single week: {start_date.date()} to {end_date.date()}\n")
    
    backtester = Backtester(db, initial_capital=100000.0)
    
    # Download data
    print("📥 Downloading historical data...")
    universe_data = await backtester._download_all_historical_data(start_date, end_date)
    print(f"✅ Got data for {len(universe_data)} stocks\n")
    
    # Get candidates for this date
    print(f"🔍 Scanning {end_date.date()}...")
    candidates = await backtester._get_historical_candidates(
        scan_date=end_date,
        strategies=['technical_breakout', 'earnings_play', 'seasonality'],
        universe_data=universe_data
    )
    
    print(f"\n📊 Found {len(candidates)} total candidates:")
    
    # Group by strategy
    from collections import Counter
    strategy_counts = Counter(c['strategy'] for c in candidates)
    
    for strategy, count in strategy_counts.items():
        print(f"   {strategy}: {count}")
    
    # Show first 10 candidates
    if candidates:
        print(f"\n🎯 First {min(10, len(candidates))} candidates:")
        for i, c in enumerate(candidates[:10], 1):
            print(f"   {i}. {c['symbol']} ({c['strategy']}): score={c['score']:.1f}, ${c['price']:.2f}")
            print(f"      {c['reason']}")
    else:
        print("\n⚠️  NO CANDIDATES FOUND!")
        print("   Checking data availability...")
        
        # Check a few random stocks
        import random
        test_symbols = random.sample(list(universe_data.keys()), min(5, len(universe_data)))
        
        for symbol in test_symbols:
            df = universe_data[symbol]
            if not df.empty:
                data_before = df[df.index <= end_date]
                print(f"\n   {symbol}:")
                print(f"      Total rows: {len(df)}")
                print(f"      Rows before {end_date.date()}: {len(data_before)}")
                if len(data_before) > 0:
                    print(f"      Latest price: ${data_before['Close'].iloc[-1]:.2f}")
                    if len(data_before) >= 50:
                        high_50d = data_before['Close'].rolling(50).max().iloc[-1]
                        current = data_before['Close'].iloc[-1]
                        pct_from_high = ((current / high_50d) - 1) * 100
                        print(f"      50-day high: ${high_50d:.2f} (current is {pct_from_high:+.1f}% from high)")
    
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
