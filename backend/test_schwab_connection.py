#!/usr/bin/env python3
"""
Test Schwab API connection with corrected redirect_uri
Based on Schwab support feedback: redirect_uri should match exactly what's in the developer portal
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_schwab_connection():
    print("🔐 Testing Schwab API Connection")
    print("=" * 60)
    print()
    
    # Get credentials
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    callback_url = os.getenv('CALLBACK_URL', 'https://127.0.0.1')
    
    # Check credentials
    if not app_key or not app_secret:
        print("❌ Missing credentials in .env file")
        print("   Please run: python backend/setup_schwab.py")
        return False
    
    if app_key.startswith('your_') or app_secret.startswith('your_'):
        print("❌ Placeholder credentials detected")
        print("   Please update .env with real credentials from Schwab Developer Portal")
        return False
    
    print(f"✅ APP_KEY found: {app_key[:8]}...{app_key[-4:]}")
    print(f"✅ APP_SECRET found: {app_secret[:4]}...{app_secret[-4:]}")
    print(f"✅ CALLBACK_URL: {callback_url}")
    print()
    
    # Schwab's feedback says to use https://127.0.0.1
    print("📋 According to Schwab Support:")
    print("   Your callback URL in developer portal is: https://127.0.0.1")
    print("   So redirect_uri parameter should be: https://127.0.0.1")
    print()
    
    # Generate authorization URL
    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1&response_type=code"
    
    print("🔗 Step 1: Get Authorization Code")
    print("-" * 60)
    print("Open this URL in your browser (or paste it):")
    print()
    print(auth_url)
    print()
    print("After you log in and authorize:")
    print("  1. You'll be redirected to: https://127.0.0.1/?code=XXXXX")
    print("  2. Browser will show 'connection refused' or similar - THIS IS NORMAL")
    print("  3. Copy the ENTIRE URL from your browser's address bar")
    print("  4. The URL contains the authorization code we need")
    print()
    print("=" * 60)
    print()
    
    # Get the callback URL
    try:
        callback_response = input("Paste the full redirect URL here: ").strip()
        
        if not callback_response:
            print("\n❌ No URL provided")
            return False
        
        # Parse authorization code
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(callback_response)
        params = parse_qs(parsed.query)
        
        if 'code' not in params:
            print(f"\n❌ No 'code' parameter found in URL")
            print(f"   URL query: {parsed.query}")
            
            # Check for error
            if 'error' in params:
                print(f"\n⚠️  Authorization error: {params['error'][0]}")
                if 'error_description' in params:
                    print(f"   Description: {params['error_description'][0]}")
            return False
        
        auth_code = params['code'][0]
        print(f"\n✅ Authorization code extracted: {auth_code[:20]}...")
        print()
        
        # Step 2: Exchange for tokens
        print("🔄 Step 2: Exchange Code for Access Token")
        print("-" * 60)
        
        import requests
        import base64
        
        token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # IMPORTANT: Use the SAME redirect_uri as in the authorization URL
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'https://127.0.0.1'  # MUST match developer portal
        }
        
        print(f"Requesting tokens from: {token_url}")
        print(f"Using redirect_uri: https://127.0.0.1")
        print()
        
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ SUCCESS! Tokens obtained")
            print()
            print(f"  Access Token: {tokens.get('access_token', 'N/A')[:30]}...")
            print(f"  Refresh Token: {tokens.get('refresh_token', 'N/A')[:30]}...")
            print(f"  Expires In: {tokens.get('expires_in', 'N/A')} seconds")
            print(f"  Token Type: {tokens.get('token_type', 'N/A')}")
            print()
            
            # Save tokens
            import json
            tokens_file = 'tokens.json'
            with open(tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"💾 Tokens saved to: {tokens_file}")
            print()
            print("🎉 Schwab API connection successful!")
            print("   You can now use the market data and trading features.")
            return True
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"\nResponse:")
            print(response.text)
            print()
            
            # Common errors
            if response.status_code == 400:
                print("💡 Troubleshooting 400 Bad Request:")
                print("   1. Make sure your app status is 'Ready for Use' (not 'Approved - Pending')")
                print("   2. Verify redirect_uri in developer portal is: https://127.0.0.1")
                print("   3. Authorization code can only be used once - get a new one")
                print("   4. Code expires quickly - complete the flow within a few minutes")
            elif response.status_code == 401:
                print("💡 Troubleshooting 401 Unauthorized:")
                print("   1. Verify APP_KEY and APP_SECRET are correct")
                print("   2. Check credentials in Schwab Developer Portal")
            
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    success = test_schwab_connection()
    print()
    
    if success:
        print("✅ All tests passed!")
        print()
        print("Next steps:")
        print("  1. Backend can now fetch real market data")
        print("  2. Test with: python backend/app/schwab_api.py")
        sys.exit(0)
    else:
        print("❌ Connection test failed")
        print()
        print("Need help?")
        print("  1. Check docs/SCHWAB-SETUP.md for detailed instructions")
        print("  2. Verify developer portal settings at https://beta-developer.schwab.com/")
        print("  3. Ensure app status is 'Ready for Use'")
        sys.exit(1)
