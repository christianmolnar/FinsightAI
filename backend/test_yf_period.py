import yfinance as yf, time
from datetime import datetime

start_cutoff = datetime.strptime("2016-01-04", "%Y-%m-%d").date()

for sym in ["ACGL", "GLD", "XLK"]:
    t0 = time.time()
    ticker = yf.Ticker(sym)
    df = ticker.history(period="max", interval="1d", auto_adjust=True)
    if df.index.tzinfo:
        df.index = df.index.tz_localize(None)
    df = df[df.index.date >= start_cutoff]
    print(f"{sym}: {len(df)} rows in {time.time()-t0:.1f}s")
