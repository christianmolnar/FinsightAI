"""
Debug: Check data structure
"""
import asyncio
from datetime import datetime, timedelta
from services.historical_data_manager import HistoricalDataManager
from services.market_scanner import MarketScanner
from app.database import SessionLocal


async def main():
    db = SessionLocal()
    hist_mgr = HistoricalDataManager(db)
    scanner = MarketScanner(db)
    
    # Get data for AAPL
    symbol = 'AAPL'
    test_date = datetime(2026, 3, 1)
    
    print(f'🔍 Checking data structure for {symbol}...')
    print(f'')
    
    df = hist_mgr.get_historical_data(
        symbol=symbol,
        start_date=test_date - timedelta(days=200),
        end_date=test_date + timedelta(days=30)
    )
    
    print(f'DataFrame shape: {df.shape}')
    print(f'DataFrame columns: {list(df.columns)}')
    print(f'Index type: {type(df.index)}')
    print(f'Index name: {df.index.name}')
    print(f'')
    print(f'First 3 rows:')
    print(df.head(3))
    print(f'')
    print(f'Last 3 rows:')
    print(df.tail(3))
    print(f'')
    
    # Try filtering by date
    print(f'Testing filter: data[data.index <= {test_date}]...')
    try:
        filtered = df[df.index <= test_date]
        print(f'Filtered shape: {filtered.shape}')
        print(f'Last row after filter:')
        print(filtered.tail(1))
    except Exception as e:
        print(f'❌ Filter failed: {e}')
        print(f'')
        print(f'Trying timezone-aware comparison...')
        test_date_aware = test_date.replace(tzinfo=df.index.tzinfo)
        filtered = df[df.index <= test_date_aware]
        print(f'Filtered shape: {filtered.shape}')
        print(f'Last row after filter:')
        print(filtered.tail(1))
    
    db.close()


if __name__ == '__main__':
    asyncio.run(main())
