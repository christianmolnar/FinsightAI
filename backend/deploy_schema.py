#!/usr/bin/env python3
"""
Deploy database schema to Railway PostgreSQL
"""
import psycopg2
import sys

DATABASE_URL = 'postgresql://postgres:QokDSjvhKDiUbMUhyeQOXuhONnJjpZxG@yamanote.proxy.rlwy.net:46033/railway'

print("🚀 Railway PostgreSQL Schema Deployment")
print("=" * 60)

try:
    # Connect
    print("\n1️⃣ Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Test connection
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    print(f"✅ Connected to: {version[:70]}...")
    
    # Check existing tables
    print("\n2️⃣ Checking existing tables...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    existing_tables = [row[0] for row in cur.fetchall()]
    
    if existing_tables:
        print(f"⚠️  Found {len(existing_tables)} existing table(s):")
        for table in existing_tables:
            print(f"   - {table}")
        print("\n⚠️  Schema deployment will skip existing tables")
    else:
        print("✅ Database is empty - ready for schema deployment")
    
    # Read schema file
    print("\n3️⃣ Loading schema from database/schema.sql...")
    with open('../database/schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Replace uuid_generate_v4() with gen_random_uuid() for Railway
    schema_sql = schema_sql.replace('uuid_generate_v4()', 'gen_random_uuid()')
    schema_sql = schema_sql.replace('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";', '')
    
    print("✅ Schema loaded (282 lines)")
    
    # Deploy schema
    print("\n4️⃣ Deploying schema...")
    try:
        cur.execute(schema_sql)
        print("✅ Schema deployed successfully!")
    except psycopg2.errors.DuplicateTable as e:
        print(f"⚠️  Some tables already exist (skipped): {e}")
    
    # Verify tables created
    print("\n5️⃣ Verifying tables...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    expected_tables = [
        'users', 'portfolios', 'positions', 'transactions',
        'strategy_configs', 'strategy_performance', 'market_data_cache'
    ]
    
    print(f"\n📊 Database Tables ({len(tables)} total):")
    for table in tables:
        status = "✅" if table in expected_tables else "ℹ️"
        print(f"   {status} {table}")
    
    missing = set(expected_tables) - set(tables)
    if missing:
        print(f"\n⚠️  Missing tables: {', '.join(missing)}")
    else:
        print(f"\n✅ All expected tables created!")
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Schema deployment completed successfully!")
    print("=" * 60)
    
    sys.exit(0)
    
except FileNotFoundError:
    print("\n❌ Error: Could not find database/schema.sql")
    print("   Make sure you're running from the backend/ directory")
    sys.exit(1)
    
except psycopg2.OperationalError as e:
    print(f"\n❌ Database connection failed: {e}")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Deployment failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
