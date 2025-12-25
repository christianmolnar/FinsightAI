# Autonomous Trading Agent Architecture

**Document Version:** 1.0  
**Created:** December 25, 2025  
**Status:** Planning - Phase 4  
**Owner:** FInsightAI AI Team

---

## 📋 Table of Contents

1. [Vision & Objectives](#vision--objectives)
2. [System Architecture](#system-architecture)
3. [Agent Components](#agent-components)
4. [Decision Framework](#decision-framework)
5. [Autonomous Bounds](#autonomous-bounds)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Technical Specifications](#technical-specifications)

---

## Vision & Objectives

### The Autonomous Agent

An AI-powered trading assistant that operates 24/7 to:

1. **Monitor** - Continuously analyze held positions and market conditions
2. **Discover** - Actively scan for new trading opportunities
3. **Decide** - Make intelligent buy/sell decisions within defined bounds
4. **Execute** - Automatically trade within authorized limits
5. **Recommend** - Suggest opportunities outside bounds for user approval

### Core Philosophy

**"Autonomy with Oversight"**
- Agent operates independently within safe boundaries
- User retains ultimate control over risky decisions
- Full transparency: Every decision explained
- Learning system: Improves from outcomes

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (React)                        │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │  Dashboard     │  │  Opportunities  │  │  Agent Controls  │  │
│  │  (Overview)    │  │  (Pending)      │  │  (Bounds Config) │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              │ WebSocket + REST API
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│                      BACKEND (FastAPI)                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         AUTONOMOUS AGENT ORCHESTRATOR                       │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Portfolio   │  │ Opportunity  │  │  Execution   │    │ │
│  │  │  Monitor     │  │   Scanner    │  │   Engine     │    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │ │
│  │         │                  │                  │            │ │
│  └─────────┼──────────────────┼──────────────────┼────────────┘ │
│            │                  │                  │              │
│            ▼                  ▼                  ▼              │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              DECISION FRAMEWORK                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ Risk         │  │ Confidence   │  │ Bounds       │  │  │
│  │  │ Analyzer     │  │ Scorer       │  │ Checker      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              AI SERVICES                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ GPT-4        │  │ Claude 3.5   │  │ Technical    │  │  │
│  │  │ (Strategy)   │  │ (Validation) │  │ Analysis     │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              DATA LAYER                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │ PostgreSQL   │  │ Redis Cache  │  │ Event Log    │  │  │
│  │  │ (Portfolio)  │  │ (Market Data)│  │ (Decisions)  │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                              │
                              │ External APIs
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Schwab API   │  │ News APIs    │  │ Market Data APIs     │  │
│  │ (Trading)    │  │ (Sentiment)  │  │ (Technical Analysis) │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└───────────────────────────────────────────────────────────────────┘
```

---

## Agent Components

### 1. Portfolio Monitor

**Purpose:** Continuously analyze held positions

**Responsibilities:**
- Monitor all positions in real-time
- Track performance vs benchmarks
- Detect stop-loss triggers
- Identify rebalancing opportunities
- Calculate risk metrics (concentration, volatility, beta)

**Analysis Cycle:**
```python
# Runs every 5 minutes during market hours
async def portfolio_monitoring_cycle():
    while market_is_open():
        # Fetch current positions
        positions = await get_portfolio_positions()
        
        # For each position
        for position in positions:
            # 1. Check stop-loss conditions
            if position.unrealized_pnl_pct < -position.stop_loss_pct:
                await create_sell_opportunity(
                    symbol=position.symbol,
                    reason="Stop-loss triggered",
                    urgency="HIGH",
                    auto_execute=True  # Within bounds
                )
            
            # 2. Check take-profit conditions
            if position.unrealized_pnl_pct > position.take_profit_pct:
                await create_sell_opportunity(
                    symbol=position.symbol,
                    reason="Take-profit target reached",
                    urgency="MEDIUM",
                    auto_execute=False  # Requires approval
                )
            
            # 3. Check rebalancing needs
            if abs(position.weight - position.target_weight) > 0.05:
                await create_rebalance_opportunity(
                    symbol=position.symbol,
                    current_weight=position.weight,
                    target_weight=position.target_weight
                )
            
            # 4. AI position analysis
            ai_analysis = await analyze_position_with_ai(position)
            if ai_analysis.action == "SELL" and ai_analysis.confidence > 0.8:
                await create_sell_opportunity(
                    symbol=position.symbol,
                    reason=ai_analysis.reasoning,
                    confidence=ai_analysis.confidence,
                    auto_execute=False  # AI suggestions require approval
                )
        
        await asyncio.sleep(300)  # 5 minutes
```

**Output:**
- Position health scores (0-100)
- Risk alerts (high concentration, volatility spikes)
- Rebalancing recommendations
- Stop-loss/take-profit triggers

---

### 2. Opportunity Scanner

**Purpose:** Discover new trading opportunities

**Responsibilities:**
- Scan universe of tradable symbols (S&P 500, NASDAQ 100, custom watchlist)
- Technical analysis (RSI, MACD, Bollinger Bands, volume patterns)
- Fundamental screening (P/E ratios, growth rates, margins)
- News sentiment analysis
- AI-powered opportunity identification
- Generate confidence scores (0-100)

**Scanning Process:**
```python
# Runs every 15 minutes during market hours
async def opportunity_scanning_cycle():
    while market_is_open():
        # 1. Define symbol universe
        symbols = await get_scan_universe()  # S&P 500 + watchlist
        
        # 2. Batch fetch market data
        market_data = await fetch_market_data_batch(symbols)
        
        # 3. Technical screening
        technical_signals = await screen_technical_indicators(market_data)
        # RSI < 30 (oversold) or > 70 (overbought)
        # MACD crossovers
        # Bollinger Band breakouts
        # Volume spikes (>2x average)
        
        # 4. Fundamental screening
        fundamental_signals = await screen_fundamentals(symbols)
        # P/E < sector average
        # Revenue growth > 20%
        # Profit margins improving
        
        # 5. News sentiment
        news_signals = await analyze_news_sentiment(symbols)
        # Positive news sentiment spikes
        # Earnings beats
        # Product announcements
        
        # 6. AI opportunity detection
        for symbol in technical_signals.top_50():
            ai_analysis = await analyze_opportunity_with_ai(
                symbol=symbol,
                technical=technical_signals[symbol],
                fundamental=fundamental_signals[symbol],
                news=news_signals[symbol]
            )
            
            if ai_analysis.confidence > 70:
                await create_buy_opportunity(
                    symbol=symbol,
                    entry_price=market_data[symbol].current_price,
                    target_price=ai_analysis.target_price,
                    stop_loss=ai_analysis.stop_loss,
                    confidence=ai_analysis.confidence,
                    reasoning=ai_analysis.reasoning,
                    auto_execute=(ai_analysis.confidence > 85 and 
                                  position_size_within_bounds())
                )
        
        await asyncio.sleep(900)  # 15 minutes
```

**Screening Filters:**

**Technical Indicators:**
- RSI < 30 (oversold) or RSI > 70 (overbought)
- MACD bullish crossover
- Price breaking above Bollinger upper band
- Volume > 2x 20-day average

**Fundamental Criteria:**
- P/E ratio < sector median
- Revenue growth > 15% YoY
- Operating margin > 10%
- Debt/Equity < 1.0

**News Sentiment:**
- Positive news score > 0.6
- Recent earnings beat
- Analyst upgrades
- Product launch announcements

**Output:**
- Opportunity queue (ranked by confidence)
- Entry prices, targets, stop-losses
- Reasoning and evidence
- Auto-execute flag (if within bounds)

---

### 3. Execution Engine

**Purpose:** Execute trading decisions

**Responsibilities:**
- Validate opportunities against bounds
- Calculate position sizes
- Place orders (market, limit)
- Monitor execution status
- Handle partial fills
- Log all trades with full context

**Execution Flow:**
```python
async def execute_opportunity(opportunity: Opportunity):
    # 1. Validate against autonomous bounds
    if not await check_autonomous_bounds(opportunity):
        # Requires user approval
        await add_to_approval_queue(opportunity)
        await notify_user_approval_needed(opportunity)
        return
    
    # 2. Calculate position size
    portfolio_value = await get_portfolio_value()
    risk_per_trade = portfolio_value * 0.01  # 1% risk per trade
    
    # Position size based on stop-loss distance
    stop_loss_distance = abs(opportunity.entry_price - opportunity.stop_loss)
    shares = risk_per_trade / stop_loss_distance
    
    # Respect maximum position size (5% of portfolio)
    max_position = portfolio_value * 0.05
    position_value = shares * opportunity.entry_price
    if position_value > max_position:
        shares = max_position / opportunity.entry_price
    
    # 3. Check available cash
    available_cash = await get_available_cash()
    total_cost = shares * opportunity.entry_price
    if total_cost > available_cash:
        logger.warning(f"Insufficient cash for {opportunity.symbol}: "
                       f"Need ${total_cost}, have ${available_cash}")
        return
    
    # 4. Place order
    order = await place_order(
        symbol=opportunity.symbol,
        side="BUY" if opportunity.type == "BUY" else "SELL",
        quantity=shares,
        order_type="LIMIT",
        limit_price=opportunity.entry_price,
        stop_loss=opportunity.stop_loss,
        take_profit=opportunity.target_price
    )
    
    # 5. Monitor execution
    await monitor_order_execution(order)
    
    # 6. Log decision
    await log_trade_decision(
        opportunity=opportunity,
        order=order,
        reasoning=opportunity.reasoning,
        confidence=opportunity.confidence
    )
    
    # 7. Notify user
    await notify_user_trade_executed(order)
```

**Position Sizing Logic:**
- **Risk-based:** 1% portfolio risk per trade
- **Stop-loss aware:** Size calculated from stop distance
- **Maximum position:** No single position > 5% portfolio value
- **Cash management:** Never exceed 95% invested (5% cash buffer)

---

## Decision Framework

### Risk Analyzer

**Purpose:** Assess risk for every opportunity

**Risk Factors:**
1. **Position Concentration Risk**
   - Current: What % of portfolio is this symbol?
   - Sector: What % of portfolio is this sector?
   - Limit: No symbol > 10%, no sector > 25%

2. **Volatility Risk**
   - ATR (Average True Range) analysis
   - Beta vs S&P 500
   - High volatility = smaller position size

3. **Liquidity Risk**
   - Average daily volume
   - Bid-ask spread
   - Market cap
   - Avoid illiquid stocks (volume < 500K shares/day)

4. **Correlation Risk**
   - How correlated with existing positions?
   - Avoid adding highly correlated positions

**Risk Score Calculation:**
```python
def calculate_risk_score(opportunity: Opportunity, portfolio: Portfolio) -> float:
    """Calculate risk score 0-100 (100 = highest risk)"""
    
    risk_factors = []
    
    # Concentration risk
    symbol_exposure = portfolio.get_position_weight(opportunity.symbol)
    sector_exposure = portfolio.get_sector_weight(opportunity.sector)
    risk_factors.append(min(symbol_exposure * 10, 40))  # Max 40 points
    risk_factors.append(min(sector_exposure * 4, 30))    # Max 30 points
    
    # Volatility risk
    volatility = opportunity.technical_data.volatility_percentile
    risk_factors.append(volatility * 0.2)  # Max 20 points
    
    # Liquidity risk
    if opportunity.technical_data.avg_volume < 500000:
        risk_factors.append(10)  # Illiquid stock penalty
    
    return sum(risk_factors)
```

### Confidence Scorer

**Purpose:** Generate confidence score for each opportunity

**Scoring Factors:**
1. **Technical Strength (40%)**
   - Multiple indicators aligned? (+10 each)
   - Strong volume confirmation? (+10)
   - Clear trend? (+10)

2. **Fundamental Quality (30%)**
   - Strong financials? (+10)
   - Growth trajectory? (+10)
   - Competitive moat? (+10)

3. **AI Analysis (20%)**
   - GPT-4 recommendation strength
   - Claude validation agreement
   - Reasoning quality

4. **News Sentiment (10%)**
   - Positive recent news?
   - Earnings beat?
   - Analyst upgrades?

**Confidence Calculation:**
```python
def calculate_confidence_score(opportunity: Opportunity) -> float:
    """Calculate confidence 0-100"""
    
    score = 0
    
    # Technical (40 points max)
    if opportunity.technical.rsi_oversold:
        score += 10
    if opportunity.technical.macd_bullish_cross:
        score += 10
    if opportunity.technical.volume_spike:
        score += 10
    if opportunity.technical.trend == "STRONG_UP":
        score += 10
    
    # Fundamental (30 points max)
    if opportunity.fundamental.pe_attractive:
        score += 10
    if opportunity.fundamental.growth_rate > 20:
        score += 10
    if opportunity.fundamental.margins_improving:
        score += 10
    
    # AI (20 points max)
    score += opportunity.ai_analysis.gpt4_score * 0.1
    score += opportunity.ai_analysis.claude_score * 0.1
    
    # News (10 points max)
    score += opportunity.news_sentiment * 10
    
    return min(score, 100)
```

---

## Autonomous Bounds

### What Agent Can Do Automatically

**Tier 1: Full Autonomy (No Approval)**
- ✅ Close positions when stop-loss hit
- ✅ Rebalance positions within 5% of target weights
- ✅ Take profit when target reached (< 5% of portfolio)
- ✅ Sell losing positions < $500 loss
- ✅ Execute high-confidence opportunities (>85%) with position size < 2% portfolio

**Tier 2: Conditional Autonomy (Auto-approve if conditions met)**
- ⚠️ New positions with confidence > 80% AND risk score < 30
- ⚠️ Sell decisions with confidence > 75%
- ⚠️ Position increases (averaging down) if within risk limits

**Tier 3: Requires Approval**
- ❌ New positions > 5% of portfolio value
- ❌ Sell decisions resulting in > $1000 realized loss
- ❌ Opportunitiesoutside watchlist
- ❌ Options trading
- ❌ Short selling
- ❌ Margin trading
- ❌ After-hours trading

### Configuration

**User-Adjustable Bounds:**
```python
class AutonomousBounds(BaseModel):
    # Position sizing
    max_position_size_pct: float = 5.0  # % of portfolio
    max_sector_exposure_pct: float = 25.0
    min_cash_reserve_pct: float = 5.0
    
    # Risk limits
    max_risk_per_trade_pct: float = 1.0  # % portfolio risk
    max_daily_loss_pct: float = 2.0
    max_drawdown_pct: float = 10.0
    
    # Confidence thresholds
    min_auto_execute_confidence: float = 85.0
    min_approval_confidence: float = 70.0
    
    # Autonomous actions
    allow_auto_stop_loss: bool = True
    allow_auto_take_profit: bool = True
    allow_auto_rebalance: bool = True
    allow_auto_buys: bool = False  # Conservative default
    
    # Position limits
    max_positions: int = 20
    min_liquidity_volume: int = 500000  # shares/day
```

---

## Implementation Roadmap

### Phase 4A: Portfolio Monitor (Week 1)
**Goal:** Monitor held positions continuously

**Tasks:**
- [ ] Create `PortfolioMonitor` service class
- [ ] Implement background worker process
- [ ] Add stop-loss detection logic
- [ ] Add take-profit detection logic
- [ ] Add rebalancing logic
- [ ] Create `portfolio_opportunities` table in DB
- [ ] Build monitor dashboard UI
- [ ] Add WebSocket for real-time updates

**Success Criteria:**
- Monitor runs 24/7 without crashes
- Stop-loss triggers detected within 1 minute
- UI shows live position health scores

### Phase 4B: Opportunity Scanner (Week 2)
**Goal:** Discover new trading opportunities

**Tasks:**
- [ ] Create `OpportunityScanner` service class
- [ ] Implement technical screening pipeline
- [ ] Add fundamental data fetching
- [ ] Integrate news sentiment API
- [ ] Build opportunity scoring system
- [ ] Create `opportunities` table in DB
- [ ] Build opportunities queue UI
- [ ] Add opportunity detail modal

**Success Criteria:**
- Scanner finds 10-20 opportunities daily
- Confidence scores correlate with outcomes (backtest)
- UI displays ranked opportunities with reasoning

### Phase 4C: Decision Framework (Week 3)
**Goal:** Intelligent decision-making

**Tasks:**
- [ ] Create `DecisionEngine` service class
- [ ] Implement risk scoring algorithm
- [ ] Implement confidence scoring algorithm
- [ ] Build autonomous bounds checker
- [ ] Create decision logging system
- [ ] Add bounds configuration UI
- [ ] Build decision history dashboard

**Success Criteria:**
- Risk scores validated against historical volatility
- Bounds respected 100% of time
- All decisions logged with full context

### Phase 4D: Execution Engine (Week 4)
**Goal:** Automated trade execution

**Tasks:**
- [ ] Create `ExecutionEngine` service class
- [ ] Implement position sizing logic
- [ ] Add order placement integration
- [ ] Build order monitoring system
- [ ] Implement execution logging
- [ ] Add user notification system
- [ ] Build execution history UI

**Success Criteria:**
- Orders execute within 30 seconds
- Position sizing respects risk limits
- User notified within 1 minute of execution

### Phase 4E: Integration & Testing (Week 5)
**Goal:** Full autonomous agent operational

**Tasks:**
- [ ] Integrate all components
- [ ] End-to-end testing (paper trading)
- [ ] Performance testing (handle 500+ symbols)
- [ ] Failure mode testing
- [ ] Documentation
- [ ] User training materials

**Success Criteria:**
- Agent operates autonomously for 5 days without intervention
- 80%+ confidence opportunities outperform benchmark
- Zero unauthorized trades

---

## Technical Specifications

### Background Worker Process

**Technology:** Python asyncio + APScheduler

```python
# /backend/app/services/autonomous_agent.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class AutonomousAgent:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.portfolio_monitor = PortfolioMonitor()
        self.opportunity_scanner = OpportunityScanner()
        self.decision_engine = DecisionEngine()
        self.execution_engine = ExecutionEngine()
    
    def start(self):
        """Start the autonomous agent"""
        # Portfolio monitoring - every 5 minutes
        self.scheduler.add_job(
            self.portfolio_monitor.run_cycle,
            'interval',
            minutes=5,
            id='portfolio_monitor'
        )
        
        # Opportunity scanning - every 15 minutes
        self.scheduler.add_job(
            self.opportunity_scanner.run_cycle,
            'interval',
            minutes=15,
            id='opportunity_scanner'
        )
        
        # Decision processing - every 1 minute
        self.scheduler.add_job(
            self.process_opportunities,
            'interval',
            minutes=1,
            id='decision_processor'
        )
        
        self.scheduler.start()
        logger.info("🤖 Autonomous agent started")
    
    async def process_opportunities(self):
        """Process pending opportunities"""
        opportunities = await get_pending_opportunities()
        
        for opp in opportunities:
            # Risk analysis
            risk_score = await self.decision_engine.calculate_risk(opp)
            
            # Confidence scoring
            confidence = await self.decision_engine.calculate_confidence(opp)
            
            # Check bounds
            if await self.decision_engine.within_autonomous_bounds(opp):
                # Auto-execute
                await self.execution_engine.execute(opp)
            else:
                # Requires approval
                await add_to_approval_queue(opp)
                await notify_user(opp)
```

### Database Schema

```sql
-- Opportunities table
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    type VARCHAR(10) NOT NULL,  -- 'BUY' or 'SELL'
    entry_price NUMERIC(10, 2) NOT NULL,
    target_price NUMERIC(10, 2),
    stop_loss NUMERIC(10, 2),
    confidence_score NUMERIC(5, 2) NOT NULL,
    risk_score NUMERIC(5, 2) NOT NULL,
    reasoning TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'PENDING', 'APPROVED', 'REJECTED', 'EXECUTED'
    auto_execute BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_symbol (symbol),
    INDEX idx_created (created_at DESC)
);

-- Decision log table
CREATE TABLE decision_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id UUID REFERENCES opportunities(id),
    decision VARCHAR(20) NOT NULL,  -- 'AUTO_EXECUTE', 'REQUIRE_APPROVAL', 'REJECT'
    risk_factors JSONB,
    bounds_check JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent configuration table
CREATE TABLE agent_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,  -- Future: per-user config
    bounds JSONB NOT NULL,  -- AutonomousBounds JSON
    active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```python
# /backend/app/api/autonomous.py

@router.get("/api/agent/status")
async def get_agent_status():
    """Get autonomous agent status"""
    return {
        "running": agent.is_running(),
        "last_portfolio_scan": agent.portfolio_monitor.last_run,
        "last_opportunity_scan": agent.opportunity_scanner.last_run,
        "pending_opportunities": await count_pending_opportunities(),
        "auto_executed_today": await count_todays_executions()
    }

@router.get("/api/opportunities")
async def list_opportunities(status: str = "PENDING"):
    """List opportunities"""
    return await get_opportunities(status=status)

@router.post("/api/opportunities/{id}/approve")
async def approve_opportunity(id: UUID):
    """Approve an opportunity for execution"""
    await execute_opportunity(id)
    return {"success": True}

@router.post("/api/opportunities/{id}/reject")
async def reject_opportunity(id: UUID, reason: str):
    """Reject an opportunity"""
    await reject_opportunity_with_reason(id, reason)
    return {"success": True}

@router.get("/api/agent/config")
async def get_agent_config():
    """Get agent configuration (bounds)"""
    return await load_agent_config()

@router.put("/api/agent/config")
async def update_agent_config(config: AutonomousBounds):
    """Update agent configuration"""
    await save_agent_config(config)
    return {"success": True}
```

---

## Success Metrics

**Operational Metrics:**
- Uptime: Agent runs 99.9% of market hours
- Latency: Opportunities processed within 60 seconds
- Accuracy: 80%+ of auto-executed trades profitable

**Trading Metrics:**
- Win rate: > 55% of trades profitable
- Risk-adjusted return: Sharpe ratio > 1.5
- Max drawdown: < 10%
- Outperformance: Beat S&P 500 by 5%+ annually

**User Experience:**
- Notification response time: < 1 minute
- False positive rate: < 20% (opportunities user rejects)
- User confidence: 80%+ of users trust agent recommendations

---

**Document Owner:** AI Development Team  
**Review Schedule:** Weekly during Phase 4 development  
**Feedback:** Update this document as architecture evolves
