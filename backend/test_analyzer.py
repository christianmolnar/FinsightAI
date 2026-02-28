"""
Test Opportunity Analyzer

Quick test to verify the analyzer works end-to-end.
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing Opportunity Analyzer...")
print("=" * 50)

async def test_analyzer():
    try:
        from services.opportunity_analyzer import get_opportunity_analyzer
        from app.database import SessionLocal
        
        print("✓ Imports successful")
        
        # Create database session
        db = SessionLocal()
        print("✓ Database connected")
        
        # Create analyzer with lower threshold for testing
        analyzer = get_opportunity_analyzer(db, confidence_threshold=0.60)
        print(f"✓ Analyzer created (threshold=60%)")
        
        # Find opportunities (limit to 2 for faster testing)
        print("\n🔍 Finding opportunities...")
        print("   (This may take 30-60 seconds for AI analysis)\n")
        
        opportunities = await analyzer.find_opportunities(
            strategies=['breakout'],  # Just test breakouts for speed
            max_opportunities=2
        )
        
        print(f"\n✅ Found {len(opportunities)} opportunities\n")
        
        if opportunities:
            for i, opp in enumerate(opportunities, 1):
                print(f"{i}. {opp['symbol']} - {opp['ai_recommendation']}")
                print(f"   Scanner: {opp['scanner_strategy']} (score: {opp['scanner_score']})")
                print(f"   AI Confidence: {opp['ai_confidence']:.0%}")
                print(f"   Final Score: {opp['final_score']}")
                print(f"   Entry: ${opp['entry_price']}, Target: ${opp['target_price']}")
                print(f"   Reasoning: {opp['ai_reasoning'][:100]}...")
                print()
        else:
            print("ℹ️  No opportunities found above confidence threshold")
            print("   (This is normal - market conditions may not show strong opportunities)")
        
        print("=" * 50)
        print("✅ Analyzer test complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'db' in locals():
            db.close()

# Run async test
if __name__ == "__main__":
    asyncio.run(test_analyzer())
