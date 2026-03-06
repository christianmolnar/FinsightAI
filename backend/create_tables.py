"""
Create database tables
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    print("Creating database tables...")
    
    from app.models import create_tables
    create_tables()
    
    print("✅ Database tables created successfully")
    print("\nCreated tables:")
    print("  - historical_prices (symbol, date, OHLCV data)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
