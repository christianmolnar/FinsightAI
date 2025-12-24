#!/usr/bin/env python3
"""
Test live market data from Schwab API
"""

from schwabdev import Client
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
app_key = os.getenv('APP_KEY')
app_secret = os.getenv('APP_SECRET')

print('Initializing Schwab client...')
client = Client(app_key, app_secret, tokens_file='tokens.json')

# Fetch live quotes
print('\n' + '='*50)
print('LIVE MARKET DATA TEST')
print('='*50)

symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']

for symbol in symbols:
    try:
        print(f'\n--- {symbol} ---')
        response = client.quote(symbol)
        
        if symbol in response:
            data = response[symbol]['quote']
            print(f"Last Price: ${data.get('lastPrice', 'N/A'):.2f}")
            print(f"Change: ${data.get('netChange', 0):.2f} ({data.get('netPercentChange', 0):.2f}%)")
            print(f"Bid: ${data.get('bidPrice', 'N/A'):.2f} x {data.get('bidSize', 0)}")
            print(f"Ask: ${data.get('askPrice', 'N/A'):.2f} x {data.get('askSize', 0)}")
            print(f"Volume: {data.get('totalVolume', 0):,}")
            print(f"52W Range: ${data.get('52WeekLow', 0):.2f} - ${data.get('52WeekHigh', 0):.2f}")
        else:
            print(f'❌ No data returned for {symbol}')
            print(json.dumps(response, indent=2))
    except Exception as e:
        print(f'❌ Error fetching {symbol}: {e}')

print('\n' + '='*50)
print('✅ Schwab API live market data test complete!')
print('='*50)
