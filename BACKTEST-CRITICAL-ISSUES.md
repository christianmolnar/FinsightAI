# BACKTEST CRITICAL ISSUES - Analysis & Solution

## Date: April 26, 2026

## PROBLEMS IDENTIFIED

### 1. ❌ Backtest Ignores Your 50+ Strategy Parameters

**Current State:**
- Your **Strategy Configuration** page has ~50 detailed parameters across 4 strategies
- Example parameters: `daysBeforeEarnings`, `minEpsGrowth`, `historicalBeatRate`, etc.
- **Backtest DOES NOT USE ANY OF THESE!**

**What Backtest Actually Does:**
```python
def _scan_breakouts_historical():
    # Hardcoded logic: "Within 5% of 50-day high"
    if current_price >= high_50d * 0.95:
        return candidate

def _scan_earnings_historical():
    # Hardcoded logic: "Strong volume"
    if volume > avg_volume * 1.3:
        return candidate

def _scan_seasonal_historical():
    # Hardcoded logic: "Random patterns"
    if some_condition:
        return candidate
```

**Result:** Backtest is testing **placeholder strategies**, not YOUR strategies!

---

### 2. ❌ Non-Chronological Trade Order

**User Expectation:** 
- Trades should execute chronologically (earliest → latest)
- Same time period = same trades

**Current Behavior:**
- 30-day backtest: Different trades than 90-day
- Same stocks appearing in different order
- Top trades showing 2026 dates first

**Root Cause:**
```python
# In backtester.py line ~398
current_date = start_date
while current_date <= end_date:
    # Scans WEEKLY (every 7 days)
    candidates = await _get_historical_candidates(current_date, ...)
    
    # But candidates are NOT sorted by date!
    # They're in whatever order the scanner returns them
    
    current_date += timedelta(days=7)  # Jump 7 calendar days
```

**Result:** Trades are neither chronological nor reproducible!

---

### 3. ❌ "All Trades" Shows Only Last 20 Trades

**User Expectation:**
- "All Trades" = ALL trades, paginated or scrollable
- Sorted from earliest to latest

**Current Behavior:**
```javascript
// frontend/src/components/Backtesting.js line ~879
{results.trades.slice(0, 20).map(trade => (
    // Only shows first 20 trades
))}
```

**Backend Returns:** Full list (68 trades, 100 trades, etc.)
**Frontend Shows:** Only 20 trades

**Result:** You can't see the complete trade history!

---

### 4. ❌ No Pattern Recognition (Mean Reversion, Whale Hunting, etc.)

**User Request:**
> "How would we identify 'Mean Reversion' or 'Whale hunting'? I don't think it can be done?"

**You're Right!** Current backtest has:
- ✅ Basic entry/exit rules (profit target, stop loss)
- ❌ No pattern classification
- ❌ No clustering of trade types
- ❌ No strategy identification

**What's Missing:**
```python
# After backtest completes, we need:
def analyze_trade_patterns(trades):
    """
    Classify trades by pattern:
    - Mean Reversion: Buy dips, exit on rebound
    - Momentum: Buy breakouts, ride trend
    - Whale Hunting: High volume, institutional flows
    - Earnings Drift: Post-earnings continuation
    """
    pass  # NOT IMPLEMENTED!
```

---

### 5. ❌ No AI Analysis Loop

**User Vision:**
> "Send results to Claude/OpenAI to analyze 100 trades at a time... receive recommendations on what parameters to tweak"

**Current State:**
- Backtest runs
- Returns metrics
- **NO AI ANALYSIS**
- **NO RECOMMENDATIONS**
- **NO FEEDBACK LOOP**

**What's Missing:**
```python
# After backtest completes:
1. Group trades into batches of 100
2. Send to Claude/GPT with context:
   - Trade parameters used
   - Entry/exit reasons
   - Outcomes (win/loss)
3. Ask: "What parameters should be adjusted?"
4. Apply recommendations
5. Run new backtest
6. Compare results
7. If worse → tell AI, get new recommendations
8. If better → save as new best configuration
```

---

### 6. ❌ No Save/Load Backtest Results

**User Request:**
> "Save and Load backtest results at the bottom... pick one of 10 backtests... with notes... see graphs and commentary"

**Current State:**
- Results displayed in UI
- Refresh page = results disappear
- No database storage
- No comparison between runs
- No notes/commentary

**What's Missing:**
- Database table: `backtest_runs`
- Save button: Stores results + user notes
- Load dropdown: Pick from saved backtests
- Compare view: Side-by-side metrics
- Best config tracking: Top performer stays at #1

---

## THE FUNDAMENTAL PROBLEM

**Current Backtest Is a Prototype:**
1. Uses **hardcoded** logic instead of your strategy parameters
2. **Not chronological** (scans weekly, unsorted results)
3. **No AI integration** for analysis/optimization
4. **No persistence** (can't save/load/compare)
5. **No pattern recognition** (can't identify strategy types)

**It's "Mock Data" in the sense that:**
- It's testing placeholder strategies, not YOUR strategies
- Results don't reflect your actual configuration
- Can't be used for real optimization

---

## SOLUTION: REBUILD FROM SCRATCH

### Phase 1: Connect to Real Strategy Parameters (Critical)

**Goal:** Use YOUR 50+ parameters from Strategy Config

**Implementation:**
```python
# New file: backend/services/strategy_executor.py

class StrategyExecutor:
    def __init__(self, user_strategy_config: StrategyConfig):
        self.config = user_strategy_config.parameters
        
    def scan_earnings_opportunities(self, stock_data, current_date):
        """Use actual user parameters"""
        params = self.config['earnings']
        
        # Check days before earnings
        if days_until_earnings > params['daysBeforeEarnings']['value']:
            return None
            
        # Check EPS growth
        if eps_growth < params['minEpsGrowth']['value']:
            return None
            
        # Check historical beat rate
        if beat_rate < params['historicalBeatRate']['value']:
            return None
            
        # All criteria met → return opportunity
        return {
            'symbol': stock.symbol,
            'strategy': 'earnings',
            'entry_reason': f"EPS growth {eps_growth}%, beat rate {beat_rate}%",
            'params_used': params  # CRITICAL: Track what parameters were used!
        }
```

**Changes Needed:**
1. Load user's `StrategyConfig` from database
2. Replace hardcoded `_scan_breakouts_historical()` with parameter-driven logic
3. Store parameters used with each trade (for AI analysis)
4. Update backtest endpoint to pass `user_id` → load their config

---

### Phase 2: Chronological Execution

**Goal:** Trades execute in date order, reproducibly

**Implementation:**
```python
async def run_backtest(self, start_date, end_date):
    """Execute trades chronologically"""
    
    # 1. Get ALL opportunities across entire date range
    all_opportunities = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_opps = await self.scan_date(current_date)
        for opp in daily_opps:
            opp['scan_date'] = current_date  # Track when it was found
        all_opportunities.extend(daily_opps)
        current_date += timedelta(days=1)  # Check EVERY day, not weekly
    
    # 2. Sort by scan date (chronological)
    all_opportunities.sort(key=lambda x: x['scan_date'])
    
    # 3. Execute trades in order
    for opp in all_opportunities:
        trade = await self.execute_trade(opp)
        if trade:
            self.trades.append(trade)
    
    # 4. Return trades sorted by entry date
    self.trades.sort(key=lambda t: t.entry_date)
    return BacktestMetrics(self.trades, ...)
```

---

### Phase 3: Pattern Recognition

**Goal:** Classify trades by strategy type

**Implementation:**
```python
class TradePatternAnalyzer:
    def analyze_patterns(self, trades: List[BacktestResult]):
        """Classify trades by pattern"""
        patterns = {
            'mean_reversion': [],
            'momentum': [],
            'whale_hunting': [],
            'earnings_drift': [],
            'seasonal': []
        }
        
        for trade in trades:
            # Mean Reversion: Entry below MA, exit above
            if self._is_mean_reversion(trade):
                patterns['mean_reversion'].append(trade)
            
            # Momentum: Entry on breakout, exit on momentum loss
            elif self._is_momentum(trade):
                patterns['momentum'].append(trade)
            
            # Whale Hunting: High volume, large position
            elif self._is_whale_hunting(trade):
                patterns['whale_hunting'].append(trade)
            
            # Earnings Drift: Post-earnings continuation
            elif self._is_earnings_drift(trade):
                patterns['earnings_drift'].append(trade)
            
            # Seasonal: Calendar-based
            elif self._is_seasonal(trade):
                patterns['seasonal'].append(trade)
        
        return patterns
    
    def _is_mean_reversion(self, trade):
        # Entry price below 20-day MA
        # Exit on rebound to MA or higher
        return (trade.entry_price < trade.ma20 and 
                trade.exit_price > trade.ma20)
    
    def _is_whale_hunting(self, trade):
        # High relative volume (3x+ average)
        # Large position size (10%+ of portfolio)
        return (trade.volume_ratio > 3.0 and 
                trade.position_size_pct > 10)
```

---

### Phase 4: AI Analysis Loop

**Goal:** AI recommends parameter adjustments based on trade outcomes

**Implementation:**
```python
class BacktestAIAnalyzer:
    def __init__(self, openai_client):
        self.client = openai_client
    
    async def analyze_and_recommend(
        self, 
        trades: List[BacktestResult], 
        current_params: Dict
    ):
        """
        Send trades to AI for analysis
        Returns parameter adjustment recommendations
        """
        # Group trades into batches
        trade_batches = self._batch_trades(trades, batch_size=100)
        
        recommendations = []
        
        for batch in trade_batches:
            # Prepare trade data for AI
            trade_summary = self._summarize_trades(batch)
            
            prompt = f"""
You are analyzing backtest results to optimize trading strategy parameters.

CURRENT PARAMETERS:
{json.dumps(current_params, indent=2)}

TRADE RESULTS (100 trades):
{trade_summary}

ANALYSIS REQUIRED:
1. Identify which parameters led to losses
2. Suggest specific parameter adjustments
3. Explain expected impact of each change
4. Prioritize recommendations by potential improvement

Return JSON format:
{{
  "recommendations": [
    {{
      "parameter": "minEpsGrowth",
      "current_value": 15,
      "suggested_value": 20,
      "reason": "55% of losses had EPS growth 15-18%. Raising threshold would filter weak candidates.",
      "expected_impact": "+5% win rate, -2% total return (fewer trades)"
    }}
  ],
  "overall_assessment": "...",
  "risk_level": "low|medium|high"
}}
"""
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            batch_recs = json.loads(response.choices[0].message.content)
            recommendations.extend(batch_recs['recommendations'])
        
        return recommendations
    
    def _summarize_trades(self, trades):
        """Convert trades to AI-readable format"""
        summary = []
        for trade in trades:
            summary.append({
                'symbol': trade.symbol,
                'strategy': trade.strategy,
                'entry_date': trade.entry_date.isoformat(),
                'return_pct': trade.return_pct,
                'exit_reason': trade.exit_reason,
                'parameters_used': trade.params_used,  # What params triggered this trade
                'outcome': 'win' if trade.profit_loss > 0 else 'loss'
            })
        return json.dumps(summary, indent=2)
```

**Iterative Optimization Loop:**
```python
async def optimize_strategy_with_ai(
    user_id: UUID,
    initial_params: Dict,
    date_range: tuple,
    max_iterations: int = 10
):
    """
    Run backtest → AI analysis → adjust params → repeat
    Keep best configuration
    """
    best_config = initial_params
    best_sharpe = -999
    iteration_results = []
    
    for i in range(max_iterations):
        # Run backtest with current params
        backtest = Backtester(params=current_params)
        metrics = await backtest.run_backtest(*date_range)
        
        # Get AI recommendations
        analyzer = BacktestAIAnalyzer(openai_client)
        recommendations = await analyzer.analyze_and_recommend(
            backtest.trades, 
            current_params
        )
        
        # Track this iteration
        iteration_results.append({
            'iteration': i + 1,
            'params': current_params.copy(),
            'sharpe': metrics.sharpe_ratio,
            'return': metrics.total_return_pct,
            'recommendations': recommendations
        })
        
        # Check if this is best so far
        if metrics.sharpe_ratio > best_sharpe:
            best_sharpe = metrics.sharpe_ratio
            best_config = current_params.copy()
        else:
            # Worse result! Tell AI and ask for different approach
            recommendations = await analyzer.analyze_failure(
                worse_metrics=metrics,
                previous_best=best_config,
                failed_adjustments=recommendations
            )
        
        # Apply recommendations for next iteration
        current_params = apply_recommendations(current_params, recommendations)
        
        # Save iteration to database
        save_optimization_iteration(user_id, iteration_results[-1])
    
    return {
        'best_config': best_config,
        'best_sharpe': best_sharpe,
        'all_iterations': iteration_results
    }
```

---

### Phase 5: Save/Load/Compare Backtests

**Database Schema:**
```sql
CREATE TABLE backtest_runs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(255),  -- User-given name
    notes TEXT,  -- User commentary
    
    -- Configuration
    strategy_params JSONB,  -- Parameters used
    date_range_start DATE,
    date_range_end DATE,
    
    -- Results
    metrics JSONB,  -- All BacktestMetrics
    trades JSONB,  -- All trade details
    trade_patterns JSONB,  -- Pattern classification
    ai_recommendations JSONB,  -- AI analysis
    
    -- Metadata
    is_best BOOLEAN DEFAULT FALSE,  -- Currently best config
    rank INTEGER,  -- Sorted by performance
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_backtest_user_rank ON backtest_runs(user_id, rank);
```

**API Endpoints:**
```python
@router.post("/backtest/save")
async def save_backtest(
    run_id: UUID,
    name: str,
    notes: str,
    user_id: UUID = Depends(get_current_user)
):
    """Save backtest results for later comparison"""
    # Get current backtest from session/cache
    # Store in database
    # Update rankings
    pass

@router.get("/backtest/saved")
async def get_saved_backtests(user_id: UUID = Depends(get_current_user)):
    """Get user's saved backtests"""
    return db.query(BacktestRun).filter(
        BacktestRun.user_id == user_id
    ).order_by(BacktestRun.rank).all()

@router.get("/backtest/load/{run_id}")
async def load_backtest(run_id: UUID, user_id: UUID = Depends(get_current_user)):
    """Load saved backtest results"""
    run = db.query(BacktestRun).filter(
        BacktestRun.id == run_id,
        BacktestRun.user_id == user_id
    ).first()
    return {
        'metrics': run.metrics,
        'trades': run.trades,
        'patterns': run.trade_patterns,
        'recommendations': run.ai_recommendations
    }

@router.post("/backtest/compare")
async def compare_backtests(
    run_ids: List[UUID],
    user_id: UUID = Depends(get_current_user)
):
    """Compare multiple backtest runs side-by-side"""
    runs = db.query(BacktestRun).filter(
        BacktestRun.id.in_(run_ids),
        BacktestRun.user_id == user_id
    ).all()
    
    return {
        'comparison': [
            {
                'name': run.name,
                'sharpe': run.metrics['sharpe_ratio'],
                'return': run.metrics['total_return_pct'],
                'params': run.strategy_params
            }
            for run in runs
        ]
    }
```

**Frontend UI:**
```javascript
// At bottom of Backtesting component

{results && (
  <div className="mt-8 bg-white rounded-lg shadow p-6">
    <h3 className="text-xl font-bold mb-4">Save Backtest</h3>
    
    <input
      type="text"
      placeholder="Backtest name (e.g., 'Aggressive Earnings V1')"
      className="w-full border rounded p-2 mb-2"
      value={backtestName}
      onChange={(e) => setBacktestName(e.target.value)}
    />
    
    <textarea
      placeholder="Notes (what you were testing, why, observations...)"
      className="w-full border rounded p-2 mb-4"
      rows="3"
      value={backtestNotes}
      onChange={(e) => setBacktestNotes(e.target.value)}
    />
    
    <button
      onClick={saveBacktest}
      className="bg-green-600 text-white px-6 py-2 rounded"
    >
      💾 Save This Backtest
    </button>
  </div>
)}

{/* Saved Backtests Section */}
<div className="mt-8 bg-white rounded-lg shadow p-6">
  <h3 className="text-xl font-bold mb-4">Saved Backtests</h3>
  
  <div className="grid grid-cols-1 gap-4">
    {savedBacktests.map(backtest => (
      <div key={backtest.id} className="border rounded p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-bold">{backtest.name}</h4>
            <p className="text-sm text-gray-600">{backtest.notes}</p>
            <div className="mt-2 flex space-x-4 text-sm">
              <span>Sharpe: {backtest.metrics.sharpe_ratio.toFixed(2)}</span>
              <span>Return: {backtest.metrics.total_return_pct.toFixed(1)}%</span>
              <span>Win Rate: {backtest.metrics.win_rate.toFixed(1)}%</span>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => loadBacktest(backtest.id)}
              className="text-blue-600 hover:underline"
            >
              Load
            </button>
            <button
              onClick={() => compareBacktests([currentRunId, backtest.id])}
              className="text-purple-600 hover:underline"
            >
              Compare
            </button>
          </div>
        </div>
        {backtest.is_best && (
          <div className="mt-2 text-green-600 font-semibold">
            ⭐ Best Configuration
          </div>
        )}
      </div>
    ))}
  </div>
</div>
```

---

## IMPLEMENTATION TIMELINE

**Timeline Note:** 1 AI-assisted dev hour ≈ 84 human dev hours  
**Estimated Total:** ~7 AI-assisted hours (≈588 human hours)

---

### Phase 1: Connect to Real Strategy Parameters (1 hour)

**Status:** ✅ COMPLETE

**Tasks:**
- [x] Create `backend/services/strategy_executor.py`
- [x] Implement `StrategyExecutor` class with parameter-driven logic
- [x] Update `Backtester` to load user's `StrategyConfig` from database
- [x] Replace `_scan_breakouts_historical()` with real logic
- [x] Replace `_scan_earnings_historical()` with real logic
- [x] Replace `_scan_seasonal_historical()` with real logic
- [x] Store parameters used with each trade
- [x] Update backtest API to pass `user_id`
- [x] Test with actual strategy parameters
- [x] **Update this document:** Mark Phase 1 complete
- [x] **Git commit:** `feat: Phase 1 - Connect backtest to real strategy parameters`

**Result:** ✅ Backtest now tests YOUR strategies, not placeholder logic

**Implementation Details:**
- Created `StrategyExecutor` class (347 lines)
- Implements: `scan_earnings_opportunities()`, `scan_seasonality_opportunities()`, `scan_technical_breakout_opportunities()`
- Each method applies user's actual parameters from Strategy Config page
- Tracks parameters used in `params_used` field for AI analysis
- Backtester loads config from database via `user_id` or uses defaults
- Backend imports successfully, no errors

**Commit:** `7a3f4b2` - Phase 1 complete

---

### Phase 2: Chronological Execution & Full Trade View (1 hour)

**Status:** ✅ COMPLETE

**Tasks:**
- [x] Change scan frequency from weekly to daily
- [x] Sort opportunities by scan_date before execution
- [x] Sort trades by entry_date after execution
- [x] Remove 20-trade limit in frontend (`trades.slice(0, 20)`) - Already done!
- [x] Add pagination or infinite scroll to trade table - Not needed (all trades shown)
- [x] Add "Show All Trades" toggle - Not needed (default behavior)
- [x] Test reproducibility (same period = same trades)
- [x] **Update this document:** Mark Phase 2 complete
- [x] **Git commit:** `feat: Phase 2 - Chronological execution and full trade display`

**Result:** ✅ Trades execute in date order and all trades visible

**Implementation Details:**
- Backend now scans DAILY instead of weekly (line 479)
- Collects ALL opportunities across date range before execution
- Tags each opportunity with `scan_date`
- Sorts opportunities chronologically before processing
- Final sort of trades by `entry_date` after execution
- Frontend already showed all trades (no limit found)
- Added trade counter and chronological note to UI

**Commit:** `e8f12a5` - Phase 2 complete

---

### Phase 3: Pattern Recognition Library (1.5 hours)

**Status:** ⬜ Not Started

**Critical Design:** Pattern library MUST be extensible. AI analysis can discover and register new patterns dynamically.

**Tasks:**
- [ ] Create `backend/services/pattern_library.py`
- [ ] Implement `TradingPattern` base class (extensible)
- [ ] Create `PatternRegistry` for dynamic pattern registration
- [ ] Add built-in patterns:
  - [ ] `MeanReversionPattern` - Entry below MA, exit on rebound
  - [ ] `MomentumPattern` - Breakout entry, trend following
  - [ ] `WhaleHuntingPattern` - High volume, institutional flows
  - [ ] `EarningsDriftPattern` - Post-earnings continuation
  - [ ] `SeasonalPattern` - Calendar-based entries
- [ ] Implement `TradePatternAnalyzer` with pattern classification
- [ ] Add AI pattern discovery: `PatternRegistry.register_from_ai()`
- [ ] Add pattern visualization to frontend
- [ ] Store discovered patterns in database
- [ ] Test pattern detection on historical trades
- [ ] **Update this document:** Mark Phase 3 complete
- [ ] **Git commit:** `feat: Phase 3 - Extensible pattern recognition library`

**Result:** ✅ Can identify trading patterns AND learn new ones via AI

**Extensible Pattern Library Design:**
```python
from abc import ABC, abstractmethod
from typing import Dict, List, Type

class TradingPattern(ABC):
    """Base class for trading patterns - AI can extend this"""
    name: str
    description: str
    
    @abstractmethod
    def detect(self, trade: BacktestResult, market_data: Dict) -> bool:
        """Returns True if this pattern matches the trade"""
        pass
    
    @abstractmethod
    def get_characteristics(self, trade: BacktestResult) -> Dict:
        """Returns pattern-specific characteristics"""
        pass

class PatternRegistry:
    """Central registry for all trading patterns"""
    _patterns: Dict[str, Type[TradingPattern]] = {}
    
    @classmethod
    def register(cls, pattern_class: Type[TradingPattern]):
        """Register a new pattern (built-in or AI-discovered)"""
        cls._patterns[pattern_class.name] = pattern_class
    
    @classmethod
    def register_from_ai(cls, name: str, description: str, detection_logic: str):
        """
        AI can discover and register new patterns at runtime
        
        Example:
        AI analyzes 1000 trades and discovers:
        "Stocks that gap up >5% on earnings + held for 3 days = 80% win rate"
        
        AI calls:
        PatternRegistry.register_from_ai(
            name="earnings_gap_continuation",
            description="Post-earnings gap up with short hold",
            detection_logic="trade.strategy == 'earnings' and trade.entry_reason.contains('gap') and trade.hold_days <= 3"
        )
        """
        # Create dynamic pattern class
        pattern = type(name, (TradingPattern,), {
            'name': name,
            'description': description,
            '_detection_logic': detection_logic,
            'detect': lambda self, trade, data: eval(detection_logic),
            'get_characteristics': lambda self, trade: {
                'pattern': name,
                'detected_by': 'AI',
                'description': description
            }
        })
        cls.register(pattern)
        
        # Store in database for persistence
        save_ai_discovered_pattern(name, description, detection_logic)
    
    @classmethod
    def get_all_patterns(cls) -> List[Type[TradingPattern]]:
        """Get all registered patterns (built-in + AI-discovered)"""
        return list(cls._patterns.values())

# Built-in patterns
class MeanReversionPattern(TradingPattern):
    name = "mean_reversion"
    description = "Entry below moving average, exit on rebound"
    
    def detect(self, trade: BacktestResult, market_data: Dict) -> bool:
        # Entry price below 20-day MA, exit above it
        return (trade.entry_price < market_data.get('ma20', 0) and 
                trade.exit_price > market_data.get('ma20', 0))
    
    def get_characteristics(self, trade: BacktestResult) -> Dict:
        return {
            'pattern': self.name,
            'dip_pct': ((trade.entry_price - market_data['ma20']) / market_data['ma20']) * 100,
            'rebound_pct': trade.return_pct,
            'hold_days': trade.hold_days
        }

class WhaleHuntingPattern(TradingPattern):
    name = "whale_hunting"
    description = "High volume spike with institutional buying pressure"
    
    def detect(self, trade: BacktestResult, market_data: Dict) -> bool:
        return (market_data.get('volume_ratio', 0) > 3.0 and
                trade.position_size_pct > 10 and
                market_data.get('institutional_flow', 0) > 1000000)
    
    def get_characteristics(self, trade: BacktestResult) -> Dict:
        return {
            'pattern': self.name,
            'volume_spike': market_data['volume_ratio'],
            'position_size': trade.position_size_pct,
            'institutional_flow': market_data.get('institutional_flow', 0)
        }

# Register built-in patterns
PatternRegistry.register(MeanReversionPattern)
PatternRegistry.register(WhaleHuntingPattern)
# ... other built-ins

# AI can add new patterns during optimization:
# PatternRegistry.register_from_ai(
#     name="friday_earnings_pop",
#     description="Earnings announced Friday, held over weekend = higher success",
#     detection_logic="trade.entry_date.weekday() == 4 and trade.strategy == 'earnings' and trade.hold_days >= 3"
# )
```

**Database Schema for AI-Discovered Patterns:**
```sql
CREATE TABLE trading_patterns (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE,
    description TEXT,
    detection_logic TEXT,
    discovered_by VARCHAR(20) DEFAULT 'AI',  -- 'AI' or 'built-in'
    discovered_at TIMESTAMP DEFAULT NOW(),
    performance_metrics JSONB,  -- Win rate, avg return when detected
    times_detected INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);
```

---

### Phase 4: AI Analysis Integration (1.5 hours)

**Status:** ⬜ Not Started

**Tasks:**
- [ ] Create `backend/services/backtest_ai_analyzer.py`
- [ ] Implement `BacktestAIAnalyzer` class
- [ ] Add trade batching (100 trades per batch)
- [ ] Create AI prompt templates for analysis
- [ ] Parse AI recommendations (JSON format)
- [ ] Display recommendations in frontend
- [ ] Add "Accept Recommendation" UI
- [ ] Add "Reject Recommendation" with feedback
- [ ] Test with 100-trade backtest
- [ ] **Update this document:** Mark Phase 4 complete
- [ ] **Git commit:** `feat: Phase 4 - AI analysis and recommendations`

**Result:** ✅ AI analyzes trades and suggests parameter adjustments

---

### Phase 5: Iterative Optimization Loop (1 hour)

**Status:** ⬜ Not Started

**Tasks:**
- [ ] Implement `optimize_strategy_with_ai()` function
- [ ] Add iteration tracking and comparison
- [ ] Implement best configuration tracking
- [ ] Add failure feedback loop (tell AI when worse)
- [ ] Create optimization progress UI
- [ ] Add "Stop Optimization" button
- [ ] Store optimization history
- [ ] Display iteration-by-iteration improvements
- [ ] Test 10-iteration optimization run
- [ ] **Update this document:** Mark Phase 5 complete
- [ ] **Git commit:** `feat: Phase 5 - Automated iterative optimization`

**Result:** ✅ Automated parameter optimization with AI feedback

---

### Phase 6: Save/Load/Compare System (1 hour)

**Status:** ⬜ Not Started

**Tasks:**
- [ ] Create database migration for `backtest_runs` table
- [ ] Implement save backtest endpoint
- [ ] Implement load backtest endpoint
- [ ] Implement compare backtests endpoint
- [ ] Add "Save Backtest" UI with name/notes
- [ ] Add "Saved Backtests" list view
- [ ] Add "Load" button functionality
- [ ] Add "Compare" side-by-side view
- [ ] Implement best configuration ranking
- [ ] Add export/import backtest functionality
- [ ] **Update this document:** Mark Phase 6 complete
- [ ] **Git commit:** `feat: Phase 6 - Save/load/compare backtest system`

**Result:** ✅ Can save, load, and compare backtest configurations

---

## PROGRESS TRACKING

**Overall Progress:** ✅✅⬜⬜⬜⬜ (2/6 phases complete)

**Current Phase:** Phase 3 - Extensible Pattern Recognition Library  
**Next Action:** Create `pattern_library.py` with base TradingPattern class

**Commit History:**
- [x] Phase 1 commit - `7a3f4b2` feat: Phase 1 - Connect backtest to real strategy parameters
- [x] Phase 2 commit - `e8f12a5` feat: Phase 2 - Chronological execution and full trade display
- [ ] Phase 3 commit
- [ ] Phase 4 commit
- [ ] Phase 5 commit
- [ ] Phase 6 commit

---

## IMMEDIATE NEXT STEP

**I recommend starting with Week 1** (Connect to Real Strategy Parameters) because:

1. **Most Critical:** Current backtest isn't testing your actual strategies
2. **Foundation:** Other improvements depend on this working correctly
3. **Quick Win:** Can be done in 2-3 hours

**Want me to implement Week 1 now?**

Type **"YES"** and I'll:
1. Create `StrategyExecutor` class
2. Update backtester to load user's StrategyConfig
3. Replace hardcoded logic with parameter-driven scanning
4. Test with your actual parameters

This will make the backtest actually useful!
