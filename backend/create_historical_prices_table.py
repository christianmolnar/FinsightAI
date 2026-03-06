"""
Create only the historical_prices table
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

try:
    print("Creating historical_prices table...")
    
    from app.database import engine
    from app.models.historical_price import HistoricalPrice
    
    # Create only the historical_prices table
    HistoricalPrice.__table__.create(bind=engine, checkfirst=True)
    
    print("✅ historical_prices table created successfully")
    print("\nTable structure:")
    print("  - id (primary key)")
    print("  - symbol (indexed)")
    print("  - date (indexed)")
    print("  - open, high, low, close, volume")
    print("  - Composite unique index on (symbol, date)")
    print("\nReady for initial data download!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
