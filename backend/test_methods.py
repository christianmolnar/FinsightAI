"""
Test script to find available Schwab API account methods
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import schwabdev

def test_schwab_methods():
    app_key = os.getenv('APP_KEY')
    app_secret = os.getenv('APP_SECRET') 
    callback_url = os.getenv('CALLBACK_URL')
    
    if not app_key or not app_secret:
        print("Missing APP_KEY or APP_SECRET")
        return
        
    try:
        client = schwabdev.Client(
            app_key=app_key,
            app_secret=app_secret,
            callback_url=callback_url,
            tokens_file="tokens.json"
        )
        
        # Get all methods that contain 'account'
        account_methods = [method for method in dir(client) if 'account' in method.lower() and not method.startswith('_')]
        print("Available account methods:")
        for method in account_methods:
            print(f"  - {method}")
            
        print("\nTesting account_linked()...")
        response = client.account_linked()
        if response.ok:
            accounts = response.json()
            print(f"Found {len(accounts)} accounts")
            
            for account in accounts:
                account_hash = account.get('hashValue')
                account_number = account.get('accountNumber')
                print(f"\nTesting account {account_number} (hash: {account_hash[:8]}...)")
                
                # Try different potential methods
                potential_methods = [
                    'account_details',
                    'account_info', 
                    'account_positions',
                    'account_balances',
                    'account_summary'
                ]
                
                for method_name in potential_methods:
                    if hasattr(client, method_name):
                        print(f"  ✅ Found method: {method_name}")
                        try:
                            method = getattr(client, method_name)
                            # Try calling with account hash
                            test_response = method(account_hash)
                            print(f"    ✅ {method_name}({account_hash[:8]}...) works!")
                        except Exception as e:
                            print(f"    ❌ {method_name}({account_hash[:8]}...) failed: {e}")
                    else:
                        print(f"  ❌ No method: {method_name}")
        else:
            print(f"Failed to get accounts: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_schwab_methods()
