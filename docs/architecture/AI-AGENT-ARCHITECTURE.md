# FInsightAI - AI Trading Agent Architecture
**Date:** December 23, 2025  
**Version:** 1.1  
**Status:** Design Phase  
**Last Updated:** December 23, 2025 (Added UI integration clarification)

---

## 🎯 Core Vision

**FInsightAI is an AI-powered trading agent that:**
1. **Researches stocks on demand** when user asks "Should I buy X?"
2. **Validates user decisions** when user says "I want to sell Y"
3. **Autonomously finds opportunities** by scanning the market 24/7
4. **Proposes trades** with full transparency (reasons, timing, amounts)
5. **Monitors existing positions** - recommends HOLD / BUY_MORE / SELL
6. **Learns from history** to improve recommendations over time

**Key Principle:** AI acts as a **collaborative partner**, not a black box. User always has final say.

---

## 🎨 UI Integration Strategy

**IMPORTANT:** We are **ENHANCING** the existing beautiful React/Tailwind UI, **NOT** rebuilding from scratch.

### What Stays The Same ✅
- ✅ Existing Dashboard layout and design
- ✅ Portfolio tab with current positions
- ✅ Market Data tab (live quotes)
- ✅ Navigation structure
- ✅ Tailwind CSS theme and styling
- ✅ All existing components

### What We're Adding 🆕
- 🆕 **Research Tab** - New tab for AI stock analysis
- 🆕 **Queue Tab** - New tab for pending transactions
- 🆕 **Dashboard Widget** - "Pending Actions" widget on existing dashboard
- 🆕 **Portfolio Enhancements** - Add AI status indicators (✅🎯⚠️) to existing position cards
- 🆕 **History Tab** - New tab for trade history with AI insights

### Integration Approach
- New components match existing design language
- Use existing Tailwind theme (colors, spacing, typography)
- Follow existing component patterns
- Add tabs to existing navigation (don't replace)
- Enhance existing screens, don't rebuild them

---

## 🏗️ System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Stock      │  │  Transaction │  │   Portfolio  │         │
│  │  Research    │  │    Queue     │  │   Dashboard  │         │
│  │   Panel      │  │   (Pending)  │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI)                          │
│  • /api/research/stock/{symbol}                                 │
│  • /api/research/validate-sell/{symbol}                         │
│  • /api/transactions/pending                                    │
│  • /api/transactions/{id}/approve                               │
│  • /api/transactions/{id}/modify                                │
│  • /api/agent/scan                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   AI AGENT CORE (Python)                        │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  1. AI RESEARCH ENGINE                                 │   │
│  │     • Stock Analyzer (fundamentals, technicals)        │   │
│  │     • News & Sentiment Scraper                         │   │
│  │     • Calendar Events (earnings, splits, etc.)         │   │
│  │     • Dual AI Verification (OpenAI + Claude)           │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  2. OPPORTUNITY SCANNER (Autonomous)                   │   │
│  │     • Market screener (finds candidates)               │   │
│  │     • Strategy-based filters (earnings, seasonality)   │   │
│  │     • Risk/reward calculator                           │   │
│  │     • Generates BUY proposals                          │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  3. POSITION MONITOR (Autonomous)                      │   │
│  │     • Tracks all open positions                        │   │
│  │     • Checks exit conditions (stop loss, target)       │   │
│  │     • Monitors news/events for held stocks             │   │
│  │     • Generates SELL proposals                         │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  4. TRANSACTION MANAGER                                │   │
│  │     • Pending transactions queue                       │   │
│  │     • User approval workflow                           │   │
│  │     • Auto-execution rules (based on confidence)       │   │
│  │     • Schwab API integration (actual execution)        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  5. LEARNING ENGINE                                    │   │
│  │     • Transaction history analysis                     │   │
│  │     • Win/loss pattern detection                       │   │
│  │     • Strategy performance tracking                    │   │
│  │     • Self-optimization feedback loop                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DATA LAYER (PostgreSQL)                        │
│  • users, portfolios, positions                                 │
│  • transactions (executed)                                      │
│  • pending_transactions (queue)                                 │
│  • ai_research_cache (avoid duplicate API calls)                │
│  • learning_history (for improvement)                           │
│  • strategy_configs (user preferences)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Three Core Workflows

### **Workflow 1: User-Initiated Research**
```
User Input: "Should I buy NVDA?"
↓
Frontend calls: POST /api/research/stock/NVDA
↓
AI Research Engine:
  1. Fetch fundamentals (P/E, EPS growth, revenue)
  2. Analyze technicals (RSI, MACD, support/resistance)
  3. Scrape recent news & social sentiment
  4. Check earnings calendar & upcoming events
  5. OpenAI generates recommendation
  6. Claude verifies & critiques
↓
Response:
{
  "symbol": "NVDA",
  "recommendation": "BUY" | "WAIT" | "AVOID",
  "confidence": 0.87,
  "entry_price": 145.50,
  "stop_loss": 141.15,
  "profit_target": 160.00,
  "position_size": 1500,
  "reasoning": {
    "openai": "Strong earnings momentum, AI sector growth...",
    "claude": "Confirmed. Valuation reasonable given growth rate..."
  },
  "risks": ["High volatility", "Overbought RSI"],
  "catalysts": ["Earnings on Jan 15", "New chip launch"],
  "wait_conditions": null | "Wait for dip below $140"
}
↓
Frontend displays:
  • Recommendation badge (BUY/WAIT/AVOID)
  • Confidence score with reasoning
  • Entry/stop/target prices
  • Suggested position size
  • Risks & catalysts
  • [Create Trade Proposal] button
↓
If user clicks button:
  → Creates pending transaction
  → Shows in Transaction Queue
```

### **Workflow 2: User-Initiated Sell Validation**
```
User Input: "I want to sell TSLA because it's overvalued"
↓
Frontend calls: POST /api/research/validate-sell/TSLA
{
  "user_reason": "overvalued",
  "current_position": { shares: 10, avg_cost: 210, current_price: 242 }
}
↓
AI Research Engine:
  1. Analyze current valuation metrics
  2. Check recent news for TSLA
  3. Assess social sentiment
  4. Compare to sector peers
  5. Calculate tax implications
  6. Review holding period
  7. OpenAI validates user reasoning
  8. Claude provides second opinion
↓
Response:
{
  "validation": "AGREE" | "WAIT" | "DISAGREE",
  "confidence": 0.78,
  "current_pnl": 320,
  "current_pnl_percent": 15.2,
  "reasoning": {
    "openai": "P/E of 82 is high for auto sector, but...",
    "claude": "Consider holding until post-earnings for tax efficiency..."
  },
  "alternative": "Hold until Jan 15 earnings, then reassess",
  "if_sell_now": {
    "proceeds": 2420,
    "tax_impact": "Short-term capital gains: ~$96"
  }
}
↓
Frontend displays:
  • Validation result (AGREE/WAIT/DISAGREE)
  • AI reasoning from both models
  • Current P&L
  • Tax implications
  • Alternative recommendations
  • [Create Sell Proposal] or [Keep Position] buttons
```

### **Workflow 3: Autonomous Agent Operation**
```
Background Process (runs every 15 minutes):

OPPORTUNITY SCANNER:
  1. Screen market for candidates:
     • Earnings plays (7 days before earnings)
     • Seasonality patterns (historical winners)
     • Breakout setups (technical triggers)
     • Macro opportunities (sector rotation)
  2. For each candidate:
     → Run AI Research Engine
     → Calculate risk/reward
     → If confidence > 75%:
        → Create pending BUY transaction
↓
POSITION MONITOR:
  1. Check all open positions:
     • Hit stop loss? → Create pending SELL
     • Hit profit target? → Create pending SELL
     • Bad news detected? → Research & propose SELL
     • Hold period expired? → Reassess & propose action
  2. For positions nearing exits:
     → Run AI validation
     → If confidence > 80%:
        → Create pending SELL transaction
↓
TRANSACTION QUEUE:
  ┌─────────────────────────────────────────┐
  │ PENDING TRANSACTIONS                    │
  ├─────────────────────────────────────────┤
  │                                         │
  │ [BUY] NVDA @ $145.50                    │
  │ AI Confidence: 87%                      │
  │ Strategy: Earnings Play                 │
  │ Amount: $1,500 (10% of portfolio)       │
  │ Scheduled: Tomorrow 9:35am              │
  │ Status: ⏰ PENDING USER APPROVAL        │
  │ [Approve] [Modify] [Reject] [Research] │
  │                                         │
  │ [SELL] TSLA @ $242.00                   │
  │ AI Confidence: 92%                      │
  │ Reason: Profit target hit (+15.2%)      │
  │ Purchased: $210 | Current: $242         │
  │ Scheduled: Today 2:00pm                 │
  │ Status: ⏰ AUTO-EXECUTE IN 2 HOURS      │
  │ [Approve Now] [Hold] [Research]         │
  │                                         │
  └─────────────────────────────────────────┘
↓
User Options:
  1. Approve → Execute immediately
  2. Modify → Change amount, price, timing
  3. Reject → Cancel proposal
  4. Research → Ask AI for more analysis
  5. Auto-execute → If confidence > threshold, executes automatically
```

---

## 🗄️ Database Schema Additions

### New Tables Required

```sql
-- Pending transactions (proposal queue)
CREATE TABLE pending_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID REFERENCES portfolios(id),
    transaction_type VARCHAR(10) NOT NULL, -- 'BUY' or 'SELL'
    symbol VARCHAR(20) NOT NULL,
    quantity DECIMAL(15, 4),
    proposed_price DECIMAL(10, 4) NOT NULL,
    stop_loss DECIMAL(10, 4),
    profit_target DECIMAL(10, 4),
    confidence DECIMAL(3, 2) NOT NULL, -- 0.00 to 1.00
    strategy_used VARCHAR(50),
    ai_reasoning JSONB NOT NULL, -- OpenAI + Claude responses
    risks JSONB,
    catalysts JSONB,
    scheduled_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, executed, cancelled
    auto_execute BOOLEAN DEFAULT false,
    created_by VARCHAR(20) NOT NULL, -- 'user' or 'agent'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI research cache (avoid duplicate API calls)
CREATE TABLE ai_research_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) NOT NULL,
    research_type VARCHAR(50) NOT NULL, -- 'buy_analysis', 'sell_validation', 'general'
    data JSONB NOT NULL,
    confidence DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '1 hour'
);

CREATE INDEX idx_research_cache_symbol_type ON ai_research_cache(symbol, research_type);
CREATE INDEX idx_research_cache_expires ON ai_research_cache(expires_at);

-- Learning history (for improvement)
CREATE TABLE learning_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id),
    predicted_outcome VARCHAR(20), -- What AI expected
    actual_outcome VARCHAR(20), -- What actually happened
    confidence_at_entry DECIMAL(3, 2),
    pnl_percent DECIMAL(8, 4),
    days_held INTEGER,
    strategy_used VARCHAR(50),
    what_went_right TEXT,
    what_went_wrong TEXT,
    lessons_learned JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_learning_history_strategy ON learning_history(strategy_used);
CREATE INDEX idx_learning_history_outcome ON learning_history(actual_outcome);
```

---

## 🔐 External Integrations

### Required APIs

1. **OpenAI GPT-4** (Primary AI)
   - Purpose: Generate recommendations, analyze stocks
   - Endpoint: `https://api.openai.com/v1/chat/completions`
   - Key: `OPENAI_API_KEY` (already configured)

2. **Anthropic Claude 3.5** (Verification AI)
   - Purpose: Verify OpenAI recommendations, catch errors
   - Endpoint: `https://api.anthropic.com/v1/messages`
   - Key: `ANTHROPIC_API_KEY` (already configured)

3. **Schwab API** (Trade Execution)
   - Purpose: Execute approved trades
   - Already integrated ✅

4. **Financial Data APIs** (Research)
   - **Option A:** Alpha Vantage (free tier, 25 calls/day)
   - **Option B:** Financial Modeling Prep (free tier, 250 calls/day)
   - **Option C:** Yahoo Finance (via yfinance, unlimited but slower)
   - **Recommendation:** Start with yfinance, upgrade to FMP later

5. **News & Sentiment** (Research)
   - **Option A:** News API (100 requests/day free)
   - **Option B:** Reddit/Twitter scraping (via PRAW/tweepy)
   - **Option C:** AI-powered web scraping (Claude with web search)
   - **Recommendation:** Start with News API + web scraping

---

## 🧪 Testing Strategy

### Progressive Testing Approach

1. **Phase 1:** User-initiated research (no execution)
   - Test: Ask AI about NVDA, TSLA, AAPL
   - Validate: Recommendations make sense
   - Verify: Dual AI model disagreements

2. **Phase 2:** Transaction queue UI (no execution)
   - Test: Create proposals manually
   - Validate: Queue displays correctly
   - Verify: Approve/reject/modify workflow

3. **Phase 3:** Paper trading execution
   - Test: Execute trades against paper portfolio
   - Validate: Position tracking works
   - Verify: P&L calculations correct

4. **Phase 4:** Autonomous scanning (paper only)
   - Test: Agent finds opportunities
   - Validate: Proposals make sense
   - Verify: Auto-execution threshold logic

5. **Phase 5:** Live trading (small amounts)
   - Test: Execute $10 trades (beta mode)
   - Validate: Schwab integration works
   - Verify: Risk limits enforced

---

## 🚀 Deployment Architecture

### Current State
- **Backend:** Railway (uvicorn on port 8000)
- **Frontend:** Local dev server (port 3000)
- **Database:** Railway PostgreSQL

### Production Goal
- **Backend:** Railway with auto-scaling
- **Frontend:** Vercel or Netlify (static deploy)
- **Database:** Railway PostgreSQL with backups
- **Background Jobs:** Railway cron jobs for agent

---

## 🔒 Security Considerations

1. **API Keys:** All stored in environment variables, never committed
2. **User Data:** Row-level security on portfolios table
3. **Trade Limits:** Max position size, daily loss limits enforced
4. **Auto-Execution:** Requires user approval for amounts > $500
5. **Data Validation:** All inputs sanitized, SQL injection prevented

---

## 📊 Success Metrics

### Technical Metrics
- AI recommendation accuracy: > 70%
- API response time: < 2 seconds
- Transaction queue latency: < 1 minute
- System uptime: > 99%

### User Experience Metrics
- User approval rate: > 60% (agent proposals)
- Average time to decision: < 5 minutes
- User satisfaction: Qualitative feedback

### Financial Metrics
- Win rate: > 55%
- Average gain: > 8%
- Max drawdown: < 15%
- Sharpe ratio: > 1.0

---

## 🔄 Future Enhancements

**Phase 6:** Multi-user authentication
**Phase 7:** Mobile app (React Native)
**Phase 8:** Advanced strategies (options, futures)
**Phase 9:** Social features (share trades, leaderboard)
**Phase 10:** Full autonomous mode (agent trades without approval)

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**Status:** Design Complete, Ready for Implementation
