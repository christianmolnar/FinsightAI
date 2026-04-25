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

# S&P 500 symbols (Top 100 most liquid - expandable to full 500)
SP500_TOP100 = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO", "ORCL", "ADBE",
    "CRM", "CSCO", "ACN", "AMD", "IBM", "INTC", "TXN", "QCOM", "AMAT", "MU",
    
    # Finance
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "C",
    "BLK", "SCHW", "CB", "PNC", "USB", "COF", "TFC", "AIG", "MET", "PRU",
    
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "TMO", "ABT", "PFE", "DHR", "BMY",
    "AMGN", "GILD", "CVS", "CI", "ELV", "HUM", "ISRG", "VRTX", "REGN", "SYK",
    
    # Consumer
    "WMT", "HD", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "TGT",
    "LOW", "TJX", "MDLZ", "CL", "PM", "MO", "KMB", "GIS", "HSY", "K",
    
    # Industrial
    "BA", "CAT", "HON", "RTX", "UPS", "LMT", "DE", "GE", "MMM", "UNP",
    
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL",
    
    # ETFs for broad market coverage
    "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "VEA", "VWO", "AGG", "LQD"
]


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
        symbols = SP500_TOP100
        print(f"📈 PRODUCTION MODE - Downloading {len(symbols)} symbols")
    
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
