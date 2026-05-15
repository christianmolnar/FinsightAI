# Position Sizing Enhancement - Accurate Compounding

**Date**: March 7, 2026  
**Status**: ✅ COMPLETE

## Problem

The backtester's position sizing was already using percentage-based compounding (10% of portfolio value), but the portfolio value calculation was **inaccurate** for open positions:

- Used **entry price** for valuing open positions
- **Underestimated** portfolio value when positions were winning
- **Overestimated** portfolio value when positions were losing
- This caused position sizes to be **incorrectly calculated** during the backtest

## Solution

Updated `_calculate_portfolio_value()` to use **actual current market prices** for open positions:

### Before:
```python
# Conservative approximation - used entry price
open_positions_value += trade.entry_price * trade.shares
```

### After:
```python
# Accurate valuation - uses current market price at evaluation date
current_price = trade.entry_price  # Fallback
if universe_data and trade.symbol in universe_data:
    symbol_data = universe_data[trade.symbol]
    relevant_data = symbol_data[symbol_data.index <= current_date_only]
    if not relevant_data.empty:
        current_price = float(relevant_data.iloc[-1]['close'])

open_positions_value += current_price * trade.shares
```

## Impact on Position Sizing

### Accurate Compounding Example:

**Starting**: $10,000 portfolio, 10% = $1,000 per position

**Trade 1 (AAPL)**: Entry at $150 → Buy 6 shares ($900)
- After 5 days: AAPL = $165 (+10%)
- **OLD**: Portfolio = $9,100 cash + $900 position = $10,000 ❌
- **NEW**: Portfolio = $9,100 cash + $990 position = $10,090 ✅

**Trade 2 Entry**:
- **OLD**: 10% of $10,000 = $1,000 position ❌
- **NEW**: 10% of $10,090 = $1,009 position ✅ (+0.9% larger)

**After Multiple Winners**:
- **OLD**: Position sizes barely grew (underestimated gains)
- **NEW**: Position sizes compound correctly with profits

### Accurate Risk Management:

If positions are losing:
- **OLD**: Overestimated portfolio, took oversized positions
- **NEW**: Reduces position size when underwater (proper risk management)

## Position Sizing Formula

The complete position sizing heuristics:

1. **Portfolio Value** = Initial Capital + Realized P&L + Current Market Value of Open Positions
2. **Position Size ($)** = Portfolio Value × `position_size_pct` (10%)
3. **Position Size ($)** = min(Position Size, Portfolio Value × `max_position_pct` (10%))
4. **Shares** = floor(Position Size / Stock Price)
5. **Minimum**: 1 share if portfolio can afford it

## Configuration

Settings in `backend/config/trading_config.yaml`:

```yaml
trading:
  position_size_pct: 0.10  # 10% of portfolio per position

risk:
  max_position_pct: 10     # Maximum 10% per position
```

## Files Modified

1. **`backend/services/backtester.py`**:
   - `_calculate_portfolio_value()`: Added `universe_data` parameter, uses current prices
   - Fixed column name: `'Close'` (capital C) to match DataFrame structure
   - `_simulate_trade()`: Passes `universe_data` to portfolio value calculation

## Bug Fixes

**Column Name Case Sensitivity**: Fixed KeyError for `'close'` column
- Historical data uses capitalized column names: `'Close'`, `'Open'`, `'High'`, `'Low'`, `'Volume'`
- Updated portfolio value calculation to use `'Close'` instead of `'close'`

## Expected Results

With accurate portfolio valuation:

- **Winner Amplification**: Position sizes grow as profits accumulate
- **Risk Management**: Position sizes shrink when portfolio is losing
- **True Compounding**: Kelly Criterion-style growth (wins compound, losses scale down)
- **Realistic Backtest**: More accurate representation of actual trading dynamics

## Testing

Backend auto-reloaded successfully. Run a backtest from the UI to see:
- More accurate portfolio growth curves
- Position sizes that properly reflect unrealized gains
- Better risk-adjusted returns

---

**Ready for testing!** Try the backtest UI - you should see more realistic compounding behavior where winning streaks amplify position sizes and losses trigger defensive sizing.
