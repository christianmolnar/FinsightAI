# Backtest Implementation Plan (Concise)

Purpose
- Make the backtester parameter-driven, chronological, persistent, and AI-analyzable.

Scope
- Phase 1: Make StrategyExecutor and Backtester honor StrategyConfig parameters and run chronologically.
- Phase 2: Persist runs to database with metadata for reproducibility.
- Phase 3: Add calibration engine to tune parameters (ML/heuristic).
- Phase 4: Integrate AI analysis to summarize trades and suggest improvements.

Checklist
- [ ] Audit current backtester for parameter usage
- [ ] Implement StrategyExecutor to accept StrategyConfig and enforce parameter bounds
- [ ] Add chrono-runner to replay bars in chronological order
- [ ] Implement storage model for backtest runs (runs table + trades table)
- [ ] Add end-to-end tests for known strategies
- [ ] Add calibration_engine integration (Phase 3)
- [ ] Add ai_analysis module to summarize runs
- [ ] Document plan and update docs/implementation/IMPLEMENTATION-INDEX.md

Notes
- Keep tests small and focused
- Use feature branches and PRs

Owner: Christian
Last updated: 2026-05-14
