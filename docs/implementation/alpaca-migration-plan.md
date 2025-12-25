# Alpaca Migration Plan

**Created:** December 25, 2025  
**Status:** Planning  
**Branch:** `feature/alpaca-migration`  
**Estimated Time:** 4-6 hours (AI-assisted)

---

## Executive Decision

**WHY MIGRATE:**
- No ties to Schwab ($300 holding, no trades)
- Permanent API keys (no 7-day re-auth)
- Better developer experience
- Fractional shares + crypto support
- Official Python SDK

**RISK MITIGATION:**
- Work on feature branch
- Keep main branch (Schwab) working
- Test thoroughly before merge
- Document all changes

---

## Phase 0: Setup (15 minutes)

### Git Branch Strategy
```bash
# Create feature branch
git checkout -b feature/alpaca-migration

# Keep main branch pristine
git push -u origin feature/alpaca-migration
```

### Alpaca Account Setup
- [ ] Open Alpaca paper trading account
- [ ] Get API keys (KEY_ID + SECRET_KEY)
- [ ] Open Alpaca live trading account
- [ ] Get live API keys
- [ ] Add to `.env` (not committed)

### Environment Variables
```bash
# .env (add these)
ALPACA_API_KEY_ID=your_key_id
ALPACA_API_SECRET_KEY=your_secret_key
ALPACA_PAPER=true  # Switch to false for live

# Remove (keep for reference during migration)
# SCHWAB_APP_KEY=...
# SCHWAB_SECRET=...
```

---

## Phase 1: Documentation Audit (30 minutes)

### Files That Reference Schwab

**High Priority (Must Update):**
- [ ] `/docs/architecture/schwab-portfolio-integration.md` → Archive or rename to `broker-integration.md`
- [ ] `/docs/architecture/schwab-vs-alpaca-comparison.md` → Add "DECISION: Migrated to Alpaca" banner
- [ ] `/docs/QUICK-START.md` → Update auth instructions
- [ ] `/docs/guides/*` → Search for Schwab-specific setup steps
- [ ] `README.md` → Update prerequisites section

**Medium Priority (Update After Testing):**
- [ ] `/docs/api/*` → Update endpoint examples
- [ ] `/docs/deployment/*` → Update environment variables
- [ ] `/docs/reference/*` → Update API client docs

**Low Priority (Archive):**
- [ ] `SCHWAB_SETUP.md` → Move to `/docs/archive/schwab-setup.md`
- [ ] `test_schwab_*.py` files → Delete after migration

### Documentation Strategy
```
/docs/
  architecture/
    ✅ broker-integration.md (rename from schwab-portfolio-integration.md)
    ✅ alpaca-api-reference.md (new)
    ❌ schwab-vs-alpaca-comparison.md (add "MIGRATED" banner)
  archive/
    📦 schwab-setup.md (moved from root)
    📦 schwab-portfolio-integration-original.md (backup)
```

---

## Phase 2: Backend Migration (2-3 hours)

### Step 1: Install Dependencies (5 min)
```bash
cd backend
pip install alpaca-py
pip freeze > requirements.txt
```

### Step 2: Create Alpaca Service (30 min - AI generates)

**File:** `/backend/app/services/alpaca_service.py`

**What I'll Generate:**
- `AlpacaService` class (replaces `SchwabService`)
- Authentication (simple API keys)
- Account info endpoint
- Positions endpoint
- Orders endpoint (buy/sell)
- Market data endpoint (quotes)

**Key Differences from Schwab:**
```python
# Schwab (OAuth complexity)
from schwabdev import Client
client = Client(app_key, app_secret)
client.update_tokens_auto()

# Alpaca (simple)
from alpaca.trading.client import TradingClient
client = TradingClient(api_key, secret_key, paper=True)
```

### Step 3: Update API Endpoints (30 min)

**Files to Update:**
- [ ] `/backend/app/api/portfolio.py` → Update imports
- [ ] `/backend/app/api/trading.py` → Replace Schwab calls
- [ ] `/backend/app/api/market_data.py` → Use Alpaca market data

**Changes:**
```python
# OLD
from app.services.schwab_service import SchwabService
schwab = SchwabService()

# NEW
from app.services.alpaca_service import AlpacaService
alpaca = AlpacaService()
```

### Step 4: Database Updates (15 min)

**Minimal Changes:**
- Positions table: Already generic (no Schwab-specific fields)
- Orders table: Already generic
- Accounts table: Change `account_hash` → `account_id` (Alpaca uses simple IDs)

**Migration Script:**
```sql
-- /database/migrations/004_alpaca_migration.sql
ALTER TABLE accounts RENAME COLUMN account_hash TO account_id;
-- That's it! (Alpaca responses already match our schema)
```

### Step 5: Remove Schwab Code (15 min)
- [ ] Delete `/backend/app/services/schwab_service.py`
- [ ] Delete `tokens.json` (no longer needed)
- [ ] Remove `schwabdev` from requirements.txt
- [ ] Clean up imports

---

## Phase 3: Frontend Updates (1 hour)

### Files to Update
- [ ] `/frontend/src/components/RealPortfolio.js`
- [ ] `/frontend/src/services/api.js`
- [ ] `/frontend/src/components/Settings.js` (if shows auth status)

**Changes:**
```javascript
// RealPortfolio.js - API calls stay the same!
// Our backend API interface doesn't change
const response = await fetch('/api/schwab/portfolio/overview')
// Just rename endpoint:
const response = await fetch('/api/portfolio/overview')
```

**UI Changes:**
- Remove "Re-authenticate" button (not needed!)
- Remove token expiry countdown
- Update "Connect Broker" flow

---

## Phase 4: Testing (1 hour)

### Test Checklist

**Unit Tests:**
- [ ] Test AlpacaService authentication
- [ ] Test account info retrieval
- [ ] Test position fetching
- [ ] Test order placement (paper)
- [ ] Test market data quotes

**Integration Tests:**
- [ ] Full portfolio load (paper account)
- [ ] Place small test order ($10)
- [ ] Verify order execution
- [ ] Test position updates
- [ ] Test P&L calculations

**UI Tests:**
- [ ] Dashboard loads
- [ ] Positions display correctly
- [ ] Order placement works
- [ ] No console errors

---

## Phase 5: Documentation Updates (30 min)

### Update These Files

**1. `/docs/architecture/broker-integration.md`** (rename from schwab)
```markdown
# Broker Integration Architecture (Alpaca)

## Authentication

**Alpaca uses permanent API keys:**
- APCA-API-KEY-ID header
- APCA-API-SECRET-KEY header
- No OAuth, no token expiration!

[... rest of updated doc ...]
```

**2. `/docs/QUICK-START.md`**
```markdown
## Prerequisites

1. Alpaca Account (https://alpaca.markets)
   - Sign up (free)
   - Enable paper trading
   - Get API keys from dashboard

2. Environment Setup
   ```bash
   ALPACA_API_KEY_ID=your_key_here
   ALPACA_API_SECRET_KEY=your_secret_here
   ALPACA_PAPER=true
   ```
```

**3. Archive Schwab Docs**
```bash
mkdir -p /docs/archive
mv SCHWAB_SETUP.md /docs/archive/
mv /docs/architecture/schwab-portfolio-integration.md \
   /docs/archive/schwab-portfolio-integration-original.md
```

**4. Update README.md**
- Replace Schwab references with Alpaca
- Update setup instructions
- Update feature list (add: fractional shares, crypto)

---

## Phase 6: Merge to Main (15 min)

### Pre-Merge Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No Schwab code remaining
- [ ] Environment variables documented
- [ ] Successful test trade ($10) in paper account

### Merge Process
```bash
# Final test on branch
pytest backend/tests/

# Commit all changes
git add .
git commit -m "feat: migrate from Schwab to Alpaca API

- Replace OAuth with permanent API keys
- Simpler authentication flow
- Better SDK (alpaca-py)
- Updated all documentation
- Archived Schwab-specific files

BREAKING CHANGE: Requires Alpaca account instead of Schwab"

# Push to remote
git push origin feature/alpaca-migration

# Switch to main and merge
git checkout main
git merge feature/alpaca-migration

# Deploy
git push origin main
```

---

## Documentation Files Requiring Updates

### Full Audit List

**CRITICAL (Must Update Before Merge):**
1. ✅ `/docs/architecture/schwab-portfolio-integration.md` → Rename to `broker-integration.md`
2. ✅ `/docs/QUICK-START.md` → Update auth setup
3. ✅ `/docs/START-HERE.md` → Update prerequisites
4. ✅ `README.md` → Update main setup instructions
5. ✅ `SCHWAB_SETUP.md` → Move to archive

**IMPORTANT (Update During Testing):**
6. ⚠️ `/docs/guides/authentication.md` (if exists)
7. ⚠️ `/docs/guides/setup-guide.md` (if exists)
8. ⚠️ `/docs/deployment/railway-setup.md` → Update env vars
9. ⚠️ `/docs/api/endpoints.md` → Update examples

**NICE TO HAVE (Update After Merge):**
10. 📝 `/docs/reference/api-client.md`
11. 📝 All `/docs/planning/*` files mentioning Schwab
12. 📝 Architecture diagrams with "Schwab API" boxes

---

## Rollback Plan

**If something goes wrong:**

```bash
# Option 1: Stay on feature branch, fix issues
git checkout feature/alpaca-migration
# Fix problems, test again

# Option 2: Abandon migration, return to main
git checkout main
# Schwab still works!

# Option 3: Revert merge (if already merged)
git revert HEAD
git push origin main
```

**Schwab code preserved:**
- Original files in git history
- Can always `git checkout main~1` to get Schwab version back

---

## Success Criteria

**Migration Complete When:**
- ✅ All tests passing with Alpaca API
- ✅ Can view portfolio in UI
- ✅ Can place orders successfully
- ✅ No authentication errors
- ✅ All documentation updated
- ✅ No references to Schwab in active code
- ✅ Successful $10 test trade in paper account

**Bonus Points:**
- ✅ No 7-day re-auth reminders!
- ✅ Cleaner codebase (no OAuth complexity)
- ✅ Better error messages
- ✅ Faster API responses

---

## Next Steps

**Ready to start?**

1. Create feature branch
2. I'll generate `AlpacaService` class
3. You test connection
4. Continue through phases

**Estimated Total Time:** 4-6 hours
**Your Time:** ~2 hours (testing, validation)
**My Time:** ~2-4 hours (code generation, docs)

---

**Question:** Should I start with Phase 0 (create branch + generate AlpacaService)?
