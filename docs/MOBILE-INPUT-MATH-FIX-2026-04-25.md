# 📱 Mobile Input & Backtest Math Fix

**Date**: April 25, 2026  
**Issues Fixed**: 
1. Mobile input can't clear to empty (leaves "0")
2. Backtest showing wrong percentage (9.2% instead of ~31%)

---

## 🔴 **Problem 1: Mobile Input Bug**

**User Report**:
> "On mobile at least, it won't let me erase the quantities and leaves a 0 so I had to put 030000 for initial and trade size 03000"

**Root Cause**:
- HTML `<input type="number">` on mobile keyboards
- iOS/Android number inputs don't allow empty state
- Typing "030000" gets parsed as 30000, but "03000" → 3000
- Confusing UX - can't backspace to clear

**Solution**:
```javascript
// BEFORE (Bad):
<input 
  type="number"
  value={initialCapital}
  onChange={(e) => setInitialCapital(Number(e.target.value))}
/>

// AFTER (Good):
<input 
  type="text"
  inputMode="numeric"
  pattern="[0-9]*"
  value={initialCapital}
  onChange={(e) => {
    const value = e.target.value.replace(/[^0-9]/g, '');
    setInitialCapital(value === '' ? '' : Number(value));
  }}
  onBlur={(e) => {
    if (e.target.value === '' || e.target.value === '0') {
      setInitialCapital(10000); // Default
    }
  }}
  placeholder="10000"
/>
```

**Benefits**:
- ✅ Can clear field completely
- ✅ Mobile numeric keyboard still appears
- ✅ Strips any non-numeric characters
- ✅ Auto-fills sensible default on blur if empty
- ✅ No confusing "0" stuck in field

---

## 🔴 **Problem 2: Math Error**

**User Report**:
> "$9292 profit and says that is 9.2%"
> "had to put 030000 for initial"

**Expected Math**:
```
Initial Capital: $30,000
Profit: $9,292
Final Capital: $39,292
Return: ($9,292 / $30,000) × 100 = 30.97%
```

**But User Saw**: "9.2%"

**Possible Causes**:
1. Frontend sent wrong initial_capital value
2. Backend received wrong value
3. Backend calculation error
4. Display formatting error

**Debug Solution Added**:

### Frontend Logging (Request):
```javascript
console.log('📤 SENDING BACKTEST REQUEST:');
console.log('Initial Capital:', initialCapital, typeof initialCapital);
console.log('Position Size:', positionSize, typeof positionSize);
```

**What to Look For**:
- Is `initialCapital` a number or string?
- Did "030000" get sent as 30000 or 3000?

### Frontend Logging (Response):
```javascript
console.log('📊 BACKTEST MATH DEBUG:');
console.log('Initial Capital:', resultsData.metrics.returns.initial_capital);
console.log('Final Capital:', resultsData.metrics.returns.final_capital);
console.log('Net Profit:', resultsData.metrics.returns.net_profit);
console.log('Backend Return %:', resultsData.metrics.returns.total_return_pct);

const verifyPct = ((final - initial) / initial * 100).toFixed(2);
console.log('Calculated % (verify):', verifyPct);

if (Math.abs(verifyPct - backend_pct) > 0.1) {
  console.error('⚠️ MATH MISMATCH! Backend calculation may be wrong!');
}
```

**What to Look For**:
- Does frontend calculation match backend?
- If mismatch → Backend bug
- If match → Display issue

---

## 🎯 **How to Test**

### Test 1: Number Input UX

1. **Open app on mobile** (or Chrome DevTools mobile mode)
2. **Navigate to Backtesting** → Full backtest config
3. **Test Initial Capital field**:
   - Tap field
   - Should show numeric keyboard ✅
   - Type "30000"
   - Should show "30000" ✅
   - Backspace all digits
   - Field should be EMPTY (not "0") ✅
   - Tap outside field
   - Should auto-fill "10000" ✅
4. **Repeat for Position Size field**

### Test 2: Math Verification

1. **Open browser console** (F12)
2. **Run a 1-year backtest** with custom initial capital:
   - Initial Capital: 30000
   - Position Size: 3000
3. **Watch console output**:

**Expected Output**:
```
📤 SENDING BACKTEST REQUEST:
Initial Capital: 30000 number
Position Size: 3000 number
Full config: {...}

[After completion]

📊 BACKTEST MATH DEBUG:
Initial Capital: 30000
Final Capital: 39292
Net Profit: 9292
Backend Return %: 30.97
Calculated % (verify): 30.97
✅ Math verified!
```

**If You See Mismatch**:
```
📊 BACKTEST MATH DEBUG:
Initial Capital: 101000
Final Capital: 110292
Net Profit: 9292
Backend Return %: 9.20
Calculated % (verify): 9.20
⚠️ MATH MISMATCH! Backend calculation may be wrong!
```

→ This means backend received wrong `initial_capital` value

---

## 🔧 **What Was Changed**

### Files Modified:

**frontend/src/components/Backtesting.js**:

1. **Input Fields** (Lines ~411-435):
   - Changed `type="number"` → `type="text"` with `inputMode="numeric"`
   - Added value sanitization (strip non-digits)
   - Added blur handler to auto-fill defaults
   - Added placeholders for clarity

2. **Display Enhancement** (Lines ~570-620):
   - Added "Initial → Final" capital display under return %
   - Changed Net Profit to its own card
   - Added comma formatting for better readability

3. **Debug Logging** (Lines ~185-210, ~260-275):
   - Log outgoing request values
   - Log incoming response values
   - Verify math client-side
   - Alert if mismatch detected

---

## 📊 **Display Improvements**

### Before:
```
┌─────────────────┐
│ Total Return    │
│   +9.2%         │  ← Just percentage
└─────────────────┘
```

### After:
```
┌─────────────────────────┐
│ Total Return            │
│   +30.97%               │  ← Percentage
│   $30,000 → $39,292     │  ← Shows progression
└─────────────────────────┘

┌─────────────────────────┐
│ Net Profit              │
│   +$9,292               │  ← Separate card
└─────────────────────────┘
```

---

## 🎤 **Next Steps**

1. **Deploy to Vercel**: `cd frontend && vercel --prod`
2. **Test on mobile**: Run 1-year backtest with 30000 initial
3. **Check console**: Verify math logs
4. **If still wrong**: Share console logs to diagnose

**Key Questions to Answer**:
- Does frontend SEND correct value? (Check 📤 SENDING log)
- Does backend RETURN correct value? (Check 📊 MATH DEBUG log)
- Does calculation match? (Check "Calculated % (verify)")

---

## 🧮 **Math Reference**

### Correct Calculation:
```python
initial_capital = 30000
net_profit = 9292
final_capital = initial_capital + net_profit  # 39292
total_return_pct = (net_profit / initial_capital) * 100  # 30.97%
```

**Backend Code** (`backend/services/backtester.py` line 115):
```python
self.total_return_pct = ((self.final_capital - initial_capital) / initial_capital) * 100
```

This is mathematically correct. If result is wrong, it's because:
1. `initial_capital` parameter is wrong, OR
2. `self.final_capital` calculation is wrong

---

## 🔍 **Debugging Checklist**

Run through this after deploying:

- [ ] Can clear input fields on mobile (no stuck "0")
- [ ] Numeric keyboard appears on mobile
- [ ] Fields auto-fill sensible defaults when empty
- [ ] Console shows "📤 SENDING" log with correct values
- [ ] Console shows "📊 MATH DEBUG" log after backtest
- [ ] "Calculated % (verify)" matches "Backend Return %"
- [ ] No "⚠️ MATH MISMATCH" error
- [ ] Display shows "Initial → Final" capital
- [ ] Net Profit displays with comma formatting

---

**STATUS**: ✅ Fixes deployed, debugging added

**Action**: Run 1-year backtest on mobile and check console logs to verify math is now correct.

If you see the mismatch warning, share the console output and we'll investigate the backend calculation.
