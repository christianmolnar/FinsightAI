# Scanner SMS Alert Setup - Quick Start

## 🎯 What This Does

**Scanner runs on Railway every 15 minutes (9:30-4pm ET):**
1. Finds technical breakout opportunities
2. AI analyzes with 75%+ confidence
3. Creates proposals in Transaction Queue
4. **Texts you when opportunities found** 📱

## ✅ What I Just Built (5 minutes)

1. **Alert Service** (`backend/services/alert_service.py`)
   - Twilio SMS integration
   - Sends texts when opportunities found
   - Also tracks executions, circuit breakers

2. **Scanner Integration** (`backend/jobs/scan_opportunities.py`)
   - Now sends SMS alert after each scan
   - Shows top opportunity + total count

3. **Railway Cron Config** (`railway.json`)
   - Runs `python jobs/run_scanner.py` every 15 min
   - Only during market hours (M-F 9:30-4pm ET)

4. **Runner Script** (`backend/jobs/run_scanner.py`)
   - CLI interface for cron job
   - Prints results, exits cleanly

5. **Requirements** (`requirements.txt`)
   - Added `twilio==8.10.0`

## 🚀 What You Need to Do (10 minutes total)

### Step 1: Use Your Existing Twilio Account (1 min)
You already have Twilio set up with number: `+1 888 973 6665`

1. Go to https://console.twilio.com
2. Copy these credentials:
   - Account SID: `AC...` (from console dashboard)
   - Auth Token: `...` (from console dashboard)
   - Phone Number: `+18889736665` (your existing toll-free number)

### Step 2: Add to Railway (2 min)
In Railway dashboard > Your f.insight project > Variables:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx          # From Twilio console
TWILIO_AUTH_TOKEN=your_token_here           # From Twilio console
TWILIO_PHONE_FROM=+18889736665              # Your existing number
ALERT_PHONE_TO=+1YOUR_PHONE_NUMBER          # YOUR personal phone
```

**Note:** Use your existing verified phone number for `ALERT_PHONE_TO`

### Step 3: Deploy (1 min)
```bash
git add .
git commit -m "feat: Add SMS alerts and Railway cron for scanner"
git push
```

Railway auto-deploys.

### Step 4: Test (2 min)
**Option A: Wait for next 15-min mark**
- Cron runs at :00, :15, :30, :45
- Check Railway logs

**Option B: Trigger manually**
```bash
curl -X POST https://your-app.railway.app/api/scanner/scan/trigger
```

Check your phone - you should get a text! 📱

### Step 5: Monitor (ongoing)
- **Railway Logs**: See scanner execution every 15 min
- **Your Phone**: Get text when opportunities found
- **Dashboard**: See proposals in Transaction Queue

---

## 📱 What The Text Looks Like

**Single opportunity:**
```
🎯 f.insight Scanner Alert

Symbol: AAPL
Strategy: technical_breakout
Confidence: 87%

AI reasoning: Strong breakout above 
50-day high with volume surge...
```

**Multiple opportunities:**
```
🎯 f.insight Scanner Alert

Found 3 opportunities!

Top: TSLA (92%)
Strategy: technical_breakout

Check Transaction Queue for details.
```

---

## 💰 Cost

- **Railway**: Free tier or ~$5/month
- **Twilio**: $0.0075/text
  - ~5 opportunities/day × 20 trading days = 100 texts/month
  - **$0.75/month** (free $15 lasts 20 months!)

**Total: $0 for 20 months** 🎉

---

## 🔍 How It Works

```
Every 15 minutes (9:30-4pm ET):
├─ Railway cron triggers run_scanner.py
├─ Scanner checks S&P 500 for breakouts
├─ AI analyzes each candidate
├─ Creates proposals in database
└─ Sends SMS via Twilio
    └─ Text arrives on your phone in ~2 seconds
```

---

## 🎯 Monday Morning

**9:30 AM:** Market opens
**9:30:00 AM:** First scan runs
**9:30:15 AM:** You get text if opportunities found

Then every 15 minutes until market close (4pm).

---

## 🐛 Troubleshooting

**No text received?**
1. Check Railway logs: Did cron run?
2. Check Railway variables: TWILIO_* set correctly?
3. Check Twilio console: Any error messages?

**Cron not running?**
1. Railway may not support cron yet (new feature)
2. Fallback: Use cron-job.org (free external service)
   - Point to `/api/scanner/scan/trigger` endpoint

**Want to test locally?**
```bash
cd backend
source venv/bin/activate  # Your venv
python jobs/run_scanner.py
```

---

## 📚 Full Documentation

See `/docs/RAILWAY-SCANNER-SETUP.md` for detailed setup and alternatives.

---

**You're done!** Push to Railway and wait for Monday morning. 🚀
