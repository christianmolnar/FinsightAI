"""
Create backtest calibration tables

Run this script to add the three new tables for Phase 4.5:
1. backtest_reports - Store backtest runs and recommendations
2. config_changes - Track configuration changes over time
3. portfolio_snapshots - Daily portfolio values for graphing

Usage:
    python create_backtest_tables.py
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def create_tables():
    """Create the three new tables for backtest calibration system"""
    
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("Creating backtest calibration tables...")
    
    # ========================================
    # TABLE 1: backtest_reports
    # ========================================
    print("\n1. Creating backtest_reports table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backtest_reports (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) DEFAULT 'default',
            run_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Configuration snapshot at time of backtest
            config_snapshot JSONB NOT NULL,
            
            -- Backtest parameters
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            initial_capital FLOAT DEFAULT 100000.00,
            
            -- Overall performance metrics
            total_trades INTEGER DEFAULT 0,
            winning_trades INTEGER DEFAULT 0,
            losing_trades INTEGER DEFAULT 0,
            win_rate FLOAT CHECK (win_rate >= 0 AND win_rate <= 100),
            total_return FLOAT,
            final_portfolio_value FLOAT,
            max_drawdown FLOAT,
            sharpe_ratio FLOAT,
            profit_factor FLOAT,
            
            -- Trade statistics
            avg_win_size FLOAT,
            avg_loss_size FLOAT,
            largest_win FLOAT,
            largest_loss FLOAT,
            avg_hold_days FLOAT,
            
            -- Strategy breakdown
            strategy_performance JSONB,
            
            -- Daily P&L for drawdown calculation
            daily_pnl JSONB,
            
            -- Generated recommendations
            recommendations JSONB,
            
            -- User interaction
            applied BOOLEAN DEFAULT FALSE,
            applied_recommendations JSONB,
            user_notes TEXT,
            
            -- Metadata
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '1 year')
        );
    """)
    
    print("   ✅ backtest_reports table created")
    
    # Create indexes
    print("   Creating indexes for backtest_reports...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_backtest_reports_user_date 
        ON backtest_reports(user_id, run_date DESC);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_backtest_reports_expiration 
        ON backtest_reports(expires_at);
    """)
    print("   ✅ Indexes created")
    
    # ========================================
    # TABLE 2: config_changes
    # ========================================
    print("\n2. Creating config_changes table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_changes (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) DEFAULT 'default',
            change_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Configuration snapshots
            before_config JSONB NOT NULL,
            after_config JSONB NOT NULL,
            changed_parameters JSONB,
            
            -- What triggered this change?
            trigger_type VARCHAR(50),
            backtest_report_id INTEGER REFERENCES backtest_reports(id),
            
            -- Performance tracking (calculated later)
            performance_before JSONB,
            performance_after JSONB,
            
            -- User notes
            user_notes TEXT,
            
            -- Metadata
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    
    print("   ✅ config_changes table created")
    
    # Create indexes
    print("   Creating indexes for config_changes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_config_changes_user_date 
        ON config_changes(user_id, change_date DESC);
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_config_changes_backtest 
        ON config_changes(backtest_report_id);
    """)
    print("   ✅ Indexes created")
    
    # ========================================
    # TABLE 3: portfolio_snapshots
    # ========================================
    print("\n3. Creating portfolio_snapshots table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(50) DEFAULT 'default',
            account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('paper', 'live')),
            snapshot_date DATE NOT NULL,
            
            -- Portfolio metrics
            portfolio_value FLOAT NOT NULL,
            cash_balance FLOAT NOT NULL,
            positions_value FLOAT NOT NULL,
            
            -- Daily performance
            daily_return FLOAT,
            daily_pnl FLOAT,
            
            -- Position count
            open_positions INTEGER DEFAULT 0,
            
            -- Link to current config
            config_change_id INTEGER REFERENCES config_changes(id),
            
            -- Metadata
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            -- Ensure one snapshot per user/account/date
            UNIQUE(user_id, account_type, snapshot_date)
        );
    """)
    
    print("   ✅ portfolio_snapshots table created")
    
    # Create indexes
    print("   Creating indexes for portfolio_snapshots...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_account_date 
        ON portfolio_snapshots(user_id, account_type, snapshot_date DESC);
    """)
    print("   ✅ Indexes created")
    
    # ========================================
    # VERIFICATION
    # ========================================
    print("\n✅ All tables created successfully!")
    print("\nVerifying tables exist...")
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('backtest_reports', 'config_changes', 'portfolio_snapshots')
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"\nFound {len(tables)} tables:")
    for table in tables:
        print(f"   ✅ {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Enhance backtester with detailed metrics")
    print("2. Create calibration engine service")
    print("3. Build frontend calibration UI")


if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
