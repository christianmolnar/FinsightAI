"""
daily_update.py — runs every weekday after market close to add the latest bar.

Designed to run as a Railway cron job. Updates all symbols in historical_prices
with any missing bars since their last entry. Safe to run multiple times (ON CONFLICT DO UPDATE).
"""
import sys, os, time, logging
sys.path.insert(0, os.path.dirname(__file__))

import yfinance as yf
from datetime import datetime, timedelta
import sqlalchemy
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)


def get_symbols_needing_update(db):
    """Return symbols whose latest bar is before today."""
    today = datetime.now().date()
    result = db.execute(sqlalchemy.text("""
        SELECT symbol, MAX(date) as latest
        FROM historical_prices
        GROUP BY symbol
        HAVING MAX(date) < :today
        ORDER BY symbol
    """), {"today": today}).fetchall()
    return [(r[0], r[1]) for r in result]


def update_symbol(db, symbol, from_date):
    today = datetime.now().strftime("%Y-%m-%d")
    from_str = (from_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    df = yf.download(symbol, start=from_str, end=today,
                     auto_adjust=True, progress=False, timeout=15)
    if df is None or df.empty:
        return 0

    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)

    rows = []
    for dt, row in df.iterrows():
        date_val = dt.date() if hasattr(dt, 'date') else dt
        rows.append({
            "symbol": symbol,
            "date": date_val,
            "open": float(row.get("Open") or 0),
            "high": float(row.get("High") or 0),
            "low": float(row.get("Low") or 0),
            "close": float(row.get("Close") or 0),
            "volume": int(row.get("Volume") or 0),
        })

    if not rows:
        return 0

    db.execute(sqlalchemy.text("""
        INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
        VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
        ON CONFLICT (symbol, date) DO UPDATE SET
            open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
            close=EXCLUDED.close, volume=EXCLUDED.volume
    """), rows)
    db.commit()
    return len(rows)


def main():
    db = SessionLocal()
    try:
        stale = get_symbols_needing_update(db)
        if not stale:
            log.info("All symbols already current. Nothing to do.")
            return

        log.info(f"Updating {len(stale)} symbols...")
        total_bars = 0
        errors = 0

        for i, (symbol, latest) in enumerate(stale, 1):
            try:
                n = update_symbol(db, symbol, latest)
                total_bars += n
                if n > 0:
                    log.info(f"[{i}/{len(stale)}] {symbol}: +{n} bars")
                else:
                    log.info(f"[{i}/{len(stale)}] {symbol}: no new bars (possibly delisted)")
            except Exception as e:
                errors += 1
                log.warning(f"[{i}/{len(stale)}] {symbol}: ERROR {e}")
                try:
                    db.rollback()
                except:
                    pass

            # Polite delay to avoid hammering yfinance
            time.sleep(0.3)

        log.info(f"Done: {total_bars} new bars, {errors} errors, {len(stale) - errors}/{len(stale)} symbols updated.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
