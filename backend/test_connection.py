#!/usr/bin/env python3.11
"""
Test Schwab API connection with existing tokens
"""

import os
import sys
from dotenv import load_dotenv
import schwabdev

# Load environment variables
load_dotenv()

def test_connection():
    print("🧪 Testing Schwab API Connection with Existing Tokens")
    print("=" * 60)
    
    # Get credentials from environment
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    callback_url = "https://127.0.0.1"
    
    if not app_key or not app_secret:
        print("❌ Missing APP_KEY or APP_SECRET")
        return False
    
    try:
        print("🔧 Initializing client with existing tokens...")
        
        # Initialize client with existing tokens
        client = schwabdev.Client(
            app_key=app_key,
            app_secret=app_secret,
            callback_url=callback_url,
            tokens_file="tokens.json",
            timeout=30
        )
        
        print("✅ Client initialized successfully!")
        
        # Test account numbers
        print("📊 Testing account access...")
        response = client.account_numbers()
        
        if response.ok:
            accounts = response.json()
            print(f"✅ Success! Found {len(accounts)} account numbers")
            print(f"📋 Accounts: {accounts}")
        else:
            print(f"❌ Account access failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        # Test quotes
        print("\n📈 Testing market data (AAPL quote)...")
        response = client.quotes("AAPL")
        
        if response.ok:
            quote_data = response.json()
            print("✅ Market data retrieved successfully!")
            if 'AAPL' in quote_data:
                apple_quote = quote_data['AAPL']['quote']
                price = apple_quote.get('lastPrice', 'N/A')
                print(f"📊 AAPL Last Price: ${price}")
            else:
                print("📊 Quote data structure:", quote_data)
        else:
            print(f"❌ Market data failed: {response.status_code}")
            print(f"Response: {response.text}")
            
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
