"""
Test backtester with database-first approach
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from services.backtester import get_backtester

async def test_backtest():
    print("🧪 Testing Backtester with Database-First Approach\n")
    
    db = SessionLocal()
    
    try:
        # Simple 30-day backtest
        end_date = datetime(2026, 4, 24)  # Latest date in database
        start_date = end_date - timedelta(days=30)
        
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial capital: $10,000")
        print(f"Max hold days: 14\n")
        
        # Get backtester
        backtester = get_backtester(
            db=db,
            initial_capital=10000.0,
            position_size_pct=0.10,  # 10% per position
            max_hold_days=14
        )
        
        print("Running backtest...")
        
        # Run backtest
        result = await backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            strategies=['technical_breakout'],  # Just one strategy for testing
            confidence_threshold=0.70,
            use_ai=False  # Disable AI for speed
        )
        
        print("\n✅ Backtest Complete!\n")
        
        # result is BacktestMetrics object - convert to dict
        metrics_dict = result.to_dict()
        
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"\nTrades: {metrics_dict['summary']['total_trades']}")
        print(f"Win Rate: {metrics_dict['summary']['win_rate']}%")
        print(f"Total Return: {metrics_dict['returns']['total_return_pct']}%")
        print(f"Net Profit: ${metrics_dict['returns']['net_profit']}")
        print(f"Final Capital: ${metrics_dict['returns']['final_capital']}")
        
        if metrics_dict['summary']['total_trades'] > 0:
            print(f"\nPerformance:")
            print(f"  Avg Win: ${metrics_dict['performance']['avg_win']:.2f}")
            print(f"  Avg Loss: ${metrics_dict['performance']['avg_loss']:.2f}")
            print(f"  Profit Factor: {metrics_dict['performance']['profit_factor']:.2f}")
            print(f"  Avg Hold: {metrics_dict['performance']['avg_hold_days']:.1f} days")
            
            if metrics_dict['risk_metrics']['sharpe_ratio']:
                print(f"\nRisk Metrics:")
                print(f"  Sharpe Ratio: {metrics_dict['risk_metrics']['sharpe_ratio']:.2f}")
                print(f"  Max Drawdown: {metrics_dict['risk_metrics']['max_drawdown']:.2f}%")
        
        if result.trades:
            print(f"\n📊 Sample Trades:")
            for i, trade in enumerate(result.trades[:5], 1):
                print(f"\n{i}. {trade.symbol}")
                print(f"   Entry: {trade.entry_date.date()} @ ${trade.entry_price:.2f}")
                print(f"   Exit: {trade.exit_date.date()} @ ${trade.exit_price:.2f}")
                print(f"   Return: {trade.return_pct:.2f}% ({trade.exit_reason})")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_backtest())
