"""
Migrate database schema to latest version
Drops and recreates all tables based on current models
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    print("🔄 Migrating database schema...")
    
    from app.database import engine
    from app.models import Base
    from sqlalchemy import text
    
    # Drop all tables with CASCADE to handle foreign keys
    print("  ⚠️  Dropping existing tables with CASCADE...")
    with engine.begin() as conn:
        # Get all table names
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # Drop each table with CASCADE
        for table in tables:
            print(f"    - Dropping {table}...")
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
    
    print("  ✅ Dropped all tables")
    
    # Recreate all tables with new schema
    print("  🔨 Creating tables with new schema...")
    Base.metadata.create_all(bind=engine)
    print("  ✅ Created all tables")
    
    # Verify portfolio table exists with correct columns
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'portfolios'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        print("\n📋 Portfolio table columns:")
        for col in columns:
            print(f"    - {col[0]}: {col[1]}")
    
    print("\n✅ Database schema migration complete!")
    print("\n⚠️  NOTE: All existing data has been deleted")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
