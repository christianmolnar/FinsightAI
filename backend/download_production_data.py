"""
Production Historical Data Downloader
Downloads 10 years of data for the full universe with visible progress
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app.models import HistoricalPrice
from app.services.alpaca_service import get_alpaca_service
from services.universe_builder import UniverseBuilder

# Create table
print("📊 Creating historical_prices table...")
HistoricalPrice.__table__.create(bind=engine, checkfirst=True)
print("✅ Table ready\n")

# Build universe
print("🌍 Building stock universe...")
builder = UniverseBuilder()
universe = builder.build_universe(['SP500', 'DOW', 'NASDAQ100'])
print(f"✅ Universe: {len(universe)} unique stocks\n")

# Date range (10 years)
end_date = datetime.now()
start_date = end_date - timedelta(days=10 * 365)

print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
print(f"⏰ Estimated time: 30-60 minutes\n")
print("="*60)

# Get Alpaca service
alpaca = get_alpaca_service(paper=True)
db = SessionLocal()

# Download in batches of 50
batch_size = 50
total_rows = 0
successful = 0
failed = 0

for i in range(0, len(universe), batch_size):
    batch = universe[i:i+batch_size]
    batch_num = i//batch_size + 1
    total_batches = (len(universe)-1)//batch_size + 1
    
    print(f"\n🔄 Batch {batch_num}/{total_batches}: Processing {len(batch)} stocks...")
    print(f"   Symbols: {', '.join(batch[:5])}{'...' if len(batch) > 5 else ''}")
    
    try:
        # Fetch from Alpaca
        bars_dict = alpaca.get_historical_bars(
            symbols=batch,
            start=start_date,
            end=end_date,
            timeframe="1Day"
        )
        
        # Insert into database
        for symbol, df in bars_dict.items():
            if df.empty:
                print(f"      ⚠️  {symbol}: No data")
                failed += 1
                continue
            
            try:
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
                
                db.commit()
                total_rows += len(df)
                successful += 1
                print(f"      ✅ {symbol}: {len(df)} rows")
                
            except Exception as e:
                # Skip duplicate key errors (data already exists)
                if "duplicate key" in str(e).lower():
                    print(f"      ⏭️  {symbol}: Data already exists (skipped)")
                    successful += 1
                else:
                    print(f"      ❌ {symbol}: {e}")
                    failed += 1
                db.rollback()
        
        print(f"   Batch complete: {successful} successful, {failed} failed, {total_rows:,} total rows")
        
    except Exception as e:
        print(f"   ❌ Batch error: {e}")
        failed += len(batch)

print("\n" + "="*60)
print(f"\n🎉 DOWNLOAD COMPLETE!")
print(f"   Total stocks processed: {len(universe)}")
print(f"   Successful: {successful}")
print(f"   Failed: {failed}")
print(f"   Total rows inserted: {total_rows:,}")
print(f"   Estimated DB size: ~{(total_rows * 100) / (1024 * 1024):.1f} MB")

db.close()

# Final verification
print("\n📊 Database verification...")
db2 = SessionLocal()
try:
    count = db2.query(HistoricalPrice).count()
    symbols_count = db2.query(HistoricalPrice.symbol).distinct().count()
    print(f"   Total rows in DB: {count:,}")
    print(f"   Unique symbols: {symbols_count}")
finally:
    db2.close()

print("\n✅ System ready for backtesting!")
