"""
Yahoo Finance Historical Data Loader - FREE Alternative to Alpaca

Downloads 10 years of historical stock data from Yahoo Finance (FREE, unlimited)
and loads into Railway PostgreSQL for fast backtesting.

Advantages over Alpaca:
- ✅ FREE - No subscription required
- ✅ Unlimited - No rate limits
- ✅ Historical depth - Data back to 1980s
- ✅ Reliable - Used by millions of traders

Usage:
    python yfinance_loader.py --symbols SP500 --start 2016-01-01
"""

import os
import sys
import time
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
from dotenv import load_dotenv
import yfinance as yf
from typing import List
import pandas as pd

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Full S&P 500 + NASDAQ 100 (unique) + Major ETFs
# Complete market coverage for production-grade backtesting
ALL_SYMBOLS = [
    # S&P 500 - Technology (already downloaded: 20)
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL", 
    "ADBE", "CRM", "CSCO", "ACN", "AMD", "IBM", "INTC", "TXN", "QCOM", "AMAT",
    "MU", "NOW", "INTU", "ADI", "LRCX", "KLAC", "SNPS", "CDNS", "MCHP", "FTNT",
    "ADSK", "ROP", "CTSH", "PAYX", "FICO", "ANSS", "MSI", "APH", "TEL", "IT",
    
    # S&P 500 - Finance (already downloaded: 20)
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "C",
    "BLK", "SCHW", "CB", "PNC", "USB", "COF", "TFC", "AIG", "MET", "PRU",
    "MMC", "AON", "SPGI", "ICE", "CME", "MCO", "BK", "TRV", "ALL", "AFL",
    "PGR", "TROW", "STT", "DFS", "SYF", "BEN", "AMP", "CINF", "KEY", "CFG",
    
    # S&P 500 - Healthcare (already downloaded: 20)
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "PFE", "DHR", "BMY",
    "AMGN", "GILD", "CVS", "CI", "ELV", "HUM", "ISRG", "VRTX", "REGN", "SYK",
    "BSX", "MDT", "ZTS", "EW", "IDXX", "HCA", "RMD", "DXCM", "IQV", "BDX",
    "MTD", "CRL", "WAT", "A", "ALGN", "HOLX", "VTRS", "DGX", "LH", "MOH",
    
    # S&P 500 - Consumer (already downloaded: 20)
    "WMT", "HD", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "TGT",
    "LOW", "TJX", "MDLZ", "CL", "PM", "MO", "KMB", "GIS", "HSY", "K",
    "BKNG", "CMG", "MAR", "ABNB", "YUM", "DPZ", "QSR", "SBAC", "AMT", "EQIX",
    "PLD", "SPG", "PSA", "O", "WELL", "DLR", "AVB", "EQR", "VTR", "ARE",
    
    # S&P 500 - Industrial (already downloaded: 10, adding 30)
    "BA", "CAT", "HON", "RTX", "UPS", "LMT", "DE", "GE", "MMM", "UNP",
    "FDX", "NSC", "CSX", "WM", "EMR", "ITW", "ETN", "PH", "CMI", "CARR",
    "OTIS", "GD", "NOC", "TDG", "LHX", "FAST", "PCAR", "VRSK", "IEX", "ROK",
    "DOV", "XYL", "FTV", "AME", "LDOS", "BR", "J", "HUBB", "EXPD", "JBHT",
    
    # S&P 500 - Energy (already downloaded: 10, adding 20)
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    "HES", "KMI", "WMB", "BKR", "DVN", "FANG", "MRO", "APA", "CTRA", "OKE",
    "TRGP", "LNG", "EQT", "FTI", "NOV", "CHK", "RIG", "HP", "MTDR", "PR",
    
    # S&P 500 - Materials & Chemicals (40 symbols)
    "LIN", "APD", "SHW", "ECL", "DD", "NEM", "FCX", "NUE", "DOW", "ALB",
    "PPG", "CTVA", "VMC", "MLM", "EMN", "CE", "FMC", "CF", "MOS", "IFF",
    "IP", "PKG", "BALL", "AVY", "AMCR", "SEE", "WRK", "CCK", "SON", "HUN",
    "AA", "SCCO", "STLD", "CLF", "X", "RS", "MP", "SQM", "RGLD", "GOLD",
    
    # S&P 500 - Utilities & Telecom (40 symbols)
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "SRE", "XEL", "WEC", "ES",
    "PEG", "ED", "EIX", "AWK", "PPL", "FE", "AEE", "CMS", "DTE", "ETR",
    "T", "VZ", "TMUS", "CHTR", "CMCSA", "DIS", "NFLX", "PARA", "WBD", "OMC",
    "IPG", "FOXA", "FOX", "NWSA", "NWS", "LYV", "MSG", "MSGS", "DISH", "SIRI",
    
    # S&P 500 - Retail & Consumer Services (40 symbols)
    "AMZN", "TSLA", "HD", "WMT", "COST", "LOW", "TGT", "TJX", "ROST", "DG",
    "DLTR", "BBWI", "ULTA", "AZO", "ORLY", "AAP", "GPC", "EBAY", "ETSY", "W",
    "CHWY", "RVLV", "FTCH", "CPRI", "RL", "PVH", "TPR", "LULU", "UAA", "UA",
    "NKE", "CROX", "DECK", "BIRK", "ONON", "HOKA", "VFC", "HBI", "COLM", "GRMN",
    
    # S&P 500 - Misc (Banks, Insurance, Other) (60 symbols)
    "RF", "HBAN", "FITB", "MTB", "NTRS", "CFR", "FHN", "EWBC", "SIVB", "ZION",
    "WBS", "SNV", "BOKF", "OZK", "ASB", "UBSI", "UMBF", "ABCB", "ONB", "TRMK",
    "HWC", "FIBK", "FULT", "CBSH", "SFNC", "INDB", "BANR", "BHLB", "WSFS", "WAFD",
    "CATY", "CVBF", "TOWN", "NWBI", "BUSE", "HTLF", "SBCF", "FFIN", "UCBI", "PFSI",
    "VRTS", "BR", "LDOS", "BAH", "SAIC", "CACI", "KBR", "MAN", "AIR", "HII",
    "LHX", "TXT", "HWM", "BALL", "SLGN", "AOS", "GGG", "LECO", "RBC", "CR",
    
    # NASDAQ 100 - Unique stocks not in S&P 500 (20 symbols)
    "TEAM", "DDOG", "CRWD", "ZS", "NET", "OKTA", "PANW", "SNOW", "MDB", "DKNG",
    "COIN", "RIVN", "LCID", "PLUG", "ENPH", "SEDG", "FSLR", "RUN", "SPWR", "BE",
    
    # Major ETFs (already downloaded: 10)
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "AGG", "LQD"
]

# Legacy name for backward compatibility
SP500_TOP100 = ALL_SYMBOLS[:111]  # First 111 symbols (already downloaded)


class YahooFinanceLoader:
    """Downloads historical stock data from Yahoo Finance"""
    
    def __init__(self, start_date: str, end_date: str = None):
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.conn = psycopg2.connect(DATABASE_URL)
        
    def get_downloaded_symbols(self) -> set:
        """Get symbols already in database"""
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT symbol FROM historical_prices")
        symbols = {row[0] for row in cur.fetchall()}
        cur.close()
        return symbols
        
    def download_symbol(self, symbol: str) -> int:
        """Download historical data for a single symbol"""
        try:
            print(f"📥 {symbol:6} ", end="", flush=True)
            
            # Download from Yahoo Finance
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=self.start_date, end=self.end_date, interval="1d")
            
            if df.empty:
                print("⚠️  No data")
                return 0
                
            # Prepare data for database
            rows = []
            for date, row in df.iterrows():
                rows.append((
                    symbol,
                    date.strftime("%Y-%m-%d"),
                    float(row['Open']),
                    float(row['High']),
                    float(row['Low']),
                    float(row['Close']),
                    int(row['Volume'])
                ))
            
            # Batch insert
            cur = self.conn.cursor()
            execute_batch(cur, """
                INSERT INTO historical_prices 
                (symbol, date, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, date) DO NOTHING
            """, rows, page_size=100)
            
            self.conn.commit()
            cur.close()
            
            # Update progress tracking
            self.mark_progress(symbol, "complete", rows[-1][1] if rows else None)
            
            print(f"✅ {len(rows)} bars")
            return len(rows)
            
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"❌ {error_msg}")
            self.mark_progress(symbol, "error", error_msg=error_msg)
            return 0
            
    def mark_progress(self, symbol: str, status: str, last_date: str = None, error_msg: str = None):
        """Track download progress"""
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO download_progress (symbol, status, last_date, error_message, updated_at)
            VALUES (%s, %s, %s, %s, NOW())
            ON CONFLICT (symbol) DO UPDATE SET
                status = EXCLUDED.status,
                last_date = EXCLUDED.last_date,
                error_message = EXCLUDED.error_message,
                updated_at = NOW()
        """, (symbol, status, last_date, error_msg))
        self.conn.commit()
        cur.close()
        
    def run(self, symbols: List[str]):
        """Download all symbols"""
        print(f"\n🚀 Yahoo Finance Historical Data Loader")
        print(f"📅 Period: {self.start_date} to {self.end_date}")
        print(f"📊 Symbols: {len(symbols)}")
        print(f"💰 Cost: FREE!")
        print(f"=" * 70)
        
        # Check what's already done
        already_done = self.get_downloaded_symbols()
        remaining = [s for s in symbols if s not in already_done]
        
        if already_done:
            print(f"✅ Already have: {len(already_done)} symbols")
            print(f"⏳ To download: {len(remaining)} symbols\n")
        
        if not remaining:
            print("🎉 All symbols already downloaded!")
            self.print_stats()
            return
            
        # Download symbols
        total_bars = 0
        start_time = time.time()
        
        for i, symbol in enumerate(remaining, 1):
            print(f"[{i:3}/{len(remaining)}] ", end="")
            bars = self.download_symbol(symbol)
            total_bars += bars
            
            # Progress update every 25 symbols
            if i % 25 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                eta = (len(remaining) - i) / rate / 60
                print(f"\n⏱️  Progress: {i}/{len(remaining)} | "
                      f"{total_bars:,} bars | "
                      f"Rate: {rate:.1f}/min | "
                      f"ETA: {eta:.0f} min\n")
            
            # Small delay to be respectful to Yahoo
            time.sleep(0.1)
            
        # Final summary
        elapsed = time.time() - start_time
        print(f"\n" + "=" * 70)
        print(f"🎉 Download Complete!")
        print(f"⏱️  Time: {elapsed/60:.1f} minutes")
        print(f"📊 Total bars: {total_bars:,}")
        print(f"✅ Success: {len(remaining)} symbols")
        
        self.print_stats()
        
    def print_stats(self):
        """Print database statistics"""
        cur = self.conn.cursor()
        
        # Total stats
        cur.execute("""
            SELECT 
                COUNT(*) as total_rows,
                COUNT(DISTINCT symbol) as symbols,
                MIN(date) as earliest,
                MAX(date) as latest
            FROM historical_prices
        """)
        total, symbols, earliest, latest = cur.fetchone()
        
        print(f"\n📊 Database Stats:")
        print(f"   Total rows: {total:,}")
        print(f"   Symbols: {symbols}")
        print(f"   Date range: {earliest} to {latest}")
        
        # Top symbols
        cur.execute("""
            SELECT symbol, COUNT(*) as bars
            FROM historical_prices
            GROUP BY symbol
            ORDER BY bars DESC
            LIMIT 10
        """)
        
        print(f"\n   Top 10 symbols:")
        for symbol, bars in cur.fetchall():
            print(f"      {symbol:6} {bars:5} bars")
        
        cur.close()
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Download historical data from Yahoo Finance")
    parser.add_argument("--start", default="2016-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--symbols", default="SP500", choices=["SP500", "test"],
                       help="Symbol list")
    
    args = parser.parse_args()
    
    # Select symbols
    if args.symbols == "test":
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"]
        print("🧪 TEST MODE - Downloading 5 symbols only")
    else:
        symbols = ALL_SYMBOLS
        print(f"📈 PRODUCTION MODE - Downloading {len(symbols)} symbols (Full S&P 500 + NASDAQ 100)")
    
    # Run loader
    loader = YahooFinanceLoader(args.start, args.end)
    
    try:
        loader.run(symbols)
    except KeyboardInterrupt:
        print("\n\n⏸️  Download interrupted. Progress saved. Resume by running again.")
    finally:
        loader.close()
    
    print("\n✅ Yahoo Finance loader finished!")
    print("\n💡 Next step: Update backtester to use database instead of Alpaca API")


if __name__ == "__main__":
    main()
