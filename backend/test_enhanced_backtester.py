"""
Test Enhanced Backtester with New Metrics

Tests:
1. Sharpe ratio calculation
2. Max drawdown calculation
3. Daily P&L tracking
4. Largest win/loss tracking
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from services.backtester import Backtester

load_dotenv()

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def test_enhanced_backtester():
    """Test the enhanced backtester with new metrics"""
    
    print("🧪 TESTING ENHANCED BACKTESTER")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Create backtester
        backtester = Backtester(
            db=db,
            initial_capital=100000.0,
            position_size=10000.0,
            max_hold_days=14
        )
        
        # Run 90-day backtest
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        print(f"\n📅 Running backtest: {start_date.date()} to {end_date.date()}")
        print(f"   Initial Capital: $100,000")
        print(f"   Position Size: $10,000")
        print(f"   Max Hold Days: 14")
        print()
        
        # Run backtest
        metrics = await backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            strategies=None,  # All strategies
            confidence_threshold=0.75,
            use_ai=False  # Scanner only for speed
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 ENHANCED METRICS TEST RESULTS")
        print("=" * 60)
        
        print("\n🎯 BASIC METRICS:")
        print(f"   Total Trades: {metrics.total_trades}")
        print(f"   Win Rate: {metrics.win_rate:.2f}%")
        print(f"   Net Profit: ${metrics.net_profit:,.2f}")
        print(f"   Total Return: {metrics.total_return_pct:+.2f}%")
        print(f"   Profit Factor: {metrics.profit_factor:.2f}")
        
        print("\n📈 NEW RISK METRICS:")
        print(f"   Max Drawdown: {metrics.max_drawdown:.2f}%")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}" if metrics.sharpe_ratio else "   Sharpe Ratio: N/A")
        print(f"   Largest Win: ${metrics.largest_win:,.2f}")
        print(f"   Largest Loss: ${metrics.largest_loss:,.2f}")
        print(f"   Avg Win Size: ${metrics.avg_win_size:,.2f}")
        print(f"   Avg Loss Size: ${metrics.avg_loss_size:,.2f}")
        
        print("\n📅 DAILY P&L TRACKING:")
        if metrics.daily_pnl:
            num_days = len(metrics.daily_pnl)
            total_pnl = sum(metrics.daily_pnl.values())
            print(f"   Days with P&L: {num_days}")
            print(f"   Total P&L: ${total_pnl:,.2f}")
            
            # Show first 5 and last 5 days
            sorted_dates = sorted(metrics.daily_pnl.keys())
            print(f"\n   First 5 days:")
            for date in sorted_dates[:5]:
                pnl = metrics.daily_pnl[date]
                print(f"      {date}: ${pnl:+,.2f}")
            
            if len(sorted_dates) > 10:
                print(f"\n   Last 5 days:")
                for date in sorted_dates[-5:]:
                    pnl = metrics.daily_pnl[date]
                    print(f"      {date}: ${pnl:+,.2f}")
        else:
            print("   ❌ No daily P&L data tracked")
        
        # Verify all new metrics are present
        print("\n✅ VERIFICATION:")
        checks = [
            ("Max Drawdown", metrics.max_drawdown is not None),
            ("Sharpe Ratio", metrics.sharpe_ratio is not None or len(metrics.daily_pnl) < 2),
            ("Largest Win", metrics.largest_win != 0),
            ("Largest Loss", metrics.largest_loss != 0),
            ("Daily P&L", len(metrics.daily_pnl) > 0),
        ]
        
        all_pass = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"   {status} {check_name}")
            if not check_result:
                all_pass = False
        
        if all_pass:
            print("\n🎉 ALL ENHANCED METRICS WORKING!")
        else:
            print("\n⚠️  SOME METRICS MISSING - CHECK IMPLEMENTATION")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_enhanced_backtester())
