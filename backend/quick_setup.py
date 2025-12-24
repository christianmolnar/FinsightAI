#!/usr/bin/env python3
"""
Quick Railway PostgreSQL Setup - Deploy Schema + Migrate Data
"""
import psycopg2
import json
import os

DATABASE_URL = 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway'

print("🚀 Railway PostgreSQL Quick Setup")
print("=" * 60)

try:
    # Connect
    print("\n📡 Connecting to Railway...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    print("✅ Connected!")
    
    # Create tables (simplified schema)
    print("\n📊 Creating tables...")
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print("✅ users table")
    
    # Portfolios table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            portfolio_type VARCHAR(20) NOT NULL CHECK (portfolio_type IN ('live', 'paper')),
            initial_cash DECIMAL(15,2) NOT NULL DEFAULT 10000.00,
            current_cash DECIMAL(15,2) NOT NULL,
            total_value DECIMAL(15,2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print("✅ portfolios table")
    
    # Positions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
            symbol VARCHAR(20) NOT NULL,
            quantity DECIMAL(15,4) NOT NULL,
            average_cost DECIMAL(10,4) NOT NULL,
            current_price DECIMAL(10,4) DEFAULT 0.00,
            market_value DECIMAL(15,2) DEFAULT 0.00,
            unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print("✅ positions table")
    
    # Transactions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
            transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('buy', 'sell')),
            symbol VARCHAR(20) NOT NULL,
            quantity DECIMAL(15,4) NOT NULL,
            price DECIMAL(10,4) NOT NULL,
            total_amount DECIMAL(15,2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print("✅ transactions table")
    
    # Load paper portfolio data
    print("\n📁 Loading paper portfolio data...")
    json_file = "paper_portfolios.json"
    
    if not os.path.exists(json_file):
        print("⚠️  No JSON file found - creating fresh portfolio")
        cash_balance = 10000.00
        positions = {}
    else:
        with open(json_file, 'r') as f:
            portfolios = json.load(f)
        default_portfolio = portfolios.get('default', {})
        cash_balance = default_portfolio.get('cash_balance', 10000)
        positions = default_portfolio.get('positions', {})
        print(f"✅ Found ${cash_balance:,.2f} cash, {len(positions)} position(s)")
    
    # Create default user
    print("\n👤 Creating default user...")
    cur.execute("""
        INSERT INTO users (email, full_name)
        VALUES ('default@finsight.ai', 'Default User')
        ON CONFLICT (email) DO NOTHING
        RETURNING id;
    """)
    result = cur.fetchone()
    if result:
        user_id = result[0]
        print(f"✅ User created: {user_id}")
    else:
        cur.execute("SELECT id FROM users WHERE email = 'default@finsight.ai'")
        user_id = cur.fetchone()[0]
        print(f"✅ User exists: {user_id}")
    
    # Create paper portfolio
    print("\n💼 Creating paper portfolio...")
    positions_value = sum(pos['quantity'] * pos['avg_price'] for pos in positions.values())
    total_value = cash_balance + positions_value
    
    cur.execute("""
        INSERT INTO portfolios (
            user_id, name, portfolio_type,
            initial_cash, current_cash, total_value
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """, (user_id, 'Paper Portfolio', 'paper', 10000.0, cash_balance, total_value))
    
    result = cur.fetchone()
    if result:
        portfolio_id = result[0]
        print(f"✅ Portfolio created: {portfolio_id}")
    else:
        cur.execute("""
            SELECT id FROM portfolios 
            WHERE user_id = %s AND portfolio_type = 'paper'
            LIMIT 1
        """, (user_id,))
        portfolio_id = cur.fetchone()[0]
        print(f"✅ Portfolio exists: {portfolio_id}")
    
    # Migrate positions
    if positions:
        print(f"\n📊 Migrating {len(positions)} position(s)...")
        for symbol, pos_data in positions.items():
            market_value = pos_data['quantity'] * pos_data['avg_price']
            
            cur.execute("""
                INSERT INTO positions (
                    portfolio_id, symbol, quantity,
                    average_cost, current_price, market_value
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                portfolio_id, symbol, pos_data['quantity'],
                pos_data['avg_price'], pos_data['avg_price'], market_value
            ))
            print(f"  ✅ {symbol}: {pos_data['quantity']} shares @ ${pos_data['avg_price']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Portfolio Summary:")
    print(f"   Cash Balance:    ${cash_balance:,.2f}")
    print(f"   Positions Value: ${positions_value:,.2f}")
    print(f"   Total Value:     ${total_value:,.2f}")
    print(f"   Positions:       {len(positions)}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
