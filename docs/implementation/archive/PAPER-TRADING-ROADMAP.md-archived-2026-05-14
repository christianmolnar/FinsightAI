# Paper Trading Autonomous Scanner - Implementation Roadmap

**Goal**: Get the cron job opportunity scanner running on paper trading

**Current Date**: March 7, 2026

---

## ✅ What's Already Working

### Backend Infrastructure
- ✅ FastAPI backend running on port 8000
- ✅ PostgreSQL database on Railway
- ✅ Alpaca API integration (paper + live)
- ✅ Market scanner with 3 strategies (earnings, technical, seasonality)
- ✅ Historical data manager with Alpaca
- ✅ Backtesting engine (557 trades, 56.2% win rate, +52.52% return)
- ✅ Calibration engine for parameter optimization

### Frontend
- ✅ React app running on port 3000
- ✅ Strategy configuration UI
- ✅ Backtesting UI with results display
- ✅ Portfolio monitoring
- ✅ Real-time market data

### Trading Components
- ✅ `trading_agent.py` - Simple automated trading agent
- ✅ `MarketScanner` - Finds opportunities (3 strategies)
- ✅ `AlpacaService` - Executes trades on paper/live
- ✅ Portfolio API - Get positions, cash, orders

---

## 🔴 What's Missing for Autonomous Paper Trading

### 1. **Decision Engine** (CRITICAL - Missing)
**Status**: ❌ Not implemented

**What's Needed**:
- Take scanner candidates → decide which to trade
- Apply risk management rules:
  - Max position size (currently flat $1000 ❌ needs fixing)
  - Max portfolio exposure
  - Max daily loss limit
  - VIX threshold checks
- Apply technical filters (RSI, volume, MA distance)
- Generate entry/exit signals with stop loss and profit targets

**Files to Create/Modify**:
- `/backend/services/decision_engine.py` (NEW)
- Update `/backend/services/market_scanner.py` to integrate decision engine

**Estimated Time**: 2-3 hours

---

### 2. **Position Sizing Logic** (HIGH PRIORITY)
**Status**: ❌ Broken (flat $1000 per trade, doesn't compound)

**Problem**:
```python
position_size = 1000  # ❌ Fixed dollar amount
```

**What's Needed**:
```python
position_size_pct = 0.10  # 10% of capital
position_size = current_portfolio_value * position_size_pct  # ✅ Compounds
```

**Impact**:
- Affects backtesting accuracy
- Affects live trading returns
- Without this, results won't compound properly

**Files to Modify**:
- `/backend/services/backtester.py`
- `/backend/services/market_scanner.py`
- Decision engine (when created)

**Estimated Time**: 1 hour

---

### 3. **Autonomous Trading Loop** (CRITICAL - Missing)
**Status**: ⚠️ Partially exists (`trading_agent.py` is simple)

**What's Needed**:
```python
# Pseudo-code for autonomous loop
while market_open:
    # 1. Scan for opportunities
    candidates = market_scanner.scan_all_strategies()
    
    # 2. Apply decision engine
    trades_to_execute = decision_engine.evaluate(candidates)
    
    # 3. Execute trades
    for trade in trades_to_execute:
        alpaca_service.submit_order(
            symbol=trade.symbol,
            qty=trade.quantity,
            side=trade.side  # buy/sell
        )
    
    # 4. Monitor existing positions
    positions = alpaca_service.get_positions()
    for position in positions:
        if should_close(position):
            alpaca_service.close_position(position.symbol)
    
    # 5. Wait for next scan
    time.sleep(300)  # 5 minutes
```

**Files to Create/Modify**:
- `/backend/autonomous_trader.py` (NEW - orchestrator)
- Update `/trading_agent.py` or replace with new version

**Estimated Time**: 2 hours

---

### 4. **Cron Job / Scheduler** (CRITICAL - Missing)
**Status**: ❌ Not implemented

**What's Needed**:
- Start autonomous trader at market open (9:30 AM ET)
- Stop at market close (4:00 PM ET)
- Run Monday-Friday only
- Auto-restart on crashes

**Options**:

**Option A: System Cron Job** (Simple)
```bash
# /etc/crontab or crontab -e
30 9 * * 1-5 cd /path/to/backend && python autonomous_trader.py
```

**Option B: Python Scheduler** (More control)
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    run_trading_loop,
    'cron',
    day_of_week='mon-fri',
    hour=9,
    minute=30,
    timezone='US/Eastern'
)
scheduler.start()
```

**Option C: systemd Service** (Production)
```ini
[Unit]
Description=FInsightAI Paper Trading Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
ExecStart=/path/to/venv/bin/python autonomous_trader.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Estimated Time**: 1 hour

---

### 5. **Logging & Monitoring** (IMPORTANT)
**Status**: ⚠️ Basic logging exists, needs improvement

**What's Needed**:
- Structured logging for all trades
- Trade journal (database table)
- Performance tracking (win rate, P&L, drawdown)
- Email/Slack alerts for errors
- Daily summary reports

**Files to Create/Modify**:
- `/backend/services/trade_logger.py` (NEW)
- `/backend/models/trade_journal.py` (NEW - database model)
- Add logging to autonomous_trader.py

**Estimated Time**: 1-2 hours

---

### 6. **Safety Guardrails** (CRITICAL)
**Status**: ❌ Not implemented

**What's Needed**:
- Daily loss limit circuit breaker
- Max position count limit
- Max single position size
- VIX-based position reduction
- Consecutive loss pause mechanism
- Emergency shutdown API endpoint

**Files to Create/Modify**:
- `/backend/services/risk_manager.py` (NEW)
- Integrate into decision engine

**Estimated Time**: 1-2 hours

---

## 📋 Implementation Checklist

### Phase 1: Core Trading Logic (4-5 hours)
- [ ] **Fix position sizing** - Make it percentage-based (1h)
- [ ] **Create decision engine** - Candidate evaluation logic (2-3h)
- [ ] **Create risk manager** - Safety guardrails (1-2h)

### Phase 2: Autonomous Operation (3-4 hours)
- [ ] **Build autonomous trader** - Main orchestration loop (2h)
- [ ] **Add trade logging** - Database + structured logs (1-2h)
- [ ] **Set up scheduler** - Cron or systemd (1h)

### Phase 3: Testing & Validation (2-3 hours)
- [ ] **Test with paper account** - Run for 1-2 days (2h active testing)
- [ ] **Monitor performance** - Check logs, trades, P&L (1h)
- [ ] **Tune parameters** - Adjust thresholds based on results (1h)

---

## 🚀 Quick Start Path (Minimal Viable Autonomous Trader)

**Goal**: Get something running in 2-3 hours

### Step 1: Fix Position Sizing (30 min)
Update backtester and scanner to use percentage-based sizing:
```python
# Instead of: position_size = 1000
# Use: position_size = portfolio_value * 0.10
```

### Step 2: Simple Decision Engine (1 hour)
Create `/backend/services/simple_decision_engine.py`:
- Take top 3 candidates from scanner
- Check if we have cash
- Check if we're under max position count
- Return buy signals

### Step 3: Simple Autonomous Runner (1 hour)
Create `/backend/autonomous_trader_simple.py`:
- Scan every 5 minutes
- Execute top signals
- Monitor existing positions for profit target/stop loss
- Log to console

### Step 4: Manual Testing (30 min)
- Run: `python autonomous_trader_simple.py`
- Watch it scan and execute trades
- Verify orders appear in Alpaca paper account
- Check logs for errors

---

## 🎯 Recommended Approach

**I recommend starting with the Quick Start Path** to get something running today, then iterate:

1. **Today**: Build and test simple autonomous trader (2-3 hours)
2. **Tomorrow**: Add proper logging and risk management (2 hours)
3. **Day 3**: Set up cron job and let it run (1 hour)
4. **Day 4-7**: Monitor, tune, improve

This way you can show your son a working paper trading bot by tonight! 🚀

---

## Current Issues to Address

### Issue 1: Backtesting UI Spinner ✅ FIXED
- **Status**: Fixed in this session
- Polling logic now robust
- Success banner added
- Ready to test

### Issue 2: Position Sizing 🔴 CRITICAL
- **Status**: Needs fixing
- Blocking accurate backtest results
- Blocking live trading accuracy

### Issue 3: No Decision Logic 🔴 CRITICAL
- **Status**: Scanner finds candidates but nothing decides to trade
- Blocking autonomous operation

---

## Questions to Answer Before Starting

1. **Risk Tolerance**: Max position size as % of portfolio? (Recommend 5-10%)
2. **Max Positions**: How many stocks can be held at once? (Recommend 5-10)
3. **Daily Loss Limit**: What % loss should pause trading? (Recommend 3-5%)
4. **Profit Target**: Default profit target %? (Recommend 8-12%)
5. **Stop Loss**: Default stop loss %? (Recommend 4-6%)

---

## Next Immediate Action

**My recommendation**: Start with **Step 1 (Fix Position Sizing)** since it affects everything else.

Would you like me to:
1. Fix position sizing first?
2. Build simple decision engine?
3. Create autonomous trader?

Let me know what you want to tackle first and I'll implement it! 🚀
