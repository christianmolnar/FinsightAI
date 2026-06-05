# FinsightAI — Architecture Coherence Audit
**Date**: 2026-05-30  
**Status**: 🔴 Issues Found — Gaps documented, fixes needed before Phase D

---

## Executive Summary

The system has two completely parallel, disconnected signal pipelines.  
The backtest path and the live trading path do not share signal generation code.  
AI gating exists only in backtesting and is not yet exposed in the UI.  
Exit rules are hardcoded globally, ignoring per-strategy parameters.  

These must be resolved before building Phase D (live autonomous execution).

---

## 1. Two Disconnected Signal Pipelines

### Problem
There are TWO entirely separate scanners with different strategies, data sources, and AI logic:

| | **Live Path** | **Backtest Path** |
|---|---|---|
| Scanner | `MarketScanner` | `StrategyExecutor` |
| Data source | Alpaca REST API (live) | `HistoricalDataManager` (DB + yfinance) |
| AI | `OpportunityAnalyzer` → `StockResearcher` + `DualAIService` | `AITradeScorer` (Phase C) |
| Confidence scale | 0.0–1.0 float | 0–100 integer |
| Strategies | earnings (TODO/skeleton), breakout, seasonal (proxy) | earnings (real yfinance), seasonality (real), macro, sentiment, breakout |
| Output | `TradeProposal` in DB | `BacktestResult` |

**Consequence**: backtesting a strategy does NOT tell you how the live scanner will behave, because they are different code.

### Fix Required
`StrategyExecutor` must become the single shared signal engine for both paths.  
`MarketScanner.scan_all_strategies()` should call `StrategyExecutor` internally for live mode.  
This is the core Phase D work.

---

## 2. Strategy Name Mismatches

### Problem
Strategy names are inconsistent across frontend, backend, and the API:

| Location | Strategy Names |
|---|---|
| Frontend `Backtesting.js` strategies state | `technical_breakout`, `earnings`, `seasonality` (3 only — missing `macro`, `sentiment`) |
| Frontend `StrategyConfig.js` | Earnings Momentum, Seasonality & Calendar, Macro & Economic, Social Sentiment |
| `StrategyExecutor` | `earnings`, `seasonality`, `macro`, `sentiment`, `technical_breakout` |
| `MarketScanner` (live) | `earnings_play`, `technical_breakout`, `seasonality` (different names!) |
| `backtest_config.py` SCANNER_CONFIG | `technical_breakout`, `earnings_play`, `seasonality` (old names) |

**Consequence**: 
- Frontend can't select macro or sentiment strategies for backtesting
- Strategy filter `if opp['strategy'] in strategies` silently drops all macro/sentiment signals when user selects "all"
- `backtest_config.py` has stale strategy names that no longer match

### Fix Required
Define a single canonical strategy name set: `earnings`, `seasonality`, `macro`, `sentiment`, `technical_breakout`.  
Update frontend `Backtesting.js` to include all 5.  
Update `backtest_config.py` SCANNER_CONFIG.  
Update `MarketScanner` strategy names to match.

---

## 3. AI Gating: Backtest Only, Not Live, Not in UI

### Problem
`AITradeScorer` (Phase C) was wired into `backtester.py` with `ai_gated=False` default.  
Three things are missing:

1. **Not in the frontend**: `Backtesting.js` has no UI control for `ai_gated` or `ai_score_threshold`. Users cannot enable it.
2. **Not in live trading**: `OpportunityScanJob` → `OpportunityAnalyzer` does NOT call `AITradeScorer`. Live trades bypass per-trade AI scoring entirely.
3. **Duplicate AI confidence systems**: The live path uses `OpportunityAnalyzer` (0.0–1.0 float confidence via `StockResearcher` + full company research). The backtest path uses `AITradeScorer` (0–100 signal-level quick score). These are different AI analyses with different scales.

### Fix Required
- Add `ai_gated` toggle and `ai_score_threshold` slider to `Backtesting.js` UI
- When Phase D live scanner is built, `AITradeScorer` must gate every signal before `TradeProposal` is created
- Decide and document which AI analysis runs where:
  - `AITradeScorer`: fast per-signal gate (0–100), runs on every signal in both backtest and live
  - `OpportunityAnalyzer` full research: deeper analysis, runs on proposals that passed the gate (live only)

---

## 4. Exit Rules Hardcoded, Ignoring Per-Strategy Parameters

### Problem
`backtest_config.py` defines global exit rules:
```python
EXIT_RULES = {
    "profit_target_pct": 15.0,
    "stop_loss_pct": -8.0,
    "max_hold_days": 60
}
```

`StrategyExecutor` returns per-strategy `exit_params` on every signal:
```python
'exit_params': {
    'profit_target': 12,   # earnings: 12%
    'stop_loss': 5,        # earnings: 5%
    'max_portfolio_weight': 20
}
```

`backtester._simulate_trade()` reads from `EXIT_RULES` and IGNORES `exit_params` from the signal.  
This means a user setting earnings profit_target=12% in Strategy Config has zero effect on the backtest simulation — the hardcoded 15% is always used.

### Fix Required
`_simulate_trade()` must read `profit_target` and `stop_loss` from `opportunity['exit_params']` first, falling back to `EXIT_RULES` only if not present.

---

## 5. Dead Parameters in `run_backtest()`

### Problem
`run_backtest()` accepts `confidence_threshold` and `use_ai` parameters that do nothing:
- `use_ai=True` is referenced in comments and logging but `_analyze_with_ai()` is never called in the current loop
- `confidence_threshold` is passed in but never used to filter anything
- Both are dead code left over from before `StrategyExecutor` replaced the old scanner

### Fix Required
Either remove these parameters or implement them clearly:
- `use_ai` → could control whether `AITradeScorer` is used (same as `ai_gated`)
- `confidence_threshold` → could be the `ai_score_threshold` / 100 equivalent  
- Simplest: deprecate `use_ai` and `confidence_threshold`, consolidate into `ai_gated` + `ai_score_threshold`

---

## 6. `MarketScanner` Earnings Strategy Is a Skeleton

### Problem
`MarketScanner._scan_earnings_plays()` (live scanner) has this code:
```python
# Alpaca does not expose earnings calendar directly.
# TODO: integrate earnings calendar API
# For now, skip earnings play without a date source.
```
It never appends any candidates — it returns an empty list always.  
The live scanner has no working earnings strategy.

### Fix Required
Wire `StrategyExecutor.scan_earnings_opportunities()` into live scanning.  
This uses yfinance earnings calendar (already built and tested).

---

## 7. Canonical Architecture (Target State)

```
                         SINGLE SIGNAL ENGINE
                         StrategyExecutor
                    (earnings, seasonality, macro,
                     sentiment, technical_breakout)
                              │
                    ┌─────────┴─────────┐
                    │                   │
             BACKTEST PATH         LIVE PATH
             Backtester            MarketScanner
                    │               (calls StrategyExecutor)
                    │                   │
              AITradeScorer       AITradeScorer
              (ai_gated gate)     (always-on gate)
                    │                   │
             BacktestResult       OpportunityAnalyzer
                    │             (deep research, optional)
             BacktestMetrics           │
                                  TradeProposal (DB)
                                       │
                                  execute_proposals.py (Phase D)
```

---

## Prioritized Fix List

| # | Fix | Impact | Effort |
|---|---|---|---|
| 1 | `_simulate_trade` use `exit_params` from signal | High — makes Strategy Config params actually work in backtest | Low |
| 2 | Frontend: add `macro` + `sentiment` to strategy selector | Medium — users can't test all strategies | Low |
| 3 | Frontend: add AI Gate toggle + threshold slider to Backtesting UI | Medium — Phase C feature is invisible | Low |
| 4 | Clean up dead `use_ai` / `confidence_threshold` params in `run_backtest` | Low — cosmetic but confusing | Low |
| 5 | `MarketScanner` call `StrategyExecutor` for live scanning | Critical — prerequisite for Phase D | High |
| 6 | Wire `AITradeScorer` into live scan job | Critical — prerequisite for Phase D | Medium |
| 7 | Unify confidence scale (0–100 everywhere or 0.0–1.0 everywhere) | Medium — prevents confusion at boundaries | Low |

**Fixes 1–4 should be done now (small, high value).**  
**Fixes 5–7 are Phase D work.**

---

## Current Status vs Implementation Plan

| Phase | Plan Status | Reality |
|---|---|---|
| Phase C — Per-Trade AI Scoring | ✅ Complete (backend) | ⚠️ Partial — backtest only, no UI, not in live path |
| Phase D — Strategy Learning & Expansion | Not started | Blocked by Fix #5 above |
| Phase E — Autonomous Execution | Not started | Blocked by Fix #5 + #6 |
