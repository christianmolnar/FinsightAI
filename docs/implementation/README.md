# Implementation Documentation

**Last Updated:** December 25, 2025

## Primary Implementation Plan

### [WHOLE-SITE-IMPLEMENTATION-PLAN.md](WHOLE-SITE-IMPLEMENTATION-PLAN.md) ⭐ **START HERE**

**Purpose:** Master roadmap for f.insight.AI v1.0

**Contents:**
- Complete 8-phase development plan
- Infrastructure → AI Features → Autonomous Trading
- Time estimates (real-time hours with AI assistance)
- Completion criteria for each phase
- Current status and next steps

**Current Phase:** Phase 1 - AI Research Engine (NEXT)

**Progress:** ~40% (Infrastructure + Broker migration complete)

---

## Broker-Specific Implementation

### Alpaca Integration (Current Broker)

📁 **Location:** `/docs/brokers/alpaca/implementation/`

**Key Documents:**
- [alpaca-migration-status.md](../brokers/alpaca/implementation/alpaca-migration-status.md) - Migration progress (COMPLETE)
- [2025-12-25-alpaca-paper-live-separation.md](../brokers/alpaca/implementation/2025-12-25-alpaca-paper-live-separation.md) - Paper/live separation

**Status:** ✅ Complete - Alpaca is now the active broker

**Migration Summary:**
- Backend: AlpacaService with paper/live endpoints
- Frontend: Both portfolio tabs working
- Paper trading: $100k operational
- Live trading: Endpoint ready, awaiting account approval

---

## How to Use This Documentation

### For Overall Project Planning
→ Read **WHOLE-SITE-IMPLEMENTATION-PLAN.md**

### For Broker Integration Details
→ See `/docs/brokers/alpaca/implementation/alpaca-migration-status.md`

### For Alpaca Architecture
→ See `/docs/brokers/alpaca/architecture/alpaca-integration.md`

### For Starting Next Phase
→ Begin with Phase 1 in **WHOLE-SITE-IMPLEMENTATION-PLAN.md**

---

## Document Standards

### File Naming
- **Master plans:** `WHOLE-SITE-*` or `MASTER-*`
- **Status tracking:** `*-status.md`
- **Date-specific work:** `YYYY-MM-DD-feature-name.md`

### Location Rules
- **Site-wide plans:** `/docs/implementation/`
- **Broker-specific:** `/docs/brokers/<broker>/implementation/`
- **Architecture:** `/docs/architecture/` or `/docs/brokers/<broker>/architecture/`

---

**Quick Navigation:**
- [Main Plan](WHOLE-SITE-IMPLEMENTATION-PLAN.md) ← Start here
- [Alpaca Status](../brokers/alpaca/implementation/alpaca-migration-status.md)
- [Alpaca Architecture](../brokers/alpaca/architecture/alpaca-integration.md)
- [Root Docs](../README.md)
