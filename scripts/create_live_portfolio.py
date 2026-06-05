#!/usr/bin/env python3
"""Create live portfolio in database"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Railway database connection
conn = psycopg2.connect(
    "postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway"
)

cur = conn.cursor(cursor_factory=RealDictCursor)

# Check existing portfolios
print("📊 Existing portfolios:")
cur.execute("SELECT id, name, portfolio_type, current_cash, user_id FROM portfolios ORDER BY created_at")
portfolios = cur.fetchall()
for p in portfolios:
    print(f"   - ID {p['id']}: {p['name']} ({p['portfolio_type']}) - ${p['current_cash']:,.2f}")

# Get the user_id from the first portfolio
user_id = portfolios[0]['user_id'] if portfolios else '00000000-0000-0000-0000-000000000001'

# Check if live portfolio exists
cur.execute("SELECT id FROM portfolios WHERE portfolio_type = 'live'")
live_exists = cur.fetchone()

if live_exists:
    print(f"\n⚠️  Live portfolio already exists (ID: {live_exists['id']})")
else:
    # Create live portfolio
    cur.execute("""
        INSERT INTO portfolios (
            user_id,
            name,
            portfolio_type,
            initial_cash,
            current_cash,
            total_value,
            created_at,
            updated_at
        ) VALUES (
            %s,
            'Schwab Live Trading',
            'live',
            100000.00,
            100000.00,
            100000.00,
            NOW(),
            NOW()
        )
        RETURNING id, name, portfolio_type, current_cash;
    """, (user_id,))
    
    portfolio = cur.fetchone()
    conn.commit()
    
    print(f"\n✅ Created live portfolio:")
    print(f"   ID: {portfolio['id']}")
    print(f"   Name: {portfolio['name']}")
    print(f"   Type: {portfolio['portfolio_type']}")
    print(f"   Cash: ${portfolio['current_cash']:,.2f}")

cur.close()
conn.close()
