"""
CLI script to run opportunity scanner
For use with Railway cron jobs or manual testing
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scan_opportunities import OpportunityScanJob

async def main():
    """Run scanner job"""
    scanner = OpportunityScanJob(
        confidence_threshold=0.75,  # 75% AI confidence minimum
        max_opportunities=5,        # Find up to 5 opportunities
        auto_create_proposals=True  # Auto-create proposals in DB
    )
    
    print("🚀 Starting f.insight Scanner...")
    result = await scanner.run()
    
    print(f"\n✅ Scan complete:")
    print(f"   Opportunities found: {result['opportunities_found']}")
    print(f"   Proposals created: {result['proposals_created']}")
    print(f"   Duration: {result['duration_seconds']}s")
    
    # Exit code 0 = success (for cron monitoring)
    exit(0 if result['status'] == 'success' else 1)

if __name__ == "__main__":
    asyncio.run(main())
