"""
Check historical data download status and restart if needed
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

load_dotenv()

def check_status():
    """Check current download status"""
    db_url = os.getenv('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check what's been downloaded
        cur.execute("""
            SELECT 
                COUNT(DISTINCT symbol) as symbols,
                COUNT(*) as total_bars,
                MIN(date) as earliest,
                MAX(date) as latest
            FROM historical_prices
        """)
        
        result = cur.fetchone()
        symbols, bars, earliest, latest = result
        
        print(f"\n📊 Current Database Status:")
        print(f"   Symbols: {symbols}")
        print(f"   Total Bars: {bars:,}")
        print(f"   Date Range: {earliest} to {latest}")
        
        # Check symbols list
        cur.execute("""
            SELECT symbol, COUNT(*) as bars
            FROM historical_prices
            GROUP BY symbol
            ORDER BY symbol
        """)
        
        downloaded_symbols = cur.fetchall()
        print(f"\n✅ Downloaded {len(downloaded_symbols)} symbols")
        
        conn.close()
        
        return symbols, bars
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return 0, 0

def restart_download():
    """Restart the download from where it left off"""
    print("\n🔄 Starting download process...")
    print("   Using yfinance (FREE, unlimited)")
    print("   Will skip already downloaded symbols\n")
    
    # Run the yfinance loader
    os.system("python3 app/services/yfinance_loader.py --resume")

if __name__ == "__main__":
    symbols, bars = check_status()
    
    if bars == 0:
        print("\n⚠️  No data found - starting fresh download")
        restart_download()
    elif symbols < 400:  # Expecting 440 symbols
        remaining = 440 - symbols
        print(f"\n⚠️  Download incomplete - {remaining} symbols remaining")
        print(f"   Would you like to resume? (Press Ctrl+C to cancel)")
        import time
        time.sleep(3)
        restart_download()
    else:
        print(f"\n✅ Download complete!")
        print(f"   {symbols} symbols with {bars:,} bars ready for backtesting")
