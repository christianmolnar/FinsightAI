# Autonomous Trader - Testing Framework

**Project**: FInsightAI Autonomous Trading Bot  
**Purpose**: Comprehensive testing strategy for production deployment  
**Date**: March 7, 2026

---

## Testing Philosophy

**"Test in production-like conditions, but with paper money"**

- All tests run against real Alpaca paper trading account
- Use real market data feeds
- Simulate real market hours and conditions
- Test failure scenarios extensively

---

## Test Phases

### Phase 1: Unit Tests (1-2 hours)

#### Position Sizing Tests
```python
# tests/unit/test_position_sizer.py

def test_position_size_10_percent():
    """Position size should be 10% of portfolio"""
    sizer = PositionSizer(initial_capital=10000, position_size_pct=0.10)
    portfolio_value = 10000
    current_price = 100.0
    
    shares = sizer.calculate_position_size(portfolio_value, current_price)
    expected_shares = 10  # $1000 / $100 = 10 shares
    
    assert shares == expected_shares

def test_position_size_compounds():
    """Position size should grow with portfolio"""
    sizer = PositionSizer(initial_capital=10000, position_size_pct=0.10)
    
    # Portfolio grows to $15k
    shares_at_15k = sizer.calculate_position_size(15000, 100.0)
    assert shares_at_15k == 15  # $1500 / $100 = 15 shares
    
    # Portfolio shrinks to $8k
    shares_at_8k = sizer.calculate_position_size(8000, 100.0)
    assert shares_at_8k == 8  # $800 / $100 = 8 shares

def test_minimum_one_share():
    """Should always buy at least 1 share"""
    sizer = PositionSizer(initial_capital=10000, position_size_pct=0.10)
    
    # High-priced stock
    shares = sizer.calculate_position_size(10000, 5000.0)
    assert shares >= 1
```

#### Risk Manager Tests
```python
# tests/unit/test_risk_manager.py

def test_daily_loss_limit_triggers_pause():
    """Should pause trading at daily loss limit"""
    config = {'daily_loss_limit_pct': 3}
    rm = RiskManager(db, config)
    
    # Simulate 3% loss
    rm.daily_loss = -300  # $300 loss
    portfolio_value = 10000
    
    allowed, reason = rm.check_trade_allowed(signal, portfolio_value, [])
    assert not allowed
    assert "Daily loss limit" in reason
    assert rm.is_paused

def test_consecutive_losses_trigger_pause():
    """Should pause after consecutive losses"""
    config = {'consecutive_loss_limit': 5}
    rm = RiskManager(db, config)
    
    # Simulate 5 losses
    for i in range(5):
        rm.update_trade_result(-10.0)
    
    assert rm.consecutive_losses == 5
    allowed, reason = rm.check_trade_allowed(signal, 10000, [])
    assert not allowed

def test_wins_reset_consecutive_losses():
    """Wins should reset loss counter"""
    config = {'consecutive_loss_limit': 5}
    rm = RiskManager(db, config)
    
    # 3 losses, then a win
    for i in range(3):
        rm.update_trade_result(-10.0)
    rm.update_trade_result(50.0)  # Win
    
    assert rm.consecutive_losses == 0
```

#### Decision Engine Tests
```python
# tests/unit/test_decision_engine.py

def test_filters_by_confidence():
    """Should only trade high-confidence candidates"""
    config = {'min_confidence': 75}
    de = DecisionEngine(db, config)
    
    candidates = [
        {'symbol': 'AAPL', 'score': 85, 'current_price': 150},
        {'symbol': 'MSFT', 'score': 65, 'current_price': 300},  # Too low
    ]
    
    signals = de.evaluate_candidates(candidates, [], 10000)
    assert len(signals) == 1
    assert signals[0].symbol == 'AAPL'

def test_respects_max_positions():
    """Should not trade if max positions reached"""
    config = {'max_positions': 3, 'min_confidence': 75}
    de = DecisionEngine(db, config)
    
    # Already have 3 positions
    current_positions = [
        {'symbol': 'AAPL'}, {'symbol': 'MSFT'}, {'symbol': 'GOOGL'}
    ]
    
    candidates = [{'symbol': 'TSLA', 'score': 90, 'current_price': 200}]
    
    signals = de.evaluate_candidates(candidates, current_positions, 10000)
    assert len(signals) == 0

def test_respects_cash_reserve():
    """Should keep minimum cash reserve"""
    config = {'min_cash_reserve': 1000, 'min_confidence': 75}
    de = DecisionEngine(db, config)
    
    # Portfolio: $2000 total, but need $1000 reserve
    # So only $1000 available for trading
    candidates = [
        {'symbol': 'AAPL', 'score': 85, 'current_price': 500},  # Would cost $500
        {'symbol': 'MSFT', 'score': 85, 'current_price': 500},  # Would cost $500
        {'symbol': 'GOOGL', 'score': 85, 'current_price': 500}, # Can't afford
    ]
    
    signals = de.evaluate_candidates(candidates, [], 2000)
    assert len(signals) <= 2  # Can only afford 2 trades
```

---

### Phase 2: Integration Tests (2-3 hours)

#### End-to-End Trading Flow
```python
# tests/integration/test_trading_flow.py

def test_full_trading_cycle():
    """Test complete flow from scan to execution"""
    # 1. Create test environment
    trader = AutonomousTrader(test_config)
    
    # 2. Mock market scanner to return known candidates
    mock_candidates = [
        {
            'symbol': 'AAPL',
            'score': 85,
            'current_price': 150.0,
            'reason': 'Strong earnings',
            'strategy': 'earnings'
        }
    ]
    trader.scanner.scan_all_strategies = lambda: mock_candidates
    
    # 3. Run one iteration
    trader.run_single_iteration()
    
    # 4. Verify trade was executed
    positions = trader.alpaca.get_positions()
    assert len(positions) == 1
    assert positions[0].symbol == 'AAPL'
    
    # 5. Verify trade was logged
    trades = trader.db.query(TradeJournal).filter_by(symbol='AAPL').all()
    assert len(trades) == 1
    assert trades[0].status == 'open'

def test_position_monitoring_closes_winner():
    """Test that profitable positions are closed"""
    trader = AutonomousTrader(test_config)
    
    # 1. Create mock position with 12% profit
    mock_position = MockPosition(
        symbol='AAPL',
        qty=10,
        avg_entry_price=100.0,
        current_price=112.0  # +12%
    )
    
    # 2. Monitor positions
    trader.monitor_positions([mock_position])
    
    # 3. Verify position was closed
    close_orders = trader.alpaca.get_orders(symbol='AAPL', status='filled')
    assert len(close_orders) > 0
    
    # 4. Verify exit was logged
    trade = trader.db.query(TradeJournal).filter_by(symbol='AAPL').first()
    assert trade.status == 'closed'
    assert trade.exit_reason == 'Profit target reached'

def test_position_monitoring_stops_loss():
    """Test that losing positions are stopped out"""
    trader = AutonomousTrader(test_config)
    
    # 1. Create mock position with -5% loss
    mock_position = MockPosition(
        symbol='AAPL',
        qty=10,
        avg_entry_price=100.0,
        current_price=95.0  # -5%
    )
    
    # 2. Monitor positions
    trader.monitor_positions([mock_position])
    
    # 3. Verify position was closed
    trade = trader.db.query(TradeJournal).filter_by(symbol='AAPL').first()
    assert trade.status == 'closed'
    assert trade.exit_reason == 'Stop loss hit'
```

#### Error Handling Tests
```python
# tests/integration/test_error_handling.py

def test_recovers_from_alpaca_api_error():
    """Should continue running after API errors"""
    trader = AutonomousTrader(test_config)
    
    # Mock Alpaca to raise error once
    call_count = 0
    def mock_get_account():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise APIError("Connection timeout")
        return MockAccount()
    
    trader.alpaca.get_account = mock_get_account
    
    # Should log error but continue
    trader.run_single_iteration()
    assert call_count == 2  # Retried after error

def test_recovers_from_database_error():
    """Should handle database errors gracefully"""
    trader = AutonomousTrader(test_config)
    
    # Mock database error
    trader.db.commit = lambda: raise_exception(DatabaseError("Connection lost"))
    
    # Should log error but not crash
    try:
        trader.run_single_iteration()
    except DatabaseError:
        pytest.fail("Should have caught database error")
```

---

### Phase 3: Paper Trading Tests (3-5 days)

#### Day 1: Small Position Test
**Objective**: Verify basic functionality with minimal risk

**Configuration**:
```yaml
trading:
  initial_capital: 10000
  position_size_pct: 0.01  # Only 1% positions ($100 each)
  scan_interval: 300
  min_confidence: 85  # Very high threshold

risk:
  max_positions: 2  # Only 2 positions max
  daily_loss_limit_pct: 1  # Very conservative
```

**Expected Behavior**:
- Trade 0-2 times today
- Position sizes ~$100
- No risk limit violations

**Success Criteria**:
- [ ] Bot runs all day without crashing
- [ ] Trades execute successfully
- [ ] Positions are monitored
- [ ] Logs are complete

---

#### Day 2-3: Normal Operations Test
**Objective**: Test with realistic settings

**Configuration**:
```yaml
trading:
  initial_capital: 10000
  position_size_pct: 0.10  # 10% positions
  scan_interval: 300
  min_confidence: 75

risk:
  max_positions: 5
  daily_loss_limit_pct: 3
```

**Expected Behavior**:
- Trade 2-5 times per day
- Position sizes ~$1000
- Some winners, some losers

**Success Criteria**:
- [ ] System operates autonomously
- [ ] Risk limits respected
- [ ] P&L tracked accurately
- [ ] No manual intervention needed

---

#### Day 4-5: Stress Test
**Objective**: Test under challenging market conditions

**Scenarios to Test**:
1. **High Volatility Day**: VIX > 25
   - Should reduce positions
   - More conservative entries

2. **Gap Down Open**: Portfolio starts down 2%
   - Risk manager should be cautious
   - May hit daily loss limit quickly

3. **Consecutive Losers**: Force 3-4 losses in a row
   - Verify consecutive loss tracking
   - Check if pauses after limit

4. **Max Positions Reached**: Force 5 open positions
   - Should not open new trades
   - Should monitor existing positions

**Success Criteria**:
- [ ] All circuit breakers work
- [ ] System doesn't over-trade in volatility
- [ ] Pauses when risk limits hit
- [ ] Recovers gracefully

---

### Phase 4: Acceptance Tests

#### Test 1: Market Hours Compliance
```python
def test_only_trades_during_market_hours():
    """Verify trading only during market hours"""
    trader = AutonomousTrader(test_config)
    
    # Test at various times
    test_times = [
        ('2026-03-10 08:00:00', False),  # Before open
        ('2026-03-10 09:30:00', True),   # Market open
        ('2026-03-10 14:00:00', True),   # Mid-day
        ('2026-03-10 16:00:00', False),  # Market closed
        ('2026-03-15 10:00:00', False),  # Saturday
    ]
    
    for time_str, should_trade in test_times:
        with freeze_time(time_str):
            is_open = trader.is_market_open()
            assert is_open == should_trade
```

#### Test 2: Position Sizing Accuracy
```python
def test_position_sizes_are_correct():
    """Verify position sizes match configuration"""
    trader = AutonomousTrader(test_config)
    
    # Run for 1 day
    trades = run_trader_for_day(trader)
    
    # Check each trade
    for trade in trades:
        portfolio_value_at_entry = get_portfolio_value_at(trade.created_at)
        expected_value = portfolio_value_at_entry * 0.10
        actual_value = trade.quantity * trade.entry_price
        
        # Allow 5% variance (due to rounding)
        assert abs(actual_value - expected_value) / expected_value < 0.05
```

#### Test 3: Risk Limit Enforcement
```python
def test_all_risk_limits_enforced():
    """Comprehensive risk limit test"""
    trader = AutonomousTrader(test_config)
    
    # Run until a risk limit is hit
    while not trader.risk_manager.is_paused:
        trader.run_single_iteration()
        time.sleep(60)
        
        # Force losses if needed for testing
        if need_to_test_loss_limit:
            force_losing_trades(trader)
    
    # Verify correct limit was triggered
    assert trader.risk_manager.is_paused
    
    # Verify no trades executed after pause
    trades_before = get_trade_count()
    trader.run_single_iteration()
    trades_after = get_trade_count()
    assert trades_before == trades_after
```

---

## Test Data & Fixtures

### Mock Objects
```python
# tests/fixtures/mock_alpaca.py

class MockAlpacaService:
    def __init__(self):
        self.positions = []
        self.orders = []
        self.account = MockAccount(
            portfolio_value=10000,
            cash=10000
        )
    
    def submit_order(self, symbol, qty, side, **kwargs):
        order = MockOrder(
            symbol=symbol,
            qty=qty,
            side=side,
            status='filled'
        )
        self.orders.append(order)
        return order
    
    def get_positions(self):
        return self.positions
    
    def close_position(self, symbol):
        self.positions = [p for p in self.positions if p.symbol != symbol]
```

### Test Database
```python
# tests/fixtures/test_database.py

@pytest.fixture
def test_db():
    """Create temporary test database"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
```

---

## Performance Benchmarks

### Targets
- **Scan time**: < 30 seconds for 100 stocks
- **Decision time**: < 5 seconds
- **Order execution**: < 2 seconds
- **Full loop**: < 60 seconds

### Measurement
```python
def test_performance_benchmarks():
    trader = AutonomousTrader(test_config)
    
    # Measure scan time
    start = time.time()
    candidates = trader.scanner.scan_all_strategies()
    scan_time = time.time() - start
    assert scan_time < 30
    
    # Measure decision time
    start = time.time()
    signals = trader.decision_engine.evaluate_candidates(...)
    decision_time = time.time() - start
    assert decision_time < 5
```

---

## Test Execution Plan

### Daily Testing Schedule
```bash
# Morning (before market open)
pytest tests/unit/ -v
pytest tests/integration/ -v

# During market hours
python tests/paper_trading/run_live_test.py

# After market close
python tests/analysis/analyze_daily_results.py
```

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: Test Autonomous Trader

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit/ -v
      - name: Run integration tests
        run: pytest tests/integration/ -v
      - name: Check test coverage
        run: pytest --cov=services --cov-report=html
```

---

## Success Metrics

### Code Coverage
- **Target**: > 80% coverage
- **Critical paths**: 100% coverage
  - Position sizing
  - Risk management
  - Trade execution

### Test Pass Rate
- **Unit tests**: 100% passing
- **Integration tests**: 100% passing
- **Paper trading**: 95%+ success rate

### Performance
- **Win rate**: > 50%
- **Profit factor**: > 1.2
- **Max drawdown**: < 15%
- **Sharpe ratio**: > 1.0

---

## Test Reports

### Daily Test Report Template
```markdown
# Paper Trading Test Report - [Date]

## Summary
- Trades Executed: X
- Win Rate: X%
- P&L: $X
- Max Drawdown: X%
- Issues Found: X

## Detailed Results
| Time | Symbol | Side | Qty | Entry | Exit | P&L | Reason |
|------|--------|------|-----|-------|------|-----|--------|
| ...  | ...    | ...  | ... | ...   | ...  | ... | ...    |

## Issues
1. [Description]
   - Severity: High/Medium/Low
   - Action: [Fix required]

## Recommendations
- [Suggestion 1]
- [Suggestion 2]
```

---

## When to Ship to Production

### Checklist
- [ ] All unit tests passing (100%)
- [ ] All integration tests passing (100%)
- [ ] 5 days of paper trading without crashes
- [ ] Win rate > 50%
- [ ] Max drawdown < 10%
- [ ] No risk limit violations
- [ ] Code review complete
- [ ] Documentation complete
- [ ] Monitoring setup
- [ ] Rollback plan ready

### Go/No-Go Decision
**GO** if all checklist items checked  
**NO-GO** if any critical issues remain

---

Ready to start testing! 🧪
