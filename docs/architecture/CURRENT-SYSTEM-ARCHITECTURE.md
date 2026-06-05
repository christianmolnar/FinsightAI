# FInsightAI — System Architecture
**Last Updated:** May 30, 2026
**Status:** ✅ Operational (Backend on Railway, Frontend on Vercel)
**Broker:** Alpaca Markets (Paper + Live)

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
