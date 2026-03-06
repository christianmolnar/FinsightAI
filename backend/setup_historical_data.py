"""
Setup Script for Historical Data

Run this script to:
1. Create historical_prices table
2. Download 10 years of data for S&P 500, DOW, NASDAQ-100
3. Set up daily update cron job

Usage:
    python setup_historical_data.py --years 10 --indices SP500 DOW NASDAQ100
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.database import SessionLocal, engine
from app.models import HistoricalPrice
from services.historical_data_manager import HistoricalDataManager


def main():
    parser = argparse.ArgumentParser(description='Setup historical data for stock universe')
    parser.add_argument('--years', type=int, default=10, help='Years of history to download (default: 10)')
    parser.add_argument('--indices', nargs='+', default=['SP500', 'DOW', 'NASDAQ100'],
                       help='Indices to include (default: SP500 DOW NASDAQ100)')
    parser.add_argument('--daily-update', action='store_true', help='Run daily update instead of bulk download')
    
    args = parser.parse_args()
    
    # Ensure historical_prices table exists (bypass other schema issues)
    print("📊 Ensuring historical_prices table exists...")
    try:
        HistoricalPrice.__table__.create(bind=engine, checkfirst=True)
        print("✅ historical_prices table ready")
    except Exception as e:
        print(f"ℹ️  Table check: {e}")
    
    # Create database session
    db = SessionLocal()
    manager = HistoricalDataManager(db)
    
    try:
        if args.daily_update:
            # Daily update mode
            print("\n📅 Running daily update...")
            stats = manager.daily_update()
            
            print(f"\n✅ UPDATE COMPLETE")
            print(f"   Updated: {stats['updated']} stocks")
            print(f"   Failed: {stats['failed']} stocks")
            print(f"   Total rows: {stats['total_rows']}")
        else:
            # Bulk download mode
            print(f"\n🚀 Starting bulk download:")
            print(f"   Years: {args.years}")
            print(f"   Indices: {', '.join(args.indices)}")
            print(f"\n⏰ This will take 30-60 minutes for 10 years of data...")
            print(f"   Progress will be logged every 50 stocks\n")
            
            stats = manager.initial_bulk_download(
                years=args.years,
                include_indices=args.indices
            )
            
            print(f"\n✅ DOWNLOAD COMPLETE")
            print(f"   Total stocks: {stats['total_stocks']}")
            print(f"   Successful: {stats['successful']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Already cached: {stats['already_cached']}")
            print(f"   Total rows: {stats['total_rows']:,}")
            
            # Estimate database size
            rows_per_stock_per_year = 252  # Trading days
            estimated_size_mb = (stats['total_rows'] * 100) / (1024 * 1024)  # ~100 bytes per row
            print(f"   Estimated DB size: ~{estimated_size_mb:.1f} MB")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
