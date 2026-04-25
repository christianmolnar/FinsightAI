"""
Historical Data Loader - Phase C

Downloads historical stock data from Alpaca and loads into Railway PostgreSQL.
Runs overnight to populate database for backtesting.

Usage:
    python historical_data_loader.py --start-date 2016-01-01 --symbols SP500

Features:
    - Batch processing with progress tracking
    - Resume capability (skips already downloaded symbols)
    - Rate limit handling
    - Error recovery with retry logic
"""

import os
import time
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from typing import List, Dict
import argparse

load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = "https://data.alpaca.markets"

# S&P 500 major symbols (Top 100 by market cap - expandable)
SP500_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "JNJ",
    "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    "COST", "AVGO", "KO", "WMT", "MCD", "CSCO", "PFE", "TMO", "ABT", "ACN",
    "DHR", "NKE", "NFLX", "CRM", "LIN", "ADBE", "DIS", "TXN", "VZ", "CMCSA",
    "INTC", "WFC", "UPS", "PM", "RTX", "AMGN", "SPGI", "HON", "INTU", "BA",
    "IBM", "CAT", "GE", "AMD", "QCOM", "SBUX", "AMAT", "BKNG", "LOW", "GS",
    "AXP", "BLK", "DE", "LMT", "ELV", "SYK", "ADI", "MDLZ", "GILD", "MMC",
    "TJX", "CI", "C", "ISRG", "VRTX", "ZTS", "PLD", "AMT", "CVS", "MO",
    "BDX", "ADP", "SO", "REGN", "TMUS", "SLB", "SCHW", "CB", "DUK", "BSX",
    "PNC", "EOG", "USB", "CL", "ITW", "FI", "HUM", "MU", "ICE", "MS",
    # Add more liquid ETFs and major stocks
    "SPY", "QQQ", "IWM", "DIA", "XLF", "XLE", "XLK", "XLV", "XLI", "XLP"
]


class HistoricalDataLoader:
    def __init__(self, start_date: str, end_date: str = None):
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.conn = psycopg2.connect(DATABASE_URL)
        self.headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY
        }
        self.batch_size = 50  # Process 50 symbols at a time
        self.request_delay = 0.3  # 300ms between requests (200/min limit)
        
    def get_already_downloaded_symbols(self) -> set:
        """Get list of symbols that have been fully downloaded"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT symbol FROM download_progress 
            WHERE status = 'complete'
        """)
        symbols = {row[0] for row in cur.fetchall()}
        cur.close()
        return symbols
        
    def mark_symbol_progress(self, symbol: str, status: str, last_date: str = None, error_msg: str = None):
        """Update download progress for a symbol"""
        cur = self.conn.cursor()
        if error_msg:
            cur.execute("""
                INSERT INTO download_progress (symbol, status, last_date, error_message, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    status = EXCLUDED.status,
                    last_date = EXCLUDED.last_date,
                    error_message = EXCLUDED.error_message,
                    updated_at = NOW()
            """, (symbol, status, last_date, error_msg))
        else:
            cur.execute("""
                INSERT INTO download_progress (symbol, status, last_date, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (symbol) DO UPDATE SET
                    status = EXCLUDED.status,
                    last_date = EXCLUDED.last_date,
                    updated_at = NOW()
            """, (symbol, status, last_date))
        self.conn.commit()
        cur.close()
        
    def download_symbol_data(self, symbol: str) -> int:
        """Download historical data for a single symbol"""
        try:
            print(f"📥 Downloading {symbol}... ", end="", flush=True)
            
            url = f"{ALPACA_BASE_URL}/v2/stocks/{symbol}/bars"
            params = {
                "start": self.start_date,
                "end": self.end_date,
                "timeframe": "1Day",
                "limit": 10000,  # Max limit
                "adjustment": "all"
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 429:
                print("⏸️  Rate limited, sleeping 60s...")
                time.sleep(60)
                return self.download_symbol_data(symbol)  # Retry
                
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                print(f"❌ {error_msg}")
                self.mark_symbol_progress(symbol, "error", error_msg=error_msg)
                return 0
                
            data = response.json()
            bars = data.get("bars", [])
            
            if not bars:
                print("⚠️  No data")
                self.mark_symbol_progress(symbol, "no_data")
                return 0
                
            # Prepare batch insert
            rows = []
            for bar in bars:
                rows.append((
                    symbol,
                    bar["t"][:10],  # Date (YYYY-MM-DD)
                    float(bar["o"]),  # Open
                    float(bar["h"]),  # High
                    float(bar["l"]),  # Low
                    float(bar["c"]),  # Close
                    int(bar["v"]),    # Volume
                    float(bar["c"])   # Adjusted close (same as close for now)
                ))
            
            # Batch insert into database
            cur = self.conn.cursor()
            execute_batch(cur, """
                INSERT INTO historical_prices 
                (symbol, date, open, high, low, close, volume, adjusted_close)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, date) DO NOTHING
            """, rows, page_size=100)
            
            self.conn.commit()
            cur.close()
            
            last_date = bars[-1]["t"][:10] if bars else None
            self.mark_symbol_progress(symbol, "complete", last_date=last_date)
            
            print(f"✅ {len(bars)} bars")
            return len(bars)
            
        except Exception as e:
            error_msg = str(e)[:200]
            print(f"❌ Error: {error_msg}")
            self.mark_symbol_progress(symbol, "error", error_msg=error_msg)
            return 0
            
    def run(self, symbols: List[str]):
        """Download data for all symbols"""
        print(f"\n🚀 Historical Data Loader - Phase C")
        print(f"📅 Period: {self.start_date} to {self.end_date}")
        print(f"📊 Symbols: {len(symbols)}")
        print(f"=" * 60)
        
        # Skip already downloaded
        already_done = self.get_already_downloaded_symbols()
        remaining = [s for s in symbols if s not in already_done]
        
        if already_done:
            print(f"✅ Already completed: {len(already_done)} symbols")
            print(f"⏳ Remaining: {len(remaining)} symbols\n")
        
        if not remaining:
            print("🎉 All symbols already downloaded!")
            return
            
        # Process in batches
        total_bars = 0
        start_time = time.time()
        
        for i, symbol in enumerate(remaining, 1):
            print(f"[{i}/{len(remaining)}] ", end="")
            bars_count = self.download_symbol_data(symbol)
            total_bars += bars_count
            
            # Progress update every 10 symbols
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining_time = avg_time * (len(remaining) - i) / 60
                print(f"\n⏱️  Progress: {i}/{len(remaining)} symbols | "
                      f"{total_bars:,} bars | "
                      f"ETA: {remaining_time:.1f} min\n")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
        # Final summary
        elapsed = time.time() - start_time
        print(f"\n" + "=" * 60)
        print(f"🎉 Download Complete!")
        print(f"⏱️  Time: {elapsed/60:.1f} minutes")
        print(f"📊 Total bars: {total_bars:,}")
        print(f"✅ Success: {len(remaining) - len(self.get_failed_symbols())} symbols")
        
        failed = self.get_failed_symbols()
        if failed:
            print(f"❌ Failed: {len(failed)} symbols")
            print(f"   {', '.join(failed[:10])}" + (" ..." if len(failed) > 10 else ""))
            
        self.print_database_stats()
        
    def get_failed_symbols(self) -> List[str]:
        """Get list of symbols that failed to download"""
        cur = self.conn.cursor()
        cur.execute("""
            SELECT symbol FROM download_progress 
            WHERE status = 'error'
        """)
        symbols = [row[0] for row in cur.fetchall()]
        cur.close()
        return symbols
        
    def print_database_stats(self):
        """Print database statistics"""
        cur = self.conn.cursor()
        
        # Total rows
        cur.execute("SELECT COUNT(*) FROM historical_prices")
        total_rows = cur.fetchone()[0]
        
        # Date range
        cur.execute("""
            SELECT MIN(date), MAX(date), COUNT(DISTINCT symbol)
            FROM historical_prices
        """)
        min_date, max_date, symbol_count = cur.fetchone()
        
        print(f"\n📊 Database Stats:")
        print(f"   Total rows: {total_rows:,}")
        print(f"   Symbols: {symbol_count}")
        print(f"   Date range: {min_date} to {max_date}")
        
        # Top 5 symbols by data points
        cur.execute("""
            SELECT symbol, COUNT(*) as bars
            FROM historical_prices
            GROUP BY symbol
            ORDER BY bars DESC
            LIMIT 5
        """)
        print(f"\n   Top symbols:")
        for symbol, bars in cur.fetchall():
            print(f"      {symbol}: {bars} bars")
        
        cur.close()
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="Download historical stock data")
    parser.add_argument("--start-date", default="2016-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--symbols", default="SP500", choices=["SP500", "test"], 
                       help="Symbol list to download")
    
    args = parser.parse_args()
    
    # Select symbol list
    if args.symbols == "test":
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"]  # Test with 5 symbols
    else:
        symbols = SP500_SYMBOLS
    
    # Run loader
    loader = HistoricalDataLoader(args.start_date, args.end_date)
    
    try:
        loader.run(symbols)
    except KeyboardInterrupt:
        print("\n\n⏸️  Download interrupted. Progress saved. Resume by running again.")
    finally:
        loader.close()
    
    print("\n✅ Historical data loader finished!")


if __name__ == "__main__":
    main()
