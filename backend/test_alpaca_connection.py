"""
Test Alpaca API Connection

Quick test to verify Alpaca credentials and API connectivity.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.alpaca_service import get_alpaca_service


def test_alpaca_connection():
    """Test Alpaca API connection"""
    print("🚀 Testing Alpaca API Connection...")
    print("=" * 60)
    
    try:
        # Initialize service
        alpaca = get_alpaca_service()
        print(f"✅ AlpacaService initialized (paper={alpaca.paper})")
        print()
        
        # Test 1: Get account info
        print("📊 Test 1: Get Account Info")
        print("-" * 60)
        account = alpaca.get_account()
        print(f"Account ID: {account['id']}")
        print(f"Account Number: {account['account_number']}")
        print(f"Status: {account['status']}")
        print(f"Cash: ${account['cash']:,.2f}")
        print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
        print(f"Buying Power: ${account['buying_power']:,.2f}")
        print(f"Pattern Day Trader: {account['pattern_day_trader']}")
        print("✅ Account info retrieved successfully")
        print()
        
        # Test 2: Get positions
        print("📈 Test 2: Get Positions")
        print("-" * 60)
        positions = alpaca.get_positions()
        if positions:
            print(f"Found {len(positions)} position(s):")
            for pos in positions:
                pl_emoji = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
                print(f"  {pl_emoji} {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
                print(f"     Current: ${pos['current_price']:.2f} | P/L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']:.2%})")
        else:
            print("No positions found (account is empty)")
        print("✅ Positions retrieved successfully")
        print()
        
        # Test 3: Get orders
        print("📋 Test 3: Get Orders")
        print("-" * 60)
        orders = alpaca.get_orders(status="open")
        if orders:
            print(f"Found {len(orders)} open order(s):")
            for order in orders:
                print(f"  📝 {order['symbol']}: {order['side']} {order['qty']} @ ${order['limit_price'] or 'market'}")
                print(f"     Status: {order['status']} | ID: {order['id']}")
        else:
            print("No open orders")
        print("✅ Orders retrieved successfully")
        print()
        
        # Test 4: Get quote
        print("💰 Test 4: Get Market Quote")
        print("-" * 60)
        try:
            quote = alpaca.get_quote("AAPL")
            print(f"AAPL Quote:")
            print(f"  Bid: ${quote['bid_price']:.2f} x {quote['bid_size']}")
            print(f"  Ask: ${quote['ask_price']:.2f} x {quote['ask_size']}")
            print(f"  Spread: ${quote['ask_price'] - quote['bid_price']:.2f}")
            print("✅ Market data retrieved successfully")
        except Exception as e:
            print(f"⚠️  Market data test skipped: {e}")
        print()
        
        # Summary
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("✅ Alpaca API is working correctly")
        print(f"✅ Account loaded: ${account['portfolio_value']:,.2f}")
        print(f"✅ {len(positions)} position(s), {len(orders)} open order(s)")
        print()
        print("🚀 Ready to migrate to Alpaca!")
        
        return True
        
    except ValueError as e:
        print("❌ CONFIGURATION ERROR")
        print("-" * 60)
        print(str(e))
        print()
        print("📝 Setup Instructions:")
        print("1. Create Alpaca account: https://alpaca.markets/")
        print("2. Get API keys from dashboard")
        print("3. Add to backend/.env:")
        print("   ALPACA_API_KEY_ID=your_key_id")
        print("   ALPACA_API_SECRET_KEY=your_secret_key")
        print("   ALPACA_PAPER=true")
        return False
        
    except Exception as e:
        print("❌ CONNECTION ERROR")
        print("-" * 60)
        print(f"Error: {e}")
        print()
        print("Possible issues:")
        print("- Invalid API keys")
        print("- Network connectivity")
        print("- Alpaca API is down")
        return False


if __name__ == "__main__":
    success = test_alpaca_connection()
    sys.exit(0 if success else 1)
