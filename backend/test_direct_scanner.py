"""
Direct test of backtester scanning strategies
"""
import asyncio
from datetime import datetime, timedelta
from services.backtester import Backtester
from services.historical_data_manager import HistoricalDataManager
from app.database import SessionLocal


async def main():
    db = SessionLocal()
    backtester = Backtester(db)
    hist_mgr = HistoricalDataManager(db)
    
    # Test on date we know has opportunities
    test_date = datetime(2026, 3, 1)
    
    print(f'🔍 Testing backtester scanner on {test_date.strftime("%Y-%m-%d")}...')
    print(f'📊 Universe size: {len(backtester.scanner.SCAN_UNIVERSE)} stocks')
    print(f'')
    
    # Download data (same as backtester does)
    print(f'📥 Downloading historical data...')
    data_start = test_date - timedelta(days=365)
    data_end = test_date + timedelta(days=30)
    
    universe_data = hist_mgr.get_batch_historical_data(
        symbols=list(backtester.scanner.SCAN_UNIVERSE),
        start_date=data_start,
        end_date=data_end
    )
    
    print(f'✅ Got data for {len(universe_data)} stocks')
    print(f'')
    
    # Test breakout scanner
    print(f'🔍 Testing breakout scanner...')
    breakouts = backtester._scan_breakouts_historical(universe_data, test_date)
    print(f'📊 Found {len(breakouts)} breakout candidates:')
    for candidate in breakouts[:10]:
        print(f'  {candidate["symbol"]}: ${candidate["price"]:.2f} - {candidate["reason"]}')
    
    print(f'')
    
    # Test earnings/momentum scanner
    print(f'🔍 Testing momentum scanner...')
    momentum = backtester._scan_earnings_historical(universe_data, test_date)
    print(f'📊 Found {len(momentum)} momentum candidates:')
    for candidate in momentum[:10]:
        print(f'  {candidate["symbol"]}: ${candidate["price"]:.2f} - {candidate["reason"]}')
    
    print(f'')
    print(f'✅ Summary:')
    print(f'  - {len(breakouts)} breakout candidates')
    print(f'  - {len(momentum)} momentum candidates')
    print(f'  - {len(breakouts) + len(momentum)} total candidates')
    
    db.close()


if __name__ == '__main__':
    asyncio.run(main())
