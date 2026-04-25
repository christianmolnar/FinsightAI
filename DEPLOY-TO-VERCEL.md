# 🚀 Deploy to Vercel - Quick Guide

## Current Status
- ✅ Frontend configured for Vercel (`frontend/vercel.json`)
- ✅ Backend running on Railway: `https://finsightai-production-442e.up.railway.app`
- ✅ Code pushed to GitHub (auto-deploy enabled)
- ✅ JWT authentication working
- ✅ Mobile responsive

## Deployment Steps

### Option 1: Auto-Deploy (GitHub Integration)

**If you already have Vercel connected to this GitHub repo:**
1. Push was already completed → Vercel auto-deploys
2. Check: https://vercel.com/your-username/finsight-ai
3. Wait 2-3 minutes for build
4. Visit your production URL

### Option 2: Manual Deploy (First Time)

**If this is your first Vercel deployment:**

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy from frontend directory**:
```bash
cd /Users/christian/Repos/f.insight.AI\ Advanced/frontend
vercel --prod
```

4. **Follow prompts**:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N** (first time) or **Y** (if exists)
   - What's your project's name? `finsight-ai`
   - In which directory is your code located? `./` (already in frontend/)
   - Want to override settings? **N**

5. **Deployment complete!**
   - Vercel will display your production URL
   - Example: `https://finsight-ai.vercel.app`

### Option 3: Vercel Dashboard

1. Go to: https://vercel.com/new
2. Import from GitHub: `FinsightAI`
3. Root Directory: `frontend`
4. Framework Preset: Create React App
5. Build Command: `npm run build`
6. Output Directory: `build`
7. Environment Variable:
   - `REACT_APP_API_URL` = `https://finsightai-production-442e.up.railway.app`
8. Click **Deploy**

## Environment Variables

**Already configured in `frontend/vercel.json`:**
```json
{
  "env": {
    "REACT_APP_API_URL": "https://finsightai-production-442e.up.railway.app"
  }
}
```

**If deploying via Vercel Dashboard, add manually:**
- Key: `REACT_APP_API_URL`
- Value: `https://finsightai-production-442e.up.railway.app`

## Post-Deployment Testing

1. **Open production URL on mobile browser**
2. **Test authentication**:
   - Login with: `chrismolhome@hotmail.com` / [your password]
   - Should see Dashboard

3. **Test backtest**:
   - Navigate to Backtesting page
   - Click "Last 30 Days" quick backtest
   - Should see results in ~3-5 seconds
   - Expected: ~68 trades, 7-8% return, 50% win rate

4. **Verify mobile responsive**:
   - Quick backtest buttons should stack vertically
   - Padding should be comfortable on mobile
   - Tables should scroll horizontally

## Backend Verification

**Backend must be running on Railway:**
```bash
# Check backend status
curl https://finsightai-production-442e.up.railway.app/health
# Should return: {"status":"healthy"}
```

**If backend is down:**
1. Go to Railway dashboard
2. Select `finsightai` project
3. Click backend service
4. Check logs for errors
5. Redeploy if needed

## Troubleshooting

### Frontend shows "Network Error"
- Check: `REACT_APP_API_URL` environment variable set correctly
- Check: Backend is running on Railway
- Check: CORS enabled in backend (`middleware/cors_middleware.py`)

### Backtest returns 401 Unauthorized
- Check: User is logged in (see username in header)
- Check: `localStorage.getItem('finsight_token')` exists in browser console
- Check: Backend logs show "✅ Authenticated: [email]"

### Mobile looks broken
- Check: Page uses responsive classes (`sm:`, `md:`, `lg:`)
- Check: Meta viewport tag in `public/index.html`
- Check: Tailwind CSS is building correctly

## What You'll Show Your Friend

1. **Open app on your phone**: `https://finsight-ai.vercel.app` (your actual URL)
2. **Login**: Show authentication working
3. **Run backtest**: "Last 30 Days" → Results in seconds
4. **Show metrics**:
   - Total trades: ~68
   - Win rate: ~50%
   - Total return: ~7-8%
   - Sharpe ratio: ~7 (excellent!)
   - Max drawdown: ~1-2% (low risk)
5. **Show trade list**: Real entries/exits with dates, prices, P&L
6. **Explain**: "This backtests my AI trading strategy using 10 years of historical data from our database"

## Demo Talking Points

**"Here's what makes this powerful":**
- ✅ Backtests against **143 stocks** from database (not live API)
- ✅ **10 years of historical data** (2016-2026)
- ✅ **Database-first** = 10x faster than API calls
- ✅ **Realistic simulation**: Chronological order, cash management, position sizing
- ✅ **Multiple strategies**: Technical breakouts, seasonal patterns
- ✅ **AI-powered**: Confidence scoring, reasoning
- ✅ **Risk management**: Stop loss (-8%), take profit (+15%), time stops
- ✅ **Professional metrics**: Sharpe ratio, max drawdown, profit factor

---

**Deployment Date**: April 25, 2026  
**Backend**: Railway (already deployed)  
**Frontend**: Vercel (ready to deploy)  
**Status**: Demo-ready! 🎉
