# How to Get Live Trading API Keys from Alpaca

**Date**: January 10, 2026  
**Source**: https://docs.alpaca.markets/  
**Status**: Verified from Official Documentation

---

## Understanding Alpaca's Two Account Types

Alpaca provides **two completely separate account types** with **different API keys**:

### 1. **Paper Trading Account** (What You Currently Have)
- ✅ **Free** - Available to anyone globally with email signup
- ✅ **$100,000 virtual cash** to practice trading
- ✅ **Full API access** with simulated trading
- ✅ **Real-time market data** (IEX feed included free)
- ✅ **No real money** involved
- 📍 **API Endpoint**: `https://paper-api.alpaca.markets`
- 🔑 **API Keys**: Paper-only keys (what you have now: `PKSCIYX2VR...`)

### 2. **Live Trading Account** (What You Need for Real Money)
- 💰 **Real money trading** with actual brokerage account
- 🇺🇸 **US residents only** (requires SSN, address verification)
- 💵 **Minimum deposit** varies (usually $0-100 to open)
- 📋 **KYC required** (Know Your Customer verification)
- 📍 **API Endpoint**: `https://api.alpaca.markets`
- 🔑 **API Keys**: Separate live trading keys (different from paper)

---

## Key Insight: Your Current API Keys

Your current keys (`ALPACA_API_KEY_ID=PKSCIYX2VRDJPUQ7FGBQCY3RHP`) are **paper trading only**. They will **NEVER** work for live trading, even if you upgrade your account. You must generate **new, separate keys** for live trading.

---

## Steps to Get Live Trading API Keys

### Step 1: Open a Live Brokerage Account

1. **Go to Alpaca Dashboard**
   - Navigate to: https://app.alpaca.markets/
   - Log in with your existing account

2. **Open Live Trading Account**
   - Click account dropdown (top-left corner)
   - Select **"Open New Live Account"** or **"Upgrade to Live Trading"**
   
3. **Complete Application**
   - **Personal Information**:
     - Full legal name
     - Date of birth
     - Social Security Number (SSN)
     - US residential address
     - Phone number
     - Email address
   
   - **Employment Information**:
     - Employment status
     - Employer name (if employed)
     - Occupation
   
   - **Financial Information**:
     - Annual income range
     - Net worth estimate
     - Liquid net worth
     - Investment experience
   
   - **Investment Profile**:
     - Investment objectives (growth, income, speculation, etc.)
     - Risk tolerance
     - Time horizon
     - Trading experience level

4. **Identity Verification**
   - Alpaca uses automated identity verification
   - May require uploading government-issued ID
   - May require proof of address (utility bill, bank statement)

5. **Sign Agreements**
   - Customer Agreement
   - Margin Agreement (if requesting margin)
   - Options Agreement (if trading options)
   - Electronic Delivery Consent
   - Privacy Policy

6. **Wait for Approval**
   - ⏱️ **Typical time**: 1-3 business days
   - ⏱️ **Fast track**: Sometimes instant for straightforward applications
   - 📧 You'll receive email when approved

### Step 2: Fund Your Live Account

1. **Link Bank Account**
   - Navigate to: Account → Funding
   - Use ACH (Automated Clearing House) transfer
   - Plaid integration for instant bank linking

2. **Make Initial Deposit**
   - **Minimum**: Usually $0 (but need money to trade)
   - **Recommended**: Start with $100-500 for testing
   - **Transfer time**: 3-5 business days for ACH

3. **Verify Funds Arrived**
   - Check account cash balance
   - Wait for funds to settle before trading

### Step 3: Generate Live Trading API Keys

1. **Navigate to API Keys**
   - Click your account name (top-left)
   - Select **"API Keys"** or go to: Settings → API Keys

2. **Select Live Trading Section**
   - You'll see **two separate sections**:
     - 📄 **Paper Trading Keys** (what you have)
     - 💰 **Live Trading Keys** (what you need)

3. **Generate Live Keys**
   - In the **Live Trading** section, click **"Generate New Key Pair"**
   - ⚠️ **IMPORTANT**: Save both keys immediately! Secret key shown only once!
   - Download keys or copy to secure location

4. **Key Format**
   ```
   Live Trading API Key ID:     PK... (starts with PK)
   Live Trading Secret Key:     ... (long string, shown once)
   ```

5. **Enable Appropriate Permissions**
   - ✅ **Trading** (required for placing orders)
   - ✅ **Account Data** (view portfolio)
   - ❌ **Withdrawals** (optional - usually keep off for security)

### Step 4: Update Your Application

1. **Add to .env File**
   ```bash
   # Paper Trading Keys (keep these)
   ALPACA_PAPER_API_KEY_ID=PKSCIYX2VRDJPUQ7FGBQCY3RHP
   ALPACA_PAPER_API_SECRET_KEY=C4i6YjfF1Y5PedB9eQNik6WYGSLAf3KiZ3UGCDk2jr4s
   
   # Live Trading Keys (add these new ones)
   ALPACA_LIVE_API_KEY_ID=YOUR_LIVE_KEY_HERE
   ALPACA_LIVE_API_SECRET_KEY=YOUR_LIVE_SECRET_HERE
   ```

2. **Update Backend Code** (Optional - for separate keys)
   
   Modify `alpaca_service.py`:
   ```python
   def __init__(self, paper: bool = True):
       if paper:
           self.api_key = os.getenv("ALPACA_PAPER_API_KEY_ID")
           self.secret_key = os.getenv("ALPACA_PAPER_API_SECRET_KEY")
       else:
           self.api_key = os.getenv("ALPACA_LIVE_API_KEY_ID")
           self.secret_key = os.getenv("ALPACA_LIVE_API_SECRET_KEY")
   ```

3. **Restart Backend**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

4. **Test Live Connection**
   - Navigate to Live Portfolio tab
   - Should now show your real account with $500 (or your deposit amount)
   - Try small test trade: 1 share of SPY (~$500)

---

## Important Security Notes

### 🔐 API Key Security

1. **Secret Keys Are Shown Once**
   - When you generate keys, the secret is displayed only once
   - If you lose it, you must regenerate (invalidates old key)
   - Store securely: password manager, encrypted file, etc.

2. **Never Commit Keys to Git**
   - Add `.env` to `.gitignore` (already done)
   - Never share keys publicly
   - Never commit to GitHub/GitLab

3. **Regenerate if Compromised**
   - If keys exposed, regenerate immediately
   - Old keys instantly invalidated
   - Update your application with new keys

4. **Use IP Whitelisting** (Optional but Recommended)
   - In API key settings, whitelist your IP addresses
   - Prevents unauthorized access even if keys stolen
   - Limits keys to specific IPs only

---

## Troubleshooting

### "Application Under Review"
- **Cause**: Your live account application is pending
- **Solution**: Wait 1-3 business days, check email for updates
- **Contact**: support@alpaca.markets if delayed >3 days

### "Cannot Generate Live Keys"
- **Cause**: Live account not approved yet
- **Solution**: Complete application, verify identity, wait for approval

### "Keys Not Working"
- **Cause 1**: Using paper keys for live endpoint (or vice versa)
- **Solution**: Verify correct keys in .env file
  
- **Cause 2**: Insufficient permissions
- **Solution**: Regenerate keys with "Trading" permission enabled
  
- **Cause 3**: Account not funded
- **Solution**: Make initial deposit, wait for funds to settle

### "Pattern Day Trader Restriction"
- **Cause**: Account < $25k, attempted 4th day trade in 5 days
- **Solution**: 
  - Deposit to reach $25k (PDT exempt)
  - OR limit to 3 day trades per 5 business days
  - OR switch to cash account (no margin)

---

## API Endpoints Summary

### Paper Trading
```
Base URL: https://paper-api.alpaca.markets
Keys: ALPACA_PAPER_API_KEY_ID / ALPACA_PAPER_API_SECRET_KEY
Account: $100k virtual money
```

### Live Trading
```
Base URL: https://api.alpaca.markets
Keys: ALPACA_LIVE_API_KEY_ID / ALPACA_LIVE_API_SECRET_KEY
Account: Real money (your deposit)
```

### Market Data (Same for Both)
```
Base URL: https://data.alpaca.markets
Keys: Same keys as trading (paper or live)
```

---

## Cost Breakdown

### Paper Trading Account
- **Account**: FREE
- **Trading**: FREE (unlimited virtual trades)
- **Market Data**: FREE (IEX real-time included)
- **API Access**: FREE (unlimited calls)

### Live Trading Account
- **Account Opening**: FREE (no minimum to open)
- **Trading Commission**: **$0** (commission-free stock trading)
- **Regulatory Fees**: Small fees per trade (~$0.01-0.05)
- **Market Data**: FREE (IEX real-time included)
- **API Access**: FREE (unlimited calls)
- **Premium Data** (Optional): $9-99/month for NYSE/NASDAQ Level 2

---

## Timeline Summary

| Step | Time Required |
|------|---------------|
| Complete application | 15-30 minutes |
| Identity verification | Instant - 24 hours |
| Account approval | 1-3 business days |
| Generate API keys | Instant |
| Fund account (ACH) | 3-5 business days |
| **TOTAL** | **4-8 business days** |

---

## Next Steps for Your Project

1. **Keep Using Paper Trading** (Current)
   - Continue testing with paper account
   - Perfect your trading strategy
   - Build confidence with platform

2. **Apply for Live Account** (When Ready)
   - Follow steps above
   - Complete application
   - Wait for approval

3. **Start Small with Live** (After Approval)
   - Deposit $100-500 to start
   - Execute small test trades (1 share)
   - Verify everything works correctly
   - Gradually increase as confidence builds

4. **Scale Up** (Over Time)
   - Increase deposit as comfortable
   - Test larger positions
   - Enable AI autonomous trading
   - Monitor performance

---

## Support Resources

- **Alpaca Documentation**: https://docs.alpaca.markets/
- **Support Email**: support@alpaca.markets
- **Community Slack**: https://alpaca.markets/slack
- **Support Hours**: 9 AM - 5 PM ET, Monday-Friday
- **Phone**: (415) 651-9141

---

**Document Complete**: Follow these steps to obtain live trading API keys and enable real money trading in f.insight.AI! 🚀
