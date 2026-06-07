"""
Daily Historical Data Updater

Fetches missing bars (from last DB date to today) for all symbols in the database.
Safe to run repeatedly — uses ON CONFLICT DO NOTHING so duplicates are skipped.

Usage:
  python scripts/update_historical_data.py            # update all existing symbols
  python scripts/update_historical_data.py --stats    # just print stats, no download
"""

import os
import sys
import time
import argparse
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import yfinance as yf

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")


def get_last_dates(conn) -> dict:
    """Return {symbol: last_date} for every symbol in historical_prices."""
    cur = conn.cursor()
    cur.execute("""
        SELECT symbol, MAX(date) as last_date
        FROM historical_prices
        GROUP BY symbol
    """)
    result = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    return result


def download_symbol(conn, symbol: str, start: str, end: str) -> int:
    """Download bars for symbol from start→end, insert into DB. Returns bar count."""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval="1d")
        if df.empty:
            return 0

        rows = []
        for dt, row in df.iterrows():
            rows.append((
                symbol,
                dt.strftime("%Y-%m-%d"),
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume']),
            ))

        cur = conn.cursor()
        execute_batch(cur, """
            INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO NOTHING
        """, rows, page_size=500)
        conn.commit()
        cur.close()
        return len(rows)

    except Exception as e:
        print(f"  ❌ {symbol}: {e}")
        return 0


def print_stats(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as total_rows,
               COUNT(DISTINCT symbol) as symbols,
               MIN(date) as earliest,
               MAX(date) as latest
        FROM historical_prices
    """)
    total, symbols, earliest, latest = cur.fetchone()
    cur.close()
    today = date.today()
    gap_days = (today - latest).days if latest else '?'
    print(f"\n📊 Database Stats:")
    print(f"   Symbols:    {symbols}")
    print(f"   Total bars: {total:,}")
    print(f"   Date range: {earliest} → {latest}")
    print(f"   Gap:        {gap_days} trading days behind today")


def main():
    parser = argparse.ArgumentParser(description="Update historical price data")
    parser.add_argument("--stats", action="store_true", help="Print stats only, no download")
    parser.add_argument("--symbol", type=str, help="Update a single symbol only")
    args = parser.parse_args()

    conn = psycopg2.connect(DATABASE_URL)

    print_stats(conn)

    if args.stats:
        conn.close()
        return

    # Determine date range
    last_dates = get_last_dates(conn)
    if not last_dates:
        print("No symbols in database. Run the initial download first.")
        conn.close()
        return

    today_str = datetime.now().strftime("%Y-%m-%d")

    # If single symbol mode
    if args.symbol:
        symbols_to_update = [args.symbol]
        last_dates = {args.symbol: last_dates.get(args.symbol)}
    else:
        symbols_to_update = sorted(last_dates.keys())

    # Filter to only symbols that are actually behind
    today = date.today()
    stale = {s: d for s, d in last_dates.items() if s in symbols_to_update and (today - d).days > 1}

    if not stale:
        print("\n✅ All symbols are up to date!")
        conn.close()
        return

    print(f"\n🔄 Updating {len(stale)} symbols that are behind...")
    print(f"   (skipping {len(symbols_to_update) - len(stale)} already up-to-date symbols)\n")

    total_new_bars = 0
    updated = 0
    failed = 0
    start_time = time.time()

    for i, (symbol, last_date) in enumerate(sorted(stale.items()), 1):
        # Start from day after last known bar
        start_str = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
        print(f"[{i:3}/{len(stale)}] {symbol:6} from {start_str}... ", end="", flush=True)

        bars = download_symbol(conn, symbol, start_str, today_str)
        if bars > 0:
            print(f"✅ +{bars} bars")
            total_new_bars += bars
            updated += 1
        else:
            print("⚠️  no new bars")

        # Small delay to be polite to Yahoo Finance
        time.sleep(0.15)

        # Progress every 50 symbols
        if i % 50 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            eta = (len(stale) - i) / rate / 60
            print(f"\n⏱️  {i}/{len(stale)} done | {total_new_bars:,} new bars | ETA: {eta:.0f} min\n")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ Update complete in {elapsed/60:.1f} min")
    print(f"   Symbols updated: {updated}")
    print(f"   New bars added:  {total_new_bars:,}")

    print_stats(conn)
    conn.close()


if __name__ == "__main__":
    main()
