#!/usr/bin/env python3
"""
FInsightAI - Simple Automated Trading Agent

This agent continuously monitors stocks and executes trades based on
a simple momentum strategy:
- BUY: When stock drops >2% in a day
- SELL: When stock rises >3% from entry price

Usage:
    python trading_agent.py
"""

import requests
import time
from datetime import datetime
import pytz

# Configuration
API_URL = "https://finsightai-production-442e.up.railway.app"
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META"]
BUY_THRESHOLD = -2.0  # Buy if down 2%
SELL_THRESHOLD = 3.0  # Sell if up 3%
SCAN_INTERVAL = 300  # Check every 5 minutes
POSITION_SIZE = 5  # Number of shares to buy
MIN_CASH_RESERVE = 1000  # Keep $1000 in cash

def is_market_open():
    """Check if US stock market is open"""
    now = datetime.now(pytz.timezone('US/Eastern'))
    
    # Weekend check
    if now.weekday() >= 5:
        return False
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.hour > 9 or (now.hour == 9 and now.minute >= 30)
    market_closed = now.hour >= 16
    
    return market_open and not market_closed

def get_market_data(symbol):
    """Fetch real-time market data for a symbol"""
    try:
        response = requests.get(f"{API_URL}/api/v1/market-data/{symbol}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Failed to get data for {symbol}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching {symbol}: {e}")
        return None

def get_portfolio():
    """Get current paper portfolio"""
    try:
        response = requests.get(f"{API_URL}/api/v1/paper/portfolio", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Failed to get portfolio: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error fetching portfolio: {e}")
        return None

def execute_buy(symbol, quantity, price=None):
    """Execute a buy trade"""
    try:
        params = {"symbol": symbol, "quantity": quantity}
        if price:
            params["price"] = price
            
        response = requests.post(
            f"{API_URL}/api/v1/paper/trade/buy",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Buy failed for {symbol}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error buying {symbol}: {e}")
        return None

def execute_sell(symbol, quantity, price=None):
    """Execute a sell trade"""
    try:
        params = {"symbol": symbol, "quantity": quantity}
        if price:
            params["price"] = price
            
        response = requests.post(
            f"{API_URL}/api/v1/paper/trade/sell",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️  Sell failed for {symbol}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error selling {symbol}: {e}")
        return None

def check_buy_signals(portfolio):
    """Scan watchlist for buy signals"""
    cash = portfolio.get("cash_balance", 0)
    positions = portfolio.get("positions", {})
    
    if cash < MIN_CASH_RESERVE:
        print(f"⚠️  Low cash: ${cash:.2f} - Skipping buys")
        return
    
    print(f"\n💰 Cash available: ${cash:.2f}")
    
    for symbol in WATCHLIST:
        # Skip if we already have a position
        if symbol in positions:
            continue
            
        data = get_market_data(symbol)
        if not data:
            continue
        
        change_pct = data.get("change_percent", 0)
        price = data.get("price", 0)
        
        # BUY SIGNAL: Stock down more than threshold
        if change_pct <= BUY_THRESHOLD:
            cost = price * POSITION_SIZE
            
            if cash >= cost + MIN_CASH_RESERVE:
                print(f"\n🔵 BUY SIGNAL: {symbol}")
                print(f"   Price: ${price:.2f}")
                print(f"   Change: {change_pct:.2f}%")
                print(f"   Cost: ${cost:.2f}")
                
                result = execute_buy(symbol, POSITION_SIZE, price)
                if result:
                    print(f"✅ Bought {POSITION_SIZE} shares of {symbol} at ${price:.2f}")
                    cash -= cost
                else:
                    print(f"❌ Failed to buy {symbol}")
        else:
            print(f"   {symbol}: ${price:.2f} ({change_pct:+.2f}%) - No signal")

def check_sell_signals(portfolio):
    """Check existing positions for sell signals"""
    positions = portfolio.get("positions", {})
    
    if not positions:
        print("\n📭 No positions to check")
        return
    
    print(f"\n📊 Checking {len(positions)} position(s)")
    
    for symbol, position in positions.items():
        data = get_market_data(symbol)
        if not data:
            continue
        
        current_price = data.get("price", 0)
        avg_cost = position.get("avg_price", 0)
        quantity = position.get("quantity", 0)
        unrealized_pnl = position.get("unrealized_pnl", 0)
        
        # Calculate gain/loss percentage
        if avg_cost > 0:
            gain_pct = ((current_price - avg_cost) / avg_cost) * 100
        else:
            gain_pct = 0
        
        print(f"\n   {symbol}:")
        print(f"   • Quantity: {quantity:.0f} shares")
        print(f"   • Entry: ${avg_cost:.2f}")
        print(f"   • Current: ${current_price:.2f}")
        print(f"   • Gain/Loss: {gain_pct:+.2f}% (${unrealized_pnl:+.2f})")
        
        # SELL SIGNAL: Profit target hit
        if gain_pct >= SELL_THRESHOLD:
            print(f"🟢 SELL SIGNAL: {symbol} up {gain_pct:.2f}%")
            result = execute_sell(symbol, quantity, current_price)
            if result:
                print(f"✅ Sold {quantity:.0f} shares of {symbol} at ${current_price:.2f}")
                print(f"   💵 Profit: ${unrealized_pnl:.2f}")
            else:
                print(f"❌ Failed to sell {symbol}")
        
        # STOP LOSS: Down more than 5%
        elif gain_pct <= -5.0:
            print(f"🔴 STOP LOSS: {symbol} down {gain_pct:.2f}%")
            result = execute_sell(symbol, quantity, current_price)
            if result:
                print(f"✅ Sold {quantity:.0f} shares of {symbol} at ${current_price:.2f}")
                print(f"   💸 Loss: ${unrealized_pnl:.2f}")
            else:
                print(f"❌ Failed to sell {symbol}")

def print_summary(portfolio):
    """Print portfolio summary"""
    cash = portfolio.get("cash_balance", 0)
    total_value = portfolio.get("total_value", 0)
    positions = portfolio.get("positions", {})
    
    print("\n" + "="*60)
    print(f"📊 PORTFOLIO SUMMARY")
    print("="*60)
    print(f"💰 Cash: ${cash:,.2f}")
    print(f"📈 Total Value: ${total_value:,.2f}")
    print(f"📦 Positions: {len(positions)}")
    
    if positions:
        print("\nHoldings:")
        for symbol, pos in positions.items():
            print(f"   • {symbol}: {pos['quantity']:.0f} shares @ ${pos['avg_price']:.2f} "
                  f"(P&L: ${pos['unrealized_pnl']:+.2f})")
    
    print("="*60 + "\n")

def trading_loop():
    """Main trading loop"""
    print("\n" + "="*60)
    print("🤖 FInsightAI Trading Agent Started")
    print("="*60)
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 API URL: {API_URL}")
    print(f"👀 Watchlist: {', '.join(WATCHLIST)}")
    print(f"📊 Strategy: Buy if down >{abs(BUY_THRESHOLD)}%, Sell if up >{SELL_THRESHOLD}%")
    print(f"🔄 Scan Interval: {SCAN_INTERVAL}s ({SCAN_INTERVAL/60:.0f} min)")
    print("="*60 + "\n")
    
    iteration = 0
    
    while True:
        iteration += 1
        now = datetime.now()
        
        print(f"\n{'='*60}")
        print(f"🔄 Iteration #{iteration}")
        print(f"⏰ {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Check if market is open
        if not is_market_open():
            print("💤 Market is CLOSED")
            print(f"   Sleeping for {SCAN_INTERVAL}s...")
            time.sleep(SCAN_INTERVAL)
            continue
        
        print("✅ Market is OPEN")
        
        # Get current portfolio
        portfolio = get_portfolio()
        if not portfolio:
            print("❌ Failed to fetch portfolio, retrying in 60s...")
            time.sleep(60)
            continue
        
        # Print summary
        print_summary(portfolio)
        
        # Check for sell signals first (exit before new entries)
        check_sell_signals(portfolio)
        
        # Then check for buy signals
        check_buy_signals(portfolio)
        
        # Wait before next scan
        print(f"\n⏳ Sleeping for {SCAN_INTERVAL}s ({SCAN_INTERVAL/60:.0f} min)...")
        print(f"   Next scan at: {(now + datetime.timedelta(seconds=SCAN_INTERVAL)).strftime('%H:%M:%S')}")
        time.sleep(SCAN_INTERVAL)

def main():
    """Entry point"""
    try:
        trading_loop()
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
        print(f"⏰ End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
