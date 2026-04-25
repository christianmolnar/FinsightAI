# Phase C Decision Tree - Do We Need Alpaca Upgrade?

**Date**: April 25, 2026  
**Question**: Should we upgrade to Alpaca Algo Trader Plus ($99/month)?

---

## 📊 Current Situation

### What We Have:
- ✅ 21,390 historical bars in database (13 symbols, 2016-2026)
- ✅ Backtester that was working in March 2026
- ✅ Scanner that produced 6,437 trades in 6-year backtest
- ✅ Free Alpaca tier (IEX + 15-min delayed SIP data)

### What We Need:
- 🎯 500+ symbols for comprehensive backtesting
- 🎯 Historical data from 2016-2026 (10 years)
- 🎯 Fast backtesting (not hitting API for every request)

---

## 🤔 The Core Question

**How was the backtester working in March with only 13 symbols in the database?**

**Answer**: It was hitting Alpaca API **live** for every data request!
- Database had 13 symbols (barely used)
- Backtester called `alpaca.get_historical_bars()` for each symbol/date needed
- Slow but functional with free tier's 15-minute delayed data

---

## 🎯 Three Options

### Option 1: Keep Using Free Tier + Live API Calls ✅ CURRENT STATE
**What it means:**
- Backtester continues hitting Alpaca API for data (slow)
- No database usage (13 symbols ignored)
- Works with free tier (15-min delayed data is fine for backtesting)

**Pros:**
- ✅ No upgrade cost ($0/month)
- ✅ Already working
- ✅ Access to 500+ symbols

**Cons:**
- ❌ SLOW (6-year backtest = 10-15 minutes)
- ❌ Rate limited (200 requests/minute)
- ❌ Network dependent

**Recommendation**: ⭐ **TEST THIS FIRST** - If it still works, no upgrade needed!

---

### Option 2: Upgrade to Algo Trader Plus + Download All Data 💰
**What it means:**
- Pay $99/month for Alpaca Algo Trader Plus
- Download 500+ symbols × 10 years = ~1.25M bars into database
- Backtester queries local database (10x faster)

**Pros:**
- ✅ FAST backtesting (6-year backtest = 1 minute)
- ✅ Real-time SIP data access
- ✅ No rate limits
- ✅ Offline capable

**Cons:**
- ❌ $99/month ongoing cost
- ❌ 4-6 hours to download initial data
- ❌ Database storage (~500MB)

**Recommendation**: Only if Option 1 fails OR you want faster backtesting

---

### Option 3: Hybrid - Use Free Tier + Cache Results 🎯
**What it means:**
- Keep free tier ($0/month)
- Modify backtester to cache API results in database as it runs
- First run slow, subsequent runs fast

**Pros:**
- ✅ No upgrade cost
- ✅ Gets faster over time
- ✅ Eventually as fast as Option 2

**Cons:**
- ❌ First backtest still slow
- ❌ Gradual database buildup
- ❌ Some coding required

**Recommendation**: ⭐ **BEST LONG-TERM** - Smart middle ground

---

## 🚀 Recommended Action Plan

### Step 1: Test Current Setup (5 minutes)
Run a simple backtest to see if free tier still works:
```bash
# Test with just 2020-2021 (1 year)
python3 -m services.backtester --start 2020-01-01 --end 2021-01-01 --strategy technical_breakout
```

**If it works:** ✅ No upgrade needed! Move to Step 2  
**If it fails with 402 error:** ❌ Need upgrade OR use Option 3

---

### Step 2: Decide Based on Results

#### ✅ If Test Passes (Free tier works):

**Immediate action:** Use as-is for now  
**Future optimization:** Implement Option 3 (cache-as-you-go)

**Timeline:**
- Today: Test backtester (5 min)
- This week: Run full 6-year backtest to verify (15 min)
- Next week: Implement caching (2 hours)
- Long term: Consider upgrade when scaling to live trading

#### ❌ If Test Fails (Need paid data):

**Immediate action:** Upgrade to Algo Trader Plus ($99/month)

**Timeline:**
- Today: Upgrade Alpaca account (5 min)
- Today: Run historical data download (4-6 hours overnight)
- Tomorrow: Update backtester to use database
- Tomorrow: Test and verify 10x speedup

---

## 💰 Cost-Benefit Analysis

### Option 1 (Free Tier):
- **Cost**: $0/month
- **Speed**: 10-15 min per full backtest
- **Good for**: Testing, development, learning

### Option 2 (Paid Tier):
- **Cost**: $99/month = $1,188/year
- **Speed**: 1-2 min per full backtest
- **Good for**: Production, frequent testing, optimization

### Break-even:
If you run backtests more than **1x per day**, paid tier saves time worth the cost.

---

## 🎯 My Recommendation

**For TODAY:**

1. ✅ **Test current setup first** (5 min)
2. ✅ **If it works, use it!** No upgrade needed
3. ✅ **Implement caching later** when time permits

**DON'T upgrade until:**
- ❌ Free tier stops working (402 error), OR
- ❌ You're running backtests 5+ times per day, OR
- ❌ You need real-time data for live trading (not needed yet)

---

## 📋 Next Step

**Want me to test if the backtester currently works with free tier?**

I'll run a quick 1-year backtest (2020-2021) to see if:
- ✅ Free tier provides historical data
- ✅ Backtester runs successfully
- ✅ We get reasonable results

**Should take ~2 minutes. Ready to test?**

