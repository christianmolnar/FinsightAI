# f.insight.AI Advanced - Documentation

**Last Updated**: March 7, 2026  
**Status**: Active Development

---

## 📊 Reports & Analysis
High-level analysis, research papers, and performance reports

- **[Backtest Performance Analysis (2026-03-07)](Reports/BACKTEST-PERFORMANCE-ANALYSIS-2026-03-07.md)** ⭐ NEW
  - Why the +329% strategy works so well
  - Analysis of proposed "fixes" - which help vs harm
  - Performance projections and recommendations
  
- **[Backtest Strategy Analysis (2026-03-07)](Reports/BACKTEST-STRATEGY-ANALYSIS-2026-03-07.md)** 
  - 6 critical issues identified in backtesting strategy
  - 4-phase implementation plan
  - Expected results after fixes
  
- [Rental Data Extraction Report](Reports/RENTAL-DATA-EXTRACTION-COMPLETE-ALL-24-PROPERTIES.md)

---

## 🚀 Quick Start

**New to this project?** Start here:
1. [START-HERE.md](START-HERE.md) - Project overview and quick start
2. [Setup Guide](setup/ALPACA-LIVE-TRADING-SETUP.md) - Get credentials and configure
3. [Implementation Status](implementation/README.md) - Current implementation state

---

## 🔧 Setup & Configuration
Getting started, credentials, and system setup

- [Alpaca Live Trading Setup Guide](setup/ALPACA-LIVE-TRADING-SETUP.md)
- [Alpaca Credentials README](setup/ALPACA-CREDENTIALS-README.md)
- [Configuration Setup Guide](setup/CONFIG-SETUP-GUIDE.md)
- [CNS Setup Complete](setup/CNS-SETUP-COMPLETE.md)

---

## 💻 Development
Development logs, status updates, and ongoing work

- **[Development Log](development/DEVELOPMENT-LOG.md)** - Ongoing development notes
- [Backend Fix Status](development/BACKEND-FIX-STATUS.md) - Backend issues and fixes
- [Frontend Portfolio Column](development/FRONTEND-PORTFOLIO-COLUMN.md) - UI enhancements
- [Next Steps](development/NEXT-STEPS.md) - Planned work
- [CNS Update (2025-12-23)](development/CNS-UPDATE-2025-12-23.md)
- [Documentation Update (2025-12-23)](development/DOCUMENTATION-UPDATE-2025-12-23.md)

---

## 📋 Implementation Tracking
Detailed implementation plans, phase tracking, and completed features

### Overview
- [Implementation README](implementation/README.md) - Implementation index

### Major Features
- [Backtesting Complete](implementation/BACKTESTING-COMPLETE.md)
- [Live Trading UI Complete](implementation/LIVE-TRADING-UI-COMPLETE.md)
- [Paper Trading Ready](implementation/PAPER-TRADING-READY.md)

### Backend Implementation
- [Position Sizing Enhancement](implementation/backend/POSITION-SIZING-ENHANCEMENT.md)
- [Backtest Portfolio Size Column](implementation/backend/BACKTEST-PORTFOLIO-SIZE-COLUMN.md)
- [Bugfix: Same-Day Position Sizing](implementation/backend/BUGFIX-SAME-DAY-POSITION-SIZING.md)

### Phase Tracking
- Phase 1-4 documents in [implementation/](implementation/) folder

---

## 🚢 Deployment
Deployment guides, Railway setup, and production configuration

- [Railway Deployment Status](deployment/RAILWAY-DEPLOYMENT-STATUS.md)
- [Railway Database Setup](deployment/RAILWAY-DATABASE-STATUS.md)
- [Deployment Success](deployment/DEPLOYMENT-SUCCESS.md)

---

## 📚 Reference
API documentation, guides, and technical reference

- [Documentation Index](DOCUMENTATION-INDEX.md) - Master documentation index
- [Agents Guide](reference/AGENTS.md) - AI agent system
- [Order Types Guide](ORDER_TYPES_GUIDE.md) - Trading order types
- [Taco Trade Research](reference/TACO-TRADE-RESEARCH.md)

---

## 📁 Documentation Structure

```
docs/
├── README.md                    ← You are here
├── Reports/                     ← Analysis & research papers
├── setup/                       ← Setup & configuration
├── development/                 ← Dev logs & status
├── implementation/              ← Feature implementation tracking
│   └── backend/                 ← Backend-specific docs
├── deployment/                  ← Deployment guides
├── reference/                   ← Technical reference
└── archive/                     ← Obsolete documents
```

---

## 🎯 Current Focus (March 2026)

### Completed
✅ Compounding position sizing implemented (+329% backtested returns)  
✅ Cash available display fixed  
✅ Performance analysis complete  
✅ Documentation consolidated and organized  

### Next Steps
- [ ] Test trailing stops implementation
- [ ] Audit database for survivorship bias
- [ ] Remove AI confidence randomness for production
- [ ] Deploy improvements to production

---

**For questions or updates, see**: [Development Log](development/DEVELOPMENT-LOG.md)
