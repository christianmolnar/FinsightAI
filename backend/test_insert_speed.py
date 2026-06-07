import sys, time
sys.path.insert(0, '.')
import yfinance as yf
from datetime import datetime
from app.database import SessionLocal
import sqlalchemy

start_cutoff = datetime.strptime("2016-01-04", "%Y-%m-%d").date()
sym = "ACGL"

t0 = time.time()
df = yf.Ticker(sym).history(period="max", interval="1d", auto_adjust=True)
df.index = df.index.tz_localize(None) if df.index.tzinfo else df.index
df = df[df.index.date >= start_cutoff]
print(f"Downloaded {sym}: {len(df)} rows in {time.time()-t0:.2f}s")

rows = [{"symbol": sym, "date": dt.date(), "open": float(r.get("Open") or 0),
         "high": float(r.get("High") or 0), "low": float(r.get("Low") or 0),
         "close": float(r.get("Close") or 0), "volume": int(r.get("Volume") or 0)}
        for dt, r in df.iterrows()]

t1 = time.time()
db = SessionLocal()
BATCH = 200
for i in range(0, len(rows), BATCH):
    db.execute(sqlalchemy.text("""
        INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
        VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
        ON CONFLICT (symbol, date) DO UPDATE SET open=EXCLUDED.open,
        high=EXCLUDED.high, low=EXCLUDED.low, close=EXCLUDED.close, volume=EXCLUDED.volume
    """), rows[i:i+BATCH])
    db.commit()
    print(f"  Batch {i//BATCH+1} committed")
db.close()
print(f"Insert time: {time.time()-t1:.2f}s total")
