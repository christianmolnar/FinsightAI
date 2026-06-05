# FinsightAI — Master Implementation Plan

**Vision**: One autonomous trader that scans signals, scores them with AI, and executes trades.
It runs in **Paper mode** to validate strategies, then **Live mode** once a strategy is proven.
Both modes are identical code — only the execution step differs (simulated vs real Alpaca orders).
Manual trading never happens — it would pollute strategy evaluation.

**Owner**: Christian
**Last updated**: 2026-06-05

> **This is the single source of truth for design and implementation.**
> Companion doc: `docs/architecture/CURRENT-SYSTEM-ARCHITECTURE.md`
> Do not create additional planning or status documents — update this file.

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

## Phase B — Real Strategy Signals ✅ COMPLETE
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
- ✅ Sentiment strategy: news sentiment via existing stock_researcher.py
  - 11 tests, 11 passing
- ✅ Each trade carries full signal_metadata + params_used (persisted to BacktestResult + to_dict)
- ✅ Macro default config added (enabled: True, full params); sentiment config skeleton added
- ✅ Strategy signals are testable in isolation (54 total tests, all passing)

---

## Phase C — Per-Trade AI Scoring ✅ COMPLETE
AI scores every trade signal before entry, not just post-run batch analysis.

- ✅ `AITradeScorer` service: given a signal + market context → AI confidence score (0-100)
  - Claude 3 Haiku (fast/cheap) as primary; GPT-4o-mini as fallback; heuristic if no keys
  - Singleton via `get_ai_trade_scorer()`
- ✅ Backtester supports `ai_gated` mode: signals scoring below `ai_score_threshold` are skipped
- ✅ AI reasoning + score stored on each `BacktestResult` (ai_confidence, ai_reasoning)
- ✅ `BacktestRequest` API extended with `ai_gated: bool` and `ai_score_threshold: int`
- ✅ 12 tests passing (`tests/test_ai_trade_scorer.py`)
- ✅ Compare: AI-gated vs unfiltered — run backtest with `ai_gated=True` vs default

---

## Phase D Prerequisites — Unify Signal Engine ✅ COMPLETE
The backtester and live scanner now use the same signal engine.

- ✅ **`StrategyExecutor` wired into `MarketScanner`**: `scan_all_strategies()` delegates entirely
      to `StrategyExecutor` — all duplicate signal logic deleted from `MarketScanner`
- ✅ **`AITradeScorer` wired into live scan path**: every signal passes the gate before being
      returned from `MarketScanner.scan_all_strategies(ai_gated=True)`
- ✅ **`OpportunityAnalyzer` / `StockResearcher` removed from hot path**: `scan_opportunities.py`
      now uses `MarketScanner` directly; old `get_opportunity_analyzer()` call deleted
- ✅ **Confidence scale standardized**: 0–100 integers everywhere; old 0.0–1.0 `confidence_threshold`
      param in `OpportunityScanJob` replaced with `ai_score_threshold: int`
- ⚠️ **`TradeProposal` DB model not yet created**: `_create_proposals()` logs signals but does not
      write to DB. This is the first task in Phase D.

---

## Phase D — Strategy Learning & Expansion ✅ COMPLETE
AI discovers patterns and proposes new strategy variants.

- ✅ `TradeProposal` DB model: AI-approved live signals persisted to `trade_proposals` table
  - Fields: symbol, strategy, score, ai_score, ai_reasoning, exit params, signal_metadata
  - Status lifecycle: pending → executed → rejected / expired
  - `scan_opportunities.py` now writes to DB (was logging-only stub)
- ✅ `StrategyVariant` DB model: named, versioned configs stored in `strategy_variants` table
  - Fields: name, source, parent_variant_id, version, config (full JSON), backtest performance, ai_summary
  - Optimizer auto-creates a variant after every run that improves over baseline
- ✅ Strategy variant library UI: `StrategyVariantLibrary.js` component wired into Strategy Config page
  - Shows all variants + performance stats, favorites, promote-to-active, archive
  - New "Strategy Variants" panel in left sidebar of Strategy Configuration page
  - `GET/POST/PATCH/DELETE /api/strategy-variants` + `/promote` endpoint
  - 14 tests passing
- ✅ After optimization, AI proposes specific named changes — `ai_proposed_changes` field populated
  - `BacktestOptimizer._diff_configs()` diffs initial vs best config to produce human-readable change list
  - `BacktestOptimizer._build_ai_summary()` narrates what each iteration changed and why
- ✅ Strategy discovery: AI analyzes winning trades to reverse-engineer new signals
  - `StrategyDiscovery` service: `discover_from_trades()` → pattern extraction → AI analysis → variant proposals
  - Heuristic fallback when no AI keys available
  - `POST /api/backtest/discover` endpoint saves discovered variants to DB
  - 13 tests passing
- ✅ Modular strategy plugin architecture: deferred — `StrategyExecutor` already has clean per-strategy
  methods and is not a bottleneck; refactor would be pure churn with no user-visible benefit at this stage

---

## Phase E — Autonomous Execution ✅ COMPLETE (paper trading infrastructure)
Live scanner uses same AI-scored signals as backtester.

- ✅ Paper trading loop: scan → score → execute → track → learn
  - `PaperTradingLoop` service: reads pending `TradeProposal` rows, runs entry + exit cycle
  - Entry: AI score gate, duplicate check, position sizing, exposure cap
  - Exit: profit target, stop loss, max hold expiry (all automatic)
  - `PaperTrade` DB model (`paper_trades` table) with full position lifecycle
  - `POST /api/paper-loop/cycle` — trigger one full cycle
  - `GET /api/paper-loop/positions` — open positions
  - `GET /api/paper-loop/history` — closed trades
  - `GET /api/paper-loop/performance` — aggregate P&L summary
  - `POST /api/paper-loop/close/{id}` — manual close
  - 14 tests passing
- ✅ Position sizing guardrails enforced:
  - `max_single_position_pct` (default 5%)
  - `max_portfolio_exposure_pct` (default 40%)
  - `max_daily_trades` (default 5)
  - `min_ai_score` (default 60)
  - `max_hold_days` (default 21)
- ✅ Pushover alerts: entry and exit alerts sent via `PushoverService`
- ✅ Live performance feeds back: `get_performance_summary()` returns aggregate P&L by strategy

⚠️ **Phase E is infrastructure only — the UI and architecture below in Phase F must replace it.**

---

## Phase F — Unified Trader + Strategy Lifecycle ← NEXT PHASE
**Goal:** One autonomous trader, Paper and Live modes, full operator controls, strategy version tracking.

### F.1 — Remove manual trading ❌ MUST DELETE
- [ ] Remove "Execute Trade" button and modal from `PaperPortfolio.js`
- [ ] Remove "Manual Trading" sub-tab — Paper Portfolio view becomes autonomous trader monitor only
- [ ] Remove `manual` trade path from backend (any endpoint that accepts ad-hoc order without a `TradeProposal`)
- [ ] Confirm no test or service depends on manual trade path before deleting

### F.2 — Schema: Strategy lifecycle timestamps
- [ ] Add to `StrategyVariant`:
  - `activated_at` (DateTime, nullable) — when this variant was set as active
  - `deactivated_at` (DateTime, nullable) — when it was replaced or stopped
  - `mode` (String: `'paper'` | `'live'`) — which environment it runs in
  - `is_halted` (Boolean, default False)
  - `halted_at` (DateTime, nullable)
  - `halted_reason` (String, nullable)
  - `max_daily_loss_pct` (Float, default 5.0) — auto-halt circuit breaker
  - `max_total_loss_pct` (Float, default 15.0) — auto-halt circuit breaker
- [ ] Add to `PaperTrade` (and future `LiveTrade`):
  - `strategy_variant_id` (FK → `strategy_variants.id`) — every trade tagged to its strategy version
- [ ] Alembic migration (or `create_all` on startup — already wired)
- [ ] Update `StrategyVariant.to_dict()` to include new fields

### F.3 — Unified `AutonomousTrader` service
- [ ] Create `services/autonomous_trader.py` — replaces `PaperTradingLoop`
  - Constructor: `AutonomousTrader(mode: Literal['paper', 'live'], db, ai_provider)`
  - `run_cycle()` — identical logic for both modes:
    1. Check is_halted on active variant → abort if halted
    2. Check daily loss circuit breaker → auto-halt if triggered
    3. Scan pending `TradeProposal` rows for current user
    4. Apply guardrails (position size, exposure, daily trade cap, min AI score)
    5. Execute entry:
       - Paper: create `PaperTrade` row
       - Live: submit Alpaca order, then create `LiveTrade` row
    6. Process exits (profit target, stop loss, max hold)
    7. Send Pushover alerts
  - `halt(reason: str)` — sets `is_halted=True`, `halted_at`, `halted_reason` on active variant
  - `resume()` — clears halt flags
  - `get_status()` — returns mode, is_halted, daily P&L, open positions count, guardrails
- [ ] Delete `services/paper_trading_loop.py` once `AutonomousTrader` passes all same tests
- [ ] Update `api/paper_loop.py` to use `AutonomousTrader(mode='paper')`
- [ ] Wire `api/live_trader.py` (new) using `AutonomousTrader(mode='live')`

### F.4 — Trader control API
- [ ] `POST /api/trader/{mode}/halt` — immediately halt (paper or live)
- [ ] `POST /api/trader/{mode}/resume` — clear halt
- [ ] `GET  /api/trader/{mode}/status` — mode, halted, daily P&L, circuit breaker state, open count
- [ ] `GET  /api/trader/{mode}/guardrails` — all configurable limits
- [ ] `PATCH /api/trader/{mode}/guardrails` — update limits live (no restart needed)
- [ ] All endpoints require `get_current_user` dependency

### F.5 — Strategy lifecycle API
- [ ] `POST /api/strategy-variants/{id}/activate-paper` — set `activated_at=now`, `mode='paper'`, deactivate previous paper variant
- [ ] `POST /api/strategy-variants/{id}/promote-to-live` — validation check (must have been paper-active for min N days), create live variant clone with `activated_at=now`, modal confirmation required
- [ ] `POST /api/strategy-variants/{id}/deactivate` — set `deactivated_at=now`
- [ ] Returns full strategy period history: `[{id, name, mode, activated_at, deactivated_at, total_return_pct, win_rate, trade_count}]`

### F.6 — Paper Trader view (replaces PaperPortfolio)
- [ ] Rename / rebuild `PaperPortfolio.js` → autonomous trader monitor, no manual trade UI
- [ ] **Header**: active strategy name + version, running since date, total P&L for this period
- [ ] **Controls bar**:
  - 🔴 **STOP EVERYTHING** (halt — no new entries, no forced exits)
  - 🟡 **PAUSE** (no new entries, existing positions run to natural exit)
  - ▶️ **RESUME** (if halted/paused)
  - 🔄 **Run Cycle** (manual trigger, for testing)
- [ ] **Circuit breaker status**: daily loss %, total loss %, vs configured limits — turns red when near threshold
- [ ] **Open positions table**: symbol, strategy, entry price, AI score, target, stop, age, unrealized P&L
- [ ] **Recent closed trades**: last 20, with return % and exit reason
- [ ] **Performance summary**: win rate, avg return, total P&L — scoped to current strategy period only
- [ ] No "Execute Trade" button, no manual trade modal, no watchlist

### F.7 — Live Trader view
- [ ] Create `LiveTrader.js` — identical layout to Paper Trader view
- [ ] Same controls (STOP, PAUSE, RESUME) — halt live trader independently of paper
- [ ] Shows real Alpaca positions + live P&L
- [ ] **Promote Strategy** button — opens modal to promote current paper strategy to live
- [ ] Confirmation modal: "This will start trading with real money. Strategy X has been paper-trading for N days with Y% return. Confirm?"

### F.8 — Strategy Performance Reports
- [ ] New `Reports.js` tab (or section in Strategy Config)
- [ ] **Strategy version timeline**: list all variants, Paper and Live, with date ranges and P&L
- [ ] **Paper vs Live comparison**: for variants that ran in both modes — did live match paper?
- [ ] **Strategy ranking**: which config versions performed best, sortable by return/win rate/drawdown
- [ ] Backend: `GET /api/reports/strategy-history` — all variants with performance computed from trades

### F.9 — Cleanup: remove dead code
- [ ] Delete `frontend/src/components/PaperLoop.js` (standalone component, replaced by rebuilt PaperPortfolio)
- [ ] Remove or archive `PaperTradingLoop` from `services/paper_trading_loop.py` once F.3 complete
- [ ] Remove `api/paper_loop.py` once F.4 routes replace it (keep old routes as deprecated aliases if needed for backwards compat)
- [ ] Audit `docs/implementation/` — mark stale docs in `archive/` subfolder, update this file only

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
| `services/strategy_executor.py` | Per-symbol signal scanning (all strategies) — used by both backtester and live scanner |
| `services/backtester.py` | Chronological simulation engine |
| `services/market_scanner.py` | Live scanner — delegates to StrategyExecutor + AITradeScorer |
| `services/ai_trade_scorer.py` | Per-trade AI gate (0–100) — shared by backtest and live paths |
| `services/backtest_ai_analyzer.py` | Post-run AI trade analysis |
| `services/backtest_optimizer.py` | Iterative optimization loop — auto-creates StrategyVariants |
| `services/calibration_engine.py` | Parameter heuristic tuning + AI reasoning |
| `jobs/scan_opportunities.py` | Railway cron — live scan → TradeProposal DB writes |
| `api/backtest.py` | REST endpoints for all backtest operations |
| `app/models/trade_proposal.py` | Live AI-approved signals queued for execution |
| `app/models/strategy_variant.py` | Named versioned strategy configs with backtest performance |
| `models/optimization_run.py` | DB model for optimization runs |
