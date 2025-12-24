#!/usr/bin/env python3
"""
Simple test for Schwab API live quotes - no browser windows!
This uses the existing tokens and handles refresh automatically.
"""

import json
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
APP_KEY = os.getenv('APP_KEY')
APP_SECRET = os.getenv('APP_SECRET')
TOKENS_FILE = 'tokens.json'

def load_tokens():
    """Load tokens from file"""
    try:
        with open(TOKENS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading tokens: {e}")
        return None

def save_tokens(tokens):
    """Save tokens to file"""
    try:
        with open(TOKENS_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
        print("✅ Tokens saved successfully")
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token"""
    print("\n🔄 Access token expired, refreshing...")
    
    token_url = "https://api.schwabapi.com/v1/oauth/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET
    }
    
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        new_tokens = response.json()
        print("✅ Access token refreshed successfully!")
        
        # Save new tokens
        save_tokens(new_tokens)
        
        return new_tokens
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        return None

def get_quote(symbol, access_token):
    """Get a quote for a symbol"""
    url = f"https://api.schwabapi.com/marketdata/v1/quotes?symbols={symbol}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # If unauthorized, might need to refresh token
        if response.status_code == 401:
            return None, True  # Signal that we need to refresh
        
        response.raise_for_status()
        return response.json(), False
        
    except Exception as e:
        print(f"❌ Error fetching quote: {e}")
        if hasattr(response, 'text'):
            print(f"Response: {response.text}")
        return None, False

def main():
    print("="*60)
    print("📈 SCHWAB API LIVE QUOTES TEST (No Browser Windows!)")
    print("="*60)
    
    # Load tokens
    tokens = load_tokens()
    if not tokens:
        print("❌ No tokens found. Please run manual_auth.py first.")
        return
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    
    print(f"\n✅ Tokens loaded from {TOKENS_FILE}")
    
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"📊 Fetching {symbol}")
        print(f"{'='*60}")
        
        # Try to get quote
        data, needs_refresh = get_quote(symbol, access_token)
        
        # If we need to refresh the token, do it once
        if needs_refresh:
            print("⚠️  Access token expired, refreshing...")
            new_tokens = refresh_access_token(refresh_token)
            
            if new_tokens:
                access_token = new_tokens.get('access_token')
                refresh_token = new_tokens.get('refresh_token')
                
                # Try again with new token
                data, _ = get_quote(symbol, access_token)
            else:
                print("❌ Failed to refresh token. You may need to re-authenticate.")
                print("   Run: python manual_auth.py")
                return
        
        # Display the quote
        if data and symbol in data:
            quote = data[symbol]['quote']
            print(f"\n💰 {symbol} - Live Quote:")
            print(f"   Last Price: ${quote.get('lastPrice', 0):.2f}")
            print(f"   Change: ${quote.get('netChange', 0):.2f} ({quote.get('netPercentChange', 0):.2f}%)")
            print(f"   Bid: ${quote.get('bidPrice', 0):.2f} x {quote.get('bidSize', 0)}")
            print(f"   Ask: ${quote.get('askPrice', 0):.2f} x {quote.get('askSize', 0)}")
            print(f"   Volume: {quote.get('totalVolume', 0):,}")
            print(f"   52W High: ${quote.get('52WeekHigh', 0):.2f}")
            print(f"   52W Low: ${quote.get('52WeekLow', 0):.2f}")
            print(f"   Market Cap: ${quote.get('marketCap', 0):,.0f}")
        else:
            print(f"❌ No data received for {symbol}")
    
    print(f"\n{'='*60}")
    print("✅ Live quotes test complete!")
    print("="*60)
    print("\n💡 No browser windows opened - tokens refreshed automatically!")

if __name__ == "__main__":
    main()
