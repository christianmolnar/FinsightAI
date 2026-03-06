"""Test backtester with 1-year period"""

import asyncio
from datetime import datetime, timedelta
from app.database import SessionLocal
from services.backtester import Backtester

async def main():
    print("🧪 Testing backtester with 1-year historical data...\n")

    db = SessionLocal()

    # Test 1-year backtest
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    print(f"📅 Backtest period: {start_date.date()} to {end_date.date()}")
    print(f"⏱️  Starting backtest...\n")

    # Create backtester with $100K capital
    backtester = Backtester(db, initial_capital=100000.0)

    # Run backtest
    results = await backtester.run_backtest(
        start_date=start_date,
        end_date=end_date
    )

    print(f"\n✅ Backtest complete\n")
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

    if results.total_trades == 0:
        print("\n⚠️  WARNING: No trades found even with 1-year data.")
        print("   This suggests the scanner isn't finding any opportunities.")
        print("   Check MarketScanner logic and data availability.")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
