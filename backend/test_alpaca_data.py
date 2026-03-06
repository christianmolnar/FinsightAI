"""
Quick test of Alpaca Data API integration
"""

from app.services.alpaca_service import get_alpaca_service
from datetime import datetime, timedelta

def test_alpaca_data():
    print("\n" + "="*60)
    print("TESTING ALPACA DATA API")
    print("="*60 + "\n")
    
    try:
        # Initialize service
        print("1. Initializing Alpaca service...")
        alpaca = get_alpaca_service(paper=True)
        print("   ✅ Service initialized\n")
        
        # Test single symbol download
        print("2. Testing single symbol download (AAPL, last 30 days)...")
        start = datetime.now() - timedelta(days=30)
        end = datetime.now()
        
        df = alpaca.get_historical_bars_single(
            symbol='AAPL',
            start=start,
            end=end,
            timeframe='1Day'
        )
        
        print(f"   ✅ Downloaded {len(df)} days of data")
        print(f"   Columns: {list(df.columns)}")
        print(f"\n   First row:")
        if len(df) > 0:
            print(f"   {df.iloc[0]}\n")
        
        # Test batch download
        print("3. Testing batch download (AAPL, MSFT, GOOGL)...")
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        bars_dict = alpaca.get_historical_bars(
            symbols=symbols,
            start=start,
            end=end,
            timeframe='1Day'
        )
        
        print(f"   ✅ Downloaded data for {len(bars_dict)} symbols:")
        for symbol, df in bars_dict.items():
            print(f"      {symbol}: {len(df)} days")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - Alpaca Data API working!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_alpaca_data()
