"""
Quick test of market scanner
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing Market Scanner...")
print("-" * 50)

try:
    from services.market_scanner import MarketScanner
    from app.database import SessionLocal
    
    print("✓ Imports successful")
    
    # Create database session
    db = SessionLocal()
    print("✓ Database connected")
    
    # Create scanner
    scanner = MarketScanner(db)
    print(f"✓ Scanner created - {len(scanner.SCAN_UNIVERSE)} stocks in universe")
    
    # Test technical breakout strategy
    print("\n🔍 Running technical breakout scan...")
    candidates = scanner._scan_technical_breakouts()
    
    print(f"\n✅ Found {len(candidates)} technical breakout candidates\n")
    
    if candidates:
        print("Top 3 candidates:")
        for i, c in enumerate(candidates[:3], 1):
            print(f"\n{i}. {c['symbol']} - Score: {c['score']}")
            print(f"   Price: ${c['current_price']:.2f}")
            print(f"   Volume: {c['volume']:,}")
            print(f"   Reason: {c['reason']}")
    else:
        print("No candidates found (market conditions may not show breakouts currently)")
    
    print("\n" + "=" * 50)
    print("Scanner test complete!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    if 'db' in locals():
        db.close()
