# Architecture: Cloud-Based Autonomous Trading

## How This Actually Runs (No PC Required!)

```
┌─────────────────────────────────────────────────────────────┐
│                         RAILWAY CLOUD                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend (Port 8000)                       │    │
│  │  - Scanner service                                  │    │
│  │  - AI analysis                                      │    │
│  │  - Trade execution                                  │    │
│  │  - Runs 24/7 in cloud                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Railway Cron Jobs (Background)                     │    │
│  │                                                      │    │
│  │  Every 15 minutes (9:30-4pm ET, M-F):               │    │
│  │  ├─ Run scanner                                     │    │
│  │  ├─ Find opportunities                              │    │
│  │  ├─ Create proposals                                │    │
│  │  └─ Send SMS alert                                  │    │
│  │                                                      │    │
│  │  Every 5 minutes (market hours):                    │    │
│  │  ├─ Monitor positions                               │    │
│  │  ├─ Check stop loss / profit targets               │    │
│  │  └─ Create exit proposals                          │    │
│  │                                                      │    │
│  │  Every 1 minute (market hours):                     │    │
│  │  └─ Auto-execute high-confidence trades            │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL Database                                 │    │
│  │  - Stores proposals, trades, positions              │    │
│  │  - Runs 24/7 in cloud                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                         VERCEL CLOUD                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  React Frontend (Port 3000)                         │    │
│  │  - Dashboard                                         │    │
│  │  - Transaction Queue                                 │    │
│  │  - Portfolio                                         │    │
│  │  - Runs 24/7 in cloud                               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↕
                        YOUR PHONE 📱
                    - Receives SMS alerts
                    - No PC needed!
```

## What Runs Where

### Railway (Backend - Already Running There!)
- **Your backend is ALREADY on Railway**
- Port 8000 is accessible at: `https://your-app.railway.app`
- Database is ALREADY on Railway PostgreSQL
- **Cron jobs will run IN THE CLOUD** (not on your PC)

### Vercel (Frontend - Already Running There!)
- Your React app is ALREADY on Vercel
- Accessible at: `https://your-app.vercel.app`
- Just displays data from Railway backend

### Your PC (Development Only)
- **Only needed for development**
- NOT needed for production
- You can shut down your PC and everything keeps running!

## When Does This Go Live?

**After you push to git:**

1. **Railway auto-deploys** (2-3 minutes)
   - Installs Twilio library
   - Registers cron job
   - Backend restarts with new code

2. **Cron starts running automatically**
   - Next 15-minute mark after deploy
   - Example: Deploy at 3:07pm → First scan at 3:15pm
   - Runs in Railway cloud 24/7

3. **Monday 9:30 AM**
   - Market opens
   - Scanner runs at 9:30, 9:45, 10:00, 10:15...
   - You get text on your phone
   - **You don't need to do anything!**

## Local Development vs Production

| Component | Local (Development) | Production (Cloud) |
|-----------|--------------------|--------------------|
| Backend | `localhost:8000` | Railway (`your-app.railway.app`) |
| Frontend | `localhost:3000` | Vercel (`your-app.vercel.app`) |
| Database | Railway (always cloud) | Railway (same) |
| Cron Jobs | Manual run for testing | Railway (automatic) |
| Your PC | Running | **Can be OFF!** |

## Testing Right Now (Before Deploy)

**Local test (PC required):**
```bash
cd backend
source venv/bin/activate
python jobs/run_scanner.py  # Runs once, manually
```

**After deploy to Railway:**
```bash
# Trigger from anywhere (even your phone!)
curl -X POST https://your-app.railway.app/api/scanner/scan/trigger
```

## Your PC Can Be Off!

Once deployed to Railway:
- ✅ Scanner runs every 15 min (Railway cron)
- ✅ Backend serves API requests (Railway)
- ✅ Database stores data (Railway)
- ✅ Frontend displays UI (Vercel)
- ✅ SMS alerts sent to phone (Twilio)

**Your PC: Completely optional!** 🎉

You can:
- Turn off your PC
- Go on vacation
- System keeps trading
- You get texts when opportunities found

## Monday Morning Scenario

**9:00 AM:** You're drinking coffee, PC is off
**9:30 AM:** Market opens, Railway cron triggers scanner
**9:32 AM:** Your phone buzzes 📱
```
🎯 f.insight Scanner Alert

Found 3 opportunities!

Top: AAPL (89%)
Strategy: technical_breakout

Check Transaction Queue for details.
```
**9:33 AM:** You open phone browser, go to Vercel app
**9:34 AM:** Review proposals, approve with one tap
**9:35 AM:** Trade executes on Alpaca

**Your PC: Still off.** ☕

## Cost Breakdown (All Cloud)

| Service | Purpose | Cost |
|---------|---------|------|
| Railway | Backend + Cron | $5-10/month |
| Vercel | Frontend | $0 (hobby plan) |
| Railway PostgreSQL | Database | Included |
| Twilio | SMS alerts | $0.75/month (~100 texts) |
| **Total** | | **~$6-11/month** |

No PC electricity costs! 💡

## Summary

**Your question: "When will we be able to run this from Railway?"**

**Answer: RIGHT NOW! It already does!**

- Backend is ALREADY on Railway
- Frontend is ALREADY on Vercel
- This commit adds cron jobs to Railway (cloud-based)
- After `git push`, it's 100% autonomous in the cloud
- Your PC is only needed for development

**You never have to run this from your PC for production!** 🚀

---

**Next:** Push to git → Railway deploys → Cron starts → Monday morning texts begin!
