"""
Debug Alpaca historical bars API response
"""

from app.services.alpaca_service import AlpacaService
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

print("Debugging Alpaca Historical Bars API")
print("=" * 60)

try:
    alpaca = AlpacaService(paper=True)
    print("✓ Service initialized\n")
    
    # Test with explicit API call
    print("Making direct API call...")
    
    end = datetime(2024, 12, 31)
    start = datetime(2024, 12, 1)
    
    request = StockBarsRequest(
        symbol_or_symbols=["AAPL"],
        timeframe=TimeFrame.Day,
        start=start,
        end=end
    )
    
    print(f"Request: {['AAPL']} from {start} to {end}")
    print(f"Timeframe: {TimeFrame.Day}\n")
    
    response = alpaca.market_data_client.get_stock_bars(request)
    
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print(f"Response keys: {response.keys() if hasattr(response, 'keys') else 'N/A'}")
    
    if 'AAPL' in response:
        bars = response['AAPL']
        print(f"\nAAPL bars type: {type(bars)}")
        print(f"AAPL bars count: {len(bars)}")
        
        if len(bars) > 0:
            first_bar = bars[0]
            print(f"\nFirst bar:")
            print(f"  Timestamp: {first_bar.timestamp}")
            print(f"  Open: {first_bar.open}")
            print(f"  Close: {first_bar.close}")
    else:
        print("\n⚠️  AAPL not in response")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
