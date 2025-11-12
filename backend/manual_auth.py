#!/usr/bin/env python3.11
"""
Manual Schwab API token setup
Creates tokens.json by manually handling the OAuth flow
"""

import os
import sys
import json
import requests
import base64
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🔐 Manual Schwab API Token Setup")
    print("=" * 50)
    
    # Get credentials from environment
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET')
    
    if not app_key or not app_secret:
        print("❌ Missing APP_KEY or APP_SECRET in .env file")
        return False
    
    print(f"📋 App Key: {app_key[:8]}...")
    print(f"📋 App Secret: {app_secret[:4]}...")
    print()
    
    # Step 1: Generate the authorization URL
    callback_url = "https://127.0.0.1"
    auth_url = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={app_key}&redirect_uri={callback_url}&response_type=code"
    
    print("🔗 Step 1: Authorization URL")
    print(f"Open this URL in your browser: {auth_url}")
    print()
    print("📋 After authorization, you'll be redirected to a URL that starts with:")
    print("https://127.0.0.1/?code=...")
    print("Copy the ENTIRE URL and paste it here.")
    print()
    
    # Get the callback URL with authorization code
    callback_response = input("Paste the full callback URL here: ").strip()
    
    if not callback_response.startswith("https://127.0.0.1"):
        print("❌ Invalid callback URL. It should start with https://127.0.0.1")
        return False
    
    # Parse the authorization code
    parsed_url = urlparse(callback_response)
    query_params = parse_qs(parsed_url.query)
    
    if 'code' not in query_params:
        print("❌ No authorization code found in the callback URL")
        return False
    
    auth_code = query_params['code'][0]
    print(f"✅ Authorization code extracted: {auth_code[:10]}...")
    
    # Step 2: Exchange code for tokens
    print("\n🔄 Step 2: Exchanging code for access token...")
    
    token_url = "https://api.schwabapi.com/v1/oauth/token"
    
    # Prepare the token request
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{app_key}:{app_secret}".encode()).decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': callback_url
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        
        if response.status_code == 200:
            tokens = response.json()
            print("✅ Tokens obtained successfully!")
            
            # Save tokens to file
            with open('tokens.json', 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print("💾 Tokens saved to tokens.json")
            print(f"🔑 Access token expires in: {tokens.get('expires_in', 'unknown')} seconds")
            print(f"🔄 Refresh token available: {'refresh_token' in tokens}")
            
            return True
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
