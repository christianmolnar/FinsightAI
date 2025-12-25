# ⚠️ ARCHIVED: Schwab Integration Documentation

**Status:** 🗄️ **ARCHIVED - LEGACY REFERENCE ONLY**  
**Deprecated:** December 25, 2025  
**Reason:** Migrated to Alpaca API  

---

## Migration Notice

**FInsightAI has migrated from Schwab to Alpaca.**

This directory contains **archived documentation** for the original Schwab API integration. This code and documentation are **no longer maintained** and are kept for historical reference only.

---

## 📚 Archived Documentation

This directory contains:
- Original Schwab API integration specifications
- OAuth 2.0 authentication documentation
- Schwab-specific setup guides
- Historical architecture decisions

**These docs are OUTDATED and should not be used for current development.**

---

## ✅ Current Documentation

For **current, active documentation**, see:
- `/docs/brokers/alpaca/` - Active Alpaca integration
- `/docs/architecture/schwab-vs-alpaca-comparison.md` - Migration decision
- `/docs/implementation/alpaca-migration-plan.md` - Migration details
- `/docs/QUICK-START.md` - Current setup guide (Alpaca)

---

## 🔍 Why Did We Migrate?

**Short Answer:** Better API, permanent auth tokens, no ties to Schwab account.

**Details:**
- Schwab required OAuth re-authentication every 7 days
- Only had $300 test account (never traded)
- Alpaca offers permanent API keys
- Better developer experience
- Simpler codebase

See `/docs/architecture/schwab-vs-alpaca-comparison.md` for full analysis.

---

## 📖 Historical Context

**Schwab Integration Timeline:**
- **Created:** [Original implementation date]
- **Active:** [Date range]
- **Deprecated:** December 25, 2025
- **Removed:** [After migration complete]

**What Was Built:**
- OAuth 2.0 authentication flow
- Token refresh automation
- Portfolio position tracking
- Order placement API
- Real-time quote integration

**Why It Was Deprecated:**
- 7-day token expiration (production limitation)
- Account opened only for API access (no real usage)
- Better alternative available (Alpaca)
- Autonomous agent needs permanent auth

---

## ⚠️ DO NOT USE

**This documentation is for historical reference only.**

If you're looking for current setup instructions:
1. Go to `/docs/QUICK-START.md`
2. See `/docs/brokers/alpaca/` for current integration
3. Join the migration: See `/docs/DOCUMENTATION-MIGRATION-PLAN.md`

---

**Archived:** December 25, 2025  
**Maintainer:** None (archive only)  
**Questions:** See current documentation in `/docs/brokers/alpaca/`
