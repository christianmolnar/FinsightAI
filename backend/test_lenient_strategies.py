"""
Test scanner with very lenient thresholds to see what it finds
"""
import asyncio
from datetime import datetime, timedelta
from services.market_scanner import MarketScanner
from services.historical_data_manager import HistoricalDataManager
from app.database import SessionLocal
import pandas as pd


async def main():
    db = SessionLocal()
    scanner = MarketScanner(db)
    hist_mgr = HistoricalDataManager(db)
    
    # Test single recent date
    test_date = datetime(2026, 3, 1)
    
    print(f'🔍 Testing what scanner would find on {test_date.strftime("%Y-%m-%d")}...')
    print(f'📊 Universe size: {len(scanner.SCAN_UNIVERSE)} stocks')
    print(f'')
    
    # Get data for all stocks
    data_dict = {}
    for symbol in scanner.SCAN_UNIVERSE:
        try:
            df = hist_mgr.get_historical_data(
                symbol=symbol,
                start_date=test_date - timedelta(days=200),  # Need 50+ days for indicators
                end_date=test_date
            )
            if not df.empty and len(df) >= 50:
                data_dict[symbol] = df
        except Exception as e:
            print(f'❌ Failed to get data for {symbol}: {e}')
    
    print(f'✅ Got data for {len(data_dict)} stocks')
    print(f'')
    
    # Check how many are near their highs (VERY lenient - within 10%)
    print(f'🔍 Checking how many stocks are within 10% of 50-day high...')
    near_high = []
    for symbol, df in data_dict.items():
        if len(df) >= 50:
            current_price = df['Close'].iloc[-1]
            high_50d = df['High'].rolling(window=50).max().iloc[-1]
            pct_from_high = ((current_price / high_50d) - 1) * 100
            
            if current_price >= high_50d * 0.90:  # Within 10%
                near_high.append((symbol, current_price, high_50d, pct_from_high))
    
    print(f'📊 Found {len(near_high)} stocks within 10% of 50-day high:')
    for symbol, price, high, pct in sorted(near_high, key=lambda x: x[3], reverse=True)[:10]:
        print(f'  {symbol}: ${price:.2f} (50d high: ${high:.2f}, {pct:+.1f}%)')
    
    print(f'')
    
    # Check momentum (any stock up 3%+ in 5 days)
    print(f'🔍 Checking momentum (up 3%+ in 5 days)...')
    momentum_stocks = []
    for symbol, df in data_dict.items():
        if len(df) >= 6:
            current_price = df['Close'].iloc[-1]
            price_5d_ago = df['Close'].iloc[-6]
            momentum = ((current_price / price_5d_ago) - 1) * 100
            
            if momentum > 3.0:
                momentum_stocks.append((symbol, momentum, current_price))
    
    print(f'📊 Found {len(momentum_stocks)} stocks up 3%+ in 5 days:')
    for symbol, mom, price in sorted(momentum_stocks, key=lambda x: x[1], reverse=True)[:10]:
        print(f'  {symbol}: +{mom:.1f}% (${price:.2f})')
    
    print(f'')
    print(f'✅ Summary:')
    print(f'  - {len(data_dict)} stocks with data')
    print(f'  - {len(near_high)} near highs (10% threshold)')
    print(f'  - {len(momentum_stocks)} with momentum (3%+ in 5d)')
    
    db.close()


if __name__ == '__main__':
    asyncio.run(main())
