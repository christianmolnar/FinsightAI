# FInsightAI Documentation Index

**Last Updated:** December 25, 2025  
**Current Broker:** Alpaca Markets

---

## 🚀 Quick Navigation

### For Active Development
- **[Alpaca Integration](/brokers/alpaca/)** - Current broker (start here)
- **[Quick Start](QUICK-START.md)** - Get started in 5 minutes
- **[Current System Architecture](architecture/CURRENT-SYSTEM-ARCHITECTURE.md)** - System overview

### For Reference
- **[Schwab Integration (Archived)](/brokers/schwab/)** - Legacy broker (deprecated)
- **[Documentation Organization](#-documentation-structure)** - How docs are organized

---

## 🏢 Broker Integrations (`/brokers`)

### **Alpaca Markets** - ✅ CURRENT ACTIVE BROKER
📁 **[/brokers/alpaca/](/brokers/alpaca/)**

Complete Alpaca integration documentation:
- **[alpaca-integration.md](/brokers/alpaca/architecture/alpaca-integration.md)** - Primary architecture
- **[alpaca-migration-status.md](/brokers/alpaca/implementation/alpaca-migration-status.md)** - Current status
- **[Implementation Plans](/brokers/alpaca/implementation/)** - Migration docs & progress

**Status:**
- ✅ Paper Trading: $100k virtual account operational
- ⏸️ Live Trading: Endpoint created, awaiting account approval

### **Charles Schwab** - ⚠️ DEPRECATED
📁 **[/brokers/schwab/](/brokers/schwab/)**

Archived Schwab integration (replaced by Alpaca):
- Historical architecture documentation
- OAuth troubleshooting guides
- Migration decision documentation

**Why Deprecated:** Complex OAuth, 7-day token refresh, limited paper trading

---

## 📁 Documentation Structure

### 📋 Specifications (`/specifications`)
Core system specifications and requirements

- **[TRADING-STRATEGY-SPECIFICATION.md](specifications/TRADING-STRATEGY-SPECIFICATION.md)** ⭐ **NEW**
  - Complete trading strategy documentation
  - All 4 strategies with detailed parameters
  - AI optimization specifications  
  - Entry/exit logic
  - Risk management rules
  - API & UI specifications

- [configuration-interface-spec.md](specifications/configuration-interface-spec.md)
- [dashboard-design-spec.md](specifications/dashboard-design-spec.md)

### 🏗️ Architecture (`/architecture`)
System design and technical architecture

- [trading-strategy-framework.md](architecture/trading-strategy-framework.md)
- [architecture.md](architecture/architecture.md)
- [backend.md](architecture/backend.md)
- [frontend.md](architecture/frontend.md)
- [database.md](architecture/database.md)
- [models.md](architecture/models.md)
- [ml.md](architecture/ml.md)

### 📊 Planning (`/planning`)
Project planning and roadmaps

- **[IMPLEMENTATION-TRACKING-PLAN.md](planning/IMPLEMENTATION-TRACKING-PLAN.md)** ⭐ **MASTER PLAN**
  - Complete 8-week implementation roadmap
  - All phases, tasks, and milestones
  - Progress tracking and success metrics
  - Sprint planning and daily tracking

- [configuration-interface-spec.md](planning/configuration-interface-spec.md)
- [dashboard-design-spec.md](planning/dashboard-design-spec.md)
- [strategic-direction-update.md](planning/strategic-direction-update.md)

### 🚀 Deployment (`/deployment`)
Deployment guides and status

- [AUTH-STATUS-DEC-22-2025.md](deployment/AUTH-STATUS-DEC-22-2025.md)
- [DEPLOYMENT-SUCCESS.md](deployment/DEPLOYMENT-SUCCESS.md)
- [RAILWAY-DEPLOYMENT-STATUS.md](deployment/RAILWAY-DEPLOYMENT-STATUS.md)
- [RAILWAY-DEPLOYMENT-FIX.md](deployment/RAILWAY-DEPLOYMENT-FIX.md)
- [RAILWAY-DATABASE-STATUS.md](deployment/RAILWAY-DATABASE-STATUS.md)
- [RAILWAY-POSTGRES-SETUP.md](deployment/RAILWAY-POSTGRES-SETUP.md)

### 📈 Status (`/status`)
Project status and progress tracking

- **[TRADING-INTELLIGENCE-STATUS.md](status/TRADING-INTELLIGENCE-STATUS.md)** ⭐ **NEW**
  - Complete intelligence implementation status
  - What's built vs what's missing
  - Current capabilities & roadmap

- [REAL-PRICES-ENABLED.md](status/REAL-PRICES-ENABLED.md)
- [PROJECT-STATUS.md](status/PROJECT-STATUS.md)
- [SYSTEM-STATUS.md](status/SYSTEM-STATUS.md)
- [WHERE-WE-ARE.md](status/WHERE-WE-ARE.md)
- [PHASE-1-COMPLETE.md](status/PHASE-1-COMPLETE.md)

### 📖 Reference (`/reference`)
Quick reference and guides

- **[TACO-TRADE-RESEARCH.md](reference/TACO-TRADE-RESEARCH.md)** 🔬 **NEW**
  - Analysis of "Trump Always Chickens Out" trade
  - Research findings and viability assessment
  - Recommendation: NOT suitable for implementation

- [SCHWAB-OAUTH-URL-FOR-SUPPORT.md](reference/SCHWAB-OAUTH-URL-FOR-SUPPORT.md)
- [QUICK-START.md](reference/QUICK-START.md)
- [START-HERE.md](reference/START-HERE.md)
- [journal.md](reference/journal.md)

### 📚 Guides (`/guides`)
How-to guides and tutorials

- [AGENTS.md](guides/AGENTS.md)
- [GCP-SETUP.md](guides/GCP-SETUP.md)
- [mockups.md](guides/mockups.md)

---

## 🎯 Key Documents for Current Work

### **Starting Development?**
→ Read [IMPLEMENTATION-TRACKING-PLAN.md](planning/IMPLEMENTATION-TRACKING-PLAN.md) ⭐ **START HERE**

### **Implementing Trading Strategies?**
→ Read [TRADING-STRATEGY-SPECIFICATION.md](specifications/TRADING-STRATEGY-SPECIFICATION.md)

### **Understanding Current Status?**
→ Read [TRADING-INTELLIGENCE-STATUS.md](status/TRADING-INTELLIGENCE-STATUS.md)

### **Deploying to Production?**
→ Read [DEPLOYMENT-SUCCESS.md](deployment/DEPLOYMENT-SUCCESS.md)

### **Researching New Strategies?**
→ Check [reference/](reference/) folder for research docs

---

## 🚀 Getting Started

**New to the project?** Start here:
1. Read [../README.md](../README.md) in root
2. Check [QUICK-START.md](reference/QUICK-START.md)
3. Review [TRADING-INTELLIGENCE-STATUS.md](status/TRADING-INTELLIGENCE-STATUS.md)
4. Read [TRADING-STRATEGY-SPECIFICATION.md](specifications/TRADING-STRATEGY-SPECIFICATION.md)

---

## 📞 Quick Links

- **Live Backend:** https://finsightai-production-442e.up.railway.app
- **Local Frontend:** http://localhost:3000
- **API Docs:** https://finsightai-production-442e.up.railway.app/docs
- **Database:** Railway PostgreSQL

---

**Maintained by:** FInsightAI Development Team
