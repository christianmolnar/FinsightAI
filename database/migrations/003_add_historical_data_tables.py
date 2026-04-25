"""
Database migration: Add historical_prices and macro_events tables

Created: April 24, 2026
Purpose: Store historical stock prices and macro economic events for backtesting
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv
from pathlib import Path

# Load backend .env (Railway production database)
backend_env = Path(__file__).parent.parent.parent / "backend" / ".env"
load_dotenv(backend_env)

DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration():
    """Create tables for historical data storage"""
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("🚀 Starting Phase C database migration...")
    
    # Create historical_prices table
    print("📊 Creating historical_prices table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historical_prices (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date DATE NOT NULL,
            open DECIMAL(10, 2) NOT NULL,
            high DECIMAL(10, 2) NOT NULL,
            low DECIMAL(10, 2) NOT NULL,
            close DECIMAL(10, 2) NOT NULL,
            volume BIGINT NOT NULL,
            adjusted_close DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, date)
        );
    """)
    
    # Create indexes for fast queries
    print("📇 Creating indexes...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_historical_symbol_date 
        ON historical_prices(symbol, date DESC);
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_historical_date 
        ON historical_prices(date DESC);
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_historical_symbol 
        ON historical_prices(symbol);
    """)
    
    # Create macro_events table
    print("📰 Creating macro_events table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS macro_events (
            id SERIAL PRIMARY KEY,
            event_date DATE NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            description TEXT,
            impact VARCHAR(20),
            source VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_macro_event_date 
        ON macro_events(event_date DESC);
    """)
    
    # Create download_progress table for tracking
    print("📝 Creating download_progress table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS download_progress (
            symbol VARCHAR(10) PRIMARY KEY,
            last_date DATE,
            status VARCHAR(20),
            error_message TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    conn.commit()
    
    # Verify tables created
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('historical_prices', 'macro_events', 'download_progress')
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    print(f"\n✅ Migration complete! Created tables: {[t[0] for t in tables]}")
    
    # Get table sizes
    cur.execute("""
        SELECT 
            'historical_prices' as table_name,
            COUNT(*) as row_count
        FROM historical_prices
        UNION ALL
        SELECT 
            'macro_events' as table_name,
            COUNT(*) as row_count
        FROM macro_events
        UNION ALL
        SELECT 
            'download_progress' as table_name,
            COUNT(*) as row_count
        FROM download_progress;
    """)
    
    counts = cur.fetchall()
    print("\n📊 Current table sizes:")
    for table, count in counts:
        print(f"   {table}: {count:,} rows")
    
    cur.close()
    conn.close()
    
    print("\n🎉 Database migration successful!")

if __name__ == "__main__":
    run_migration()
