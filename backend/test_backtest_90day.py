"""
Test backtester with 90-day historical data
"""
import asyncio
from datetime import datetime, timedelta
from services.backtester import Backtester
from app.database import SessionLocal


async def main():
    db = SessionLocal()
    
    # Create backtester with initial capital
    backtester = Backtester(db, initial_capital=100000.0)
    
    # Test with 90 days
    end_date = datetime(2026, 3, 2)
    start_date = end_date - timedelta(days=90)
    
    print(f'🧪 Testing backtester with 90-day historical data...')
    print(f'')
    print(f'📅 Backtest period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
    print(f'⏱️  Starting backtest...')
    print(f'')
    
    results = await backtester.run_backtest(
        start_date=start_date,
        end_date=end_date,
        use_ai=False  # Bypass random AI filter for now
    )
    
    print(f'')
    print(f'✅ Backtest complete')
    print(f'')
    print('=' * 60)
    print('RESULTS:')
    print('=' * 60)
    print(f'Total Trades: {results.total_trades}')
    print(f'Winning Trades: {results.winning_trades}')
    print(f'Losing Trades: {results.losing_trades}')
    
    if results.total_trades > 0:
        print(f'Win Rate: {results.win_rate:.1f}%')
        print(f'Total Return: {results.total_return_pct:+.2f}%')
        print(f'Final Portfolio Value: ${results.final_capital:,.2f}')
        
        print(f'')
        print(f'First 5 trades:')
        for i, trade in enumerate(results.trades[:5]):
            print(f'  {i+1}. {trade.symbol}: {trade.strategy} - P&L: ${trade.profit_loss:+.2f}')
    else:
        print(f'Win Rate: 0.0%')
        print(f'Total Return: 0.00%')
        print(f'Final Portfolio Value: ${results.initial_capital:,.2f}')
        print(f'')
        print(f'⚠️  WARNING: No trades found.')
    
    print('=' * 60)
    
    db.close()


if __name__ == '__main__':
    asyncio.run(main())
