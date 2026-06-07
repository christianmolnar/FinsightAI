"""
Catch-up script: update only the 322 symbols stuck at Apr 24, 2026.
Each symbol commits independently — one failure won't cascade.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))

import yfinance as yf
from datetime import datetime, timedelta
from app.database import SessionLocal
import sqlalchemy

STALE_SYMBOLS = [
    "COIN","COLM","COP","COST","CPRI","CR","CRL","CRM","CROX","CRWD",
    "CSCO","CSX","CTRA","CTSH","CTVA","CVBF","CVS","CVX","D","DD",
    "DDOG","DE","DECK","DG","DGX","DHR","DIA","DIS","DKNG","DLR",
    "DLTR","DOV","DOW","DPZ","DTE","DUK","DVN","DXCM","EBAY","ECL",
    "ED","EIX","ELV","EMN","EMR","ENPH","EOG","EQIX","EQR","EQT",
    "ES","ETN","ETR","ETSY","EW","EWBC","EXC","EXPD","FANG","FAST",
    "FCX","FDX","FE","FFIN","FHN","FIBK","FICO","FITB","FMC","FOX",
    "FOXA","FSLR","FTI","FTNT","FTV","FULT","GD","GE","GGG","GILD",
    "GIS","GOLD","GOOG","GOOGL","GPC","GRMN","GS","HAL","HBAN","HCA",
    "HD","HII","HOLX","HON","HP","HSY","HUBB","HUM","HUN","HWC",
    "HWM","IBM","ICE","IDXX","IEX","IFF","INDB","INTC","INTU","IP",
    "IQV","ISRG","IT","ITW","IWM","J","JBHT","JNJ","JPM","KBR",
    "KEY","KLAC","KMB","KMI","KO","LCID","LDOS","LECO","LH","LHX",
    "LIN","LLY","LMT","LNG","LOW","LQD","LRCX","LULU","LYV","MA",
    "MAN","MAR","MCD","MCHP","MCO","MDB","MDLZ","MDT","MELI","MET",
    "META","MLM","MMM","MNST","MO","MOH","MOS","MP","MPC","MRK",
    "MS","MSFT","MSGS","MSI","MTB","MTD","MTDR","MU","NEE","NEM",
    "NET","NFLX","NKE","NOC","NOV","NOW","NSC","NTRS","NUE","NVDA",
    "NWBI","NWS","NWSA","O","OKE","OKTA","OMC","ONB","ONON","ORCL",
    "ORLY","OTIS","OXY","OZK","PANW","PAYX","PCAR","PEG","PEP","PFE",
    "PFSI","PG","PGR","PH","PKG","PLD","PLUG","PM","PNC","PPG",
    "PPL","PR","PRU","PSA","PSX","PVH","PYPL","QCOM","QQQ","QSR",
    "RBC","REGN","RF","RGLD","RIG","RIVN","RL","RMD","ROK","ROP",
    "ROST","RS","RTX","RUN","RVLV","SAIC","SBAC","SBCF","SBUX","SCCO",
    "SCHW","SEDG","SEE","SFNC","SHW","SIRI","SLB","SLGN","SNOW","SNPS",
    "SO","SON","SPG","SPGI","SPWR","SPY","SQM","SRE","STLD","STT",
    "SYF","SYK","T","TDG","TEAM","TEL","TFC","TGT","TJX","TMO",
    "TMUS","TOWN","TPR","TRGP","TRMK","TROW","TRV","TSLA","TXN","TXT",
    "UA","UAA","UBSI","ULTA","UMBF","UNH","UNP","UPS","USB","V",
    "VEA","VFC","VLO","VMC","VOO","VRSK","VRTS","VRTX","VTI","VTR",
    "VTRS","VWO","VZ","W","WAFD","WAT","WBD","WBS","WEC","WELL",
    "WFC","WM","WMB","WMT","WSFS","XEL","XOM","XYL","YUM","ZION",
    "ZS","ZTS",
]

def update_symbol(db, symbol, from_date):
    try:
        df = yf.download(symbol, start=from_date, end=datetime.today().strftime("%Y-%m-%d"),
                         auto_adjust=True, progress=False, timeout=15)
        if df is None or df.empty:
            return 0

        # Flatten MultiIndex if present
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
    except Exception as e:
        db.rollback()
        raise e


def main():
    start_from = "2026-04-25"
    total = len(STALE_SYMBOLS)
    new_bars = 0
    errors = 0

    print(f"Updating {total} stale symbols from {start_from}...\n")

    db = SessionLocal()
    try:
        for i, sym in enumerate(STALE_SYMBOLS, 1):
            try:
                n = update_symbol(db, sym, start_from)
                new_bars += n
                status = f"✅ +{n} bars" if n > 0 else "⚠️  no new bars"
            except Exception as e:
                errors += 1
                status = f"❌ {e}"

            print(f"[{i:3}/{total}] {sym:<8} {status}")

            if i % 50 == 0:
                print(f"\n⏱️  {i}/{total} done | {new_bars:,} new bars | {errors} errors\n")
            
            time.sleep(0.3)  # be polite to yfinance

    finally:
        db.close()

    print(f"\n✅ Done: {new_bars:,} new bars added | {errors} errors | {total - errors}/{total} symbols updated")


if __name__ == "__main__":
    main()
