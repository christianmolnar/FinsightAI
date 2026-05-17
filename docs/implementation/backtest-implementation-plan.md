# FinsightAI — Autonomous AI Trader Implementation Plan

**Vision**: An autonomous trader that evaluates every trade signal across all strategies using AI,
learns from results, and can discover and add new strategies on its own.

**Owner**: Christian
**Last updated**: 2026-05-16

---

## Status Legend
- ✅ Complete
- 🔧 In Progress
- [ ] Not started
- ❌ Known broken

---

## Phase 1 — Parameter-Driven Backtester ✅ COMPLETE
Make StrategyExecutor and Backtester honor StrategyConfig parameters and run chronologically.

- ✅ StrategyExecutor accepts StrategyConfig and applies user parameters
- ✅ Backtester runs chronologically (bar-by-bar simulation)
- ✅ StrategyExecutor wired into Backtester hot path
- ✅ Earnings, Seasonality, Technical Breakout strategies implemented (as signal proxies)
- ✅ Backtester loads user strategy config from DB or uses defaults

---

## Phase 2 — Persistence ✅ COMPLETE
Persist runs to database with metadata for reproducibility.

- ✅ backtest_reports table (25+ columns)
- ✅ historical_prices table with caching
- ✅ OptimizationRun model and DB saves
- ✅ CalibrationEngine saves/retrieves recommendations from DB
- ✅ Full CRUD for backtest reports

---

## Phase 3 — Calibration Engine ✅ COMPLETE
AI-powered parameter tuning via heuristic analysis.

- ✅ CalibrationEngine (888 lines) with 4 analysis methods
- ✅ Real AI calls: GPT-4o-mini + Claude-3-haiku with fallback
- ✅ 20 parameters with validation and metadata
- ✅ Analyzes: profit targets, stop losses, position sizing, technical filters
- ✅ test_ai_calibration.py passes end-to-end

---

## Phase 4 — AI Trade Analysis ✅ COMPLETE (infrastructure)
AI analyzes trade batches and suggests parameter improvements.

- ✅ BacktestAIAnalyzer: batch trade analysis, real Claude/GPT calls
- ✅ analyze_and_recommend() — main entry point
- ✅ analyze_failure() — analyzes losing trades specifically
- ✅ Consolidates recommendations across batches
- ✅ Frontend UI: provider selection, confidence badges, priority sorting
- ✅ API endpoints: /api/backtest/analyze, /api/backtest/apply-recommendations
- ✅ AI analysis in backtester hot path: intentionally deferred to Phase C (per-trade AI gate)

---

## Phase 5 — Iterative Optimization Loop ✅ COMPLETE (infrastructure)
Automated: run → AI → apply → repeat until convergence.

- ✅ BacktestOptimizer: iterative loop with convergence detection
- ✅ Saves each iteration to DB (OptimizationRun)
- ✅ Tracks best config found across iterations
- ✅ **FIXED**: method call corrected to `analyze_and_recommend()`
- ✅ **FIXED**: `_apply_recommendation()` now maps all strategy params

---

## Phase A — Fix Broken Loop ✅ COMPLETE
Get the existing AI infrastructure actually running end-to-end.

- ✅ Fix `analyze_trades` → `analyze_and_recommend` method name mismatch in BacktestOptimizer
- ✅ Cleaned up backtester hot path (removed stub, documented Phase C AI gate)
- ✅ Fix `_apply_recommendation()` to map all 50+ strategy-specific params
  (stopLoss, profitTarget, daysBeforeEarnings, minEpsGrowth, and all strategy variants)
- ✅ Add `test_optimizer_loop.py` — 5 tests, all passing
- ✅ Verify /api/backtest/optimize endpoint works from frontend
  - Fixed `/results/{id}` to return optimizer's native format for optimization runs
    (previously would KeyError on `results['metrics']`; optimizer returns `best_config`/`best_return_pct`)

---

## Phase B — Real Strategy Signals
Wire strategies to real data, not technical proxies.

- ✅ Earnings strategy: use yfinance earnings calendar for actual earnings dates + EPS data
  - Added `earnings_data.py` service (yfinance fetch + 12hr cache)
  - Fixed `pd.Timestamp` comparison bug across all scanner methods
  - 12 tests, 12 passing
- ✅ Seasonality strategy: compute real historical monthly/quarterly patterns per symbol
  - Real monthly avg return computation across all historical years
  - Entry window: `weeksBeforePeak` param, looks 1–3 months ahead for strong peak
  - Consistency scoring: % of years the peak month was positive
  - 7 tests, 7 passing
- ✅ Macro strategy: implement using VIX, yield curve, sector rotation signals
  - Added `macro_data.py` service (yfinance fetch + 1hr cache): VIX, 10Y-2Y spread, sector ETF momentum
  - Gates: maxVix, minYieldSpread, requirePositiveSectorMomentum params
  - Scoring: low VIX, steep curve, sector breadth all contribute
  - 8 tests, 8 passing
- [ ] Sentiment strategy: news sentiment via existing stock_researcher.py
- [ ] Each trade carries full signal metadata (what triggered it, confidence, params used)
- [ ] Strategy signals are testable in isolation (unit tests per strategy)

---

## Phase C — Per-Trade AI Scoring
AI scores every trade signal before entry, not just post-run batch analysis.

- [ ] `AITradeScorer` service: given a signal + market context → AI confidence score (0-100)
- [ ] Each strategy scanner calls AITradeScorer before emitting a signal
- [ ] Trades filtered by per-trade AI confidence threshold (user-configurable)
- [ ] AI reasoning stored per trade for review
- [ ] Backtester supports `ai_gated` mode (only enter trades AI approves)
- [ ] Compare: AI-gated vs unfiltered backtest results

---

## Phase D — Strategy Learning & Expansion
AI discovers patterns and proposes new strategy variants.

- [ ] `StrategyVariant` model: named configs stored in DB, versioned
- [ ] After each optimization run, AI proposes a new variant worth testing
- [ ] Strategy variant library: user can see all variants + their backtest results
- [ ] Modular strategy plugin architecture (each strategy = self-contained class)
- [ ] AI can propose entirely new strategy logic (not just param tweaks)
- [ ] Strategy discovery: AI analyzes winning trades to reverse-engineer new signals

---

## Phase E — Autonomous Execution
Live scanner uses same AI-scored signals as backtester.

- [ ] Live scanner shares StrategyExecutor + AITradeScorer with backtester
- [ ] Paper trading loop: scan → score → execute → track → learn
- [ ] Graduated live execution: paper first, then small live, then full
- [ ] Position sizing guardrails: max per-trade, max portfolio exposure
- [ ] Live performance feeds back into next optimization cycle
- [ ] Pushover alerts for AI-approved signals with confidence scores

---

## Architecture Reference

```
StrategyExecutor (signals)
    ↓
AITradeScorer (per-trade AI gate) ← Phase C
    ↓
Backtester / LiveScanner
    ↓
BacktestAIAnalyzer (post-run batch analysis)
    ↓
BacktestOptimizer (iterative improvement loop)
    ↓
CalibrationEngine (parameter validation + heuristics)
    ↓
StrategyVariant DB (learned configs) ← Phase D
```

---

## Key Files

| File | Purpose |
|---|---|
| `services/strategy_executor.py` | Per-symbol signal scanning (all strategies) |
| `services/backtester.py` | Chronological simulation engine |
| `services/backtest_ai_analyzer.py` | Post-run AI trade analysis |
| `services/backtest_optimizer.py` | Iterative optimization loop |
| `services/calibration_engine.py` | Parameter heuristic tuning + AI reasoning |
| `services/pattern_library.py` | Reusable pattern detection |
| `api/backtest.py` | REST endpoints for all backtest operations |
| `models/optimization_run.py` | DB model for optimization runs |
