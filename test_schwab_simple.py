#!/usr/bin/env python3
"""
Simple Schwab OAuth URL generator and token exchanger
No external dependencies required
"""

import os
import sys

def main():
    print("🔐 Schwab API Connection Test")
    print("═" * 60)
    print()
    
    # Read .env file manually
    env_vars = {}
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("❌ .env file not found")
        return False
    
    app_key = env_vars.get('APP_KEY', '')
    app_secret = env_vars.get('APP_SECRET', '')
    callback_url = env_vars.get('CALLBACK_URL', 'https://127.0.0.1')
    
    if not app_key or not app_secret:
        print("❌ Missing APP_KEY or APP_SECRET in .env")
        return False
    
    print(f"✅ APP_KEY: {app_key[:8]}...{app_key[-4:]}")
    print(f"✅ APP_SECRET: {app_secret[:4]}...{app_secret[-4:]}")
    print(f"✅ CALLBACK_URL: {callback_url}")
    print()
    
    # Generate authorization URL
    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri=https://127.0.0.1&response_type=code"
    
    print("🔗 Step 1: Get Authorization Code")
    print("─" * 60)
    print()
    print("Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("After you log in and authorize:")
    print("  • You'll be redirected to: https://127.0.0.1/?code=XXXXX")
    print("  • Browser will show 'connection refused' - THIS IS NORMAL ✅")
    print("  • Copy the ENTIRE URL from your browser's address bar")
    print()
    print("═" * 60)
    print()
    
    # Get callback URL from user
    try:
        redirect_url = input("Paste the full redirect URL here: ").strip()
        
        if not redirect_url:
            print("\n❌ No URL provided")
            return False
        
        # Parse authorization code
        if '?code=' in redirect_url:
            auth_code = redirect_url.split('?code=')[1].split('&')[0]
        elif '&code=' in redirect_url:
            auth_code = redirect_url.split('&code=')[1].split('&')[0]
        else:
            print("\n❌ No 'code' parameter found in URL")
            if 'error=' in redirect_url:
                error = redirect_url.split('error=')[1].split('&')[0]
                print(f"   Authorization error: {error}")
            return False
        
        print(f"\n✅ Authorization code extracted: {auth_code[:20]}...")
        print()
        
        # Step 2: Exchange for tokens
        print("🔄 Step 2: Exchange Code for Access Token")
        print("─" * 60)
        print()
        
        import urllib.request
        import urllib.parse
        import json
        import base64
        
        token_url = "https://api.schwabapi.com/v1/oauth/token"
        
        # Create basic auth header
        credentials = f"{app_key}:{app_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Prepare request
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': 'https://127.0.0.1'
        }
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        print(f"Requesting tokens from: {token_url}")
        print(f"Using redirect_uri: https://127.0.0.1")
        print()
        
        # Make request
        req = urllib.request.Request(
            token_url,
            data=urllib.parse.urlencode(data).encode(),
            headers=headers
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                tokens = json.loads(response.read().decode())
                
                print("✅ SUCCESS! Tokens obtained")
                print()
                print(f"  Access Token: {tokens.get('access_token', 'N/A')[:30]}...")
                print(f"  Refresh Token: {tokens.get('refresh_token', 'N/A')[:30]}...")
                print(f"  Expires In: {tokens.get('expires_in', 'N/A')} seconds")
                print(f"  Token Type: {tokens.get('token_type', 'N/A')}")
                print()
                
                # Save tokens
                with open('tokens.json', 'w') as f:
                    json.dump(tokens, f, indent=2)
                
                print(f"💾 Tokens saved to: tokens.json")
                print()
                print("🎉 Schwab API connection successful!")
                print("   You can now use market data and trading features.")
                return True
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            print(f"❌ Token exchange failed: {e.code}")
            print(f"\nResponse:")
            print(error_body)
            print()
            
            if e.code == 400:
                print("💡 Troubleshooting 400 Bad Request:")
                print("   1. App status must be 'Ready for Use' (not 'Approved - Pending')")
                print("   2. Verify redirect_uri in portal is: https://127.0.0.1")
                print("   3. Authorization code can only be used once")
                print("   4. Code expires quickly - complete flow within minutes")
            elif e.code == 401:
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
    success = main()
    print()
    
    if success:
        print("═" * 60)
        print("✅ All tests passed!")
        print()
        print("Next steps:")
        print("  1. Backend can now fetch real market data")
        print("  2. Tokens will auto-refresh when they expire")
        sys.exit(0)
    else:
        print("═" * 60)
        print("❌ Connection test failed")
        print()
        print("Need help?")
        print("  1. Check docs/SCHWAB-CONNECTION-FIX.md")
        print("  2. Verify portal at https://beta-developer.schwab.com/")
        print("  3. Ensure app status is 'Ready for Use'")
        sys.exit(1)
