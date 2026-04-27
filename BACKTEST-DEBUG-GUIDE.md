# Backtest Debug Mode Guide

## Overview

The backtest debug mode provides comprehensive logging to understand every calculation step in the backtesting engine. This is useful for:

- **Diagnosing calculation errors** - Verify P&L calculations are correct
- **Understanding trade decisions** - See why trades were entered/exited
- **Tracking capital flow** - Follow cash and portfolio value changes
- **Validating percentages** - Ensure return percentages match actual P&L

## Enabling Debug Mode

### Method 1: Environment Variable (Persistent)

Set the `BACKTEST_DEBUG` environment variable before starting the backend:

```bash
export BACKTEST_DEBUG=true
uvicorn app.main:app --reload
```

### Method 2: API Endpoint (Runtime)

Enable/disable debug mode without restarting:

```bash
# Enable debug logging
curl -X POST http://localhost:8000/api/backtest/debug/enable

# Disable debug logging
curl -X POST http://localhost:8000/api/backtest/debug/disable

# Check current status
curl http://localhost:8000/api/backtest/debug/status
```

## Debug Output

When debug mode is enabled, you'll see detailed logging in the backend console:

### 1. Backtest Run Parameters

```
================================================================
🚀 BACKTEST RUN STARTED - DEBUG MODE ENABLED
================================================================
Parameters:
  Date Range: 2024-01-01 to 2025-01-01
  Initial Capital: $30,000.00
  Position Size: 10.0% of portfolio
  Compounding: True
  Max Hold Days: 14
  Strategies: ALL
  AI: True (threshold: 75%)
  Exit Rules:
    - Profit Target: +15.0%
    - Stop Loss: -8.0%
    - Max Hold Days: 60
================================================================
```

### 2. Individual Trade Simulation

```
──────────────────────────────────────────────────
🔍 SIMULATING TRADE: AAPL
──────────────────────────────────────────────────
      Entry: $150.25 x 20 shares = $3,005.00
      Exit Rules: Profit=15.0%, Stop=-8.0%, MaxDays=60
      
      ✅ PROFIT TARGET hit on day 12: +16.4% at $174.89
      
      💰 FINAL P&L: +$492.80 (+16.4%)
         Entry: $150.25 × 20 = $3,005.00
         Exit: $174.89 × 20 = $3,497.80
         Reason: profit_target
```

### 3. Final Metrics Calculation

```
================================================================
🔍 BACKTEST METRICS CALCULATION DEBUG
================================================================
Initial Capital: $30,000.00
Total Trades: 1966

Profit/Loss Breakdown:
  Winning Trades: 1575 (80.1%)
  Total Profit from Winners: $12,450.75
  Total Loss from Losers: $-4,287.48
  Net Profit (Total P&L): $8,163.27

Capital Analysis:
  Starting: $30,000.00
  Net P&L: +$8,163.27
  Ending: $38,163.27
  Return: +27.21%
  Calculation: (38,163.27 - 30,000.00) / 30,000.00 * 100
  Verify: (8,163.27) / 30,000.00 * 100 = 27.21%
```

## Understanding the Output

### Exit Reasons

- **profit_target** - Trade hit the profit target (default: +15%)
- **stop_loss** - Trade hit the stop loss (default: -8%)
- **max_hold_time** - Trade held for maximum days (default: 60)
- **backtest_end** - Backtest period ended while trade was open

### Percentage Calculations

The return percentage is calculated as:

```python
return_pct = (final_capital - initial_capital) / initial_capital * 100
```

For example:
- Initial: $30,000
- Net P&L: +$8,163.27
- Final: $38,163.27
- Return: ($38,163.27 - $30,000) / $30,000 * 100 = **27.21%**

### Verification Formula

The debug output includes a verification formula that recalculates the percentage to catch any discrepancies:

```
Verify: (8,163.27) / 30,000.00 * 100 = 27.21%
```

If this doesn't match the displayed return percentage, there's a calculation bug.

## Troubleshooting Math Issues

If you see incorrect percentages:

1. **Check Initial Capital** - Verify the correct initial capital is being used
2. **Verify Net Profit** - Sum all trade P&Ls manually and compare
3. **Compare Verification** - The "Verify" line should match the "Return" line
4. **Check for Rounding** - Look for accumulation of rounding errors

### Example Issue

**User Report**: "$8,163.27 profit showing as 81.63% instead of 27.21%"

**Debug Analysis**:
```
# If you see:
Return: +81.63%
Verify: 27.21%

# This indicates initial_capital is being used incorrectly
# 81.63% suggests: $8,163 / $10,000 = 81.63%
# But actual: $8,163 / $30,000 = 27.21%

# Solution: Find where $10,000 is being used instead of $30,000
```

## Configuration

Exit rules and position sizing can be adjusted in `backend/config/backtest_config.py`:

```python
# Exit rules configuration
EXIT_RULES = {
    "profit_target_pct": 15.0,  # Take profit at +15%
    "stop_loss_pct": -8.0,      # Stop loss at -8%
    "trailing_stop_pct": None,   # Trailing stop (disabled)
    "max_hold_days": 60          # Maximum hold time
}

# Position sizing configuration
POSITION_SIZING = {
    "min_pct": 0.05,   # Minimum 5% per trade
    "max_pct": 0.15,   # Maximum 15% per trade
    "default_pct": 0.10  # Default 10%
}
```

## Performance Impact

Debug logging adds minimal overhead:

- **Console output only** - No file I/O
- **Conditional checks** - Only evaluates when BACKTEST_DEBUG=true
- **~5-10% slower** - Due to string formatting and logging calls

For production backtests, keep debug mode disabled.

## Tips

1. **Enable before testing** - Always enable debug mode when investigating issues
2. **Capture output** - Save logs to file for analysis:
   ```bash
   export BACKTEST_DEBUG=true
   uvicorn app.main:app --reload 2>&1 | tee backtest_debug.log
   ```
3. **Compare runs** - Run same backtest twice and diff the logs
4. **Check timestamps** - Verify trades are happening on correct dates
5. **Validate cash** - Ensure cash never goes negative

## Support

If debug logs reveal calculation errors:

1. Save the complete log output
2. Note the specific discrepancy (e.g., "Return shows X but should be Y")
3. Include the exact backtest parameters used
4. Provide the screenshot or error message

This helps diagnose issues quickly.
