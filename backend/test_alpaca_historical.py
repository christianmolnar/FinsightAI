"""
Test Alpaca Historical Data API Integration

This script tests the new Alpaca-based historical data methods
to ensure they work correctly before updating the full system.
"""

from app.services.alpaca_service import get_alpaca_service
from datetime import datetime, timedelta
import sys


def test_single_symbol():
    """Test fetching historical data for a single symbol"""
    print("=" * 60)
    print("TEST 1: Single Symbol Historical Data")
    print("=" * 60)
    
    try:
        alpaca = get_alpaca_service(paper=True)
        print("✓ AlpacaService initialized\n")
        
        # Test with AAPL for 30 days
        symbol = 'AAPL'
        end = datetime.now()
        start = end - timedelta(days=30)
        
        print(f"Fetching {symbol} data from {start.date()} to {end.date()}...")
        df = alpaca.get_historical_bars_single(symbol, start, end)
        
        if not df.empty:
            print(f"✓ SUCCESS: Retrieved {len(df)} bars")
            print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"  Latest close: ${df['close'].iloc[-1]:.2f}")
            print("\nFirst 3 rows:")
            print(df.head(3))
            print("\nLast 3 rows:")
            print(df.tail(3))
            return True
        else:
            print("✗ FAILED: No data returned")
            return False
            
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_symbols():
    """Test fetching historical data for multiple symbols"""
    print("\n" + "=" * 60)
    print("TEST 2: Multiple Symbols Historical Data")
    print("=" * 60)
    
    try:
        alpaca = get_alpaca_service(paper=True)
        
        # Test with multiple symbols
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        end = datetime.now()
        start = end - timedelta(days=7)
        
        print(f"Fetching data for {symbols} (last 7 days)...")
        result = alpaca.get_historical_bars(symbols, start, end)
        
        success = True
        for symbol in symbols:
            if symbol in result and not result[symbol].empty:
                df = result[symbol]
                print(f"✓ {symbol}: {len(df)} bars, latest close: ${df['close'].iloc[-1]:.2f}")
            else:
                print(f"✗ {symbol}: No data returned")
                success = False
        
        return success
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Test performance with batch download"""
    print("\n" + "=" * 60)
    print("TEST 3: Performance Test (10 symbols)")
    print("=" * 60)
    
    try:
        import time
        alpaca = get_alpaca_service(paper=True)
        
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
                   'TSLA', 'NVDA', 'JPM', 'BAC', 'WFC']
        end = datetime.now()
        start = end - timedelta(days=90)
        
        print(f"Fetching 90 days of data for {len(symbols)} symbols...")
        start_time = time.time()
        
        result = alpaca.get_historical_bars(symbols, start, end)
        
        elapsed = time.time() - start_time
        
        total_bars = sum(len(df) for df in result.values() if not df.empty)
        success_count = sum(1 for df in result.values() if not df.empty)
        
        print(f"\n✓ Completed in {elapsed:.2f} seconds")
        print(f"  Successful: {success_count}/{len(symbols)} symbols")
        print(f"  Total bars: {total_bars}")
        print(f"  Rate: {total_bars/elapsed:.1f} bars/second")
        
        return success_count == len(symbols)
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Testing Alpaca Historical Data API Integration")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Single Symbol", test_single_symbol()))
    results.append(("Multiple Symbols", test_multiple_symbols()))
    results.append(("Performance", test_performance()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Alpaca integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
