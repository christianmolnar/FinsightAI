# Alpaca Live Trading Setup Guide

**Date:** January 10, 2026  
**Status:** Ready to configure live API keys

---

## 🔐 Getting Your Live API Keys

### Step 1: Access Alpaca Dashboard
1. Go to: https://app.alpaca.markets/
2. Log in with your approved account credentials

### Step 2: Navigate to API Keys
- **Option A:** Click "Paper Trading" dropdown → Select "Live Trading"
- **Option B:** Go to Account Settings → API Keys → Live Trading tab

### Step 3: Generate Live Keys
1. Click **"Generate New API Keys"** or **"Create New Key"**
2. **Important:** Choose **"Live Trading"** (not Paper Trading)
3. You'll receive:
   - **API Key ID** (Example: `PKXXXXXXXXXXXXXXXXXX`)
   - **Secret Key** (Example: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

⚠️ **CRITICAL:** Copy the Secret Key immediately - it only displays once!

---

## 📝 Adding Keys to Your Project

### Edit `.env` File
1. Open: `/Users/christian/Repos/f.insight.AI Advanced/.env`
2. Find the Alpaca section:
   ```bash
   # Alpaca Trading API
   ALPACA_API_KEY_ID=your_alpaca_api_key_id_here
   ALPACA_API_SECRET_KEY=your_alpaca_secret_key_here
   ```
3. Replace the placeholder values with your actual keys:
   ```bash
   ALPACA_API_KEY_ID=PKXXXXXXXXXXXXXXXXXX
   ALPACA_API_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
4. Save the file

---

## ✅ Verifying Your Setup

### 1. Start Backend Server
```bash
cd "/Users/christian/Repos/f.insight.AI Advanced/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Live Account Connection (Read-Only)
```bash
curl http://localhost:8000/api/v1/alpaca/live/account
```

**Expected Response:**
```json
{
  "id": "your-account-id",
  "cash": 1000.00,
  "portfolio_value": 1000.00,
  "buying_power": 2000.00,
  "status": "ACTIVE",
  ...
}
```

### 3. Check Live Positions
```bash
curl http://localhost:8000/api/v1/alpaca/live/positions
```

---

## 🧪 Safe Test Trade Procedure

### Recommended First Trade:
- **Stock:** A stable, liquid stock (AAPL, MSFT, SPY, etc.)
- **Quantity:** 1 share only
- **Order Type:** Limit order (not market) for price control
- **Amount:** $10-50 maximum

### Test Process:
1. **View in UI:** Open http://localhost:3000 → "Live Portfolio" tab
2. **Verify Account:** Confirm cash balance and account status
3. **Place Small Order:** Use Trade button → Set quantity to 1
4. **Monitor:** Watch order status in UI
5. **Close Position:** Sell the share after confirming trade worked

---

## 🔒 Security Best Practices

### ✅ DO:
- Store keys only in `.env` file (never commit to git)
- Use different keys for paper vs live trading
- Enable 2FA on your Alpaca account
- Start with very small trades ($10-20)
- Test on paper trading first if nervous

### ❌ DON'T:
- Share your secret keys with anyone
- Commit `.env` file to git (already in `.gitignore`)
- Start with large position sizes
- Trade without testing the connection first

---

## 📊 Current Project Status

### ✅ Completed:
- Alpaca integration code (paper + live endpoints)
- Frontend UI (Paper Portfolio + Live Portfolio tabs)
- Transaction queue system
- AI research engine

### ⚙️ Ready for Live Trading:
- Backend API endpoints: `/api/v1/alpaca/live/*`
- Frontend Live Portfolio component
- Order placement and position tracking

### 🔄 Needs Configuration:
- Add your live Alpaca API keys to `.env`
- Start backend server
- Test connection
- Execute first trade

---

## 🚨 Troubleshooting

### "Error: Alpaca API credentials not found"
- Check `.env` file has correct key names
- Restart backend after adding keys
- Verify no extra spaces in key values

### "Error: 401 Unauthorized"
- Keys might be paper keys instead of live keys
- Generate new live trading keys from dashboard
- Ensure keys are for live trading account

### "Error: Account not approved"
- Your live trading account may still be pending
- Check email for approval notification
- Contact Alpaca support if delayed

---

## 📞 Support Resources

- **Alpaca Documentation:** https://docs.alpaca.markets/
- **Alpaca API Reference:** https://docs.alpaca.markets/reference/
- **Support:** https://alpaca.markets/support

---

**Next Steps:**
1. Get your live API keys from Alpaca dashboard
2. Add them to `.env` file
3. Restart backend server
4. Test connection with read-only API call
5. Execute small test trade when ready
