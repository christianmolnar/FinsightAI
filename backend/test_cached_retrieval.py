from app.database import SessionLocal
from services.historical_data_manager import HistoricalDataManager
from datetime import datetime, timedelta

db = SessionLocal()
manager = HistoricalDataManager(db)

end = datetime(2026, 3, 1)
start = end - timedelta(days=30)

print('Testing HistoricalDataManager.get_historical_data()...')
df = manager.get_historical_data('AAPL', start, end)
print(f'✅ Retrieved {len(df)} rows for AAPL')
print(f'Date range: {df.index[0]} to {df.index[-1]}')
print(f'Latest close: ${df["close"].iloc[-1]:.2f}')

db.close()
