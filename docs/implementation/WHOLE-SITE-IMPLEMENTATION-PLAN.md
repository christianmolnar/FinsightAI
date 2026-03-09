# FInsightAI - Complete Site Implementation Plan
**AI Trading Agent Development Roadmap - Full v1.0 Delivery**

**Date Created:** December 22, 2025
**Last Updated:** March 8, 2026 - Auth, Alerts, Scanner, Autonomous Trading
**Project Status:** Full stack deployed to cloud. Frontend on Vercel, Backend on Railway.
**Current Phase:** Phase A - Authentication (CRITICAL - financial data exposed)
**Next Phase:** Phase B - ntfy.sh Alerts Verified → Phase C - Autonomous Scanner

**Overall Progress:** ~55% complete toward FINAL OBJECTIVE

> **⚠️ CRITICAL SECURITY ISSUE:** Financial account data is currently exposed with no authentication.
> Phase A (Authentication) must be completed before any other new features.

---

## 🎯 FINAL OBJECTIVE

A **fully autonomous paper trading system** running 24/7 on Railway/Vercel that:
1. ✅ Is **secured** — no financial data exposed publicly
2. ✅ **Finds opportunities** autonomously — scans market, scores candidates, creates proposals
3. ✅ **Executes trades** autonomously — buys and sells on paper account without human input
4. ✅ **Sends push notifications** for every buy, sell, and alert via ntfy.sh
5. ✅ **Backtests** the current strategy against historical data in Railway PostgreSQL
6. ✅ **Zero hardcoding** — all parameters configurable, all workflows complete
7. ✅ **Switch-ready** — flip one env var (`ALPACA_PAPER=false`) to go live

**Paper trading period:** Run autonomously for 2+ weeks on paper, validate, then flip to live.

---

## 📊 TRUE CURRENT STATE (March 8, 2026)

### ✅ What Is Actually Built & Working
| Component | Status | Notes |
|---|---|---|
| Backend (FastAPI) | ✅ Deployed on Railway | `https://finsightai-production-442e.up.railway.app` |
| Frontend (React) | ✅ Deployed on Vercel | `https://frontend-pi-kohl-57.vercel.app` |
| Database | ✅ Railway PostgreSQL | Always-on |
| Alpaca Integration | ✅ Paper + Live | `alpaca_service.py` (430 lines) |
| AI Research Engine | ✅ Complete | OpenAI + Claude dual-model |
| Sell Validation | ✅ Complete | Tax analysis, dual AI |
| Transaction Queue | ✅ Complete | 9 REST endpoints |
| Market Scanner | ✅ Built, using Alpaca now | 3 strategies, expanded universe |
| Universe Builder | ✅ Updated | SP500+DOW+NASDAQ100+Alpaca US equities |
| Railway Cron (Scanner) | ✅ Configured | Every 15 min market hours |
| ntfy.sh Service | ✅ Built | `ntfy_service.py` + `alert_service.py` updated |
| ntfy.sh Railway Vars | ✅ Set by user | `NTFY_TOKEN`, `NTFY_TOPIC` configured |
| Backtester | ✅ Built | `backtester.py`, backtest reports table |
| Calibration Engine | ✅ Built | `calibration_engine.py` |
| Historical Data Manager | ✅ Built | Alpaca-based, `historical_data_manager.py` |
| Kaggle 30yr Market Data | ✅ Downloaded | `docs/IndexDB/30-yr-financial-events/` (3 CSVs) |

### ❌ What Is NOT Built / NOT Working
| Component | Status | Priority |
|---|---|---|
| **User Authentication** | ❌ NOT BUILT | 🔴 CRITICAL |
| **Route Protection** | ❌ NOT BUILT | 🔴 CRITICAL |
| ntfy.sh end-to-end verified | ❌ NOT TESTED | 🔴 HIGH |
| Historical data in Railway DB | ❌ NOT POPULATED | 🔴 HIGH |
| Auto-execute trades (buy/sell) | ❌ NOT BUILT | 🔴 HIGH |
| Position Monitor | ❌ NOT BUILT | 🔴 HIGH |
| Earnings calendar (scanner) | ❌ Strategy skeleton only | 🟡 MEDIUM |
| Frontend Auth UI | ❌ NOT BUILT | 🔴 CRITICAL |

### ⚠️ Current Security State
- **The app is publicly accessible** at the Vercel URL with NO login required
- Anyone with the URL can see your portfolio, positions, and trading history
- CORS is configured for Vercel URLs but there is no JWT/session authentication
- The existing `app/api/auth.py` is **Schwab OAuth only** — not user login

---

## 🗺️ IMPLEMENTATION ROADMAP

### **Phase A: Authentication** 🔴 CRITICAL — DO FIRST
**Goal:** Secure the app with username/password login before anything else
**Estimated Time:** 3-4 hours

#### What to Build
- [ ] **A.1 JWT Authentication Backend**
  - [ ] `backend/api/user_auth.py` — register, login, refresh endpoints
  - [ ] `backend/services/auth_service.py` — JWT creation/validation, bcrypt passwords
  - [ ] `backend/middleware/auth_middleware.py` — `get_current_user` dependency
  - [ ] Protect ALL existing API routes with `Depends(get_current_user)`
  - [ ] Add `password_hash` column to `users` table
  - [ ] Migration: `database/migrations/add_auth_to_users.sql`
  - **Packages needed:** `python-jose[cryptography]`, `passlib[bcrypt]`, `python-multipart`

- [ ] **A.2 Railway Env Vars**
  - [ ] `JWT_SECRET_KEY` — strong random string (set in Railway dashboard)
  - [ ] `JWT_EXPIRE_MINUTES=1440` — 24-hour sessions

- [ ] **A.3 Frontend Auth**
  - [ ] `frontend/src/components/Login.js` — clean login page
  - [ ] `frontend/src/components/Register.js` — registration (invite-only for now)
  - [ ] `frontend/src/context/AuthContext.js` — JWT token storage + refresh
  - [ ] `frontend/src/utils/apiClient.js` — axios instance that injects Bearer token
  - [ ] Wrap all existing components in auth guard — redirect to login if not authenticated
  - [ ] Update ALL existing `fetch()` calls to use `apiClient`

**Completion Criteria:**
- [ ] Cannot access any page without logging in
- [ ] JWT token stored in httpOnly cookie or localStorage
- [ ] Token included in all API requests automatically
- [ ] Login page is clean and branded

---

### **Phase B: Verify ntfy.sh Push Notifications** 🟠 HIGH
**Goal:** Confirm alerts actually arrive on phone before building more automation
**Estimated Time:** 30 minutes

#### What to Build
- [ ] **B.1 Test Endpoint**
  - [ ] `POST /api/alerts/test` — sends a test notification via ntfy
  - [ ] Protected by auth (Phase A must be done first)

- [ ] **B.2 Frontend Test Button**
  - [ ] "Send Test Alert" button in settings/dashboard
  - [ ] Shows success/failure

- [ ] **B.3 Phone Setup**
  - [ ] Install ntfy app on phone
  - [ ] Subscribe to topic: `finsight-alerts`
  - [ ] Confirm test notification received

**Completion Criteria:**
- [ ] Click button in app → push notification appears on phone within 5 seconds

---

### **Phase C: Populate Historical Data (Railway DB)** 🟠 HIGH
**Goal:** Load historical stock data into Railway PostgreSQL for backtesting
**Estimated Time:** 2-3 hours build + background download time

#### Data Strategy
| Data | Source | Range | Purpose |
|---|---|---|---|
| Individual stock OHLCV | Alpaca API | 2016–present | Backtesting + scanner |
| Macro context (indices, commodities, bonds) | Kaggle CSV (already downloaded) | 1995–present | Market regime context |
| Market events (crises, crashes) | Kaggle CSV (already downloaded) | 1997–present | Event-aware backtesting |

#### What to Build
- [ ] **C.1 Import Kaggle Macro Data**
  - [ ] `backend/scripts/import_kaggle_macro.py`
  - [ ] Import `30_yr_market_data.csv` → `macro_data` table
  - [ ] Import `30_yr_financial_events.csv` → `financial_events` table
  - [ ] Run once as Railway one-off command

- [ ] **C.2 Alpaca Historical Download (2016–present)**
  - [ ] `backend/download_chunk.py` — chunked downloader (resume-safe, 100 symbols/batch)
  - [ ] Downloads to `historical_prices` table in Railway
  - [ ] Run as Railway one-off command, not as a background cron

- [ ] **C.3 Daily Update Job**
  - [ ] Add to `railway.json` cron: daily at 6pm ET → download yesterday's bars
  - [ ] Uses `historical_data_manager.daily_update()`

**Completion Criteria:**
- [ ] `historical_prices` table has data for 500+ symbols from 2016
- [ ] `macro_data` table populated from 1995
- [ ] `financial_events` table populated (10 major events)
- [ ] Backtester can run a 90-day backtest without hitting Alpaca API

---

### **Phase D: Autonomous Trading Engine** 🔴 HIGH
**Goal:** System finds opportunities, buys, monitors, and sells without human input
**Estimated Time:** 4-5 hours

This is the core of the Final Objective. Phases A-C must be complete first.

#### D.1 Position Monitor (missing piece)
- [ ] `backend/services/position_evaluator.py`
  - [ ] Fetches all open positions from Alpaca paper account
  - [ ] For each position, evaluates: SELL / BUY_MORE / HOLD / WATCH
  - [ ] **Exit signals:** stop loss breach, profit target hit, trailing stop, bad news
  - [ ] **Scale-in signals:** dip to better entry, improving fundamentals
  - [ ] Creates proposals in transaction queue
  - [ ] Sends ntfy alert for SELL signals

- [ ] `backend/jobs/monitor_positions.py`
  - [ ] Railway cron: every 5 minutes during market hours
  - [ ] Calls position_evaluator

#### D.2 Auto-Execute Logic
- [ ] `backend/services/auto_executor.py`
  - [ ] Reads pending proposals with `auto_execute=True`
  - [ ] Executes via Alpaca paper API if confidence ≥ threshold
  - [ ] Sends ntfy alert: "🤖 AUTO-BUY: 10 NVDA @ $142.30"
  - [ ] All parameters come from strategy config (no hardcoding)

- [ ] `backend/jobs/execute_proposals.py`
  - [ ] Railway cron: every 5 minutes during market hours

#### D.3 Complete the Scanner → Execute Pipeline
Current flow: Scanner finds candidates → Creates proposals (stops here ❌)
Target flow: Scanner → Proposals → Auto-executor → Alpaca order → ntfy alert ✅

- [ ] Wire `scan_opportunities.py` → auto_executor when confidence ≥ threshold
- [ ] Wire `monitor_positions.py` → auto_executor for SELL signals
- [ ] All auto-executions logged + ntfy notification sent

#### D.4 Railway Cron Jobs (final config)
```json
"cronJobs": [
  { "name": "opportunity-scanner", "schedule": "*/15 9-16 * * 1-5", "command": "cd backend && python jobs/run_scanner.py" },
  { "name": "position-monitor",    "schedule": "*/5 9-16 * * 1-5",  "command": "cd backend && python jobs/monitor_positions.py" },
  { "name": "auto-executor",       "schedule": "*/5 9-16 * * 1-5",  "command": "cd backend && python jobs/execute_proposals.py" },
  { "name": "daily-data-update",   "schedule": "0 18 * * 1-5",      "command": "cd backend && python jobs/daily_data_update.py" }
]
```

**Completion Criteria:**
- [ ] System buys a paper position without human input
- [ ] System sells a paper position when stop loss hit, without human input
- [ ] ntfy notification received for every buy and sell
- [ ] All parameters (stop loss %, position size, confidence threshold) come from DB config

---

### **Phase E: Frontend Polish** 🟡 MEDIUM
**Goal:** Dashboard shows autonomous system status clearly
**Estimated Time:** 2 hours

- [ ] **Agent Status Widget** — last scan time, positions monitored, proposals today
- [ ] **Position Status Indicators** — ✅ Healthy / ⚠️ Warning / 🔴 Alert / 💰 Buy More
- [ ] **Notifications Log** — show last 20 ntfy alerts sent
- [ ] **Auth UI** — login page, user menu, logout

---

## 📋 PRIORITY ORDER (What to build next)

```
1. 🔴 Phase A — Authentication        (security crisis — do TODAY)
2. 🟠 Phase B — Verify ntfy.sh        (30 min, confirm alerts work)
3. 🟠 Phase C — Historical Data       (needed for backtesting)
4. 🔴 Phase D — Autonomous Engine     (the main goal)
5. 🟡 Phase E — Frontend Polish       (nice to have)
```

---

## 🚀 DEPLOYMENT PROCESS

Since the app is cloud-hosted, all changes deploy via git push:

```bash
# Make changes → commit → push → Railway/Vercel auto-deploy
git add -A
git commit -m "feat: [description]"
git push origin main
# Railway redeploys backend automatically (~2 min)
# Vercel redeploys frontend automatically (~1 min)
```

**Railway env vars** (set in Railway Dashboard → Variables):
| Variable | Value | Status |
|---|---|---|
| `NTFY_TOKEN` | `tk_ep8ay6l7llrce6fezrdqxg1e7yox6` | ✅ Set |
| `NTFY_TOPIC` | `finsight-alerts` | ✅ Set |
| `NTFY_URL` | `https://ntfy.sh` | ✅ Set |
| `JWT_SECRET_KEY` | Generate strong random string | ❌ Not set yet |
| `JWT_EXPIRE_MINUTES` | `1440` | ❌ Not set yet |
| `ALPACA_PAPER_API_KEY_ID` | Your paper key | ✅ Set |
| `ALPACA_PAPER_API_SECRET_KEY` | Your paper secret | ✅ Set |
| `OPENAI_API_KEY` | Your key | ✅ Set |
| `ANTHROPIC_API_KEY` | Your key | ✅ Set |

---

## 📂 Key Files Reference

### Backend Services
| File | Purpose | Status |
|---|---|---|
| `services/alpaca_service.py` | Broker integration (paper+live) | ✅ |
| `services/market_scanner.py` | 3-strategy scanner, Alpaca data | ✅ Updated |
| `services/universe_builder.py` | SP500+DOW+NASDAQ+Alpaca US equities | ✅ Updated |
| `services/ntfy_service.py` | Push notifications | ✅ New |
| `services/alert_service.py` | Alert dispatcher → ntfy | ✅ Updated |
| `services/historical_data_manager.py` | Alpaca OHLCV download + cache | ✅ |
| `services/backtester.py` | Strategy backtesting engine | ✅ |
| `services/calibration_engine.py` | Backtest → strategy recommendations | ✅ |
| `services/ai_models.py` | OpenAI + Claude dual-model | ✅ |
| `services/position_evaluator.py` | Position monitoring + signals | ❌ Not built |
| `services/auto_executor.py` | Auto-execute approved proposals | ❌ Not built |

### Backend Jobs
| File | Purpose | Status |
|---|---|---|
| `jobs/run_scanner.py` | Railway cron entrypoint | ✅ |
| `jobs/scan_opportunities.py` | Full scan job | ✅ |
| `jobs/monitor_positions.py` | Position monitor job | ❌ Not built |
| `jobs/execute_proposals.py` | Auto-executor job | ❌ Not built |
| `jobs/daily_data_update.py` | Daily Alpaca data pull | ❌ Not built |

### Backend API
| File | Purpose | Status |
|---|---|---|
| `app/api/auth.py` | Schwab OAuth only (NOT user auth) | ⚠️ Misleading name |
| `api/user_auth.py` | JWT user auth (register/login) | ❌ Not built |
| `api/queue.py` | Transaction queue (9 endpoints) | ✅ |
| `api/scanner.py` | Scanner endpoints | ✅ |
| `api/backtest.py` | Backtesting endpoints | ✅ |

### Frontend
| File | Purpose | Status |
|---|---|---|
| `src/components/Login.js` | Login page | ❌ Not built |
| `src/context/AuthContext.js` | Auth state management | ❌ Not built |
| `src/utils/apiClient.js` | Axios + Bearer token | ❌ Not built |
| `src/components/Dashboard.js` | Main dashboard | ✅ |
| `src/components/TransactionQueue.js` | Queue UI | ✅ |
| `src/components/Backtesting.js` | Backtest UI | ✅ |
| `src/components/StrategyConfig.js` | Strategy config | ✅ |

### Data
| File | Purpose | Status |
|---|---|---|
| `docs/IndexDB/30-yr-financial-events/30_yr_market_data.csv` | 1995–present macro data | ✅ Downloaded |
| `docs/IndexDB/30-yr-financial-events/30_yr_financial_events.csv` | 10 major market events | ✅ Downloaded |
| Railway `historical_prices` table | Individual stock OHLCV | ❌ Not populated |
| Railway `macro_data` table | Macro index data | ❌ Not populated |

---

## ✅ COMPLETION CRITERIA FOR FINAL OBJECTIVE

The system is ready for 2-week paper trading run when:

- [ ] **Security:** Cannot access app without login
- [ ] **Alerts:** ntfy push notification received on phone for test alert
- [ ] **Data:** `historical_prices` populated for 500+ stocks from 2016
- [ ] **Backtesting:** Can run 90-day backtest from UI, see results
- [ ] **Scanning:** Railway cron runs scanner every 15 min market hours ✅ (already works)
- [ ] **Auto-buy:** Scanner finds opportunity → auto-executes paper buy → ntfy notification sent
- [ ] **Auto-sell:** Position hits stop loss → auto-executes paper sell → ntfy notification sent
- [ ] **Monitoring:** Dashboard shows last scan time, open positions with status
- [ ] **No hardcoding:** All thresholds/sizes/targets in DB strategy config
- [ ] **Live-ready:** Changing `ALPACA_PAPER=false` in Railway is the ONLY change needed to go live

---

*Last Updated: March 8, 2026*
*Next action: Build Phase A — JWT Authentication*
