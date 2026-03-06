"""Test direct database query to see what data exists"""

from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models import HistoricalPrice
from sqlalchemy import and_, func

db = SessionLocal()

# Test for specific symbols
test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

print("\n🔍 Checking database for test symbols...\n")

for symbol in test_symbols:
    count = db.query(func.count(HistoricalPrice.id)).filter(
        HistoricalPrice.symbol == symbol
    ).scalar()
    
    if count > 0:
        earliest = db.query(func.min(HistoricalPrice.date)).filter(
            HistoricalPrice.symbol == symbol
        ).scalar()
        
        latest = db.query(func.max(HistoricalPrice.date)).filter(
            HistoricalPrice.symbol == symbol
        ).scalar()
        
        print(f"✅ {symbol}: {count} rows ({earliest} to {latest})")
    else:
        print(f"❌ {symbol}: NO DATA")

# Check 90-day window
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

print(f"\n🗓️  90-day window: {start_date.date()} to {end_date.date()}\n")

for symbol in test_symbols:
    count = db.query(func.count(HistoricalPrice.id)).filter(
        and_(
            HistoricalPrice.symbol == symbol,
            HistoricalPrice.date >= start_date.date(),
            HistoricalPrice.date <= end_date.date()
        )
    ).scalar()
    
    print(f"   {symbol}: {count} rows in window")

db.close()
