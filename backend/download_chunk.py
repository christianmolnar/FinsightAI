"""
Chunked Historical Data Downloader

Downloads historical data in small batches so you can stop/resume anytime.
Each run downloads N symbols (default: 20) and skips already-cached ones.

Usage:
    python download_chunk.py                    # Download next 20 uncached symbols
    python download_chunk.py --chunk-size 50   # Download next 50
    python download_chunk.py --years 10         # Specify years (default: 10)
    python download_chunk.py --status           # Show how many symbols are cached
    python download_chunk.py --list-symbols     # Show all symbols and their status

Run it multiple times until all symbols are downloaded.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import HistoricalPrice
from services.universe_builder import UniverseBuilder
from app.services.alpaca_service import get_alpaca_service
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_cached_symbols(db) -> set:
    """Get set of symbols that already have data in DB."""
    rows = db.execute(text("SELECT DISTINCT symbol FROM historical_prices")).fetchall()
    return {r[0] for r in rows}


def get_status(db, universe: list) -> dict:
    """Get download status."""
    cached = get_cached_symbols(db)
    total_rows = db.execute(text("SELECT COUNT(*) FROM historical_prices")).scalar()
    symbols_with_data = len(cached)
    return {
        'total_symbols': len(universe),
        'cached_symbols': symbols_with_data,
        'remaining_symbols': len(universe) - symbols_with_data,
        'total_rows': total_rows,
        'percent_complete': (symbols_with_data / len(universe) * 100) if universe else 0
    }


def bulk_insert_bars(db, symbol: str, bars_df) -> int:
    """Fast bulk insert using raw SQL with ON CONFLICT DO NOTHING."""
    if bars_df.empty:
        return 0

    rows = []
    for idx, row in bars_df.iterrows():
        date_val = idx.date() if hasattr(idx, 'date') else idx
        rows.append({
            'symbol': symbol,
            'date': date_val,
            'open': float(row.get('open', row.get('Open', 0))),
            'high': float(row.get('high', row.get('High', 0))),
            'low': float(row.get('low', row.get('Low', 0))),
            'close': float(row.get('close', row.get('Close', 0))),
            'volume': int(row.get('volume', row.get('Volume', 0))),
        })

    if not rows:
        return 0

    # Build bulk insert SQL
    sql = text("""
        INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
        VALUES (:symbol, :date, :open, :high, :low, :close, :volume)
        ON CONFLICT (symbol, date) DO NOTHING
    """)

    try:
        db.execute(sql, rows)
        db.commit()
        return len(rows)
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk insert failed for {symbol}: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(description='Download historical data in small chunks')
    parser.add_argument('--chunk-size', type=int, default=20, help='Symbols to download per run (default: 20)')
    parser.add_argument('--years', type=int, default=10, help='Years of history (default: 10)')
    parser.add_argument('--indices', nargs='+', default=['SP500', 'DOW', 'NASDAQ100'],
                        help='Indices to include (default: SP500 DOW NASDAQ100)')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    parser.add_argument('--list-symbols', action='store_true', help='List all symbols with status')
    parser.add_argument('--all', action='store_true', help='Download ALL remaining symbols (no chunk limit)')
    args = parser.parse_args()

    print("\n📊 Connecting to database...")
    db = SessionLocal()

    print("🗂️  Building universe...")
    universe_builder = UniverseBuilder()
    universe = universe_builder.build_universe(args.indices)
    print(f"   Universe: {len(universe)} unique symbols from {', '.join(args.indices)}")

    # Ensure table exists
    HistoricalPrice.__table__.create(bind=engine, checkfirst=True)

    # Status check
    status = get_status(db, universe)
    print(f"\n📈 Current Status:")
    print(f"   Cached:    {status['cached_symbols']:>4} / {status['total_symbols']} symbols  ({status['percent_complete']:.1f}%)")
    print(f"   Remaining: {status['remaining_symbols']:>4} symbols")
    print(f"   DB Rows:   {status['total_rows']:,}")

    if args.status:
        db.close()
        return

    if args.list_symbols:
        cached = get_cached_symbols(db)
        print(f"\n{'Symbol':<8} {'Status'}")
        print("-" * 20)
        for sym in universe:
            status_str = "✅ Cached" if sym in cached else "⏳ Pending"
            print(f"{sym:<8} {status_str}")
        db.close()
        return

    # Find uncached symbols
    cached = get_cached_symbols(db)
    remaining = [s for s in universe if s not in cached]

    if not remaining:
        print("\n🎉 ALL SYMBOLS ALREADY DOWNLOADED! Nothing to do.")
        db.close()
        return

    # Select chunk
    if args.all:
        chunk = remaining
        print(f"\n🚀 Downloading ALL {len(chunk)} remaining symbols...")
    else:
        chunk = remaining[:args.chunk_size]
        print(f"\n🚀 Downloading next {len(chunk)} symbols (of {len(remaining)} remaining)...")

    print(f"   Symbols: {', '.join(chunk[:10])}{'...' if len(chunk) > 10 else ''}")
    print(f"   Years: {args.years}")
    print()

    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.years * 365)

    # Get Alpaca service
    alpaca = get_alpaca_service(paper=True)

    # Download in batches of 50 (Alpaca multi-symbol limit)
    batch_size = 50
    total_rows = 0
    successful = 0
    failed = 0

    for i in range(0, len(chunk), batch_size):
        batch = chunk[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(chunk) - 1) // batch_size + 1

        print(f"📥 Batch {batch_num}/{total_batches}: Fetching {len(batch)} symbols from Alpaca...")

        try:
            bars_dict = alpaca.get_historical_bars(
                symbols=batch,
                start=start_date,
                end=end_date,
                timeframe="1Day"
            )

            for symbol in batch:
                hist = bars_dict.get(symbol)
                if hist is None or (hasattr(hist, 'empty') and hist.empty):
                    logger.warning(f"   ❌ {symbol}: No data returned")
                    failed += 1
                    continue

                rows_saved = bulk_insert_bars(db, symbol, hist)
                if rows_saved > 0:
                    print(f"   ✅ {symbol}: {rows_saved} rows")
                    total_rows += rows_saved
                    successful += 1
                else:
                    logger.warning(f"   ⚠️  {symbol}: 0 rows saved (already cached or empty)")
                    successful += 1  # Not a failure

        except Exception as e:
            logger.error(f"Batch {batch_num} failed: {e}")
            failed += len(batch)

    # Final summary
    status_after = get_status(db, universe)
    print(f"\n✅ CHUNK COMPLETE")
    print(f"   Downloaded: {successful} symbols, {total_rows:,} rows")
    print(f"   Failed:     {failed} symbols")
    print(f"\n📈 Overall Progress:")
    print(f"   Cached:    {status_after['cached_symbols']:>4} / {status_after['total_symbols']} symbols  ({status_after['percent_complete']:.1f}%)")
    print(f"   Remaining: {status_after['remaining_symbols']:>4} symbols")
    print(f"   DB Rows:   {status_after['total_rows']:,}")

    if status_after['remaining_symbols'] > 0 and not args.all:
        print(f"\n💡 Run again to download next chunk:")
        print(f"   python download_chunk.py --chunk-size {args.chunk_size} --years {args.years}")
    else:
        print(f"\n🎉 ALL DONE! Historical data is complete.")

    db.close()


if __name__ == "__main__":
    main()
