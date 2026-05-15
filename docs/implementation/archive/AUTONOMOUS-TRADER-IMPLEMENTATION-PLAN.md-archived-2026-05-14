# Autonomous Paper Trading System - Complete Implementation Plan

**Project**: FInsightAI Autonomous Trading Bot  
**Goal**: Production-ready paper trading system with full risk management  
**Timeline**: 8-10 hours of focused implementation  
**Date**: March 7, 2026

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Implementation Phases](#implementation-phases)
3. [Risk Management Framework](#risk-management-framework)
4. [Testing Strategy](#testing-strategy)
5. [Deployment Plan](#deployment-plan)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## System Architecture

### High-Level Flow
```
┌─────────────────┐
│  Market Opens   │
│   9:30 AM ET    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   Autonomous Trading Loop           │
│   (Runs every 5 minutes)            │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│ Market Scanner  │─────▶│ Decision Engine  │
│ (3 strategies)  │      │ (Risk checks)    │
└─────────────────┘      └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  Risk Manager    │
                         │  (Guardrails)    │
                         └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ Trade Executor   │
                         │ (Alpaca API)     │
                         └─────────┬────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │  Trade Logger    │
                         │  (Database)      │
                         └──────────────────┘
```

### Components to Build

1. **Position Sizing Module** - Smart compounding position sizing
2. **Decision Engine** - Candidate evaluation and trade signals
3. **Risk Manager** - Safety guardrails and circuit breakers
4. **Trade Executor** - Order management and execution
5. **Trade Logger** - Comprehensive logging and journaling
6. **Autonomous Loop** - Main orchestration and scheduling
7. **Monitoring Dashboard** - Real-time status and alerts

---

## Implementation Phases

### Phase 1: Foundation (2-3 hours)

#### Task 1.1: Fix Position Sizing
**Status**: 🔴 CRITICAL  
**Time**: 30 minutes  
**Priority**: HIGH (blocks everything else)

**Current Problem**:
```python
# In backtester.py and market_scanner.py
position_size = 1000  # ❌ Fixed dollar amount
```

**Solution**:
```python
class PositionSizer:
    def __init__(self, initial_capital: float, position_size_pct: float = 0.10):
        self.initial_capital = initial_capital
        self.position_size_pct = position_size_pct  # 10% default
    
    def calculate_position_size(self, current_portfolio_value: float, 
                                current_price: float) -> int:
        """Calculate shares to buy based on % of portfolio"""
        dollar_size = current_portfolio_value * self.position_size_pct
        shares = int(dollar_size / current_price)
        return max(1, shares)  # At least 1 share
    
    def get_max_position_value(self, current_portfolio_value: float) -> float:
        """Get maximum position value in dollars"""
        return current_portfolio_value * self.position_size_pct
```

**Files to Modify**:
- `/backend/services/position_sizer.py` (NEW)
- `/backend/services/backtester.py` (update to use PositionSizer)
- `/backend/services/market_scanner.py` (update to use PositionSizer)

**Testing**:
- Unit test: $10k portfolio → $1k position (10%)
- Unit test: $15k portfolio → $1.5k position (10%)
- Integration test: Run backtest, verify position sizes compound

**Acceptance Criteria**:
- ✅ Position sizes scale with portfolio value
- ✅ Backtests show compounding returns
- ✅ No divide-by-zero errors for low prices

---

#### Task 1.2: Create Decision Engine
**Status**: 🔴 CRITICAL  
**Time**: 2 hours  
**Priority**: HIGH

**Purpose**: Decide WHICH opportunities to trade

**Logic Flow**:
```python
class DecisionEngine:
    def __init__(self, db: Session, config: Dict):
        self.db = db
        self.config = config
        self.position_sizer = PositionSizer(
            initial_capital=config['initial_capital'],
            position_size_pct=config['position_size_pct']
        )
    
    def evaluate_candidates(self, candidates: List[Dict], 
                          current_positions: List[Dict],
                          portfolio_value: float) -> List[TradeSignal]:
        """
        Evaluate scanner candidates and return trade signals
        
        Returns:
            List of TradeSignal objects with:
            - symbol
            - side (buy/sell)
            - quantity
            - order_type
            - stop_loss
            - profit_target
            - reason
            - confidence
        """
        signals = []
        
        # 1. Filter by confidence threshold
        high_confidence = [c for c in candidates if c['score'] >= 75]
        
        # 2. Check portfolio limits
        if len(current_positions) >= self.config['max_positions']:
            return []  # Max positions reached
        
        # 3. Check cash availability
        cash_available = self.get_available_cash()
        if cash_available < self.config['min_cash_reserve']:
            return []  # Keep cash reserve
        
        # 4. Sort by score, take top N
        top_candidates = sorted(high_confidence, 
                              key=lambda x: x['score'], 
                              reverse=True)[:3]
        
        # 5. Generate trade signals
        for candidate in top_candidates:
            # Calculate position size
            quantity = self.position_sizer.calculate_position_size(
                portfolio_value, 
                candidate['current_price']
            )
            
            # Create trade signal
            signal = TradeSignal(
                symbol=candidate['symbol'],
                side='buy',
                quantity=quantity,
                order_type='limit',
                limit_price=candidate['current_price'],
                stop_loss=self.calculate_stop_loss(candidate),
                profit_target=self.calculate_profit_target(candidate),
                reason=candidate['reason'],
                confidence=candidate['score']
            )
            
            signals.append(signal)
        
        return signals
```

**Configuration Parameters**:
```python
config = {
    'initial_capital': 10000,
    'position_size_pct': 0.10,  # 10% per position
    'max_positions': 5,          # Max 5 positions at once
    'min_confidence': 75,        # 75% minimum confidence
    'min_cash_reserve': 1000,    # Keep $1k cash
    'profit_target_pct': 0.12,   # 12% profit target
    'stop_loss_pct': 0.05,       # 5% stop loss
}
```

**Files to Create**:
- `/backend/services/decision_engine.py` (NEW)
- `/backend/models/trade_signal.py` (NEW - data model)

**Testing**:
- Unit test: Filter by confidence threshold
- Unit test: Respect max positions limit
- Unit test: Respect cash reserve
- Unit test: Calculate correct position sizes
- Integration test: End-to-end with scanner output

**Acceptance Criteria**:
- ✅ Only trades high-confidence candidates
- ✅ Respects all portfolio limits
- ✅ Generates valid trade signals
- ✅ Position sizing works correctly

---

#### Task 1.3: Create Risk Manager
**Status**: 🔴 CRITICAL  
**Time**: 1-2 hours  
**Priority**: HIGH

**Purpose**: Safety guardrails and circuit breakers

**Logic Flow**:
```python
class RiskManager:
    def __init__(self, db: Session, config: Dict):
        self.db = db
        self.config = config
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.is_paused = False
    
    def check_trade_allowed(self, signal: TradeSignal, 
                           portfolio_value: float,
                           current_positions: List) -> Tuple[bool, str]:
        """
        Check if trade is allowed by risk rules
        
        Returns:
            (allowed: bool, reason: str)
        """
        # 1. Check if trading is paused
        if self.is_paused:
            return False, "Trading paused due to risk limits"
        
        # 2. Check daily loss limit
        daily_loss_pct = (self.daily_loss / portfolio_value) * 100
        if daily_loss_pct >= self.config['daily_loss_limit_pct']:
            self.pause_trading("Daily loss limit reached")
            return False, f"Daily loss limit reached: {daily_loss_pct:.1f}%"
        
        # 3. Check max drawdown
        current_drawdown = self.calculate_drawdown(portfolio_value)
        if current_drawdown >= self.config['max_drawdown_pct']:
            self.pause_trading("Max drawdown reached")
            return False, f"Max drawdown: {current_drawdown:.1f}%"
        
        # 4. Check position limits
        if len(current_positions) >= self.config['max_positions']:
            return False, "Max positions reached"
        
        # 5. Check position size limits
        position_value = signal.quantity * signal.limit_price
        position_pct = (position_value / portfolio_value) * 100
        if position_pct > self.config['max_position_pct']:
            return False, f"Position too large: {position_pct:.1f}%"
        
        # 6. Check VIX threshold (reduce positions in high volatility)
        vix = self.get_current_vix()
        if vix > self.config['vix_threshold']:
            # Only allow if we have < half max positions
            if len(current_positions) >= self.config['max_positions'] / 2:
                return False, f"VIX too high: {vix:.1f}"
        
        # 7. Check consecutive losses
        if self.consecutive_losses >= self.config['consecutive_loss_limit']:
            self.pause_trading("Consecutive loss limit reached")
            return False, f"Too many consecutive losses: {self.consecutive_losses}"
        
        return True, "Trade allowed"
    
    def update_trade_result(self, trade_pnl: float):
        """Update risk metrics after trade closes"""
        self.daily_loss += trade_pnl
        
        if trade_pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0  # Reset on win
    
    def reset_daily_metrics(self):
        """Reset daily metrics at market open"""
        self.daily_loss = 0.0
        self.is_paused = False
```

**Configuration Parameters**:
```python
risk_config = {
    'max_position_pct': 10,         # Max 10% per position
    'max_positions': 5,              # Max 5 positions
    'daily_loss_limit_pct': 3,      # Stop if down 3% today
    'max_drawdown_pct': 15,          # Pause if down 15% from peak
    'vix_threshold': 25,             # Reduce positions if VIX > 25
    'consecutive_loss_limit': 5,     # Pause after 5 losses in a row
}
```

**Files to Create**:
- `/backend/services/risk_manager.py` (NEW)

**Testing**:
- Unit test: Daily loss limit triggers pause
- Unit test: Max drawdown triggers pause
- Unit test: Consecutive losses trigger pause
- Unit test: VIX threshold reduces positions
- Integration test: Full risk check flow

**Acceptance Criteria**:
- ✅ All circuit breakers work
- ✅ Pausing mechanism works
- ✅ Metrics update correctly
- ✅ Reset at market open

---

### Phase 2: Execution (2-3 hours)

#### Task 2.1: Create Trade Executor
**Status**: 🟡 MEDIUM  
**Time**: 1-2 hours  
**Priority**: MEDIUM

**Purpose**: Execute trades via Alpaca API

**Logic Flow**:
```python
class TradeExecutor:
    def __init__(self, alpaca_service: AlpacaService, db: Session):
        self.alpaca = alpaca_service
        self.db = db
    
    def execute_signal(self, signal: TradeSignal) -> Dict:
        """
        Execute a trade signal
        
        Returns:
            {
                'success': bool,
                'order_id': str,
                'message': str
            }
        """
        try:
            # 1. Submit order to Alpaca
            order = self.alpaca.submit_order(
                symbol=signal.symbol,
                qty=signal.quantity,
                side=signal.side,
                type=signal.order_type,
                time_in_force='day',
                limit_price=signal.limit_price if signal.order_type == 'limit' else None
            )
            
            # 2. Create stop loss order
            if signal.stop_loss:
                self.alpaca.submit_order(
                    symbol=signal.symbol,
                    qty=signal.quantity,
                    side='sell',
                    type='stop',
                    time_in_force='gtc',
                    stop_price=signal.stop_loss
                )
            
            # 3. Create take profit order
            if signal.profit_target:
                self.alpaca.submit_order(
                    symbol=signal.symbol,
                    qty=signal.quantity,
                    side='sell',
                    type='limit',
                    time_in_force='gtc',
                    limit_price=signal.profit_target
                )
            
            return {
                'success': True,
                'order_id': order.id,
                'message': f"Order submitted: {signal.symbol} x{signal.quantity}"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return {
                'success': False,
                'order_id': None,
                'message': str(e)
            }
```

**Files to Create**:
- `/backend/services/trade_executor.py` (NEW)

**Testing**:
- Unit test: Order submission (mocked Alpaca)
- Unit test: Stop loss creation
- Unit test: Profit target creation
- Unit test: Error handling
- Integration test: End-to-end with paper account

**Acceptance Criteria**:
- ✅ Orders submit successfully
- ✅ Stop loss orders created
- ✅ Profit targets created
- ✅ Errors handled gracefully

---

#### Task 2.2: Create Trade Logger
**Status**: 🟡 MEDIUM  
**Time**: 1 hour  
**Priority**: MEDIUM

**Purpose**: Comprehensive logging and trade journaling

**Database Model**:
```python
class TradeJournal(Base):
    __tablename__ = 'trade_journal'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String(10), nullable=False)
    side = Column(String(4), nullable=False)  # buy/sell
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    profit_target = Column(Float)
    strategy = Column(String(50))
    confidence = Column(Float)
    reason = Column(Text)
    order_id = Column(String(100))
    status = Column(String(20))  # open/closed/cancelled
    pnl = Column(Float)
    pnl_pct = Column(Float)
    hold_duration = Column(Integer)  # minutes
    exit_reason = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Logger Class**:
```python
class TradeLogger:
    def __init__(self, db: Session):
        self.db = db
    
    def log_trade_entry(self, signal: TradeSignal, order_id: str):
        """Log trade entry"""
        entry = TradeJournal(
            symbol=signal.symbol,
            side=signal.side,
            quantity=signal.quantity,
            entry_price=signal.limit_price,
            stop_loss=signal.stop_loss,
            profit_target=signal.profit_target,
            strategy=signal.strategy,
            confidence=signal.confidence,
            reason=signal.reason,
            order_id=order_id,
            status='open'
        )
        self.db.add(entry)
        self.db.commit()
    
    def log_trade_exit(self, order_id: str, exit_price: float, 
                      exit_reason: str):
        """Log trade exit"""
        trade = self.db.query(TradeJournal).filter_by(
            order_id=order_id
        ).first()
        
        if trade:
            trade.exit_price = exit_price
            trade.exit_reason = exit_reason
            trade.status = 'closed'
            trade.pnl = (exit_price - trade.entry_price) * trade.quantity
            trade.pnl_pct = ((exit_price / trade.entry_price) - 1) * 100
            trade.hold_duration = (datetime.utcnow() - trade.created_at).seconds // 60
            self.db.commit()
```

**Files to Create**:
- `/backend/models/trade_journal.py` (NEW)
- `/backend/services/trade_logger.py` (NEW)

**Testing**:
- Unit test: Entry logging
- Unit test: Exit logging
- Unit test: P&L calculation
- Integration test: Full trade lifecycle

**Acceptance Criteria**:
- ✅ All trades logged to database
- ✅ P&L calculated correctly
- ✅ Trade history queryable

---

### Phase 3: Orchestration (2-3 hours)

#### Task 3.1: Build Autonomous Trading Loop
**Status**: 🔴 CRITICAL  
**Time**: 2 hours  
**Priority**: HIGH

**Main Loop**:
```python
class AutonomousTrader:
    def __init__(self, config: Dict):
        self.config = config
        self.db = get_db_session()
        self.alpaca = get_alpaca_service(paper=True)
        self.scanner = MarketScanner(self.db)
        self.decision_engine = DecisionEngine(self.db, config)
        self.risk_manager = RiskManager(self.db, config['risk'])
        self.trade_executor = TradeExecutor(self.alpaca, self.db)
        self.trade_logger = TradeLogger(self.db)
        self.is_running = False
    
    def start(self):
        """Start autonomous trading"""
        logger.info("🚀 Starting autonomous trading bot...")
        self.is_running = True
        
        # Reset daily metrics
        self.risk_manager.reset_daily_metrics()
        
        while self.is_running:
            try:
                # 1. Check if market is open
                if not self.is_market_open():
                    logger.info("Market is closed. Waiting...")
                    time.sleep(60)
                    continue
                
                # 2. Scan for opportunities
                logger.info("🔍 Scanning market for opportunities...")
                candidates = self.scanner.scan_all_strategies()
                logger.info(f"Found {len(candidates)} candidates")
                
                # 3. Get current portfolio state
                portfolio = self.alpaca.get_account()
                positions = self.alpaca.get_positions()
                portfolio_value = float(portfolio.portfolio_value)
                
                # 4. Generate trade signals
                signals = self.decision_engine.evaluate_candidates(
                    candidates, 
                    positions, 
                    portfolio_value
                )
                logger.info(f"Generated {len(signals)} trade signals")
                
                # 5. Check risk limits and execute
                for signal in signals:
                    allowed, reason = self.risk_manager.check_trade_allowed(
                        signal, 
                        portfolio_value, 
                        positions
                    )
                    
                    if allowed:
                        result = self.trade_executor.execute_signal(signal)
                        if result['success']:
                            self.trade_logger.log_trade_entry(
                                signal, 
                                result['order_id']
                            )
                            logger.info(f"✅ Trade executed: {signal.symbol}")
                        else:
                            logger.error(f"❌ Trade failed: {result['message']}")
                    else:
                        logger.warning(f"⚠️  Trade blocked: {reason}")
                
                # 6. Monitor existing positions
                self.monitor_positions(positions)
                
                # 7. Wait for next scan
                logger.info(f"💤 Sleeping for {self.config['scan_interval']}s...")
                time.sleep(self.config['scan_interval'])
                
            except Exception as e:
                logger.error(f"❌ Error in trading loop: {e}")
                time.sleep(60)
    
    def monitor_positions(self, positions):
        """Monitor open positions for exit conditions"""
        for position in positions:
            # Check if profit target or stop loss hit
            current_price = float(position.current_price)
            entry_price = float(position.avg_entry_price)
            pnl_pct = ((current_price / entry_price) - 1) * 100
            
            # Close if profit target hit
            if pnl_pct >= self.config['profit_target_pct']:
                self.close_position(position, "Profit target reached")
            
            # Close if stop loss hit
            elif pnl_pct <= -self.config['stop_loss_pct']:
                self.close_position(position, "Stop loss hit")
    
    def close_position(self, position, reason: str):
        """Close a position"""
        try:
            self.alpaca.close_position(position.symbol)
            self.trade_logger.log_trade_exit(
                position.order_id,
                float(position.current_price),
                reason
            )
            logger.info(f"📤 Closed {position.symbol}: {reason}")
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
```

**Configuration File** (`config.yaml`):
```yaml
trading:
  initial_capital: 10000
  position_size_pct: 0.10
  scan_interval: 300  # 5 minutes
  min_confidence: 75
  profit_target_pct: 12
  stop_loss_pct: 5

risk:
  max_position_pct: 10
  max_positions: 5
  daily_loss_limit_pct: 3
  max_drawdown_pct: 15
  vix_threshold: 25
  consecutive_loss_limit: 5
  min_cash_reserve: 1000

market:
  open_time: "09:30"
  close_time: "16:00"
  timezone: "US/Eastern"
```

**Files to Create**:
- `/backend/autonomous_trader.py` (NEW)
- `/backend/config/trading_config.yaml` (NEW)

**Testing**:
- Unit test: Market hours check
- Unit test: Position monitoring
- Integration test: Full loop (dry run)
- Integration test: With paper account

**Acceptance Criteria**:
- ✅ Runs continuously during market hours
- ✅ Scans and executes trades
- ✅ Monitors positions
- ✅ Handles errors gracefully

---

#### Task 3.2: Create Scheduler
**Status**: 🟡 MEDIUM  
**Time**: 1 hour  
**Priority**: MEDIUM

**Systemd Service** (`/etc/systemd/system/finsightai-trader.service`):
```ini
[Unit]
Description=FInsightAI Autonomous Trading Bot
After=network.target postgresql.service

[Service]
Type=simple
User=christian
WorkingDirectory=/Users/christian/Repos/f.insight.AI Advanced/backend
Environment="PATH=/Users/christian/Repos/f.insight.AI Advanced/backend/venv/bin"
ExecStart=/Users/christian/Repos/f.insight.AI Advanced/backend/venv/bin/python autonomous_trader.py
Restart=on-failure
RestartSec=30
StandardOutput=append:/var/log/finsightai/trader.log
StandardError=append:/var/log/finsightai/trader-error.log

[Install]
WantedBy=multi-user.target
```

**Python Scheduler Alternative**:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Start trading at 9:30 AM ET, Monday-Friday
    scheduler.add_job(
        start_trading,
        CronTrigger(
            day_of_week='mon-fri',
            hour=9,
            minute=30,
            timezone='US/Eastern'
        ),
        id='start_trading'
    )
    
    # Stop trading at 4:00 PM ET
    scheduler.add_job(
        stop_trading,
        CronTrigger(
            day_of_week='mon-fri',
            hour=16,
            minute=0,
            timezone='US/Eastern'
        ),
        id='stop_trading'
    )
    
    scheduler.start()
    logger.info("📅 Scheduler started")
```

**Files to Create**:
- `/backend/scheduler.py` (NEW)
- `finsightai-trader.service` (systemd)

**Testing**:
- Manual test: Start/stop via systemd
- Manual test: Check logs
- Manual test: Auto-restart on crash

**Acceptance Criteria**:
- ✅ Auto-starts at market open
- ✅ Auto-stops at market close
- ✅ Restarts on failure
- ✅ Logs to file

---

### Phase 4: Monitoring (1-2 hours)

#### Task 4.1: Create Monitoring Dashboard
**Status**: 🟢 NICE TO HAVE  
**Time**: 1-2 hours  
**Priority**: LOW

**Status API Endpoint**:
```python
@router.get("/api/trader/status")
async def get_trader_status():
    """Get current trading bot status"""
    return {
        'is_running': trader.is_running,
        'is_paused': trader.risk_manager.is_paused,
        'daily_pnl': trader.get_daily_pnl(),
        'open_positions': len(trader.get_positions()),
        'trades_today': trader.get_trades_today_count(),
        'last_scan': trader.last_scan_time.isoformat(),
        'next_scan': trader.next_scan_time.isoformat(),
    }
```

**Files to Create**:
- `/backend/api/trader_status.py` (NEW)
- `/frontend/src/components/TraderDashboard.js` (NEW)

---

## Risk Management Framework

### Circuit Breakers
1. **Daily Loss Limit**: Pause if down 3% in one day
2. **Max Drawdown**: Pause if down 15% from peak
3. **Consecutive Losses**: Pause after 5 losses in a row
4. **VIX Threshold**: Reduce positions when VIX > 25
5. **Position Limits**: Max 5 positions, 10% each

### Position Sizing Rules
- **Base Size**: 10% of current portfolio value
- **Scaling**: Reduces automatically as portfolio shrinks
- **Minimum**: At least 1 share
- **Maximum**: Never exceed 10% of portfolio

### Emergency Shutdown
```python
# Emergency stop via API
POST /api/trader/emergency-stop
{
    "reason": "Manual intervention required"
}
```

---

## Testing Strategy

### Unit Tests
- Position sizing calculations
- Decision engine logic
- Risk manager checks
- Trade signal generation

### Integration Tests
- Scanner → Decision → Risk → Execute flow
- Position monitoring and exit logic
- Error handling and recovery
- Database operations

### Paper Trading Tests
1. **Day 1**: Run with very small positions ($100 each)
2. **Day 2-3**: Monitor behavior, check logs
3. **Day 4-5**: Increase to normal position sizes
4. **Week 2**: Full production settings

### Acceptance Tests
- [ ] Trades only during market hours
- [ ] Respects all risk limits
- [ ] Position sizes compound properly
- [ ] Logs all activity
- [ ] Recovers from errors
- [ ] Can be paused/resumed

---

## Deployment Plan

### Pre-Deployment Checklist
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Database migrations run
- [ ] Configuration file created
- [ ] Logs directory created
- [ ] Paper trading account funded

### Deployment Steps
1. Deploy code to production server
2. Run database migrations
3. Create systemd service
4. Start service
5. Monitor logs for 1 hour
6. Verify trades appearing in Alpaca

### Rollback Plan
If issues occur:
1. Stop systemd service: `sudo systemctl stop finsightai-trader`
2. Check logs: `/var/log/finsightai/`
3. Fix issues
4. Redeploy
5. Restart: `sudo systemctl start finsightai-trader`

---

## Monitoring & Alerts

### Metrics to Monitor
- Trades executed per day
- Win rate (rolling 30 days)
- Daily P&L
- Max drawdown (current)
- Open positions count
- Cash balance
- Error rate

### Alerts
- Email on trading pause
- Slack on daily loss > 2%
- SMS on system crash
- Daily summary report at 4:30 PM

---

## Success Criteria

### Week 1
- [ ] System runs without crashing
- [ ] Executes 5-10 trades
- [ ] No risk limit violations
- [ ] Logs are complete and readable

### Month 1
- [ ] Win rate > 50%
- [ ] Positive total return
- [ ] Max drawdown < 10%
- [ ] No manual interventions needed

### Quarter 1
- [ ] Win rate > 55%
- [ ] Return > 10%
- [ ] Sharpe ratio > 1.5
- [ ] Ready for live trading consideration

---

## Next Steps

**Immediate** (Today):
1. Read and approve this plan
2. Answer risk tolerance questions
3. Review configuration parameters

**Tomorrow**:
1. Start Phase 1 implementation
2. Fix position sizing
3. Build decision engine

**This Weekend**:
1. Complete all phases
2. Deploy to paper trading
3. Monitor first trades

Let's build this right! 🚀
