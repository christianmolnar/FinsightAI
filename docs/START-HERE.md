# FInsightAI - Start Here

**Welcome to FInsightAI!** This is your AI-powered trading partner.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Understand What We Built
FInsightAI is an **autonomous trading system** that uses AI to find opportunities, analyze stocks, propose trades, and learn from results.

**Current Status:** Backtesting engine complete ✅ | Agent ready for Paper mode testing ⏳

### Step 2: Test Drive with Backtesting
**Before risking real money, validate strategies with historical data.**

1. **Start backend and frontend:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

2. **Navigate to Backtesting:**
   - Open browser: http://localhost:3000
   - Click "Backtesting" tab (purple)

3. **Run your first backtest:**
   - Click "90 Days" button
   - Wait 30-60 seconds
   - Review results:
     - ✅ Win Rate > 60%? Good sign!
     - ✅ Profit Factor > 2.0? Excellent!
     - ✅ Total Return positive? Strategy works!

4. **Optimize settings:**
   - Adjust AI Confidence Threshold slider (try 85%)
   - Select specific strategies (test one at a time)
   - Run again and compare results

**Full Tutorial:** [BACKTESTING-QUICKSTART.md](docs/implementation/BACKTESTING-QUICKSTART.md)

### Step 3: Review Documentation
- **[Documentation Index](docs/DOCUMENTATION-INDEX.md)** - Navigate all project docs
- **[Trading Strategy Spec](docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md)** - How strategies work
- **[User Experience Spec](docs/specifications/2025-12-23-USER-EXPERIENCE-SPEC.md)** - UI/UX design
- **[Development Log](docs/DEVELOPMENT-LOG.md)** - What's been built

---

## 🎯 What FInsightAI Does

### 1. Market Scanner (✅ Complete)
- Scans top 100 stocks by volume
- Detects 5 types of opportunities:
  - **Breakouts:** Stocks hitting 50-day highs
  - **Earnings:** Pre-earnings momentum plays
  - **Seasonality:** Historical monthly patterns
  - **Macro:** Economic catalyst beneficiaries
  - **Sentiment:** Social media trend analysis

### 2. AI Analyzer (✅ Complete)
- Analyzes each opportunity with OpenAI GPT-4
- Generates confidence scores (0-100%)
- Provides natural language reasoning
- Suggests entry/exit prices
- Identifies risks and catalysts

### 3. Backtesting Engine (✅ Complete - NEW!)
- Tests strategies on historical data (1-5 years)
- Simulates complete trading workflow
- Calculates performance metrics:
  - Win rate (% profitable trades)
  - Profit factor (wins / losses ratio)
  - Average hold time
  - Total return
- Quick presets: 30d, 90d, 1y
- Custom configuration: dates, capital, strategies, AI threshold
- **Use this to validate before live trading!**

### 4. Trade Proposals (🟡 In Progress)
- Creates actionable trade proposals
- User approves/rejects/modifies
- Stores in transaction queue
- Executes when conditions met

### 5. Learning Engine (📅 Planned)
- Analyzes every trade outcome
- Identifies winning patterns
- Proposes strategy improvements
- Gets smarter over time

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│  Dashboard | Research | Backtesting | Portfolio | Config    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                      REST API                               │
│  /api/backtest | /api/scanner | /api/analyzer | /api/trade │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICES                          │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scanner    │  │  Backtester  │  │  AI Analyzer │     │
│  │  (Live data) │  │ (Historical) │  │  (OpenAI)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Executor   │  │   Learning   │  │     Risk     │     │
│  │  (Schwab)    │  │   Engine     │  │  Management  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                             │
│  yfinance | Schwab | OpenAI | News APIs | Social Media     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Task Queue:** Background tasks
- **Data:** yfinance, Schwab API
- **AI:** OpenAI GPT-4

### Frontend
- **Framework:** React
- **Styling:** CSS + Ant Design
- **Charts:** Recharts
- **State:** React Hooks

### Infrastructure
- **Development:** Local (localhost:3000 frontend, localhost:8000 backend)
- **Production:** Railway (planned)
- **Monitoring:** Built-in logging

---

## 📈 Recommended Workflow

### For First-Time Setup
1. **Read specifications:**
   - [Trading Strategy Spec](docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md) (understand how it works)
   - [User Experience Spec](docs/specifications/2025-12-23-USER-EXPERIENCE-SPEC.md) (see what's coming)

2. **Run backtesting:**
   - Test different configurations
   - Identify optimal AI threshold
   - Document best-performing strategies

3. **Configure agent:**
   - Apply backtest learnings
   - Set position sizes
   - Enable Paper mode

4. **Monitor performance:**
   - Compare live results to backtests
   - Adjust if deviation exceeds 10%
   - Iterate monthly

### For Daily Use
1. Check backtesting results (weekly)
2. Review trade proposals (if agent enabled)
3. Approve/reject trades
4. Monitor open positions
5. Analyze closed trades

---

## 🎓 Learning Path

### Beginner (Day 1-7)
- ✅ Read this START-HERE.md
- ✅ Review [Trading Strategy Spec](docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md) sections 1-3
- ✅ Run 3 backtests (30d, 90d, 1y)
- ✅ Understand metrics: win rate, profit factor
- ✅ Read [Backtesting Quick Start](docs/implementation/BACKTESTING-QUICKSTART.md)

### Intermediate (Week 2-4)
- ✅ Deep dive into each trading strategy
- ✅ Test different AI confidence thresholds
- ✅ Compare strategy combinations
- ✅ Read [Full Backtesting Docs](docs/implementation/BACKTESTING-COMPLETE.md)
- ✅ Review [Development Log](docs/DEVELOPMENT-LOG.md)

### Advanced (Month 2+)
- ✅ Enable agent in Paper mode
- ✅ Monitor live vs backtest performance
- ✅ Propose strategy improvements
- ✅ Contribute to learning engine
- ✅ Analyze trade outcomes

---

## 🚦 Current Project Status

### ✅ Complete (Ready to Use)
- [x] Market Scanner with 5 strategies
- [x] AI Analyzer with OpenAI integration
- [x] Background job scheduler
- [x] Agent configuration API
- [x] **Backtesting engine with UI** ⭐
- [x] Comprehensive documentation (2,500+ lines)

### 🟡 In Progress
- [ ] TradeProposal model (Phase 6.1) - Next up
- [ ] Trade execution logic (Phase 7) - After proposals
- [ ] Risk management (Phase 8)

### 📅 Planned
- [ ] Monitoring & alerts (Phase 9)
- [ ] Learning engine (Phase 10)
- [ ] Database persistence for backtests
- [ ] Live agent enablement

### 🎯 Next Milestone
**Enable agent in Paper mode** (2 weeks estimated)
1. Build TradeProposal model - 30 min
2. Create proposal CRUD API - 30 min
3. Test Scanner → Analyzer → Proposals - 1 hour
4. Build auto-execution logic - 2 hours
5. Add risk management - 2 hours
6. Enable Paper mode trading - 30 min
7. Monitor and iterate - Ongoing

---

## 🔧 Development Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- OpenAI API key
- Schwab API credentials (for live trading)

### Installation
```bash
# Clone repository
git clone <repo-url>
cd f.insight.AI Advanced

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure API keys

# Database setup
createdb finsightai
python setup_db.py

# Frontend setup
cd ../frontend
npm install
```

### Running
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start

# Access at:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Backtesting endpoint tests
./test-backtest.sh

# Frontend tests
cd frontend
npm test
```

---

## 📚 Essential Documentation

### Must Read (Start Here)
1. **[This File (START-HERE.md)](docs/START-HERE.md)** - You are here! ✓
2. **[Backtesting Quick Start](docs/implementation/BACKTESTING-QUICKSTART.md)** - Test in 5 minutes
3. **[Documentation Index](docs/DOCUMENTATION-INDEX.md)** - Navigate all docs

### Core Specifications
4. **[Trading Strategy Spec](docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md)** - Complete strategy reference (1,623 lines)
5. **[User Experience Spec](docs/specifications/2025-12-23-USER-EXPERIENCE-SPEC.md)** - UI/UX design (750+ lines)

### Implementation Details
6. **[Backtesting Complete](docs/implementation/BACKTESTING-COMPLETE.md)** - Full technical docs (600+ lines)
7. **[Implementation Plan](docs/implementation/WHOLE-SITE-IMPLEMENTATION-PLAN.md)** - Detailed task breakdown
8. **[Development Log](docs/DEVELOPMENT-LOG.md)** - Chronological progress

---

## 🤝 Contributing

### Adding Features
1. Check [Implementation Plan](docs/implementation/WHOLE-SITE-IMPLEMENTATION-PLAN.md)
2. Create feature branch: `git checkout -b feature/name`
3. Build and test feature
4. Document in `/docs/implementation/`
5. Update specs if needed
6. Update [Documentation Index](docs/DOCUMENTATION-INDEX.md)
7. Submit PR with documentation

### Reporting Issues
- Use GitHub Issues
- Include: What you expected, what happened, steps to reproduce
- Attach screenshots if UI-related
- Include logs if backend-related

---

## 💡 Tips & Best Practices

### Backtesting
- ✅ **DO:** Run 90+ day backtests for statistical significance
- ✅ **DO:** Test multiple time periods (bull, bear, sideways)
- ✅ **DO:** Adjust one parameter at a time
- ❌ **DON'T:** Overfit to recent data
- ❌ **DON'T:** Assume historical = future performance

### Agent Configuration
- ✅ **DO:** Start with Paper mode
- ✅ **DO:** Monitor live vs backtest performance
- ✅ **DO:** Set position size limits (5-10% max)
- ❌ **DON'T:** Enable live trading without validation
- ❌ **DON'T:** Use high leverage

### Risk Management
- ✅ **DO:** Use stop losses
- ✅ **DO:** Diversify strategies
- ✅ **DO:** Review trades weekly
- ❌ **DON'T:** Risk more than 2% per trade
- ❌ **DON'T:** Ignore repeated losses

---

## 🆘 Getting Help

### Quick Links
- **Backtesting Issues:** [BACKTESTING-COMPLETE.md - Troubleshooting](docs/implementation/BACKTESTING-COMPLETE.md#troubleshooting)
- **API Reference:** http://localhost:8000/docs (when backend running)
- **All Documentation:** [DOCUMENTATION-INDEX.md](docs/DOCUMENTATION-INDEX.md)

### Common Questions
**Q: Backtest shows 0 trades?**  
A: Lower AI confidence threshold or enable more strategies.

**Q: How to apply backtest settings to agent?**  
A: Navigate to Agent Config tab → Set parameters → Save.

**Q: What's a good win rate?**  
A: 60%+ is good, 70%+ is excellent for this system.

**Q: When can I enable live trading?**  
A: After validating in Paper mode for 30+ days with good results.

---

## 🎯 Next Steps

### Right Now (5 minutes)
1. Run your first backtest (click "90 Days")
2. Review the results
3. Read [Backtesting Quick Start](docs/implementation/BACKTESTING-QUICKSTART.md)

### This Week
1. Test different AI confidence thresholds
2. Compare strategy combinations
3. Document optimal configuration
4. Review [Trading Strategy Spec](docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md)

### This Month
1. Help build TradeProposal system
2. Validate agent in Paper mode
3. Analyze first live trades
4. Contribute improvements

---

**Ready to get started?** Run your first backtest now! 🚀

**Questions?** Check the [Documentation Index](docs/DOCUMENTATION-INDEX.md) or review [Development Log](docs/DEVELOPMENT-LOG.md).

**Project Status:** Active Development | Backtesting Complete ✅ | Agent Ready for Paper Mode ⏳
