#!/usr/bin/env python3.11
"""
Simple Schwab API test with correct method names
"""

import os
import sys
from dotenv import load_dotenv
import schwabdev

# Load environment variables
load_dotenv()

def test_simple():
    print("🧪 Simple Schwab API Test")
    print("=" * 40)
    
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    
    try:
        # Initialize client with existing tokens
        client = schwabdev.Client(
            app_key=app_key,
            app_secret=app_secret,
            callback_url="https://127.0.0.1",
            tokens_file="tokens.json",
            timeout=30
        )
        
        print("✅ Client initialized!")
        print(f"📋 Available methods: {[m for m in dir(client) if not m.startswith('_') and callable(getattr(client, m))]}")
        
        # Try to find the right method
        if hasattr(client, 'account_linked'):
            print("📊 Testing account_linked()...")
            response = client.account_linked()
            print(f"Status: {response.status_code}")
            if response.ok:
                print(f"✅ Success: {response.json()}")
            else:
                print(f"❌ Failed: {response.text}")
        
        if hasattr(client, 'quotes'):
            print("\n📈 Testing quotes('AAPL')...")
            response = client.quotes("AAPL")
            print(f"Status: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"✅ Success! Keys: {list(data.keys())}")
            else:
                print(f"❌ Failed: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple()
