# Backtest Calibration System - Specification

**Purpose:** Defines WHAT to build for backtest calibration and performance tracking  
**Status:** Phase 2 Complete, Phase 3 In Progress  
**For implementation details, see:** `/docs/implementation/BACKTEST-CALIBRATION-TRACKER.md`

---

## 🎯 User Requirements

### Core Functionality

1. **Backtest-Driven Recommendations**
   - Run 90-day backtest with current strategy config
   - AI analyzes results (win rate, Sharpe, drawdown, etc.)
   - Generate 5-10 specific parameter recommendations
   - Each recommendation includes:
     - Parameter name (e.g., "earnings.profitTarget")
     - Current value
     - Recommended value
     - AI reasoning (2-3 sentences explaining why)
     - Confidence score (0-100%)
     - Expected improvement estimate

2. **UI Parameter Coverage**
   - All recommendations must map to existing UI controls (sliders, inputs)
   - Coverage required:
     - Trading Strategies (4 strategies): profit targets, stop losses, position sizing
     - Risk Management (5 params): max position, drawdown limits, VIX threshold
     - Technical Filters (5 params): RSI ranges, volume, MA200 distance
   - **Total: 20 configurable parameters**

3. **Apply/Reject Workflow**
   - User reviews recommendations in modal
   - Individual apply/reject per recommendation
   - "Apply All" / "Reject All" buttons
   - Show before/after config comparison
   - Track which recommendations were applied

4. **Performance History Tracking** (Phase 4)
   - Store 1-year history of backtest reports
   - Timeline chart showing portfolio value + config change markers
   - Before/after metrics for each config change
   - Attribution: "This change improved returns by X%"
   - Paper vs Live comparison

---

## 🏗️ System Components

### 1. Calibration Engine (Backend)
**Purpose:** Analyze backtest results, generate recommendations

**Inputs:**
- BacktestMetrics (trades, returns, Sharpe, drawdown, etc.)
- Current strategy configuration (JSON)
- Trade list with entry/exit details

**Outputs:**
- Array of recommendations with AI reasoning
- Confidence scores
- Expected improvements

**AI Integration:**
- OpenAI GPT-4o-mini for reasoning generation
- Anthropic Claude-3-haiku as fallback
- Statistical analysis as final fallback

### 2. Calibration Modal (Frontend)
**Purpose:** Display recommendations, handle user acceptance

**Features:**
- Backtest summary metrics display
- List of recommendations with reasoning
- Apply/Reject buttons per recommendation
- Before/after config preview
- "Apply All" bulk action
- Success/error feedback

### 3. Database Persistence
**Purpose:** Store backtest reports and recommendations

**Schema:**
- backtest_reports table (25+ columns)
- JSON config snapshots (before/after)
- JSON recommendations array
- Applied tracking (flag + parameters)
- 1-year auto-expiration

### 4. Performance Dashboard (Phase 4)
**Purpose:** Visualize config changes over time

**Features:**
- Timeline chart (portfolio value + markers)
- Config change history table
- Before/after comparison for each change
- Paper vs Live performance comparison
- Attribution analysis

---

## 📊 Data Flow

```
User runs backtest
    ↓
Backtester generates metrics + trades
    ↓
User clicks "Calibrate from Backtest"
    ↓
CalibrationEngine analyzes results
    ↓
AI generates reasoning for recommendations
    ↓
Recommendations displayed in CalibrationModal
    ↓
User applies selected recommendations
    ↓
Strategic Config updated
    ↓
Changes saved to database
    ↓
User can re-run backtest with new config
```

---

## 🎯 Success Criteria

### Phase 2: Calibration Engine (Complete ✅)
- [x] CalibrationEngine service generates recommendations
- [x] AI reasoning integration working
- [x] 20 parameters with validation
- [x] Database persistence functional
- [x] All tests passing

### Phase 3: Frontend UI (In Progress)
- [ ] "AI Optimize" button removed
- [ ] "Calibrate from Backtest" button added
- [ ] CalibrationModal component created
- [ ] Recommendations displayed with reasoning
- [ ] Apply/Reject functionality working
- [ ] Config updates persisted

### Phase 4: Performance Dashboard (Planned)
- [ ] Timeline chart with config markers
- [ ] Config change history table
- [ ] Before/after comparison
- [ ] Paper vs Live comparison
- [ ] 1-year data retention working

---

## 🔧 Technical Constraints

1. **Parameter Coverage:** Must cover all 20 UI-configurable parameters
2. **AI Cost:** Keep per-backtest cost under $0.01
3. **Response Time:** Calibration analysis < 5 seconds
4. **Database:** 1-year retention, auto-expire older reports
5. **UI Mapping:** Every recommendation must map to existing UI control

---

## 📝 User Stories

**As a trader, I want to:**
1. Run a backtest and get data-driven suggestions for improving my strategy
2. Understand WHY each suggestion is being made (AI reasoning)
3. Choose which suggestions to apply (individual accept/reject)
4. See how my config changes affect performance over time
5. Compare Paper vs Live performance to identify execution issues

---

## 🚫 Out of Scope

- Automated parameter optimization (Phase 4.6 - separate feature)
- Real-time strategy adjustment
- Multi-strategy backtesting
- Walk-forward analysis
- Monte Carlo simulations (already exists)

---

**This is a SPECIFICATION document. For implementation details, progress tracking, and task breakdowns, see `/docs/implementation/BACKTEST-CALIBRATION-TRACKER.md`**
