"""
Simple diagnostic test for Alpaca API
"""

from app.services.alpaca_service import get_alpaca_service
from datetime import datetime, timedelta

print("Testing Alpaca API...")
print("=" * 60)

try:
    # Initialize service
    alpaca = get_alpaca_service(paper=True)
    print("✓ Service initialized")
    
    # Test 1: Account info
    print("\n1. Testing account info...")
    account = alpaca.get_account()
    print(f"   Account ID: {account['id']}")
    print(f"   Buying Power: ${account['buying_power']:,.2f}")
    print("   ✓ Account info works")
    
    # Test 2: Latest quote
    print("\n2. Testing latest quote...")
    quote = alpaca.get_quote("AAPL")
    print(f"   AAPL Bid: ${quote['bid_price']:.2f}")
    print(f"   AAPL Ask: ${quote['ask_price']:.2f}")
    print(f"   Timestamp: {quote['timestamp']}")
    print("   ✓ Quote works")
    
    # Test 3: Historical bars with different date ranges
    print("\n3. Testing historical bars...")
    
    # Try current date
    end = datetime.now()
    start = end - timedelta(days=7)
    print(f"   Trying {start.date()} to {end.date()}...")
    
    df = alpaca.get_historical_bars_single("AAPL", start, end)
    print(f"   Result: {len(df)} bars")
    
    if df.empty:
        # Try further back
        end = datetime(2024, 12, 31)
        start = end - timedelta(days=30)
        print(f"\n   Trying historical: {start.date()} to {end.date()}...")
        df = alpaca.get_historical_bars_single("AAPL", start, end)
        print(f"   Result: {len(df)} bars")
        
        if not df.empty:
            print(f"   Latest bar: {df.index[-1]}")
            print(f"   Close: ${df['close'].iloc[-1]:.2f}")
            print("   ✓ Historical data works (but current date issue)")
        else:
            print("   ✗ No data even for 2024")
    else:
        print(f"   Latest bar: {df.index[-1]}")
        print(f"   Close: ${df['close'].iloc[-1]:.2f}")
        print("   ✓ Historical data works")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
