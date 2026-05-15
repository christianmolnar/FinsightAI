# Morning Checklist - April 25, 2026

**Good morning!** Here's where we left off and what to do next.

---

## ✅ What Was Completed Last Night

### 1. API Key Rotation ✅
- All Alpaca keys rotated (Live + Paper)
- OpenAI and Anthropic keys rotated
- Keys stored in Railway environment variables

### 2. Vercel Production Deployment ✅
- Frontend deployed to https://www.f-insight.ai
- Removed "Forgot Password" link
- JWT authentication working
- All tests passed

### 3. Phase C Database Setup ✅
- Created `historical_prices` table (for stock data)
- Created `macro_events` table (for market events)
- Created `download_progress` table (for tracking)
- **Discovered**: 21,390 rows already exist! (13 symbols, 2016-2021)

### 4. Historical Data Loader ✅
- Complete Python script ready
- Handles batch processing, resume, rate limits
- Ready to download 110 symbols × 10 years

---

## ⏸️ Where We Stopped

**Issue**: API 401 error when downloading historical data

**Reason**: backend/.env has old Alpaca keys (before rotation)

**Solution needed**: Update backend/.env with new keys from Railway

---

## 🚀 Morning Tasks (30 minutes)

### Step 1: Get New API Keys from Railway (5 min)

```bash
# Option A: Railway Dashboard
# 1. Go to https://railway.app
# 2. Select f.insight.AI project
# 3. Click "Variables" tab
# 4. Copy these values:
#    - ALPACA_API_KEY
#    - ALPACA_SECRET_KEY  
#    - ALPACA_PAPER_API_KEY
#    - ALPACA_PAPER_SECRET_KEY

# Option B: Railway CLI
railway variables
```

### Step 2: Update backend/.env (2 min)

Edit `/Users/christian/Repos/f.insight.AI Advanced/backend/.env`:

```bash
# Replace these lines with new keys from Railway:
ALPACA_API_KEY=your_new_key_here
ALPACA_SECRET_KEY=your_new_secret_here
ALPACA_PAPER_API_KEY=your_new_paper_key
ALPACA_PAPER_SECRET_KEY=your_new_paper_secret
```

### Step 3: Test Download (2 min)

```bash
cd "/Users/christian/Repos/f.insight.AI Advanced/backend"
source venv/bin/activate
python3 app/services/historical_data_loader.py --symbols test
```

**Expected output:**
```
🚀 Historical Data Loader - Phase C
📅 Period: 2016-01-01 to 2026-04-25
📊 Symbols: 5
============================================================
[1/5] 📥 Downloading AAPL... ✅ 2520 bars
[2/5] 📥 Downloading MSFT... ✅ 2520 bars
...
```

### Step 4: Run Full Download (if test passes)

```bash
# This will take 4-6 hours, so run in background
nohup python3 app/services/historical_data_loader.py --symbols SP500 > /tmp/download.log 2>&1 &

# Monitor progress:
tail -f /tmp/download.log
```

**OR** wait and we'll run it together after testing!

---

## 📊 What You'll See

### During Download:
```
[10/110] 📥 Downloading BA... ✅ 2520 bars
[20/110] 📥 Downloading C... ✅ 2520 bars
⏱️  Progress: 20/110 symbols | 50,400 bars | ETA: 45.2 min
```

### When Complete:
```
🎉 Download Complete!
⏱️  Time: 52.3 minutes
📊 Total bars: 277,200
✅ Success: 110 symbols
```

---

## 🧪 Testing the Backtester (after download)

Once data is loaded, we'll update the backtester to use Railway DB:

```bash
# 1. Test current backtester (uses Alpaca API)
python3 -m app.services.backtester --start 2020-01-01 --end 2026-03-31

# 2. After we modify it to use DB, test again
# Should be 10x faster and produce same results!
```

---

## 🎯 Today's Goal

**End of day**: Backtester running on Railway database data, 10x faster than before

**Success criteria**:
- ✅ Historical data downloaded (2016-2026, 110+ symbols)
- ✅ Backtester queries Railway DB instead of Alpaca API
- ✅ Same backtest results (proves data integrity)
- ✅ 10x performance improvement

---

## 🚨 If Something Goes Wrong

### Test fails with 401 error:
- Check if keys are for Paper or Live account
- Historical data requires **Live keys** (paper might not have access)
- Try with ALPACA_API_KEY (live) instead of ALPACA_PAPER_API_KEY

### Test fails with rate limit (429):
- Normal! Script will automatically retry after 60s
- Alpaca free tier: 200 requests/min
- Our script: 300ms delay = ~200/min (right at limit)

### Download stops mid-way:
- Progress is saved in `download_progress` table
- Just run the command again - it will resume automatically
- Script skips already-downloaded symbols

---

## 📝 Questions to Ask Me

1. "Show me the new API keys from Railway" 
2. "Test the historical data loader with 5 symbols"
3. "Run the full download in the background"
4. "Update the backtester to use the database"
5. "Run a test backtest and compare performance"

---

## 🎉 What's Next After Phase C

Once Phase C is complete:

### Phase D: Autonomous Trading Engine
- Position Monitor (checks open positions every 5 min)
- Auto-Executor (executes approved trades automatically)
- Wire everything together for full autonomy

### Phase E: Polish & Launch
- Frontend improvements
- Performance optimization
- Final testing
- Switch from paper to live trading

---

**Status**: Ready to resume as soon as API keys are updated  
**Estimated time to Phase C complete**: 4-6 hours (mostly download time)  
**Next milestone**: Phase D - Autonomous Engine

**Have a great morning! Let me know when you're ready to continue.** ☕️

