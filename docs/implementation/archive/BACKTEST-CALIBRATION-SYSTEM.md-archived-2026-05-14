# Backtest Calibration & Performance Tracking System
**Implementation Plan for Strategy Optimization & Historical Analysis**

**Created:** March 2, 2026  
**Status:** 🔲 Planning  
**Priority:** HIGH  
**Estimated Time:** 12-15 hours  

---

## 📋 Overview

**Goal:** Build a comprehensive system that:
1. **Runs backtests** with current strategy configurations
2. **Generates data-driven recommendations** for all configurable parameters
3. **Tracks performance over time** with every configuration change
4. **Visualizes trends** showing how config changes affected portfolio performance
5. **Compares Paper vs Live** performance to identify execution issues
6. **Retains 1-year history** of all backtest reports and config snapshots

---

## 🎯 User Requirements

### **From User Questions:**

1. **"Are all these recommendations things I can change with sliders?"**
   - YES - Recommendations must map to existing UI controls
   - Coverage: Trading Strategies (4), Risk Management (6), Technical Filters (6)
   - Total: ~35 configurable parameters

2. **"Generate recommendations and give me choice to change settings"**
   - Show before/after comparison
   - Individual approve/reject per recommendation
   - One-click "Apply All" option

3. **"What is the function of AI Optimize?"**
   - REMOVE standalone "AI Optimize" button
   - AI becomes PART of backtest analysis (interprets results, explains reasoning)
   - Backtest-driven recommendations replace generic AI suggestions

4. **"Track every strategy change for last year with performance graphs"**
   - Timeline showing portfolio value + config change markers
   - Before/after metrics for each config period
   - Paper vs Live comparison
   - Attribution: "This change improved returns by X%"

---

## 🏗️ System Architecture

### **Components:**

```
┌─────────────────────────────────────────────────────────────┐
│                    STRATEGY CONFIG UI                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  [Calibrate from Backtest] Button                      │ │
│  │  (Replaces "AI Optimize")                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              BACKTEST CALIBRATION ENGINE                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  1. Capture current config snapshot                    │ │
│  │  2. Run enhanced 90-day backtest                       │ │
│  │  3. Analyze results (win rate, returns, drawdown)      │ │
│  │  4. Generate recommendations (AI-assisted)             │ │
│  │  5. Save report to database (1-year retention)         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CALIBRATION MODAL                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  📊 Current Performance:                               │ │
│  │  • Win Rate: 58.5%                                     │ │
│  │  • Return: +8.63% (90 days)                            │ │
│  │  • Max Drawdown: -5.2%                                 │ │
│  │  ──────────────────────────────────────────────────────│ │
│  │  ✅ Recommended Changes:                               │ │
│  │                                                         │ │
│  │  Earnings Strategy - Profit Target                     │ │
│  │  12% → 14% [Reject] [Apply]                            │ │
│  │  Reason: Avg winning trade was +15%, leaving money     │ │
│  │          on table. AI confidence: 85%                  │ │
│  │  ──────────────────────────────────────────────────────│ │
│  │  Risk Management - Max Single Position                 │ │
│  │  5% → 6% [Reject] [Apply]                              │ │
│  │  Reason: 58.5% win rate supports larger sizing         │ │
│  │  ──────────────────────────────────────────────────────│ │
│  │  [Apply All] [Reject All] [View Full Report]          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓ (User applies changes)
┌─────────────────────────────────────────────────────────────┐
│           CONFIG CHANGE TRACKING                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Timestamp of change                                 │ │
│  │  • Before/after snapshot of all parameters             │ │
│  │  • Which backtest report triggered the change          │ │
│  │  • Which recommendations were applied/rejected         │ │
│  │  • User notes (optional)                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│       PERFORMANCE TRACKING DASHBOARD (NEW TAB)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  📈 Portfolio Performance Timeline (Last Year)         │ │
│  │  ┌───────────────────────────────────────────────────┐│ │
│  │  │                                                    ││ │
│  │  │   $120K ●━━━━━━━━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━●  ││ │
│  │  │         ↑                   ↑                   ↑   ││ │
│  │  │      Config #1          Config #2          Config #3││ │
│  │  │    Dec 2025: +8.2%    Jan 2026: +10.5%   Feb: +12% ││ │
│  │  │   (Increased profit   (Tightened stop   (Raised AI ││ │
│  │  │     target to 14%)      loss to 4.5%)   threshold) ││ │
│  │  └───────────────────────────────────────────────────┘│ │
│  │                                                         │ │
│  │  ⚖️ Paper vs Live Comparison                           │ │
│  │  ┌────────────────────┬────────────────────┐          │ │
│  │  │ Paper Trading      │ Live Trading       │          │ │
│  │  ├────────────────────┼────────────────────┤          │ │
│  │  │ Return: +12.3%     │ Return: +9.8%      │          │ │
│  │  │ Win Rate: 60.2%    │ Win Rate: 56.5%    │          │ │
│  │  │ Drawdown: -4.1%    │ Drawdown: -6.3%    │          │ │
│  │  │ Avg Slippage: $0.02│ Avg Slippage: $0.15│          │ │
│  │  └────────────────────┴────────────────────┘          │ │
│  │  ⚠️ Analysis: Live underperforming by 2.5%             │ │
│  │     Likely due to slippage on momentum trades          │ │
│  │                                                         │ │
│  │  📊 Configuration Change History                       │ │
│  │  ┌───────────────────────────────────────────────────┐│ │
│  │  │ Date       │ Changes         │ Impact   │ Applied ││ │
│  │  ├───────────────────────────────────────────────────┤│ │
│  │  │ Feb 15 '26│ Profit Target   │ +1.8%    │ ✅      ││ │
│  │  │            │ 12% → 14%       │          │         ││ │
│  │  │ Jan 28 '26│ Stop Loss       │ -0.5%    │ ✅      ││ │
│  │  │            │ 5% → 4.5%       │ (reduced │         ││ │
│  │  │            │                 │ drawdown)│         ││ │
│  │  │ Jan 10 '26│ AI Threshold    │ +2.1%    │ ✅      ││ │
│  │  │            │ 75% → 85%       │          │         ││ │
│  │  └───────────────────────────────────────────────────┘│ │
│  │  [Export Report] [Compare Configs] [View Backtest]    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### **1. backtest_reports Table**
Stores every backtest run with full results

```sql
CREATE TABLE backtest_reports (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default',
    run_date TIMESTAMP DEFAULT NOW(),
    
    -- Configuration snapshot at time of backtest
    config_snapshot JSONB NOT NULL,  -- All strategy/risk/filter settings
    
    -- Backtest parameters
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(15, 2) DEFAULT 100000.00,
    
    -- Overall performance metrics
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),  -- 58.5% = 58.50
    total_return DECIMAL(8, 4),  -- 8.63% = 8.6300
    final_portfolio_value DECIMAL(15, 2),
    max_drawdown DECIMAL(8, 4),  -- Calculated during backtest
    sharpe_ratio DECIMAL(6, 3),  -- Risk-adjusted return
    profit_factor DECIMAL(6, 3),  -- Total wins / Total losses
    
    -- Trade statistics
    avg_win_size DECIMAL(10, 2),
    avg_loss_size DECIMAL(10, 2),
    largest_win DECIMAL(10, 2),
    largest_loss DECIMAL(10, 2),
    avg_hold_days DECIMAL(6, 2),
    
    -- Strategy breakdown (JSON array)
    strategy_performance JSONB,  -- Per-strategy metrics
    /*
    Example:
    [
        {
            "strategy": "technical_breakout",
            "trades": 345,
            "win_rate": 62.1,
            "return": 5.2,
            "profit_factor": 2.1
        },
        {
            "strategy": "earnings_play",
            "trades": 289,
            "win_rate": 55.3,
            "return": 3.4,
            "profit_factor": 1.8
        }
    ]
    */
    
    -- Daily P&L for drawdown calculation
    daily_pnl JSONB,  -- {"2025-12-01": 234.50, "2025-12-02": -123.00, ...}
    
    -- Generated recommendations
    recommendations JSONB,  -- AI-generated parameter adjustments
    /*
    Example:
    [
        {
            "parameter": "earnings.profitTarget",
            "current_value": 12,
            "recommended_value": 14,
            "reasoning": "Average winning trade was +15%, leaving money on table",
            "confidence": 0.85,
            "expected_improvement": "+1.2% annual return",
            "category": "strategy"
        },
        {
            "parameter": "riskManagement.maxSinglePosition",
            "current_value": 5,
            "recommended_value": 6,
            "reasoning": "58.5% win rate supports larger position sizing",
            "confidence": 0.78,
            "expected_improvement": "+0.8% annual return",
            "category": "risk"
        }
    ]
    */
    
    -- User interaction
    applied BOOLEAN DEFAULT FALSE,  -- Did user apply any recommendations?
    applied_recommendations JSONB,  -- Which ones were applied
    user_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 year'),
    
    CONSTRAINT valid_win_rate CHECK (win_rate >= 0 AND win_rate <= 100)
);

CREATE INDEX idx_backtest_reports_user_date ON backtest_reports(user_id, run_date DESC);
CREATE INDEX idx_backtest_reports_expiration ON backtest_reports(expires_at);
```

### **2. config_changes Table**
Tracks every time user changes strategy configuration

```sql
CREATE TABLE config_changes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default',
    change_date TIMESTAMP DEFAULT NOW(),
    
    -- Configuration snapshots
    before_config JSONB NOT NULL,  -- Full config before change
    after_config JSONB NOT NULL,   -- Full config after change
    changed_parameters JSONB,      -- Just the diffs
    /*
    Example:
    [
        {
            "parameter": "earnings.profitTarget",
            "before": 12,
            "after": 14,
            "change_type": "manual" | "backtest_calibration"
        }
    ]
    */
    
    -- What triggered this change?
    trigger_type VARCHAR(50),  -- 'manual', 'backtest_calibration', 'ai_optimize'
    backtest_report_id INTEGER REFERENCES backtest_reports(id),  -- If from calibration
    
    -- Performance tracking (calculated later)
    performance_before JSONB,  -- Metrics from period before this config
    performance_after JSONB,   -- Metrics from period after this config
    /*
    Calculated after sufficient time has passed (30-90 days)
    {
        "before": {
            "period_days": 90,
            "return": 8.6,
            "win_rate": 58.5,
            "drawdown": 5.2
        },
        "after": {
            "period_days": 90,
            "return": 10.3,
            "win_rate": 61.2,
            "drawdown": 4.1
        },
        "improvement": {
            "return_delta": +1.7,
            "win_rate_delta": +2.7,
            "drawdown_delta": -1.1
        }
    }
    */
    
    -- User notes
    user_notes TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_config_changes_user_date ON config_changes(user_id, change_date DESC);
CREATE INDEX idx_config_changes_backtest ON config_changes(backtest_report_id);
```

### **3. portfolio_snapshots Table**
Daily portfolio snapshots for performance tracking

```sql
CREATE TABLE portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default',
    account_type VARCHAR(20) NOT NULL,  -- 'paper' or 'live'
    snapshot_date DATE NOT NULL,
    
    -- Portfolio metrics
    portfolio_value DECIMAL(15, 2),
    cash_balance DECIMAL(15, 2),
    positions_value DECIMAL(15, 2),
    
    -- Daily performance
    daily_return DECIMAL(8, 4),  -- % return for this day
    daily_pnl DECIMAL(10, 2),    -- $ P&L for this day
    
    -- Position count
    open_positions INTEGER DEFAULT 0,
    
    -- Link to current config
    config_change_id INTEGER REFERENCES config_changes(id),  -- Most recent config
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, account_type, snapshot_date)
);

CREATE INDEX idx_portfolio_snapshots_user_account_date 
    ON portfolio_snapshots(user_id, account_type, snapshot_date DESC);
```

---

## 🔧 Implementation Tasks

### **Phase 1: Database & Backend Core (3-4 hours)**

#### **Task 1.1: Create Database Tables**
- [ ] Create migration for `backtest_reports` table
- [ ] Create migration for `config_changes` table
- [ ] Create migration for `portfolio_snapshots` table
- [ ] Test migrations on dev database

**Files:**
- `/backend/alembic/versions/YYYY_MM_DD_backtest_calibration_tables.py`

#### **Task 1.2: Create Pydantic Models**
- [ ] `BacktestReport` model with all metrics
- [ ] `ConfigChange` model with before/after snapshots
- [ ] `PortfolioSnapshot` model for daily tracking
- [ ] `CalibrationRecommendation` model

**Files:**
- `/backend/app/models/backtest.py`
- `/backend/app/models/config_tracking.py`

#### **Task 1.3: Enhance Backtester with Detailed Metrics**
- [ ] Track daily P&L for drawdown calculation
- [ ] Calculate Sharpe ratio
- [ ] Calculate profit factor
- [ ] Break down performance by strategy
- [ ] Calculate average win/loss sizes
- [ ] Track hold time statistics

**Files:**
- `/backend/services/backtester.py` (enhance existing)

---

### **Phase 2: Calibration Engine** ✅ **COMPLETE** (2.5 hours actual)

**Status:** ✅ Production ready  
**Completion Date:** March 5, 2026  
**Time:** 2.5 hours (estimate: 4-5 hours, 50% ahead)

#### **Task 2.1: Build Recommendation Generator** ✅
- [x] Analyze backtest results
- [x] Use AI to interpret metrics and generate reasoning
- [x] Map recommendations to existing UI parameters
- [x] Calculate expected improvements
- [x] Generate confidence scores

**Files:**
- ✅ `/backend/services/calibration_engine.py` (702 lines)

**Delivered:**
- 4 analysis methods (profit targets, stop losses, position sizing, technical filters)
- AI integration (OpenAI + Anthropic with fallback)
- 20 parameters with validation
- Full CRUD database operations
- 4 comprehensive test scripts (all passing)

**Key Functions:**
```python
class CalibrationEngine:
    def generate_recommendations(
        self, 
        backtest_results: BacktestMetrics,
        current_config: Dict
    ) -> List[Recommendation]:
        """
        Analyze backtest results and generate parameter recommendations
        
        Returns list of recommendations with:
        - parameter path (e.g., "earnings.profitTarget")
        - current value
        - recommended value
        - reasoning (AI-generated)
        - confidence score
        - expected improvement
        """
        pass
    
    def calculate_position_sizing(
        self, 
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """Kelly Criterion for position sizing"""
        pass
    
    def optimize_profit_target(
        self,
        winning_trades: List[Trade]
    ) -> float:
        """Analyze winning trades to find optimal exit point"""
        pass
```

#### **Task 2.2: Create Calibration API Endpoint**
- [ ] POST `/api/v1/backtest/calibrate` - Run backtest & generate recommendations
- [ ] GET `/api/v1/backtest/reports` - List historical reports
- [ ] GET `/api/v1/backtest/reports/{id}` - Get specific report
- [ ] POST `/api/v1/config/apply-recommendations` - Apply changes & track

**Files:**
- `/backend/api/calibration.py` (NEW - 200 lines)

---

### **Phase 3: Frontend Calibration UI (3-4 hours)**

#### **Task 3.1: Remove "AI Optimize" Button**
- [ ] Remove `handleAIOptimization` function
- [ ] Remove AI optimize button from StrategyConfig.js
- [ ] Remove fallback hardcoded recommendations

**Files:**
- `/frontend/src/components/StrategyConfig.js` (lines 122-199 DELETE)

#### **Task 3.2: Add "Calibrate from Backtest" Button**
- [ ] Add button to Strategy Config header
- [ ] Implement `handleBacktestCalibration` function
- [ ] Show loading state during backtest
- [ ] Handle errors gracefully

**Files:**
- `/frontend/src/components/StrategyConfig.js` (modify)

#### **Task 3.3: Build Calibration Modal Component**
- [ ] Show current performance metrics
- [ ] Display recommendations with reasoning
- [ ] Individual approve/reject buttons per recommendation
- [ ] "Apply All" / "Reject All" buttons
- [ ] "View Full Report" link
- [ ] Apply changes to strategy state & save to backend

**Files:**
- `/frontend/src/components/CalibrationModal.js` (NEW - 400 lines)

**Component Structure:**
```jsx
<CalibrationModal
  visible={showCalibration}
  currentConfig={currentConfig}
  backtestResults={backtestResults}
  recommendations={recommendations}
  onApply={(appliedChanges) => {
    // Update strategy sliders
    // Save config change to backend
    // Close modal
  }}
  onReject={() => setShowCalibration(false)}
  onViewReport={() => navigate(`/backtest/reports/${reportId}`)}
/>
```

#### **Task 3.4: Remove Backtesting Sub-Tab**
- [ ] Remove "Backtesting" button from sidebar (line ~340)
- [ ] Remove backtest panel JSX (lines 490-510)
- [ ] Update `activePanel` state to only include: strategies, risk, technical

**Files:**
- `/frontend/src/components/StrategyConfig.js` (modify)

---

### **Phase 4: Performance Tracking Dashboard (4-5 hours)**

#### **Task 4.1: Create Performance Dashboard Component**
- [ ] New top-level tab in App.js
- [ ] Timeline chart showing portfolio value + config change markers
- [ ] Paper vs Live comparison cards
- [ ] Config change history table
- [ ] Attribution analysis (impact of each change)

**Files:**
- `/frontend/src/components/PerformanceDashboard.js` (NEW - 600 lines)

#### **Task 4.2: Build Portfolio Timeline Chart**
- [ ] Use Chart.js or Recharts
- [ ] Plot portfolio value over time (daily snapshots)
- [ ] Add vertical markers for config changes
- [ ] Tooltips showing config details on hover
- [ ] Color-code performance periods (green = improving, red = declining)

**Component:**
```jsx
<PortfolioTimeline
  snapshots={portfolioSnapshots}  // Daily values
  configChanges={configChanges}   // Config change markers
  dateRange="1y"  // 1 month, 3 months, 6 months, 1 year
  accountType="paper"  // or "live" or "both"
/>
```

#### **Task 4.3: Build Config Change History Table**
- [ ] Table showing all config changes
- [ ] Before/after values for changed parameters
- [ ] Performance impact (calculated after sufficient time)
- [ ] Attribution: "This change improved returns by X%"
- [ ] Drill-down to view backtest report

**Component:**
```jsx
<ConfigChangeHistory
  changes={configChanges}
  onViewBacktest={(reportId) => navigate(`/backtest/reports/${reportId}`)}
  onCompareConfigs={(changeId1, changeId2) => showComparison()}
/>
```

#### **Task 4.4: Build Paper vs Live Comparison**
- [ ] Side-by-side metrics cards
- [ ] Return, Win Rate, Drawdown, Slippage
- [ ] Highlight differences (red if live underperforming)
- [ ] AI analysis of differences
- [ ] Drill-down to trade-level comparison

**Component:**
```jsx
<PaperVsLiveComparison
  paperMetrics={paperPerformance}
  liveMetrics={livePerformance}
  period="90d"
/>
```

#### **Task 4.5: Add Portfolio Snapshot Capture (Background Job)**
- [ ] Daily cron job to capture portfolio snapshots
- [ ] Store in `portfolio_snapshots` table
- [ ] Calculate daily return and P&L
- [ ] Link to current config_change_id

**Files:**
- `/backend/jobs/snapshot_portfolios.py` (NEW - 150 lines)
- Add to Railway cron jobs or use APScheduler

---

### **Phase 5: Performance Attribution & Analysis (2-3 hours)**

#### **Task 5.1: Calculate Performance Impact of Config Changes**
- [ ] Background job runs weekly
- [ ] For each config change > 30 days old:
  - Calculate metrics for 90 days before change
  - Calculate metrics for 90 days after change
  - Compute deltas (return improvement, win rate improvement)
  - Update `config_changes.performance_before/after`

**Files:**
- `/backend/jobs/calculate_config_impact.py` (NEW - 200 lines)

#### **Task 5.2: Build AI Analysis of Differences**
- [ ] Compare Paper vs Live performance
- [ ] Identify root causes (slippage, execution timing, different fills)
- [ ] Generate actionable insights
- [ ] Display in Performance Dashboard

**Files:**
- `/backend/services/performance_analyzer.py` (NEW - 250 lines)

---

## 🎯 Acceptance Criteria

### **Minimum Viable Product (MVP):**

✅ **User can:**
1. Click "Calibrate from Backtest" button in Strategy Config
2. See loading indicator while backtest runs (~12 seconds)
3. View calibration modal with:
   - Current performance metrics
   - List of recommendations with reasoning
   - Individual approve/reject buttons
4. Apply recommendations → sliders update automatically
5. View saved backtest reports (list of past calibrations)

✅ **System automatically:**
1. Saves every backtest report to database (1-year retention)
2. Tracks every config change with before/after snapshots
3. Captures daily portfolio snapshots (paper & live)
4. Calculates performance impact of config changes (after 30+ days)

✅ **Performance Dashboard shows:**
1. Timeline chart with portfolio value + config change markers
2. Paper vs Live comparison with key metrics
3. Config change history table with performance impact
4. Export functionality for reports

---

## 📊 Success Metrics

**Quantitative:**
- ✅ Backtest calibration completes in <15 seconds
- ✅ All recommendations map to existing UI sliders (100% coverage)
- ✅ 1-year data retention working (auto-delete after 365 days)
- ✅ Performance Dashboard loads in <2 seconds
- ✅ Zero data loss (all backtest reports and config changes persisted)

**Qualitative:**
- ✅ User can see clear before/after comparison for config changes
- ✅ AI reasoning is understandable and actionable
- ✅ Performance attribution answers "Did my changes help or hurt?"
- ✅ Paper vs Live comparison helps identify execution issues

---

## 🗓️ Timeline Estimate

| Phase | Tasks | Estimated Time | Dependencies |
|-------|-------|----------------|--------------|
| **Phase 1** | Database & Backend Core | 3-4 hours | None |
| **Phase 2** | Calibration Engine | 4-5 hours | Phase 1 |
| **Phase 3** | Frontend Calibration UI | 3-4 hours | Phase 2 |
| **Phase 4** | Performance Dashboard | 4-5 hours | Phase 1 |
| **Phase 5** | Attribution & Analysis | 2-3 hours | Phase 4 |

**Total: 16-21 hours** (2-3 days of focused work)

---

## 📝 Testing Plan

### **Unit Tests:**
- [ ] CalibrationEngine.generate_recommendations()
- [ ] CalibrationEngine.calculate_position_sizing()
- [ ] CalibrationEngine.optimize_profit_target()
- [ ] Backtester calculates max_drawdown correctly
- [ ] Backtester calculates Sharpe ratio correctly

### **Integration Tests:**
- [ ] POST /api/v1/backtest/calibrate returns valid recommendations
- [ ] Config changes tracked in database correctly
- [ ] Portfolio snapshots captured daily
- [ ] Performance impact calculated after 30 days

### **E2E Tests:**
- [ ] Click "Calibrate from Backtest" → Modal appears with recommendations
- [ ] Apply recommendations → Sliders update, config saved
- [ ] View Performance Dashboard → Timeline shows config changes
- [ ] Compare Paper vs Live → Shows accurate metrics

---

## 🚀 Deployment Notes

### **Database Migrations:**
```bash
cd backend
alembic revision -m "Add backtest calibration tables"
alembic upgrade head
```

### **Environment Variables:**
None required (uses existing database connection)

### **Background Jobs:**
Add to Railway or use APScheduler:
1. **Daily snapshot job** (runs at midnight UTC)
2. **Weekly attribution job** (runs Sunday at 1am UTC)

---

## 📚 Related Documentation

- **Master Plan:** `/docs/implementation/WHOLE-SITE-IMPLEMENTATION-PLAN.md`
- **Backtester Guide:** `/docs/implementation/BACKTESTING-COMPLETE.md`
- **Historical Data System:** `/docs/implementation/HISTORICAL-DATA-SYSTEM-GUIDE.md`
- **Strategy Config Spec:** `/docs/specifications/2025-12-23-TRADING-STRATEGY-SPECIFICATION.md`

---

## 🔄 Future Enhancements

### **PHASE 4.6: Automated Optimization Loop** 🆕
**Priority:** HIGH (User Requested)  
**Estimated Time:** 8-10 hours

**Goal:** Build an automated iterative optimizer that finds optimal parameter settings through AI-guided backtest loops.

#### **Features:**

1. **Looping Optimizer Engine**
   - Starts with reasonable default parameter positions
   - Runs 1-year backtest with current config
   - AI analyzes results and tunes each parameter
   - Measures improvement vs previous iteration
   - Repeats until convergence or diminishing returns
   - Stops when optimal results achieved

2. **Convergence Detection**
   - Target Sharpe ratio reached (e.g., > 2.0)
   - Improvement < 0.5% for 2 consecutive iterations
   - 3 consecutive declines in performance
   - Maximum iterations reached (safety limit: 20)

3. **Top 10 Config Library**
   - Stores best 10 configurations found during optimization
   - Each with full metrics and AI reasoning
   - Ranked by risk-adjusted returns (Sharpe ratio)
   - One-click load any config for live/paper trading

4. **Final Optimization Report**
   - Complete iteration history with metrics
   - Parameter evolution graphs
   - AI analysis of why final config is optimal
   - Strengths and limitations identified
   - Overfitting warnings and recommendations
   - Paper trading readiness assessment

5. **Database Schema Addition**
   ```sql
   CREATE TABLE optimization_runs (
       id SERIAL PRIMARY KEY,
       user_id VARCHAR(50) DEFAULT 'default',
       start_time TIMESTAMP DEFAULT NOW(),
       end_time TIMESTAMP,
       
       -- Configuration
       initial_config JSONB NOT NULL,
       backtest_period_days INTEGER DEFAULT 365,
       max_iterations INTEGER DEFAULT 20,
       
       -- Results
       total_iterations INTEGER,
       convergence_reason VARCHAR(100),
       best_iteration INTEGER,
       best_config JSONB,
       best_metrics JSONB,
       
       -- Top configs
       top_10_configs JSONB,  -- Array of configs with metrics
       
       -- AI analysis
       ai_report TEXT,
       strengths JSONB,
       limitations JSONB,
       recommendations TEXT,
       
       -- Metadata
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

#### **Implementation Files:**
- `/backend/services/automated_optimizer.py` - Main loop logic
- `/backend/app/api/v1/optimization.py` - API endpoints
- `/frontend/src/components/OptimizationRunner.js` - UI for starting/monitoring runs
- `/frontend/src/components/OptimizationReport.js` - Results display

#### **API Endpoints:**
- `POST /api/v1/optimization/start` - Start optimization run
- `GET /api/v1/optimization/{run_id}/status` - Get progress
- `GET /api/v1/optimization/{run_id}/report` - Get final report
- `POST /api/v1/optimization/load-config` - Load config from library

---

### **Time Series Reporting Enhancements** 🆕
**Already Included in Phase 4 (Performance Dashboard)**

The current plan ALREADY includes these user-requested features:

1. **Calibration Improvement Over Time**
   - ✅ `backtest_reports` table stores all calibration runs (1-year retention)
   - ✅ Timeline chart showing parameter evolution
   - ✅ Win rate and return trends graphed
   - ✅ Each config change linked to backtest that triggered it

2. **Real Life vs Backtest Comparison**
   - ✅ `portfolio_snapshots` table tracks Paper AND Live accounts daily
   - ✅ Performance Dashboard shows Paper vs Live side-by-side
   - ✅ AI analyzes gaps (slippage, execution delays, etc.)
   - ✅ Attribution: "This config change improved live returns by X%"

3. **Data Retention Strategy**
   - ✅ NOT storing individual trades (too much data)
   - ✅ Storing daily P&L summaries (enough for graphing)
   - ✅ Storing aggregate metrics (win rate, returns, Sharpe)
   - ✅ 1-year auto-expiration on old backtest reports

**No additional work needed** - Phases 2-4 deliver these features!

---

### **Post-MVP Ideas:**

1. **A/B Testing Framework**
   - Run multiple backtests with different configs in parallel
   - Compare results side-by-side
   - Recommend optimal config

2. **Live Performance Alerts**
   - "Your live account is underperforming paper by 5% - investigate"
   - "Config change from Feb 15 showing +2.1% improvement - keep it!"
   - "Slippage on TSLA trades is 3x higher than other symbols"

3. **Config Rollback**
   - One-click rollback to previous config
   - Compare current vs previous performance
   - A/B test between configs

4. **Multi-User Support**
   - Share backtest reports with other users
   - Compare your performance vs community average
   - Learn from top-performing configs

---

**Ready to implement? Let me know which phase to start with!**
