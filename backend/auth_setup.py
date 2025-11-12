#!/usr/bin/env python3.11
"""
One-time Schwab API authentication setup script
This will create the tokens.json file needed for API access
"""

import os
import sys
from dotenv import load_dotenv
import schwabdev

# Load environment variables
load_dotenv()

def main():
    print("🔐 Schwab API Authentication Setup")
    print("=" * 50)
    
    # Get credentials from environment
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    # Use localhost for easier callback capture
    callback_url = "https://127.0.0.1"
    
    if not app_key or not app_secret:
        print("❌ Missing APP_KEY or APP_SECRET in .env file")
        return False
    
    print(f"📋 App Key: {app_key[:8]}...")
    print(f"🔗 Using localhost callback for easier authentication")
    print()
    
    try:
        print("🚀 Starting authentication process...")
        print("📝 This will create a tokens.json file for API access")
        print("🌐 A browser will open for Schwab authentication")
        print("📋 After authorization, copy the FULL redirect URL and paste it back here")
        print()
        
        # Initialize client - this will handle the OAuth flow
        client = schwabdev.Client(
            app_key=app_key,
            app_secret=app_secret,
            callback_url=callback_url,
            tokens_file="tokens.json",
            timeout=30
        )
        
        print("✅ Authentication successful!")
        print("💾 Tokens saved to tokens.json")
        
        # Test the connection
        print("\n🧪 Testing API connection...")
        try:
            accounts = client.account_linked()
            if accounts.ok:
                account_data = accounts.json()
                print(f"📊 Successfully connected! Found {len(account_data)} linked accounts")
                return True
            else:
                print(f"❌ API test failed: {accounts.status_code}")
                return False
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n📋 Troubleshooting tips:")
        print("1. Make sure your Schwab Developer app status is 'Ready for Use'")
        print("2. Ensure TOS (Thinkorswim) is enabled on your Schwab account")
        print("3. Use your regular Schwab brokerage account credentials")
        print("4. Make sure both APIs are added to your developer app:")
        print("   - Accounts and Trading Production")
        print("   - Market Data Production")
        print("5. Update your Schwab Developer app callback URL to: https://127.0.0.1")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
