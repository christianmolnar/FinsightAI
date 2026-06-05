# Quick Debug Checklist

## 🚀 Enable Debug Mode

```bash
cd backend
export BACKTEST_DEBUG=true
uvicorn app.main:app --reload
```

## 🧪 Run Test Backtest

1. Open https://www.f-insight.ai
2. Login to your account
3. Go to Backtesting tab
4. Enter these parameters:
   - Initial Capital: **$30,000**
   - Position Size: **$3,000**
   - Date Range: **1 year** (or same as screenshot)
   - Enable Compounding: **Yes**
5. Click **Run Backtest**
6. **Watch backend console** for debug output

## 🔍 What to Look For

### 1. Initial Parameters (at start)
```
🚀 BACKTEST RUN STARTED - DEBUG MODE ENABLED
Initial Capital: $30,000.00  ← VERIFY THIS!
```

### 2. Individual Trades (during run)
```
🔍 SIMULATING TRADE: AAPL
💰 FINAL P&L: +$492.80 (+16.4%)
```

### 3. Final Calculation (at end)
```
🔍 BACKTEST METRICS CALCULATION DEBUG
Initial Capital: $30,000.00  ← Check 1: Correct?
Net Profit (Total P&L): $8,163.27  ← Check 2: Matches sum?
Final Capital: $38,163.27  ← Check 3: $30k + $8.16k?
Return: +XX.XX%  ← Check 4: Should be 27.21%
Verify: ... = XX.XX%  ← Check 5: Should match Return
```

## ⚠️ Red Flags

❌ **Initial Capital shows $10,000** instead of $30,000
❌ **Return shows 81.63%** but Verify shows 27.21%
❌ **Net Profit** doesn't match sum of all trade P&Ls
❌ **Final Capital** ≠ Initial + Net Profit

## ✅ Success Criteria

✅ Initial Capital = $30,000.00
✅ Net Profit = $8,163.27 (or similar)
✅ Final Capital = $30,000 + Net Profit
✅ Return % matches Verify %
✅ Math: (Final - Initial) / Initial * 100 = Return %

## 📊 Expected Math

For your screenshot numbers:
- Initial: **$30,000.00**
- Net P&L: **$8,163.27**
- Final: **$38,163.27**
- Return: **(38,163.27 - 30,000) / 30,000 * 100 = 27.21%** ✅

NOT:
- Return: **$8,163 / $10,000 * 100 = 81.63%** ❌

## 📝 Save the Logs

```bash
# Start with logging to file
export BACKTEST_DEBUG=true
uvicorn app.main:app --reload 2>&1 | tee debug_output.log
```

Then you can search the file:
```bash
grep "Initial Capital" debug_output.log
grep "Return:" debug_output.log
grep "Verify:" debug_output.log
```

## 🐛 Found the Bug?

Once you see the discrepancy in the logs, note:
1. What value is WRONG (e.g., "Initial Capital shows $10,000")
2. What line number it appears on
3. Screenshot or copy the relevant log section

Then we can fix it!

## 📞 Share Results

Send me:
- [ ] Screenshot of debug output (Initial Capital section)
- [ ] Screenshot of debug output (Final Calculation section)
- [ ] Any values that don't match expected
- [ ] The exact parameters you entered

This will tell us exactly what's wrong.

---

**Time to debug**: ~5 minutes
**Expected outcome**: Clear evidence of where the math goes wrong
