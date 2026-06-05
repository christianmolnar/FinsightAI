# FInsightAI — System Architecture
**Last Updated:** June 5, 2026
**Status:** ✅ Operational (Backend on Railway, Frontend on Vercel)
**Broker:** Alpaca Markets (Paper + Live)

---

## Core Design Principles

1. **One autonomous trader, two modes.** The same code runs for Paper and Live. The only difference is the execution step: Paper creates a `PaperTrade` row; Live submits an Alpaca order and creates a `LiveTrade` row.
2. **No manual trading, ever.** Manual trades pollute strategy evaluation. The UI has no "Execute Trade" button. All positions come from the autonomous trader.
3. **Strategy versions have timestamps.** Every trade is tagged to the exact `StrategyVariant` that was active when it was placed. Performance is always scoped to a strategy period.
4. **Paper proves, Live inherits.** A strategy must run in Paper for a meaningful period before it can be promoted to Live. The promotion creates a new Live variant record with `activated_at = now`.
5. **Operator controls are first-class.** STOP, PAUSE, and circuit breakers (daily loss %, total loss %) are always visible and always functional — in both Paper and Live views.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│                   https://www.f-insight.ai                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React / Vercel)                 │
│  Backtesting  │  Strategy Config  │  Paper  │  Live  │  Reports │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API (JWT Bearer)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI / Railway)                │
│       https://finsightai-production-442e.up.railway.app     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SIGNAL ENGINE (source of truth)        │    │
│  │  StrategyExecutor — all 5 strategies                │    │
│  │  • earnings  • seasonality  • macro                 │    │
│  │  • sentiment  • technical_breakout                  │    │
│  │  Reads: StrategyConfig (DB) + historical_prices     │    │
│  │  Emits: signal dict {symbol, strategy, score,       │    │
│  │         price, exit_params, signal_metadata}        │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              ▼                     ▼                        │
│  ┌───────────────────┐  ┌──────────────────────────────┐    │
│  │   BACKTESTER      │  │   AUTONOMOUS TRADER          │    │
│  │   Backtester.py   │  │   AutonomousTrader(mode=     │    │
│  │   Chronological   │  │   'paper'|'live')            │    │
│  │   bar-by-bar sim  │  │   Same logic, mode flag      │    │
│  │   Validates       │  │   controls execution step    │    │
│  │   strategy before │  │   Circuit breakers + halt    │    │
│  │   paper testing   │  │   controls always active     │    │
│  └────────┬──────────┘  └──────────────────────────────┘    │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              AI LAYER                               │    │
│  │  AITradeScorer   — per-trade gate (0–100) ✅        │    │
│  │  BacktestAIAnalyzer — post-run batch analysis ✅    │    │
│  │  BacktestOptimizer — iterative improvement ✅       │    │
│  │  CalibrationEngine — heuristic param tuning ✅      │    │
│  │  StrategyDiscovery — reverse-engineer new signals   │    │
│  │  Primary: Claude 3 Haiku  │  Fallback: GPT-4o-mini  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌───────────────────────┐
│  PostgreSQL DB   │     │   Alpaca Markets API  │
│  (Railway)       │     │   Paper + Live        │
│  • paper_trades  │     │   Market Data         │
│  • strategy_     │     │   Orders (live only)  │
│    variants      │     └───────────────────────┘
│  • trade_        │
│    proposals     │
│  • backtest_rpts │
│  • historical_px │
│  • users / auth  │
└──────────────────┘
```

---

## Strategy Lifecycle

```
Backtest (validate config)
    ↓
Activate as Paper (StrategyVariant: mode='paper', activated_at=now)
    ↓
AutonomousTrader(mode='paper') runs cycles
    ↓
All PaperTrades tagged: strategy_variant_id = this variant
    ↓
Operator reviews performance reports (scoped to this variant period)
    ↓
Promote to Live (new StrategyVariant: mode='live', activated_at=now,
                 previous paper variant: deactivated_at=now)
    ↓
AutonomousTrader(mode='live') runs same cycles + Alpaca order submission
    ↓
Reports compare Paper vs Live for same strategy config
```

---

## Operator Controls (both Paper and Live views)

| Control | Behavior |
|---|---|
| 🔴 STOP EVERYTHING | Sets `is_halted=True` on active variant. No new entries. No forced exits. Positions run until natural exit or manual review. |
| 🟡 PAUSE | No new entries. Existing positions run to natural exit (profit target / stop loss / max hold). |
| ▶️ RESUME | Clears halt/pause. Resumes normal cycle. |
| Daily loss circuit breaker | Auto-halts if portfolio drops `max_daily_loss_pct` in one trading day. Stored on StrategyVariant. |
| Total loss circuit breaker | Auto-halts if cumulative loss exceeds `max_total_loss_pct`. |
| Run Cycle (manual) | Triggers one scan → score → execute → exit cycle. For testing and forcing a scan outside the cron schedule. |

---

## Signal Engine — Unified ✅

Both backtester and live scanner use `StrategyExecutor` + `AITradeScorer`.

| | Backtester | Live Scanner |
|---|---|---|
| Signal engine | `StrategyExecutor` ✅ | `MarketScanner` (delegates to `StrategyExecutor`) ✅ |
| Strategies | All 5 | All 5 |
| AI gate | `AITradeScorer` ✅ | `AITradeScorer` ✅ |
| Exit params | Per-signal from strategy config | Per-signal from strategy config |

---

## Key Services

| File | Purpose | Status |
|---|---|---|
| `services/strategy_executor.py` | All-strategy signal scanner | ✅ Complete |
| `services/backtester.py` | Chronological simulation engine | ✅ Complete |
| `services/ai_trade_scorer.py` | Per-trade AI gate (0–100) | ✅ Complete |
| `services/backtest_ai_analyzer.py` | Post-run batch AI analysis | ✅ Complete |
| `services/backtest_optimizer.py` | Iterative optimization loop | ✅ Complete |
| `services/calibration_engine.py` | Parameter heuristic tuning | ✅ Complete |
| `services/market_scanner.py` | Live opportunity scanning | ✅ Uses StrategyExecutor |
| `services/strategy_discovery.py` | AI reverse-engineers new signals from winners | ✅ Complete |
| `services/autonomous_trader.py` | Unified Paper+Live trader with controls | [ ] Phase F.3 |
| `services/paper_trading_loop.py` | ⚠️ Interim — will be deleted when F.3 complete | ⚠️ Interim |
| `services/earnings_data.py` | yfinance earnings calendar | ✅ Complete |
| `services/macro_data.py` | VIX, yield curve, sector ETF data | ✅ Complete |
| `api/backtest.py` | All backtest REST endpoints | ✅ Complete |
| `api/paper_loop.py` | ⚠️ Interim — will be replaced by `/api/trader/paper/*` | ⚠️ Interim |
| `api/strategy_variants.py` | Strategy variant CRUD + promote | ✅ Complete |
| `jobs/scan_opportunities.py` | Railway cron — live scan → TradeProposal DB writes | ✅ Complete |

---

## Data Flow — Backtesting ✅

```
BacktestRequest (dates, strategies, ai_gated, ai_score_threshold)
    → StrategyExecutor.scan_all_strategies(symbol, date)
    → AITradeScorer.score(signal)   [if ai_gated=True]
    → _simulate_trade(signal)
    → BacktestResult saved to DB (with strategy_variant_id when variant active)
```

## Data Flow — Autonomous Trader (Paper or Live) [Phase F target]

```
Cron / manual trigger
    → AutonomousTrader(mode).run_cycle()
        → check is_halted, check circuit breakers
        → read pending TradeProposals (from MarketScanner cron)
        → apply guardrails (size, exposure, daily cap, AI score)
        → execute entry:
            paper: create PaperTrade(strategy_variant_id=active_variant.id)
            live:  submit Alpaca order + create LiveTrade(strategy_variant_id=...)
        → process exits (profit target, stop loss, max hold)
        → update circuit breaker state (daily P&L)
        → send Pushover alerts
```

---

## Frontend Views (Phase F target)

| Tab | Purpose | Status |
|---|---|---|
| Backtesting | Historical simulation, optimization, AI analysis, strategy discovery | ✅ Complete |
| Strategy Config | Configure parameters, variant library, promote to paper | ✅ Complete |
| Paper Trader | Autonomous trader monitor — controls, positions, performance | [ ] Phase F.6 |
| Live Trader | Identical to Paper Trader — real money, requires promotion | [ ] Phase F.7 |
| Reports | Strategy version history, Paper vs Live comparison | [ ] Phase F.8 |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, uvicorn |
| Frontend | React 18, Tailwind CSS, Recharts |
| Database | PostgreSQL 15 (Railway) |
| AI Primary | Anthropic Claude 3 Haiku (`claude-3-haiku-20240307`) |
| AI Fallback | OpenAI GPT-4o-mini |
| AI Batch | Claude 3.5 Sonnet + GPT-4-turbo (post-run analysis) |
| Market Data | yfinance (historical), Alpaca (live quotes) |
| Auth | JWT (bcrypt, `user_auth.py`) |
| Notifications | Pushover (push alerts) |
| Hosting | Railway (backend + DB + cron), Vercel (frontend) |

---

## Test Coverage

```
tests/test_earnings_strategy.py        12 tests ✅
tests/test_seasonality_strategy.py      7 tests ✅
tests/test_macro_strategy.py            8 tests ✅
tests/test_sentiment_strategy.py       11 tests ✅
tests/test_ai_trade_scorer.py          12 tests ✅
tests/test_optimizer_loop.py            5 tests ✅
tests/test_strategy_variants.py        14 tests ✅
tests/test_strategy_discovery.py       13 tests ✅
tests/test_paper_trading_loop.py       14 tests ✅  (interim — will be replaced by test_autonomous_trader.py)
                                       ──────────
Total:                                107 tests ✅
```

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│              https://frontend-pi-kohl-57.vercel.app         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (React / Vercel)                 │
│  Backtesting  │  Strategy Config  │  Portfolio  │  Scanner  │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API (JWT Bearer)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI / Railway)                │
│       https://finsightai-production-442e.up.railway.app     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SIGNAL ENGINE (source of truth)        │    │
│  │  StrategyExecutor — all 5 strategies                │    │
│  │  • earnings  • seasonality  • macro                 │    │
│  │  • sentiment  • technical_breakout                  │    │
│  │  Reads: StrategyConfig (DB) + historical_prices     │    │
│  │  Emits: signal dict {symbol, strategy, score,       │    │
│  │         price, exit_params, signal_metadata}        │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              ▼                     ▼                        │
│  ┌───────────────────┐  ┌──────────────────────────────┐    │
│  │   BACKTESTER      │  │  LIVE SCANNER (MarketScanner)│    │
│  │   Backtester.py   │  │  ⚠️  DOES NOT YET USE        │    │
│  │   Chronological   │  │  StrategyExecutor — BLOCKER  │    │
│  │   bar-by-bar sim  │  │  for Phase D (see plan)      │    │
│  └────────┬──────────┘  └──────────────────────────────┘    │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              AI LAYER                               │    │
│  │  AITradeScorer   — per-trade gate (Phase C) ✅      │    │
│  │  BacktestAIAnalyzer — post-run batch analysis ✅    │    │
│  │  BacktestOptimizer — iterative improvement ✅       │    │
│  │  CalibrationEngine — heuristic param tuning ✅      │    │
│  │  Primary: Claude 3 Haiku  │  Fallback: GPT-4o-mini  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐     ┌───────────────────────┐
│  PostgreSQL DB   │     │   Alpaca Markets API  │
│  (Railway)       │     │   Paper + Live        │
│  • backtest_rpts │     │   Market Data         │
│  • historical_px │     │   Orders & Positions  │
│  • strategy_cfg  │     └───────────────────────┘
│  • optimization  │
│  • users / auth  │
└──────────────────┘
```

---

## Signal Engine — Unified ✅

Both backtester and live scanner now use StrategyExecutor + AITradeScorer.

| | Backtester | Live Scanner |
|---|---|---|
| Signal engine | `StrategyExecutor` | `MarketScanner` (own logic) |
| Strategies | All 5 (earnings, seasonality, macro, sentiment, breakout) | Partial (earnings skeleton returns empty) |
| AI gate | `AITradeScorer` ✅ | Not wired |
| Exit params | Per-signal from strategy config | Hardcoded |

**Impact:** Backtest results are not predictive of live performance because they use different logic.
**Fix (Phase D prerequisite):** Wire `StrategyExecutor` into `MarketScanner` so both paths use identical signal logic.

---

## Key Services

| File | Purpose | Status |
|---|---|---|
| `services/strategy_executor.py` | All-strategy signal scanner | ✅ Complete |
| `services/backtester.py` | Chronological simulation engine | ✅ Complete |
| `services/ai_trade_scorer.py` | Per-trade AI gate (0–100) | ✅ Complete |
| `services/backtest_ai_analyzer.py` | Post-run batch AI analysis | ✅ Complete |
| `services/backtest_optimizer.py` | Iterative optimization loop | ✅ Complete |
| `services/calibration_engine.py` | Parameter heuristic tuning | ✅ Complete |
| `services/market_scanner.py` | Live opportunity scanning | ⚠️ Uses own signal logic |
| `services/opportunity_analyzer.py` | Live AI analysis (StockResearcher) | ⚠️ Separate AI path |
| `services/earnings_data.py` | yfinance earnings calendar | ✅ Complete |
| `services/macro_data.py` | VIX, yield curve, sector ETF data | ✅ Complete |
| `api/backtest.py` | All backtest REST endpoints | ✅ Complete |
| `jobs/scan_opportunities.py` | Railway cron — live scan job | ⚠️ Not using StrategyExecutor |

---

## Data Flow — Backtesting (Current)

```
BacktestRequest (dates, strategies, ai_gated, ai_score_threshold)
    → StrategyExecutor.scan_all_strategies(symbol, date)
        → Earnings / Seasonality / Macro / Sentiment / Breakout
        → Returns: signal {score, exit_params, signal_metadata}
    → AITradeScorer.score(signal)   [if ai_gated=True]
        → Claude 3 Haiku → score 0–100
        → Skip if score < ai_score_threshold
    → _simulate_trade(signal)
        → Uses exit_params from signal (profit_target, stop_loss)
        → Tracks portfolio equity, cash, positions
    → BacktestResult saved to DB
```

## Data Flow — Live Scanning (Current — DIVERGED)

```
OpportunityScanJob (Railway cron, every 15 min market hours)
    → MarketScanner.scan_all_strategies(symbol)   ← DIFFERENT logic
        → Own earnings/technical implementations (not StrategyExecutor)
    → OpportunityAnalyzer (StockResearcher AI)    ← DIFFERENT AI path
    → TradeProposal created
    → Alpaca paper order placed
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, uvicorn |
| Frontend | React 18, Tailwind CSS, Recharts |
| Database | PostgreSQL 15 (Railway) |
| AI Primary | Anthropic Claude 3 Haiku (`claude-3-haiku-20240307`) |
| AI Fallback | OpenAI GPT-4o-mini |
| AI Batch | Claude 3.5 Sonnet + GPT-4-turbo (post-run analysis) |
| Market Data | yfinance (historical), Alpaca (live quotes) |
| Auth | JWT (bcrypt, `user_auth.py`) |
| Notifications | Pushover (push alerts) |
| Hosting | Railway (backend + DB + cron), Vercel (frontend) |

---

## Test Coverage

```
tests/test_earnings_strategy.py      12 tests ✅
tests/test_seasonality_strategy.py    7 tests ✅
tests/test_macro_strategy.py          8 tests ✅
tests/test_ai_trade_scorer.py        12 tests ✅
tests/test_optimizer_loop.py          5 tests ✅
                                     ──────────
Total:                               44 tests ✅
```
