# Documentation Migration Plan: Schwab → Alpaca

**Created:** December 25, 2025  
**Status:** 🚧 In Progress  
**Branch:** `feature/alpaca-migration`  
**Owner:** FInsightAI Documentation Team

---

## 📋 Overview

**Goal:** Restructure `/docs` to separate Schwab (legacy/archived) from Alpaca (current/active) documentation.

**Strategy:**
- Keep Schwab docs pristine and archived
- Create new Alpaca-specific documentation
- Only migrate/rewrite docs as needed
- Track completion status

---

## 🗂️ New Documentation Structure

```
/docs/
  ├── README.md (updated: points to Alpaca docs)
  ├── START-HERE.md (updated: Alpaca quick start)
  ├── QUICK-START.md (updated: Alpaca setup)
  ├── DOCUMENTATION-INDEX.md (updated: new structure)
  ├── DOCUMENTATION-MIGRATION-PLAN.md (this file)
  │
  ├── /brokers/
  │   ├── /schwab/ (ARCHIVED - LEGACY)
  │   │   ├── README.md ("⚠️ ARCHIVED: Schwab integration deprecated")
  │   │   ├── schwab-portfolio-integration.md (original spec)
  │   │   ├── SCHWAB_SETUP.md (moved from root)
  │   │   ├── schwab-api-reference.md
  │   │   └── oauth-flow.md
  │   │
  │   └── /alpaca/ (ACTIVE - CURRENT)
  │       ├── README.md ("✅ CURRENT: Alpaca integration")
  │       ├── alpaca-portfolio-integration.md (NEW - rewritten from Schwab)
  │       ├── alpaca-setup.md (NEW)
  │       ├── alpaca-api-reference.md (NEW)
  │       └── authentication.md (NEW - simple API keys)
  │
  ├── /architecture/ (broker-agnostic + Alpaca-specific)
  │   ├── system-architecture.md (updated for Alpaca)
  │   ├── autonomous-trading-agent.md (✅ already broker-agnostic)
  │   ├── schwab-vs-alpaca-comparison.md (✅ updated with migration decision)
  │   └── database-schema.md (minimal changes needed)
  │
  ├── /implementation/
  │   ├── alpaca-migration-plan.md (✅ COMPLETE)
  │   ├── phase-1-foundation.md (needs Alpaca update)
  │   ├── phase-2-portfolio.md (needs Alpaca update)
  │   └── phase-3-trading.md (needs Alpaca update)
  │
  ├── /guides/ (mostly broker-agnostic)
  │   ├── getting-started.md (update: Alpaca setup)
  │   ├── portfolio-management.md (✅ stays same)
  │   ├── trading-strategies.md (✅ stays same)
  │   └── deployment.md (update: Alpaca env vars)
  │
  ├── /api/ (needs Alpaca updates)
  │   ├── endpoints.md (update examples)
  │   ├── authentication.md (NEW - rewrite for Alpaca)
  │   └── portfolio-endpoints.md (update examples)
  │
  └── /reference/
      ├── environment-variables.md (update for Alpaca)
      └── error-codes.md (✅ mostly stays same)
```

---

## 📊 Migration Status Tracker

### Phase 1: Archive Schwab Documentation ✅

**Status:** Ready to execute

| Task | Status | Files | Priority |
|------|--------|-------|----------|
| Create `/docs/brokers/schwab/` directory | ⏸️ Ready | - | HIGH |
| Move Schwab-specific docs to archive | ⏸️ Ready | 5 files | HIGH |
| Add archive warning README | ⏸️ Ready | 1 file | HIGH |
| Update root README.md | ⏸️ Ready | 1 file | HIGH |

**Files to Archive:**
- [ ] `/SCHWAB_SETUP.md` → `/docs/brokers/schwab/SCHWAB_SETUP.md`
- [ ] `/docs/architecture/schwab-portfolio-integration.md` → `/docs/brokers/schwab/schwab-portfolio-integration.md`
- [ ] Any test files: `test_schwab_*.py` → Delete (not archive)

---

### Phase 2: Create Alpaca Documentation 🚧

**Status:** In Progress

| Document | Status | Based On | Est. Time | Priority |
|----------|--------|----------|-----------|----------|
| `/docs/brokers/alpaca/README.md` | ⏸️ Todo | New | 15 min | HIGH |
| `/docs/brokers/alpaca/alpaca-setup.md` | ⏸️ Todo | SCHWAB_SETUP.md | 30 min | HIGH |
| `/docs/brokers/alpaca/alpaca-portfolio-integration.md` | ⏸️ Todo | schwab-portfolio-integration.md | 1 hour | HIGH |
| `/docs/brokers/alpaca/alpaca-api-reference.md` | ⏸️ Todo | New | 45 min | MEDIUM |
| `/docs/brokers/alpaca/authentication.md` | ⏸️ Todo | New | 20 min | HIGH |

**Total Estimated Time:** 2.5 hours (AI-assisted)

---

### Phase 3: Update Root Documentation 🚧

**Status:** In Progress

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `/docs/README.md` | ⏸️ Todo | Update broker references | 15 min | HIGH |
| `/docs/START-HERE.md` | ⏸️ Todo | Alpaca quick start | 20 min | HIGH |
| `/docs/QUICK-START.md` | ⏸️ Todo | Alpaca setup instructions | 30 min | HIGH |
| `/docs/DOCUMENTATION-INDEX.md` | ⏸️ Todo | New structure | 15 min | HIGH |
| `/README.md` (root) | ⏸️ Todo | Prerequisites update | 15 min | HIGH |

**Total Estimated Time:** 1.5 hours

---

### Phase 4: Update Architecture Docs 🚧

**Status:** Partial

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `architecture/system-architecture.md` | ⏸️ Todo | Update diagrams (Schwab→Alpaca) | 30 min | MEDIUM |
| `architecture/autonomous-trading-agent.md` | ✅ Done | Already broker-agnostic | 0 min | - |
| `architecture/schwab-vs-alpaca-comparison.md` | ✅ Done | Updated with decision | 0 min | - |
| `architecture/database-schema.md` | ⏸️ Todo | Minor updates (account_hash→account_id) | 15 min | LOW |

**Total Estimated Time:** 45 minutes

---

### Phase 5: Update Implementation Docs 🚧

**Status:** Partial

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `implementation/alpaca-migration-plan.md` | ✅ Done | Complete | 0 min | - |
| `implementation/phase-1-foundation.md` | ⏸️ Todo | Update auth flow | 20 min | LOW |
| `implementation/phase-2-portfolio.md` | ⏸️ Todo | Update API examples | 20 min | LOW |
| `implementation/phase-3-trading.md` | ⏸️ Todo | Update order examples | 20 min | LOW |

**Total Estimated Time:** 1 hour

---

### Phase 6: Update Guides 🚧

**Status:** Not Started

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `guides/getting-started.md` | ⏸️ Todo | Alpaca setup steps | 30 min | MEDIUM |
| `guides/portfolio-management.md` | ✅ Done | Broker-agnostic (no changes) | 0 min | - |
| `guides/trading-strategies.md` | ✅ Done | Broker-agnostic (no changes) | 0 min | - |
| `guides/deployment.md` | ⏸️ Todo | Update env vars | 15 min | MEDIUM |

**Total Estimated Time:** 45 minutes

---

### Phase 7: Update API Reference 🚧

**Status:** Not Started

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `api/endpoints.md` | ⏸️ Todo | Update examples with Alpaca responses | 30 min | MEDIUM |
| `api/authentication.md` | ⏸️ Todo | Rewrite for API keys (not OAuth) | 30 min | HIGH |
| `api/portfolio-endpoints.md` | ⏸️ Todo | Update response schemas | 20 min | MEDIUM |

**Total Estimated Time:** 1.5 hours

---

### Phase 8: Update Reference Docs 🚧

**Status:** Not Started

| Document | Status | Changes Needed | Est. Time | Priority |
|----------|--------|----------------|-----------|----------|
| `reference/environment-variables.md` | ⏸️ Todo | Remove Schwab vars, add Alpaca | 15 min | HIGH |
| `reference/error-codes.md` | ✅ Done | Mostly same (minor updates) | 5 min | LOW |

**Total Estimated Time:** 20 minutes

---

## 📈 Progress Summary

**Overall Documentation Migration:**

| Phase | Status | Files | Est. Time | Actual Time |
|-------|--------|-------|-----------|-------------|
| 1. Archive Schwab | ⏸️ Ready | 3 files | 15 min | - |
| 2. Create Alpaca Docs | 🚧 In Progress | 5 files | 2.5 hours | - |
| 3. Update Root Docs | ⏸️ Todo | 5 files | 1.5 hours | - |
| 4. Update Architecture | 🚧 Partial | 4 files | 45 min | - |
| 5. Update Implementation | 🚧 Partial | 4 files | 1 hour | - |
| 6. Update Guides | ⏸️ Todo | 4 files | 45 min | - |
| 7. Update API Docs | ⏸️ Todo | 3 files | 1.5 hours | - |
| 8. Update Reference | ⏸️ Todo | 2 files | 20 min | - |

**Total Estimated Time:** ~8.5 hours (AI-assisted)  
**Completed:** 2 files (schwab-vs-alpaca-comparison.md, alpaca-migration-plan.md)  
**Remaining:** 28 files

---

## 🎯 Execution Strategy

### Parallel with Code Migration

**During Code Migration (Hours 1-6):**
- ✅ Create `/docs/brokers/schwab/` archive (5 min)
- ✅ Create `/docs/brokers/alpaca/` structure (5 min)
- ✅ Generate `alpaca-setup.md` as we test (30 min)
- ✅ Generate `alpaca-api-reference.md` as we code (45 min)

**After Code Migration (Hours 7-8):**
- Update root documentation (README, QUICK-START, etc.)
- Update architecture diagrams
- Update guide examples

**Low Priority (After Merge):**
- Update implementation phase docs
- Polish API reference docs
- Update minor reference docs

### Documentation Generation Approach

**AI-Assisted (Fast):**
- I generate new Alpaca docs from Schwab templates
- You review for accuracy
- Iterate on examples/code

**Critical Human Review:**
- Authentication flows (verify correct)
- API response examples (test with real API)
- Setup instructions (validate steps work)

---

## 🚀 Quick Start: Archive Schwab Now

**Execute immediately (5 minutes):**

```bash
# 1. Create archive structure
mkdir -p /docs/brokers/schwab
mkdir -p /docs/brokers/alpaca

# 2. Move Schwab docs
mv SCHWAB_SETUP.md docs/brokers/schwab/
mv docs/architecture/schwab-portfolio-integration.md docs/brokers/schwab/

# 3. Create archive README
echo "⚠️ ARCHIVED: Schwab Integration (Deprecated)" > docs/brokers/schwab/README.md

# 4. Create Alpaca placeholder
echo "✅ CURRENT: Alpaca Integration (Active)" > docs/brokers/alpaca/README.md

# 5. Commit
git add docs/brokers/
git commit -m "docs: archive Schwab, create Alpaca structure"
```

---

## 📝 Documentation Standards

**For All Alpaca Docs:**

### File Headers
```markdown
# [Title]

**Document Version:** 1.0  
**Created:** December 25, 2025  
**Status:** ✅ Active / 🚧 Draft / 📋 Planning  
**Broker:** Alpaca  
**Owner:** [Team]

---
```

### Code Examples
```python
# ✅ Good: Complete, runnable examples
from alpaca.trading.client import TradingClient

client = TradingClient(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    paper=True
)

# Get account info
account = client.get_account()
print(f"Buying power: ${account.buying_power}")
```

### Diagrams
- Use ASCII diagrams for workflows
- Keep Schwab references in archived docs only
- Update system architecture with "Alpaca API"

---

## ✅ Completion Checklist

**Documentation migration complete when:**

- [ ] All Schwab docs moved to `/docs/brokers/schwab/`
- [ ] Archive warning added to Schwab README
- [ ] `/docs/brokers/alpaca/` created with 5 core docs
- [ ] Root README.md updated
- [ ] QUICK-START.md rewritten for Alpaca
- [ ] System architecture diagram updated
- [ ] API endpoint examples updated
- [ ] Environment variables documented
- [ ] Getting started guide updated
- [ ] All broken links fixed
- [ ] DOCUMENTATION-INDEX.md reflects new structure

---

## 🔄 Ongoing Maintenance

**After Migration:**

### Keep Updated
- `/docs/brokers/alpaca/` - Active development
- `/docs/architecture/` - System changes
- `/docs/guides/` - New features

### Archive Only
- `/docs/brokers/schwab/` - No updates (legacy reference only)

### Review Cadence
- **Weekly:** During Phase 4 (autonomous agent dev)
- **Monthly:** After Phase 4 complete
- **As Needed:** New features, API changes

---

## 📞 Support

**Questions about documentation structure?**
- See: `/docs/DOCUMENTATION-INDEX.md`
- Ask: Architecture team
- Update: This file as we learn

**Found outdated docs?**
- Create issue
- Update immediately
- Mark as 🚧 Draft until verified

---

**Next Action:** Execute Phase 1 (Archive Schwab docs) - 5 minutes

**See Also:**
- `/docs/implementation/alpaca-migration-plan.md` - Code migration
- `/docs/architecture/schwab-vs-alpaca-comparison.md` - Decision rationale
