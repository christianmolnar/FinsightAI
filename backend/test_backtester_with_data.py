"""
Quick test to verify backtester finds trades with full historical data
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal
from services.backtester import Backtester

# Create database session
db = SessionLocal()

try:
    print("🧪 Testing backtester with full historical data...\n")
    
    # Initialize backtester
    backtester = Backtester(db, initial_capital=100000)
    
    # Run a 90-day backtest (should be fast now with cached data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"📅 Backtest period: {start_date.date()} to {end_date.date()}")
    print(f"⏱️  Starting backtest...\n")
    
    start_time = datetime.now()
    
    # Use async method
    import asyncio
    results = asyncio.run(backtester.run_backtest(
        start_date=start_date,
        end_date=end_date
    ))
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print(f"\n✅ Backtest complete in {elapsed:.2f} seconds\n")
    print("=" * 60)
    print("RESULTS:")
    print("=" * 60)
    print(f"Total Trades: {results.total_trades}")
    print(f"Winning Trades: {results.winning_trades}")
    print(f"Losing Trades: {results.losing_trades}")
    print(f"Win Rate: {results.win_rate:.1f}%")
    print(f"Total Return: {results.total_return_pct:.2f}%")
    print(f"Final Portfolio Value: ${results.final_capital:,.2f}")
    print("=" * 60)
    
    # Check if we found trades
    if results.total_trades > 0:
        print("\n🎉 SUCCESS! Backtester is finding trades with cached data!")
    else:
        print("\n⚠️  WARNING: No trades found. May need more data or different parameters.")
        
finally:
    db.close()
