# Alpaca Migration: Next Steps

**Status:** 🚧 Phase 1 Complete - AlpacaService created  
**Branch:** `feature/alpaca-migration`  
**Time Elapsed:** 15 minutes  

---

## ✅ What We've Done

1. **Created feature branch** - `feature/alpaca-migration`
2. **Archived Schwab docs** - Moved to `/docs/brokers/schwab/`
3. **Installed Alpaca SDK** - `alpaca-py==0.43.2`
4. **Created AlpacaService** - Complete service layer with:
   - Account management
   - Position tracking  
   - Order placement (market + limit)
   - Market data (quotes)
5. **Added test script** - `test_alpaca_connection.py`

---

## 🎯 Next Steps (YOUR ACTION REQUIRED)

### Step 1: Get Alpaca API Keys (5 minutes)

**Paper Trading Account (Recommended First):**
1. Go to https://alpaca.markets/
2. Sign up for free account
3. Go to Dashboard → Paper Trading
4. Generate API keys
5. Copy:
   - **API Key ID** (looks like: `PKXXXXXXXXXXXXXXXX`)
   - **Secret Key** (looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

**Live Trading Account (Optional):**
- Same process but use "Live Trading" section
- Requires funding account

---

### Step 2: Add API Keys to .env (2 minutes)

Edit `/backend/.env`:

```bash
# Alpaca API Configuration
ALPACA_API_KEY_ID=PKXXXXXXXXXXXXXXXX
ALPACA_API_SECRET_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ALPACA_PAPER=true  # Set to false for live trading

# ⚠️ DEPRECATED (keep for now, will remove after migration)
# SCHWAB_APP_KEY=...
# SCHWAB_SECRET=...
```

**Important:**
- ✅ Set `ALPACA_PAPER=true` for testing
- ✅ Keep Schwab keys (don't delete yet - backup)
- ✅ `.env` is git-ignored (safe)

---

### Step 3: Test Connection (1 minute)

```bash
cd backend
python3 test_alpaca_connection.py
```

**Expected Output:**
```
🚀 Testing Alpaca API Connection...
✅ AlpacaService initialized (paper=True)

📊 Test 1: Get Account Info
Account ID: ...
Cash: $100,000.00
Portfolio Value: $100,000.00
✅ Account info retrieved successfully

📈 Test 2: Get Positions
No positions found (account is empty)
✅ Positions retrieved successfully

📋 Test 3: Get Orders
No open orders
✅ Orders retrieved successfully

💰 Test 4: Get Market Quote
AAPL Quote:
  Bid: $XXX.XX x XXX
  Ask: $XXX.XX x XXX
✅ Market data retrieved successfully

🎉 ALL TESTS PASSED!
```

**If tests fail:**
- Check API keys are correct
- Verify `.env` file location
- Check internet connection
- Verify keys are for paper trading

---

## 📝 What Comes Next (After Tests Pass)

### Hour 2-3: Update Backend API Endpoints
- Replace `SchwabService` with `AlpacaService` in:
  - `/backend/app/api/portfolio.py`
  - `/backend/app/api/trading.py`
  - `/backend/app/api/market_data.py`
- Update route handlers
- Test each endpoint

### Hour 4: Frontend Updates
- Minimal changes (API interface stays mostly same)
- Remove OAuth re-auth UI
- Update any Schwab-specific references

### Hour 5-6: Integration Testing
- Test full portfolio flow
- Place test order ($1)
- Verify all features work
- Document any issues

---

## 🚨 Troubleshooting

### "ValueError: Alpaca API credentials not found"
**Fix:** Add `ALPACA_API_KEY_ID` and `ALPACA_API_SECRET_KEY` to `/backend/.env`

### "Connection refused" or timeout
**Fix:** Check internet connection, verify API keys are valid

### "Invalid API key"
**Fix:** 
- Verify you copied the full key (no spaces)
- Make sure using Paper Trading keys if `ALPACA_PAPER=true`
- Regenerate keys if needed

### Tests pass but see "Market data test skipped"
**Normal:** Market closed or data feed issue, not critical

---

## 📊 Migration Progress

```
Phase 0: Setup ✅ (15 min)
├─ Feature branch created
├─ Schwab docs archived
├─ Alpaca SDK installed
└─ AlpacaService created

Phase 1: Test Connection ⏸️ (5 min) ← YOU ARE HERE
├─ Get Alpaca API keys
├─ Add to .env
└─ Run test_alpaca_connection.py

Phase 2: Backend Migration (2-3 hours)
├─ Update API endpoints
├─ Replace Schwab calls
└─ Integration testing

Phase 3: Frontend Updates (1 hour)
├─ Update API calls
├─ Remove OAuth UI
└─ Test UI flows

Phase 4: Testing & Validation (1 hour)
├─ End-to-end testing
├─ Place real test order
└─ Verify all features

Phase 5: Merge & Deploy (30 min)
├─ Final commit
├─ Merge to main
└─ Deploy
```

**Total Estimated Time:** 4-6 hours  
**Completed:** 15 minutes (Phase 0)  
**Remaining:** 4-5 hours

---

## 🎯 Your Immediate Task

**Right now, you need to:**

1. ✅ Go to https://alpaca.markets/ and create account
2. ✅ Get Paper Trading API keys
3. ✅ Add to `/backend/.env`
4. ✅ Run `python3 backend/test_alpaca_connection.py`
5. ✅ Report back with test results

**I'll wait for your test results before continuing!** 🚀

---

**Questions?**
- Stuck getting API keys? Ask me
- Tests failing? Share the error
- Ready to continue? Let me know!
