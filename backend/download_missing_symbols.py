"""Download full 10-year data for previously skipped symbols"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import HistoricalPrice
from app.services.alpaca_service import get_alpaca_service
import pandas as pd

# Symbols that were skipped (had incomplete test data)
SYMBOLS_TO_DOWNLOAD = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
    'ABBV', 'ABNB', 'ABT', 'ADBE', 'ADI', 
    'ADP', 'AMAT', 'AMD', 'AMGN', 'AVGO',
    'AXP', 'BA', 'BAC', 'BKNG', 'BLK',
    'C', 'CAT', 'CMCSA', 'COP', 'COST',
    'CRM', 'CSCO', 'CVX', 'DE', 'DHR'
]

# Date range (10 years)
end_date = datetime.now()
start_date = end_date - timedelta(days=10 * 365)

print(f"📊 Downloading {len(SYMBOLS_TO_DOWNLOAD)} symbols...")
print(f"📅 Date range: {start_date.date()} to {end_date.date()}")
print(f"⏰ Estimated time: 5-10 minutes\n")

alpaca = get_alpaca_service()
db = SessionLocal()

total_rows = 0
successful = 0
failed = 0

for i, symbol in enumerate(SYMBOLS_TO_DOWNLOAD, 1):
    try:
        print(f"[{i}/{len(SYMBOLS_TO_DOWNLOAD)}] Downloading {symbol}...", end=' ', flush=True)
        
        # Download from Alpaca
        df = alpaca.get_historical_bars_single(
            symbol=symbol,
            start=start_date,
            end=end_date,
            timeframe="1Day"
        )
        
        if df.empty:
            print("❌ No data")
            failed += 1
            continue
        
        # Save to database
        for idx, row in df.iterrows():
            if isinstance(idx, pd.Timestamp):
                date_value = idx.date()
            else:
                date_value = idx
            
            price = HistoricalPrice(
                symbol=symbol,
                date=date_value,
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            )
            db.add(price)
        
        db.commit()
        total_rows += len(df)
        successful += 1
        print(f"✅ {len(df)} rows")
        
    except Exception as e:
        print(f"❌ {e}")
        db.rollback()
        failed += 1

db.close()

print(f"\n🎉 Complete!")
print(f"   Successful: {successful}")
print(f"   Failed: {failed}")
print(f"   Total rows: {total_rows:,}")
