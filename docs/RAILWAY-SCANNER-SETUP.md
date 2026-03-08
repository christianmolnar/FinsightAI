# Railway Cron Job Setup

## Enable Scanner with SMS Alerts

### 1. Get Twilio Credentials (2 minutes)

1. Go to https://www.twilio.com/try-twilio
2. Sign up (free trial gives $15 credit = ~500 texts)
3. Get your credentials from console:
   - Account SID
   - Auth Token
   - Phone Number (assigned to you)

### 2. Configure Railway Environment Variables (2 minutes)

In Railway dashboard > Your Project > Variables:

```bash
# Twilio SMS Alerts
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_FROM=+1234567890  # Your Twilio number
ALERT_PHONE_TO=+1234567890     # YOUR phone number to receive texts

# Database (already configured)
DATABASE_URL=postgresql://...
```

### 3. Add Twilio to Requirements (1 minute)

Railway will auto-install when you push:

```bash
echo "twilio==8.10.0" >> requirements.txt
```

### 4. Configure Cron Job in Railway (2 minutes)

**Option A: Railway Cron (Recommended)**

Add to `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "cronJobs": [
      {
        "schedule": "*/15 9-16 * * 1-5",
        "command": "python backend/jobs/run_scanner.py",
        "timezone": "America/New_York"
      }
    ]
  }
}
```

Schedule breakdown:
- `*/15` = Every 15 minutes
- `9-16` = 9am-4pm Eastern
- `1-5` = Monday-Friday

**Option B: External Cron Service (if Railway cron doesn't work)**

Use cron-job.org (free):
1. Create account at https://cron-job.org
2. Add job: `POST https://your-app.railway.app/api/scanner/scan/trigger`
3. Schedule: Every 15 minutes, M-F 9:30am-4pm ET

### 5. Create Scanner Runner Script (1 minute)

Create `backend/jobs/run_scanner.py`:
```python
"""
CLI script to run opportunity scanner
For use with Railway cron jobs
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scan_opportunities import OpportunityScanJob

async def main():
    scanner = OpportunityScanJob(
        confidence_threshold=0.75,
        max_opportunities=5,
        auto_create_proposals=True
    )
    result = await scanner.run()
    
    print(f"Scan complete: {result['opportunities_found']} found, {result['proposals_created']} proposals created")
    
    # Exit code 0 = success for cron monitoring
    exit(0 if result['status'] == 'success' else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

### 6. Test Locally (2 minutes)

```bash
cd backend
python jobs/run_scanner.py
```

Expected output:
```
🔍 Starting opportunity scan #1
   Threshold: 75%, Max: 5
📊 Found 3 opportunities
✅ Created 3 trade proposals
✅ SMS sent: SM1234567890
✅ Scan #1 complete in 12.3s
```

Check your phone - you should get a text! 📱

### 7. Deploy and Monitor (3 minutes)

```bash
git add .
git commit -m "feat: Add SMS alerts and Railway cron for scanner"
git push
```

Railway auto-deploys. Check logs in Railway dashboard.

**First scan will run at next 15-minute mark** (9:00, 9:15, 9:30, etc.)

---

## Testing Your Setup

### Manual Test (Immediate)
```bash
curl -X POST https://your-app.railway.app/api/scanner/scan/trigger
```

### Check if it's working:
1. **Railway Logs**: See scanner execution
2. **Your Phone**: Get text when opportunities found
3. **Dashboard**: See proposals in Transaction Queue

---

## Cost Estimate

- **Railway**: $0 (free tier, or ~$5/month if over free limits)
- **Twilio**: $0.0075 per text
  - 5 opportunities/day × 20 trading days = 100 texts/month = **$0.75/month**
  - Free $15 credit lasts **20 months**

**Total: $0 for the first 20 months** 🎉

---

## Alternative: Free Discord Webhook (No SMS)

If you prefer Discord notifications instead:

```python
# In alert_service.py, add Discord support
import requests

def _send_discord(self, message: str):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={"content": message})
```

Get webhook URL: Discord Server Settings > Integrations > Webhooks

---

## What You'll Get

**Every 15 minutes during market hours (9:30-4pm ET):**
1. Scanner finds technical breakouts
2. AI analyzes opportunities
3. Creates proposals in Transaction Queue
4. **Texts you the top opportunity** 📱
5. You check dashboard and approve/reject

**Monday morning first scan: 9:30 AM**
You'll get your first text when the market opens! 🚀
