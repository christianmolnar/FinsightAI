# Strategy Parameter Optimization Guide

## Overview

Now that backtesting works correctly, you can use it to tune strategy parameters systematically. This guide shows you how to optimize parameters using backtest results.

## Current System

### What's Already Built ✅

1. **Strategy Parameter Database** (`backend/app/models/strategy_parameters.py`)
   - Stores all tunable parameters
   - Tracks AI-suggested values
   - Records optimization performance
   - Supports per-stock overrides

2. **Backtest System** (Just Fixed!)
   - Runs historical simulations
   - Returns detailed metrics (return %, win rate, Sharpe ratio, max drawdown)
   - Debug mode for transparency

3. **AI Optimizer Skeleton** (`backend/api/ai_optimizer.py`)
   - Framework exists but needs connection to backtesting

## Parameter Categories

### 1. Exit Rules (Currently in `config/backtest_config.py`)

```python
EXIT_RULES = {
    "profit_target_pct": 15.0,  # Take profit at +15%
    "stop_loss_pct": -8.0,      # Stop loss at -8%
    "trailing_stop_pct": None,   # Trailing stop (disabled)
    "max_hold_days": 60          # Maximum hold time
}
```

**What to tune:**
- Profit target: Higher = fewer wins but bigger gains
- Stop loss: Tighter = more stops, looser = bigger losses
- Max hold days: Shorter = faster turnover, longer = more patience

### 2. Position Sizing (Currently in `config/backtest_config.py`)

```python
POSITION_SIZING = {
    "min_pct": 0.05,     # Minimum 5% per trade
    "max_pct": 0.15,     # Maximum 15% per trade
    "default_pct": 0.10  # Default 10%
}
```

**What to tune:**
- Larger positions = higher risk/reward
- Smaller positions = more diversification

### 3. Entry Criteria (In Scanner/AI Analyzer)

**Scanner thresholds:**
- Technical breakout: RSI, volume, price action
- Earnings momentum: EPS growth, beat rate
- Seasonality: Historical win rate, calendar patterns

**AI confidence:**
- Minimum confidence threshold (currently 75%)
- How much weight to give AI vs scanner scores

## How to Optimize: Two Approaches

### Approach 1: Manual Grid Search (Simple, Transparent)

**Step 1: Define Parameter Grid**
```python
# Example: Optimize exit rules
param_grid = {
    "profit_target": [10, 15, 20, 25],
    "stop_loss": [-5, -8, -10, -12],
    "max_hold_days": [30, 60, 90]
}

# Total combinations: 4 × 4 × 3 = 48 backtests
```

**Step 2: Run Backtests for Each Combination**
```python
results = []
for profit in param_grid["profit_target"]:
    for stop in param_grid["stop_loss"]:
        for hold in param_grid["max_hold_days"]:
            # Update config
            EXIT_RULES["profit_target_pct"] = profit
            EXIT_RULES["stop_loss_pct"] = stop
            EXIT_RULES["max_hold_days"] = hold
            
            # Run backtest
            metrics = run_backtest(
                start_date="2025-01-01",
                end_date="2026-04-26",
                initial_capital=30000
            )
            
            results.append({
                "profit_target": profit,
                "stop_loss": stop,
                "max_hold_days": hold,
                "return_pct": metrics.total_return_pct,
                "win_rate": metrics.win_rate,
                "sharpe_ratio": metrics.sharpe_ratio,
                "max_drawdown": metrics.max_drawdown
            })

# Find best combination
best = max(results, key=lambda x: x["sharpe_ratio"])
print(f"Best params: {best}")
```

**Step 3: Apply Best Parameters**
Update `config/backtest_config.py` with winning values.

---

### Approach 2: Automated Optimization (Advanced, Faster)

**Create Parameter Optimization Endpoint**

I can create this for you - it will:

1. **Accept parameter ranges**:
   ```json
   {
     "optimize": ["exit_rules", "position_sizing"],
     "date_range": {"start": "2025-01-01", "end": "2026-04-26"},
     "objective": "sharpe_ratio",  // or "return", "win_rate", etc.
     "max_iterations": 50
   }
   ```

2. **Use smart search** (Bayesian optimization):
   - Tries promising parameter combinations first
   - Learns from each backtest result
   - Converges faster than brute-force grid search

3. **Return best parameters**:
   ```json
   {
     "best_params": {
       "profit_target_pct": 18.5,
       "stop_loss_pct": -7.2,
       "max_hold_days": 45,
       "position_size_pct": 0.12
     },
     "performance": {
       "sharpe_ratio": 2.4,
       "return_pct": 48.3,
       "win_rate": 62.5,
       "max_drawdown": -12.3
     },
     "iterations_tested": 50
   }
   ```

## What Metrics to Optimize For?

### 1. **Sharpe Ratio** (Recommended)
- **Best for**: Overall risk-adjusted returns
- **Formula**: (Return - Risk-Free Rate) / Standard Deviation
- **Interpretation**: Higher is better, >1 is good, >2 is excellent

### 2. **Total Return %**
- **Best for**: Maximum gains (ignoring risk)
- **Caution**: May suggest overly aggressive parameters

### 3. **Win Rate**
- **Best for**: Consistency
- **Caution**: High win rate with small wins isn't always better than low win rate with big wins

### 4. **Max Drawdown**
- **Best for**: Risk management
- **Goal**: Minimize largest peak-to-trough decline

### 5. **Profit Factor**
- **Best for**: Risk/reward balance
- **Formula**: Total Wins / Total Losses
- **Interpretation**: >1.5 is good, >2 is excellent

## Implementation Options

### Option A: Simple Script (Do it yourself)

I can create a Python script you run locally:

```bash
python optimize_parameters.py --period 1y --objective sharpe_ratio
```

This will:
- Test parameter combinations
- Save results to CSV
- Show best parameters
- Update config file (with your approval)

### Option B: Web Interface (More polished)

Add to frontend:
- "Optimize Parameters" button on Strategy/Config page
- Shows progress as backtests run
- Displays results in sortable table
- One-click to apply winning parameters

### Option C: Scheduled Optimization (Automated)

Run optimization weekly:
- Automatically tests parameters on recent data
- Emails you if it finds significantly better settings
- You approve before applying

## Recommended Next Steps

1. **Start Simple**: Manually run 5-10 backtests with different exit rules
2. **Compare Results**: Which combo gives best Sharpe ratio?
3. **Implement Winner**: Update config with best parameters
4. **Monitor**: Track live performance vs backtest expectations
5. **Iterate**: Re-optimize quarterly as market conditions change

## Quick Win: Optimize Exit Rules Now

Want me to create a quick script that:
1. Tests 20 combinations of exit rules
2. Runs each backtest on last year's data
3. Shows you which parameters performed best?

This would take ~5 minutes to implement and ~10 minutes to run.

## Example Results You Might See

```
Testing 20 parameter combinations...

┌────────┬──────────┬──────────┬────────┬─────────┬────────┐
│ Profit │ Stop     │ Max Hold │ Return │ Sharpe  │ Win %  │
├────────┼──────────┼──────────┼────────┼─────────┼────────┤
│ 15%    │ -8%      │ 60 days  │ 24.5%  │  1.8    │ 58%    │ ← Current
│ 20%    │ -10%     │ 45 days  │ 32.1%  │  2.3    │ 52%    │ ← Best!
│ 10%    │ -5%      │ 90 days  │ 18.2%  │  1.2    │ 64%    │
│ 25%    │ -12%     │ 30 days  │ 28.9%  │  1.9    │ 48%    │
└────────┴──────────┴──────────┴────────┴─────────┴────────┘

Recommendation: Use profit_target=20%, stop_loss=-10%, max_hold=45 days
Expected improvement: +31% return, +0.5 Sharpe ratio
```

## Want Me To Build It?

Let me know which option you prefer:

**A** = Simple script (fastest, run locally)  
**B** = Web interface (polished, integrated)  
**C** = Show me manual process first (learn, then automate)

I can implement any of these in ~30 minutes!
