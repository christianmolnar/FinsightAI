"""
expand_universe.py — one-time script to add:
  1. All 206 S&P 500 stocks currently missing from historical_prices
  2. 11 SPDR sector ETFs (XLK, XLF, XLE, etc.)
  3. Commodity ETFs (GLD, SLV, USO, GDX, CORN, WEAT)

Each symbol commits independently. Safe to re-run.
"""
import sys, os, time, logging
sys.path.insert(0, os.path.dirname(__file__))

import yfinance as yf
from datetime import datetime
import sqlalchemy
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

# ── S&P 500 missing symbols (from Wikipedia comparison, June 2026) ────────────
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

# ── Sector ETFs (SPDR) ────────────────────────────────────────────────────────
SECTOR_ETFS = [
    "XLK",   # Technology
    "XLF",   # Financials
    "XLE",   # Energy
    "XLV",   # Health Care
    "XLI",   # Industrials
    "XLY",   # Consumer Discretionary
    "XLP",   # Consumer Staples
    "XLU",   # Utilities
    "XLB",   # Materials
    "XLRE",  # Real Estate
    "XLC",   # Communication Services
]

# ── Commodity ETFs ─────────────────────────────────────────────────────────────
COMMODITY_ETFS = [
    "GLD",   # Gold
    "SLV",   # Silver
    "USO",   # Oil (WTI)
    "UNG",   # Natural Gas
    "GDX",   # Gold Miners
    "GDXJ",  # Junior Gold Miners
    "CORN",  # Corn
    "WEAT",  # Wheat
    "SOYB",  # Soybeans
    "DBA",   # Diversified Agriculture
    "DBC",   # Diversified Commodities
]

ALL_NEW = SP500_MISSING + SECTOR_ETFS + COMMODITY_ETFS
START_DATE = "2016-01-04"


def insert_symbol(db, symbol, start_date):
    today = datetime.now().strftime("%Y-%m-%d")
    df = yf.download(symbol, start=start_date, end=today,
                     auto_adjust=True, progress=False, timeout=20)
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
    # Skip symbols already in DB
    db = SessionLocal()
    try:
        in_db = set(r[0] for r in db.execute(
            sqlalchemy.text("SELECT DISTINCT symbol FROM historical_prices")
        ).fetchall())
    finally:
        db.close()

    to_add = [s for s in ALL_NEW if s not in in_db]
    log.info(f"Symbols to add: {len(to_add)} ({len(ALL_NEW) - len(to_add)} already in DB)")

    if not to_add:
        log.info("Nothing to do — all symbols already in DB.")
        return

    total_bars = 0
    errors = 0
    db = SessionLocal()
    try:
        for i, sym in enumerate(to_add, 1):
            try:
                n = insert_symbol(db, sym, START_DATE)
                total_bars += n
                log.info(f"[{i:3}/{len(to_add)}] {sym:<8} ✅ +{n} bars")
            except Exception as e:
                errors += 1
                log.warning(f"[{i:3}/{len(to_add)}] {sym:<8} ❌ {e}")
                try:
                    db.rollback()
                except:
                    pass
            time.sleep(0.4)
    finally:
        db.close()

    log.info(f"\nDone: {total_bars:,} bars added | {errors} errors | {len(to_add)-errors}/{len(to_add)} symbols")


if __name__ == "__main__":
    main()
