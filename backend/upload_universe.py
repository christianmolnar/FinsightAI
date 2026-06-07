#!/usr/bin/env python3
"""
upload_universe.py — meant to run as a Railway one-off command.

Railway has ~0ms latency to its own PostgreSQL. Running this there
should complete in <5 minutes vs 33 hours from a remote machine.

Usage on Railway:
  railway run python upload_universe.py

Or trigger via the API endpoint: POST /api/data/expand-universe
"""
import sys, os, time, logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)

import yfinance as yf
from datetime import datetime
import sqlalchemy

# Resolve path whether running locally or on Railway
sys.path.insert(0, os.path.dirname(__file__))
from app.database import SessionLocal

START_DATE = "2016-01-04"

# ── S&P 500 missing symbols ───────────────────────────────────────────────────
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

SECTOR_ETFS = [
    "XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC",
]

COMMODITY_ETFS = [
    "GLD","SLV","USO","UNG","GDX","GDXJ","CORN","WEAT","SOYB","DBA","DBC",
]

ALL_NEW = SP500_MISSING + SECTOR_ETFS + COMMODITY_ETFS
START_CUTOFF = datetime.strptime(START_DATE, "%Y-%m-%d").date()


def insert_symbol(db, symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="max", interval="1d", auto_adjust=True)

    if df is None or df.empty:
        return 0

    if df.index.tzinfo:
        df.index = df.index.tz_localize(None)
    df = df[df.index.date >= START_CUTOFF]

    if df.empty:
        return 0

    rows = []
    for dt, row in df.iterrows():
        rows.append({
            "symbol": symbol,
            "date": dt.date() if hasattr(dt, "date") else dt,
            "open":   float(row.get("Open")   or 0),
            "high":   float(row.get("High")   or 0),
            "low":    float(row.get("Low")    or 0),
            "close":  float(row.get("Close")  or 0),
            "volume": int  (row.get("Volume") or 0),
        })

    if not rows:
        return 0

    # Insert all at once — on Railway this is a local connection, so fast
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
        in_db = set(
            r[0] for r in db.execute(
                sqlalchemy.text("SELECT DISTINCT symbol FROM historical_prices")
            ).fetchall()
        )
    finally:
        db.close()

    to_add = [s for s in ALL_NEW if s not in in_db]
    log.info(f"Universe expansion: {len(to_add)} symbols to add ({len(ALL_NEW)-len(to_add)} already present)")

    if not to_add:
        log.info("Nothing to do.")
        return

    total_bars = 0
    errors = 0
    db = SessionLocal()

    try:
        for i, sym in enumerate(to_add, 1):
            try:
                t0 = time.time()
                n = insert_symbol(db, sym)
                total_bars += n
                elapsed = time.time() - t0
                log.info(f"[{i:3}/{len(to_add)}] {sym:<8} +{n:>5} bars  ({elapsed:.1f}s)")
            except Exception as e:
                errors += 1
                log.warning(f"[{i:3}/{len(to_add)}] {sym:<8} ERROR: {e}")
                try:
                    db.rollback()
                except Exception:
                    pass
            time.sleep(0.2)
    finally:
        db.close()

    log.info(f"\n✅ Done: {total_bars:,} bars | {errors} errors | {len(to_add)-errors}/{len(to_add)} symbols")


if __name__ == "__main__":
    main()
