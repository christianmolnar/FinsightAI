"""
Quick test of historical data download
Downloads 1 year of data for 5 stocks to test the system
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app.models import HistoricalPrice
from app.services.alpaca_service import get_alpaca_service

# Create table
print("Creating table...")
HistoricalPrice.__table__.create(bind=engine, checkfirst=True)
print("✅ Table ready")

# Test symbols
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

# Date range (1 year)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

print(f"\nFetching 1 year of data for {len(symbols)} stocks...")
print(f"Date range: {start_date.date()} to {end_date.date()}")

# Get Alpaca service
alpaca = get_alpaca_service(paper=True)

# Fetch data
print("\nCalling Alpaca API...")
bars_dict = alpaca.get_historical_bars(
    symbols=symbols,
    start=start_date,
    end=end_date,
    timeframe="1Day"
)

print(f"\n✅ Received data for {len(bars_dict)} symbols")

# Insert into database
db = SessionLocal()
total_rows = 0

try:
    for symbol, df in bars_dict.items():
        if df.empty:
            print(f"   ⚠️  {symbol}: No data")
            continue
        
        print(f"   📊 {symbol}: {len(df)} rows")
        
        for idx, row in df.iterrows():
            price_record = HistoricalPrice(
                symbol=symbol,
                date=idx.date(),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            )
            db.add(price_record)
            total_rows += 1
    
    db.commit()
    print(f"\n✅ INSERTED {total_rows} rows into database")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    db.rollback()
finally:
    db.close()

# Verify
db2 = SessionLocal()
try:
    count = db2.query(HistoricalPrice).count()
    unique_symbols = db2.query(HistoricalPrice.symbol).distinct().count()
    print(f"\n📊 Database verification:")
    print(f"   Total rows: {count}")
    print(f"   Unique symbols: {unique_symbols}")
finally:
    db2.close()

print("\n🎉 Test complete!")
