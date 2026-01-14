# Stock Order Types - Educational Guide

## Overview
Understanding different order types is crucial for implementing effective trading strategies. Each order type serves specific purposes and use cases in real-world trading.

---

## 1. Market Order

### Description
A **market order** executes immediately at the best available price in the market.

### How It Works
- Submits to the market instantly
- Fills at whatever price buyers/sellers are offering right now
- Guarantees execution (if market is open)
- Does NOT guarantee price

### Use Cases
- You want to enter/exit a position immediately
- Liquidity is high (popular stocks)
- You prioritize speed over price precision

### Example
```
Current F price: $14.02
Place market BUY order for 100 shares
→ Executes immediately at $14.02 (or very close)
```

### Pros
✅ Instant execution  
✅ Guaranteed to fill (during market hours)  
✅ Simple and straightforward

### Cons
❌ No price control  
❌ Can get "slippage" (different price than expected)  
❌ Risky in volatile or low-liquidity stocks

---

## 2. Limit Order

### Description
A **limit order** only executes at your specified price **or better**.

### How It Works
- Sets a maximum price (for BUY) or minimum price (for SELL)
- Order sits in queue until price condition is met
- May never fill if price doesn't reach your limit
- "Or better" means: buy at limit or LOWER, sell at limit or HIGHER

### Use Cases
- You want price control
- You're patient and willing to wait
- You want to avoid overpaying/underselling

### Example: Limit BUY
```
Current F price: $14.02
Place limit BUY at $14.10 for 100 shares
→ Executes immediately at $14.02 (better than limit!)

Current F price: $14.50
Place limit BUY at $14.10 for 100 shares
→ Queues and waits until price drops to $14.10 or below
```

### Example: Limit SELL
```
Current AAPL price: $180
Place limit SELL at $185 for 50 shares
→ Queues and waits until price rises to $185 or above
```

### Pros
✅ Price control  
✅ Can get better price than expected  
✅ Good for illiquid stocks (avoid slippage)

### Cons
❌ May never execute  
❌ Can miss opportunities if price moves away  
❌ Requires monitoring

---

## 3. Stop Order (Stop Market Order)

### Description
A **stop order** triggers a market order when the price reaches your stop price. Used for **breakout trading** (buy) or **stop-loss** (sell).

### How It Works
- Monitors market price continuously
- When price hits stop price, converts to market order
- Executes immediately after trigger (at whatever market price)
- Stop BUY: Triggers when price RISES to stop price
- Stop SELL: Triggers when price DROPS to stop price

### Use Cases

#### Stop BUY (Breakout Trading)
- **Scenario**: Stock is consolidating, you want to enter only if it breaks out
- **Strategy**: Place stop buy ABOVE current price
- **Benefit**: Only buy if momentum confirms

#### Stop SELL (Stop-Loss)
- **Scenario**: You own stock, want to limit losses if price drops
- **Strategy**: Place stop sell BELOW current price
- **Benefit**: Automatic risk management

### Example: Stop BUY (Breakout)
```
Current F price: $14.02
Resistance level: $14.50
Place stop BUY at $14.50 for 100 shares

If price rises to $14.50:
→ Triggers immediately
→ Converts to market order
→ Executes at ~$14.50 (or higher if momentum is strong)

If price stays below $14.50:
→ Order remains queued
→ No execution, no risk
```

**Real-World Application**: Momentum/breakout trading
- Stock stuck in range $13-$14
- You believe breakout above $14.50 signals bullish trend
- Stop buy at $14.50 ensures you only enter if breakout happens

### Example: Stop SELL (Stop-Loss)
```
Own 100 shares of AAPL at $180 avg cost
Current price: $185 (up $5)
Place stop SELL at $182 for 100 shares

If price drops to $182:
→ Triggers immediately
→ Converts to market order
→ Executes at ~$182, locking in +$2/share profit

If price stays above $182:
→ Order remains queued
→ Position protected from major loss
```

**Real-World Application**: Risk management
- Protect gains on winning positions
- Limit losses on losing positions
- Sleep well knowing downside is capped

### Pros
✅ Automatic execution when conditions met  
✅ Captures breakout momentum  
✅ Protects against large losses  
✅ No constant monitoring required

### Cons
❌ No price control after trigger (market order)  
❌ Can trigger on temporary price spikes  
❌ "Slippage" - execution price may differ from stop price  
❌ Can be triggered by flash crashes or manipulation

---

## 4. Stop-Limit Order

### Description
A **stop-limit order** combines stop and limit orders: triggers at stop price, then becomes a limit order.

### How It Works
- Monitors market for stop price (trigger)
- When triggered, converts to LIMIT order (not market)
- Only executes at limit price or better
- Provides price control after trigger

### Use Cases
- Want stop protection but with price control
- Willing to risk non-execution for better price
- Volatile stocks where slippage is a concern

### Example: Stop-Limit BUY
```
Current F price: $14.02
Place stop-limit BUY:
- Stop price: $14.50 (trigger point)
- Limit price: $14.55 (max willing to pay)

If price rises to $14.50:
→ Triggers
→ Becomes limit order at $14.55
→ Only executes between $14.50-$14.55
→ If price jumps to $14.60, order doesn't fill
```

### Example: Stop-Limit SELL
```
Own 100 TSLA at $200
Current price: $220
Place stop-limit SELL:
- Stop price: $210 (trigger point)
- Limit price: $208 (minimum acceptable)

If price drops to $210:
→ Triggers
→ Becomes limit order at $208
→ Only executes at $208 or above
→ If price crashes to $200, order doesn't fill (you're still holding)
```

### Pros
✅ Stop trigger for automation  
✅ Price control after trigger  
✅ Avoid worst-case slippage scenarios

### Cons
❌ May not execute (double risk)  
❌ More complex to set up  
❌ Can leave you unprotected if price moves too fast  
❌ Requires both stop and limit price decisions

---

## Comparison Table

| Order Type | Execution Speed | Price Control | Guaranteed Fill | Best For |
|------------|----------------|---------------|-----------------|----------|
| **Market** | ⚡ Instant | ❌ None | ✅ Yes (market hours) | Immediate entry/exit |
| **Limit** | ⏳ When price reached | ✅ Yes | ❌ No | Price-sensitive trades |
| **Stop** | ⚡ After trigger | ❌ None | ⚡ Yes (after trigger) | Breakouts, stop-loss |
| **Stop-Limit** | ⏳ After trigger + limit | ✅ Yes | ❌ No | Protected breakouts |

---

## Real-World Trading Scenarios

### Scenario 1: Conservative Investor (Limit Orders)
**Goal**: Buy undervalued stock at good price
```
Stock trading at $50
Analysis shows fair value: $45
Place limit BUY at $46
→ Only buy if price drops to opportunity zone
→ Willing to wait or miss the trade
```

### Scenario 2: Momentum Trader (Stop Orders)
**Goal**: Catch breakout moves
```
Stock consolidating at $30-$32 for weeks
Resistance at $33
Place stop BUY at $33.10
→ Only enter if breakout confirmed
→ Avoid false breakouts (price bounces back)
```

### Scenario 3: Risk Manager (Stop-Loss)
**Goal**: Protect portfolio from large losses
```
Own 1000 shares at $100
Willing to risk 5% max
Place stop SELL at $95
→ Automatically exit if loss threshold hit
→ Prevents emotional decision-making
```

### Scenario 4: Swing Trader (Stop-Limit)
**Goal**: Catch swing moves with price control
```
Stock at $60, expecting move to $65
Place stop-limit BUY:
- Stop: $62 (confirmation of uptrend)
- Limit: $62.50 (max willing to pay)
→ Enter on confirmation but avoid chasing
```

---

## Current Implementation Status

### ✅ Implemented (January 13, 2026)
- Market orders (immediate execution)
- Limit orders (price-controlled execution)
- Stop orders (breakout/stop-loss triggers)
- Stop-limit orders (triggered + price-controlled)

### UI Features
- Order type dropdown with 4 options
- Context-aware helper text (changes based on BUY/SELL)
- Conditional input fields (limit price, stop price)
- Real-time price display
- Estimated total calculation
- Validation for required fields

### Backend Support
- Full Alpaca SDK integration
- All order types supported for live and paper trading
- Automatic conversion to Alpaca API format
- Error handling and validation

---

## Testing Recommendations

### Safe Testing Approach
1. **Start with Paper Account**: Test all order types risk-free
2. **Small Position Sizes**: Use 1-5 shares for live testing
3. **Cheap Stocks**: Test with $5-$15 stocks to minimize risk
4. **Market Hours**: Test during active trading for realistic fills

### Test Scenarios

#### Test 1: Limit Order Below Market
```
Pick stock at $14.50
Place limit BUY at $14.00
Observe: Order queues, waits for price drop
```

#### Test 2: Stop Buy Breakout
```
Pick stock at $14.00
Place stop BUY at $14.50
Observe: Order queues, triggers when price rises
```

#### Test 3: Stop-Loss Protection
```
Buy 1 share at market
Place stop SELL 2% below entry
Observe: Order queues as protection
```

---

## Key Takeaways

1. **Market Orders**: Speed over price - use when urgency matters
2. **Limit Orders**: Price over speed - use when patience pays
3. **Stop Orders**: Automation + momentum - use for breakouts and protection
4. **Stop-Limit Orders**: Automation + control - use when you want both

**Remember**: The "best" order type depends on your:
- Trading strategy
- Risk tolerance
- Time horizon
- Market conditions
- Stock liquidity

---

*Last Updated: January 13, 2026*  
*Feature Branch: feature/alpaca-migration*
