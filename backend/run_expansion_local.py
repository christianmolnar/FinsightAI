#!/usr/bin/env python3
"""
run_expansion_local.py — run locally, writes directly to Railway DB.

Uses psycopg2 execute_values (single INSERT per symbol = 1 DB round-trip).
~3.5s per symbol = ~13 min for 221 symbols via Railway proxy.

Usage:
  cd backend && source venv/bin/activate
  python3 run_expansion_local.py
"""
import sys, time, logging
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

DB_URL = "postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway"
START_CUTOFF = date(2016, 1, 4)

SP500_MISSING = [
    "ACGL","ADM","AES","AIZ","AJG","AKAM","ALLE","ANET","APO","APP",
    "APTV","ARES","ATO","AXON","BAX","BBY","BF-B","BG","BIIB","BLDR",
    "BNY","BRK-B","BRO","BX","BXP","CAG","CAH","CASY","CBOE","CBRE",
    "CCI","CCL","CDW","CEG","CHD","CHRW","CIEN","CLX","CNC","CNP",
    "COHR","COO","COR","CPAY","CPB","CPRT","CPT","CRH","CSGP","CTAS",
    "CVNA","DAL","DASH","DELL","DHI","DOC","DRI","DVA","EA","EFX",
    "EG","EL","EME","ERIE","ESS","EVRG","EXE","EXPE","EXR","F",
    "FDS","FFIV","FIS","FISV","FIX","FRT","GDDY","GEHC","GEN","GEV",
    "GL","GLW","GM","GNRC","GPN","GWW","HAS","HIG","HLT","HOOD",
    "HPE","HPQ","HRL","HSIC","HST","IBKR","INCY","INVH","IR","IRM",
    "IVZ","JBL","JCI","JKHY","KDP","KEYS","KHC","KIM","KKR","KR",
    "KVUE","L","LEN","LII","LNT","LUV","LVS","LYB","MAA","MAS",
    "MCK","MGM","MKC","MPWR","MRNA","MSCI","NCLH","NDAQ","NDSN","NI",
    "NRG","NTAP","NVR","NXPI","ODFL","ON","PCG","PFG","PHM","PLTR",
    "PNR","PNW","PODD","POOL","PTC","PWR","Q","RCL","REG","RJF",
    "ROL","RSG","RVTY","SJM","SMCI","SNA","SOLV","STE","STX","STZ",
    "SW","SWK","SWKS","SYY","TAP","TDY","TECH","TER","TKO","TPL",
    "TRMB","TSCO","TSN","TT","TTD","TTWO","TYL","UAL","UBER","UDR",
    "UHS","URI","VEEV","VICI","VLTO","VRSN","VRT","VST","WAB","WDAY",
    "WDC","WRB","WSM","WST","WTW","WY","WYNN","ZBH","ZBRA",
]
SECTOR_ETFS = ["XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"]
COMMODITY_ETFS = ["GLD","SLV","USO","UNG","GDX","GDXJ","CORN","WEAT","SOYB","DBA","DBC"]
ALL_NEW = SP500_MISSING + SECTOR_ETFS + COMMODITY_ETFS


def get_in_db():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT symbol FROM historical_prices")
    result = set(r[0] for r in cur.fetchall())
    conn.close()
    return result


def db_connect(retries=6, delay=20):
    """Connect to DB with retries (waits for crash recovery)."""
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(DB_URL, connect_timeout=15)
            return conn
        except Exception as e:
            if attempt < retries - 1:
                log.warning(f"DB connect attempt {attempt+1}/{retries} failed: {e} — retrying in {delay}s")
                time.sleep(delay)
            else:
                raise


def checkpoint(conn):
    """Force a DB checkpoint to flush WAL and reclaim disk space."""
    try:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("CHECKPOINT")
        conn.autocommit = False
    except Exception as e:
        log.debug(f"CHECKPOINT failed (non-fatal): {e}")


def vacuum_analyze(conn):
    """Run VACUUM ANALYZE to reclaim space (outside transaction)."""
    try:
        old_isolation = conn.isolation_level
        conn.set_isolation_level(0)  # autocommit required for VACUUM
        cur = conn.cursor()
        cur.execute("VACUUM ANALYZE historical_prices")
        conn.set_isolation_level(old_isolation)
        log.info("  [VACUUM ANALYZE done]")
    except Exception as e:
        log.warning(f"  VACUUM ANALYZE failed: {e}")


def insert_symbol(conn, sym):
    ticker = yf.Ticker(sym)
    df = ticker.history(period="max", interval="1d", auto_adjust=True)

    if df is None or df.empty:
        return 0

    if df.index.tzinfo:
        df.index = df.index.tz_localize(None)
    df = df[df.index.date >= START_CUTOFF]

    if df.empty:
        return 0

    rows = [
        (sym, dt.strftime("%Y-%m-%d"),
         float(r.get("Open") or 0), float(r.get("High") or 0),
         float(r.get("Low") or 0),  float(r.get("Close") or 0),
         int(r.get("Volume") or 0))
        for dt, r in df.iterrows()
    ]

    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO historical_prices (symbol, date, open, high, low, close, volume) VALUES %s
        ON CONFLICT (symbol, date) DO UPDATE SET
            open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
            close=EXCLUDED.close, volume=EXCLUDED.volume
    """, rows, page_size=len(rows))
    conn.commit()
    return len(rows)


def main():
    log.info("Checking what's already in DB...")
    in_db = get_in_db()
    to_add = [s for s in ALL_NEW if s not in in_db]
    already = len(ALL_NEW) - len(to_add)
    log.info(f"Universe: {len(ALL_NEW)} total | {already} already present | {len(to_add)} to add")

    if not to_add:
        log.info("Nothing to do — all symbols already in DB!")
        return

    # Pre-run VACUUM FULL + CHECKPOINT to start with max free space
    log.info("Pre-run VACUUM FULL + CHECKPOINT to clear WAL space and reclaim disk...")
    conn = db_connect()
    try:
        conn.set_isolation_level(0)  # autocommit needed for VACUUM FULL
        cur = conn.cursor()
        log.info("  Running VACUUM FULL (may take ~30s)...")
        cur.execute("VACUUM FULL ANALYZE historical_prices")
        log.info("  VACUUM FULL done")
        cur.execute("CHECKPOINT")
        log.info("  CHECKPOINT done")
    finally:
        conn.close()

    log.info(f"Starting expansion ({len(to_add)} symbols, ~{len(to_add)*4/60:.0f} min estimated)...")
    t_start = time.time()
    total_bars = 0
    errors = 0
    skipped = 0

    conn = db_connect()
    try:
        for i, sym in enumerate(to_add, 1):
            t0 = time.time()
            # Reconnect if connection dropped (e.g., after a DB blip)
            try:
                conn.cursor().execute("SELECT 1")
            except Exception:
                log.warning("  Connection lost, reconnecting...")
                try:
                    conn.close()
                except Exception:
                    pass
                conn = db_connect()

            try:
                n = insert_symbol(conn, sym)
                elapsed = time.time() - t0
                if n == 0:
                    skipped += 1
                    log.info(f"[{i:3}/{len(to_add)}] {sym:<8} SKIP (no data)  ({elapsed:.1f}s)")
                else:
                    total_bars += n
                    log.info(f"[{i:3}/{len(to_add)}] {sym:<8} +{n:>5} bars  ({elapsed:.1f}s)")
            except Exception as e:
                errors += 1
                log.warning(f"[{i:3}/{len(to_add)}] {sym:<8} ERROR: {e}  ({time.time()-t0:.1f}s)")
                try:
                    conn.rollback()
                except Exception:
                    pass

            # CHECKPOINT every 10 symbols to prevent WAL disk bloat
            if i % 10 == 0:
                log.info(f"  [{i}/{len(to_add)}] CHECKPOINT...")
                checkpoint(conn)

            time.sleep(0.3)
    finally:
        conn.close()

    elapsed_total = time.time() - t_start
    log.info(f"\n{'='*60}")
    log.info(f"✅ Done in {elapsed_total/60:.1f} min")
    log.info(f"   Symbols:  {len(to_add)-errors-skipped} added | {skipped} skipped | {errors} errors")
    log.info(f"   Bars:     {total_bars:,} added")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    main()
