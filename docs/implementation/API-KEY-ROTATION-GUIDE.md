# API Key Rotation Guide - f.insight.AI Advanced
**Date:** April 22, 2026  
**Purpose:** Rotate Alpaca and Vercel API keys/tokens for security

---

## 📋 Current System Status

### Architecture Overview
- **Backend**: FastAPI on Railway (`https://finsightai-production-442e.up.railway.app`)
- **Frontend**: React on Vercel (`https://frontend-pi-kohl-57.vercel.app`)
- **Database**: Railway PostgreSQL
- **Trading**: Alpaca Markets (Paper + Live accounts)
- **Current Phase**: Phase C (Populate Historical Data in Railway DB)

### Current API Keys & Tokens (from .env)

#### 🔴 Alpaca Paper Trading (NEEDS ROTATION)
```
ALPACA_PAPER_API_KEY_ID=PK[REDACTED - Previously exposed]
ALPACA_PAPER_API_SECRET_KEY=[REDACTED - Previously exposed]
```
- **Account**: Virtual $100k paper trading
- **Dashboard**: https://app.alpaca.markets/paper/dashboard/overview
- **Status**: ⚠️ EXPOSED IN REPO - Must rotate immediately

#### 🔴 Alpaca Live Trading (NEEDS ROTATION)
```
ALPACA_LIVE_API_KEY_ID=AK[REDACTED - Previously exposed]
ALPACA_LIVE_API_SECRET_KEY=[REDACTED - Previously exposed]
```
- **Account**: Real money trading ($500 Individual Trading)
- **Dashboard**: https://app.alpaca.markets/brokerage/dashboard/overview
- **Status**: ⚠️ EXPOSED IN REPO - **CRITICAL** - Must rotate immediately

#### 🟢 AI API Keys (Optional Rotation)
```
OPENAI_API_KEY=sk-proj-[REDACTED - Previously exposed in repo]
ANTHROPIC_API_KEY=sk-ant-api03-[REDACTED - Previously exposed in repo]
```
- **Status**: ⚠️ EXPOSED IN REPO - Consider rotation for best practices

#### 🟡 Pushover (Notification Service)
```
NTFY_TOKEN=tk_[REDACTED - Previously exposed]
PUSHOVER_TOKEN=[Not visible in .env - set in Railway]
PUSHOVER_USER_KEY=[Not visible in .env - set in Railway]
```
- **Status**: ⚠️ ntfy token exposed, Pushover tokens safe in Railway

---

## 🔐 Key Rotation Checklist

### Priority 1: Alpaca Live Trading Keys (CRITICAL)
**Why Critical**: Real money account ($500) exposed in Git history

- [ ] **1.1 Generate New Live Keys**
  - Go to: https://app.alpaca.markets/brokerage/dashboard/overview
  - Navigate to "API Keys" section
  - Click "Generate New Key Pair"
  - **Save immediately** - Secret shown only once
  - Keys format: `AK...` (Key ID), `secret_key` (Secret)

- [ ] **1.2 Update Local .env**
  ```bash
  cd "/Users/christian/Repos/f.insight.AI Advanced"
  # Edit .env file
  ALPACA_LIVE_API_KEY_ID=<new_live_key_id>
  ALPACA_LIVE_API_SECRET_KEY=<new_live_secret>
  ```

- [ ] **1.3 Update Railway Environment Variables**
  - Go to: https://railway.app/project/[your-project]
  - Click "Variables" tab
  - Update:
    - `ALPACA_LIVE_API_KEY_ID`
    - `ALPACA_LIVE_API_SECRET_KEY`
  - Click "Redeploy" after updating

- [ ] **1.4 Revoke Old Keys**
  - Return to Alpaca Dashboard
  - Delete the old key pair
  - Verify deletion

- [ ] **1.5 Test Live Portfolio**
  - Visit: https://frontend-pi-kohl-57.vercel.app
  - Log in
  - Navigate to "Live Portfolio"
  - Verify account data loads correctly

### Priority 2: Alpaca Paper Trading Keys (HIGH)
**Why Important**: Paper trading testing account exposed

- [ ] **2.1 Generate New Paper Keys**
  - Go to: https://app.alpaca.markets/paper/dashboard/overview
  - Navigate to "API Keys" section
  - Click "Generate New Key Pair"
  - **Save immediately** - Secret shown only once
  - Keys format: `PK...` (Key ID), `secret_key` (Secret)
  - **Note**: Paper keys start with "PK", not "AK"

- [ ] **2.2 Update Local .env**
  ```bash
  ALPACA_PAPER_API_KEY_ID=<new_paper_key_id>
  ALPACA_PAPER_API_SECRET_KEY=<new_paper_secret>
  ```

- [ ] **2.3 Update Railway Environment Variables**
  - Update:
    - `ALPACA_PAPER_API_KEY_ID`
    - `ALPACA_PAPER_API_SECRET_KEY`
  - Redeploy

- [ ] **2.4 Revoke Old Keys**
  - Delete old paper key pair from dashboard

- [ ] **2.5 Test Paper Portfolio**
  - Navigate to "Paper Portfolio" in app
  - Verify $100k virtual account loads

### Priority 3: OpenAI API Key (MEDIUM)
**Why Rotate**: Exposed in repo, used for AI research engine

- [ ] **3.1 Generate New OpenAI Key**
  - Go to: https://platform.openai.com/api-keys
  - Click "Create new secret key"
  - Name: "finsight-production-apr2026"
  - Save immediately

- [ ] **3.2 Update Local .env**
  ```bash
  OPENAI_API_KEY=<new_openai_key>
  ```

- [ ] **3.3 Update Railway**
  - Variable: `OPENAI_API_KEY`
  - Redeploy

- [ ] **3.4 Revoke Old Key**
  - Return to OpenAI dashboard
  - Delete old key
  - **Note**: Key starts with `sk-proj-`

- [ ] **3.5 Test AI Features**
  - Test transaction queue AI research
  - Verify AI-powered trade proposals work

### Priority 4: Anthropic (Claude) API Key (MEDIUM)
**Why Rotate**: Exposed in repo, used for dual-AI validation

- [ ] **4.1 Generate New Anthropic Key**
  - Go to: https://console.anthropic.com/settings/keys
  - Click "Create Key"
  - Name: "finsight-production-apr2026"
  - Save immediately

- [ ] **4.2 Update Local .env**
  ```bash
  ANTHROPIC_API_KEY=<new_anthropic_key>
  ```

- [ ] **4.3 Update Railway**
  - Variable: `ANTHROPIC_API_KEY`
  - Redeploy

- [ ] **4.4 Revoke Old Key**
  - Delete from Anthropic console
  - **Note**: Key starts with `sk-ant-api03-`

- [ ] **4.5 Test Dual-AI**
  - Test sell validation (uses both OpenAI + Claude)
  - Verify AI confidence scoring works

### Priority 5: Vercel (If Applicable) (LOW)
**Status**: Vercel doesn't use API tokens for basic deployments

**Check if needed:**
- [ ] **5.1 Check Vercel Project Settings**
  - Go to: https://vercel.com/[your-team]/frontend
  - Click "Settings" → "Environment Variables"
  - **Look for**: Any API tokens or secrets set
  
- [ ] **5.2 If Vercel API Token Exists**
  - Go to: https://vercel.com/account/tokens
  - Generate new token
  - Update in CI/CD if used
  - Delete old token

**Note**: Standard Vercel deployments (Git-based) don't require API tokens. Only needed if using Vercel CLI or API programmatically.

---

## 📍 Where Keys Are Used

### Backend (Railway)
**File**: `/backend/app/services/alpaca_service.py`
```python
def __init__(self, paper=True):
    if paper:
        self.api_key = os.getenv("ALPACA_PAPER_API_KEY_ID")
        self.secret_key = os.getenv("ALPACA_PAPER_API_SECRET_KEY")
    else:
        self.api_key = os.getenv("ALPACA_LIVE_API_KEY_ID")
        self.secret_key = os.getenv("ALPACA_LIVE_API_SECRET_KEY")
```

**Key Services Using Alpaca**:
- `alpaca_service.py` - Trading execution
- `market_scanner.py` - Opportunity scanning
- `historical_data_manager.py` - Data downloads
- `backtester.py` - Strategy backtesting

**AI Services**:
- `ai_research_engine.py` - Uses OpenAI + Anthropic
- `sell_validator.py` - Dual-AI validation

### Frontend (Vercel)
**Files**:
- `src/components/portfolios/RealPortfolio.js` - Live trading UI
- `src/components/portfolios/PaperPortfolio.js` - Paper trading UI

**Communication**: Frontend → Backend API (JWT auth) → Alpaca
- Frontend does NOT directly use Alpaca keys
- All trading goes through Railway backend

### Local Development
**File**: `.env` (project root)
- Used by local backend during development
- **CRITICAL**: Never commit this file
- Already in `.gitignore` (but previously committed - see Git history cleanup below)

---

## 🔒 Security Best Practices

### After Rotation

- [ ] **Add .env to .gitignore** (if not already)
  ```bash
  echo ".env" >> .gitignore
  git add .gitignore
  git commit -m "chore: ensure .env is gitignored"
  ```

- [ ] **Remove .env from Git History** (CRITICAL)
  ```bash
  # WARNING: This rewrites Git history - coordinate with team
  cd "/Users/christian/Repos/f.insight.AI Advanced"
  
  # Option 1: BFG Repo Cleaner (recommended)
  brew install bfg
  bfg --delete-files .env
  git reflog expire --expire=now --all
  git gc --prune=now --aggressive
  
  # Option 2: git-filter-repo (alternative)
  pip install git-filter-repo
  git filter-repo --invert-paths --path .env
  ```

- [ ] **Force Push After Cleanup** (CAREFUL)
  ```bash
  # This will break anyone else's clones - coordinate first
  git push --force --all
  git push --force --tags
  ```

- [ ] **Create .env.example**
  ```bash
  # Create template file (no real keys)
  cat > .env.example << 'EOF'
# Environment variables for FinsightAI
# Copy to .env and fill in real values

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/finsight

# FastAPI
SECRET_KEY=generate_secure_random_key_here
ENV=development

# Frontend
REACT_APP_API_URL=http://localhost:8000

# AI Integration
OPENAI_API_KEY=sk-proj-your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Alpaca Paper Trading
ALPACA_PAPER_API_KEY_ID=PK...
ALPACA_PAPER_API_SECRET_KEY=...

# Alpaca Live Trading
ALPACA_LIVE_API_KEY_ID=AK...
ALPACA_LIVE_API_SECRET_KEY=...

# Pushover Notifications
PUSHOVER_TOKEN=...
PUSHOVER_USER_KEY=...
EOF
  
  git add .env.example
  git commit -m "docs: add .env.example template"
  ```

- [ ] **Document Rotation in CHANGELOG**
  ```bash
  # Add entry to RELEASE-NOTES or CHANGELOG
  echo "## Security - API Key Rotation (April 22, 2026)" >> RELEASE-NOTES-V1.0.md
  echo "- Rotated all Alpaca API keys (paper + live)" >> RELEASE-NOTES-V1.0.md
  echo "- Rotated OpenAI and Anthropic API keys" >> RELEASE-NOTES-V1.0.md
  echo "- Removed .env from Git history" >> RELEASE-NOTES-V1.0.md
  git commit -am "security: document API key rotation"
  ```

### Ongoing Security

- **Never commit .env files**
- **Use Railway environment variables** for production
- **Rotate keys every 90 days** (set calendar reminder)
- **Monitor API usage** on Alpaca/OpenAI/Anthropic dashboards for anomalies
- **Enable 2FA** on all accounts (Alpaca, OpenAI, Anthropic, Railway, Vercel)

---

## 🧪 Testing After Rotation

### Full System Test

- [ ] **1. Local Backend Test**
  ```bash
  cd backend
  source venv/bin/activate  # or: .venv/bin/activate
  uvicorn app.main:app --reload
  ```
  - Should start without errors
  - Check logs for Alpaca connection

- [ ] **2. Railway Backend Test**
  - Visit: https://finsightai-production-442e.up.railway.app/docs
  - Should see FastAPI docs
  - Test `/api/alpaca/account` endpoint

- [ ] **3. Frontend Test**
  - Visit: https://frontend-pi-kohl-57.vercel.app
  - Log in with test account
  - Navigate to:
    - **Paper Portfolio** - Should show $100k virtual account
    - **Live Portfolio** - Should show real account balance
    - **Market Scanner** - Should fetch data
    - **Transaction Queue** - Should show proposals

- [ ] **4. AI Features Test**
  - Create a new trade proposal
  - Verify AI research generates
  - Check dual-AI validation (OpenAI + Claude)

- [ ] **5. Trading Test (Paper Only)**
  ```bash
  # Test paper trading execution
  # Use "Execute Trade" button in Paper Portfolio
  # Buy 1 share of a low-cost stock (e.g., F - Ford)
  ```
  - Should execute successfully
  - Check Alpaca paper dashboard for order

---

## 📞 Support & Resources

### Dashboards
- **Alpaca Paper**: https://app.alpaca.markets/paper/dashboard/overview
- **Alpaca Live**: https://app.alpaca.markets/brokerage/dashboard/overview
- **OpenAI**: https://platform.openai.com/account/usage
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Railway**: https://railway.app/dashboard
- **Vercel**: https://vercel.com/dashboard

### Documentation
- Alpaca API Docs: https://alpaca.markets/docs/
- OpenAI API Docs: https://platform.openai.com/docs/
- Anthropic API Docs: https://docs.anthropic.com/

### Emergency Contacts
- **Alpaca Support**: support@alpaca.markets
- **Railway Support**: https://railway.app/help

---

## ✅ Completion Checklist

- [ ] All Alpaca keys rotated (paper + live)
- [ ] All AI API keys rotated (OpenAI + Anthropic)
- [ ] Railway environment variables updated
- [ ] Old keys revoked on all platforms
- [ ] .env removed from Git history
- [ ] .env.example created
- [ ] Full system test passed
- [ ] Documentation updated
- [ ] Team notified of changes

**Date Completed**: _____________  
**Completed By**: _____________

---

**Last Updated**: April 22, 2026  
**Next Scheduled Rotation**: July 22, 2026 (90 days)
