"""
Create pending_transactions table and any other missing tables
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import psycopg2

db_url = os.getenv("DATABASE_URL", "").replace('postgresql+psycopg://', 'postgresql://')

conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("Creating pending_transactions table...")
cur.execute("""
    CREATE TABLE IF NOT EXISTS pending_transactions (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        portfolio_id UUID,
        transaction_type VARCHAR(10) NOT NULL,
        symbol VARCHAR(20) NOT NULL,
        quantity INTEGER NOT NULL,
        proposed_price FLOAT,
        confidence_score INTEGER,
        ai_reasoning JSONB,
        risk_factors TEXT[],
        catalysts TEXT[],
        stop_loss FLOAT,
        profit_target FLOAT,
        reason_for_trade TEXT,
        auto_execute BOOLEAN DEFAULT FALSE,
        scheduled_time TIMESTAMP,
        expires_at TIMESTAMP,
        created_by VARCHAR(50) DEFAULT 'user',
        status VARCHAR(20) DEFAULT 'pending',
        executed_at TIMESTAMP,
        execution_price FLOAT,
        rejection_reason TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    )
""")

conn.commit()
print("✓ pending_transactions table created")

# Verify
cur.execute("SELECT COUNT(*) FROM pending_transactions")
count = cur.fetchone()[0]
print(f"✓ Table verified: {count} rows")

cur.close()
conn.close()
print("Done!")
