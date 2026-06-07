"""
Data Management API (Phase G-prep)

Provides endpoints for managing historical price data:
  GET  /api/data/status          — DB stats, freshness, symbol count
  POST /api/data/update          — trigger incremental update (fills gap to today)
  GET  /api/data/update/status   — poll running update progress

The update runs in a background thread so it doesn't block the request.
Use a Railway cron job or external scheduler to call POST /api/data/update
after market close each trading day (~4:30 PM ET).
"""

import logging
import threading
import time
import os
from datetime import datetime, timedelta, date, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text

import psycopg2
from psycopg2.extras import execute_batch

from app.database import get_db
from app.models import HistoricalPrice

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/data", tags=["data"])

# Track background update state
_update_state = {
    "running": False,
    "started_at": None,
    "symbols_total": 0,
    "symbols_done": 0,
    "new_bars": 0,
    "errors": 0,
    "last_completed_at": None,
    "last_result": None,
}
_update_lock = threading.Lock()


def _get_raw_conn():
    """Direct psycopg2 connection for bulk inserts."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(db_url)


def _do_update():
    """Background thread: fill gap between last DB date and today for all symbols."""
    import yfinance as yf

    global _update_state
    conn = None
    try:
        conn = _get_raw_conn()
        cur = conn.cursor()

        # Get per-symbol last dates
        cur.execute("""
            SELECT symbol, MAX(date) as last_date
            FROM historical_prices
            GROUP BY symbol
        """)
        rows = cur.fetchall()
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        stale = [(sym, last_d) for sym, last_d in rows if (today - last_d).days > 1]

        with _update_lock:
            _update_state["symbols_total"] = len(stale)
            _update_state["symbols_done"] = 0
            _update_state["new_bars"] = 0
            _update_state["errors"] = 0

        logger.info(f"[data update] {len(stale)} symbols to update")

        for sym, last_date in stale:
            start_str = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
            try:
                ticker = yf.Ticker(sym)
                # Use history() which is single-threaded and faster for small date ranges
                df = ticker.history(start=start_str, end=today_str, interval="1d", auto_adjust=True)
                if not df.empty:
                    insert_rows = []
                    for dt, row in df.iterrows():
                        insert_rows.append((
                            sym,
                            dt.strftime("%Y-%m-%d"),
                            float(row['Open']),
                            float(row['High']),
                            float(row['Low']),
                            float(row['Close']),
                            int(row['Volume']),
                        ))
                    execute_batch(cur, """
                        INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol, date) DO NOTHING
                    """, insert_rows, page_size=500)
                    conn.commit()

                    with _update_lock:
                        _update_state["new_bars"] += len(insert_rows)

            except Exception as e:
                logger.warning(f"[data update] {sym}: {e}")
                with _update_lock:
                    _update_state["errors"] += 1

            with _update_lock:
                _update_state["symbols_done"] += 1

            time.sleep(0.1)  # polite delay for Yahoo Finance

        result = {
            "symbols_updated": len(stale),
            "new_bars": _update_state["new_bars"],
            "errors": _update_state["errors"],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        with _update_lock:
            _update_state["last_completed_at"] = datetime.now(timezone.utc).isoformat()
            _update_state["last_result"] = result
            _update_state["running"] = False

        logger.info(f"[data update] complete — {result['new_bars']} new bars across {len(stale)} symbols")

    except Exception as e:
        logger.error(f"[data update] failed: {e}", exc_info=True)
        with _update_lock:
            _update_state["running"] = False
            _update_state["last_result"] = {"error": str(e)}
    finally:
        if conn:
            conn.close()


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/status")
def get_data_status(db: Session = Depends(get_db)):
    """DB stats: symbol count, date range, freshness."""
    total = db.query(func.count(HistoricalPrice.id)).scalar() or 0
    symbols = db.query(func.count(func.distinct(HistoricalPrice.symbol))).scalar() or 0
    result = db.execute(
        text("SELECT MIN(date), MAX(date) FROM historical_prices")
    ).fetchone()
    earliest, latest = result if result else (None, None)

    today = date.today()
    gap_days = (today - latest).days if latest else None

    with _update_lock:
        update_state = dict(_update_state)

    return {
        "total_bars": total,
        "symbol_count": symbols,
        "earliest_date": str(earliest) if earliest else None,
        "latest_date": str(latest) if latest else None,
        "gap_days": gap_days,
        "is_fresh": gap_days is not None and gap_days <= 3,
        "update": update_state,
    }


@router.post("/update")
def trigger_update():
    """
    Trigger an incremental data update (fills gap to today).
    Runs in background — poll /api/data/update/status for progress.
    Idempotent: does nothing if an update is already running.
    """
    with _update_lock:
        if _update_state["running"]:
            return {"status": "already_running", "state": dict(_update_state)}
        _update_state["running"] = True
        _update_state["started_at"] = datetime.now(timezone.utc).isoformat()

    thread = threading.Thread(target=_do_update, daemon=True)
    thread.start()
    return {"status": "started", "message": "Update running in background. Poll /api/data/update/status for progress."}


@router.get("/update/status")
def get_update_status():
    """Poll running update progress."""
    with _update_lock:
        state = dict(_update_state)
    pct = 0
    if state["symbols_total"] > 0:
        pct = round(state["symbols_done"] / state["symbols_total"] * 100, 1)
    state["progress_pct"] = pct
    return state


# ── Universe expansion ────────────────────────────────────────────────────────

_expand_state = {"running": False, "done": 0, "total": 0, "bars": 0, "errors": 0, "message": "idle"}
_expand_lock = threading.Lock()


def _do_expand():
    """
    Add 221 missing symbols (S&P 500 gaps + sector/commodity ETFs).
    Runs in background. On Railway this is a local DB connection so it's fast (~5 min).
    """
    import yfinance as yf
    from datetime import date

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

    conn = None
    try:
        conn = _get_raw_conn()
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT symbol FROM historical_prices")
        in_db = set(r[0] for r in cur.fetchall())
        to_add = [s for s in ALL_NEW if s not in in_db]

        with _expand_lock:
            _expand_state.update({"total": len(to_add), "done": 0, "bars": 0, "errors": 0,
                                   "message": f"Adding {len(to_add)} symbols..."})

        logger.info(f"[expand] {len(to_add)} symbols to add")

        for i, sym in enumerate(to_add, 1):
            try:
                ticker = yf.Ticker(sym)
                df = ticker.history(period="max", interval="1d", auto_adjust=True)
                if df is None or df.empty:
                    with _expand_lock:
                        _expand_state["done"] += 1
                    continue

                if df.index.tzinfo:
                    df.index = df.index.tz_localize(None)
                df = df[df.index.date >= START_CUTOFF]

                if df.empty:
                    with _expand_lock:
                        _expand_state["done"] += 1
                    continue

                insert_rows = []
                for dt, row in df.iterrows():
                    insert_rows.append((
                        sym, dt.strftime("%Y-%m-%d"),
                        float(row.get("Open") or 0), float(row.get("High") or 0),
                        float(row.get("Low") or 0), float(row.get("Close") or 0),
                        int(row.get("Volume") or 0),
                    ))

                execute_batch(cur, """
                    INSERT INTO historical_prices (symbol, date, open, high, low, close, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol, date) DO UPDATE SET
                        open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
                        close=EXCLUDED.close, volume=EXCLUDED.volume
                """, insert_rows, page_size=500)
                conn.commit()

                with _expand_lock:
                    _expand_state["bars"] += len(insert_rows)
                    _expand_state["done"] += 1
                    _expand_state["message"] = f"[{i}/{len(to_add)}] {sym} done (+{len(insert_rows)} bars)"

                logger.info(f"[expand] [{i}/{len(to_add)}] {sym}: +{len(insert_rows)} bars")

            except Exception as e:
                logger.warning(f"[expand] {sym}: {e}")
                with _expand_lock:
                    _expand_state["errors"] += 1
                    _expand_state["done"] += 1
                try:
                    conn.rollback()
                except Exception:
                    pass

            time.sleep(0.3)

        with _expand_lock:
            _expand_state["running"] = False
            _expand_state["message"] = (
                f"Complete: {_expand_state['bars']:,} bars added, "
                f"{_expand_state['errors']} errors, "
                f"{len(to_add)} symbols processed"
            )
        logger.info(f"[expand] done — {_expand_state['bars']:,} bars")

    except Exception as e:
        logger.error(f"[expand] failed: {e}", exc_info=True)
        with _expand_lock:
            _expand_state["running"] = False
            _expand_state["message"] = f"Error: {e}"
    finally:
        if conn:
            conn.close()


@router.post("/expand-universe")
def trigger_expand_universe():
    """
    Add 221 missing symbols (full S&P 500 + sector ETFs + commodity ETFs).
    Runs in background on the Railway server — fast because DB is local.
    Poll GET /api/data/expand-universe/status for progress.
    """
    with _expand_lock:
        if _expand_state["running"]:
            return {"status": "already_running", "state": dict(_expand_state)}
        _expand_state["running"] = True
        _expand_state["message"] = "Starting..."

    thread = threading.Thread(target=_do_expand, daemon=True)
    thread.start()
    return {"status": "started", "message": "Universe expansion started on Railway. Poll /api/data/expand-universe/status for progress."}


@router.get("/expand-universe/status")
def get_expand_status():
    """Poll universe expansion progress."""
    with _expand_lock:
        state = dict(_expand_state)
    if state["total"] > 0:
        state["progress_pct"] = round(state["done"] / state["total"] * 100, 1)
    else:
        state["progress_pct"] = 0
    return state
