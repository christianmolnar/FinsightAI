# FInsightAI - User Experience Specification
**Date:** December 23, 2025  
**Version:** 1.0  
**Status:** Design Phase

---

## 🎯 Product Vision

**FInsightAI is your AI-powered trading partner** that helps you make better investment decisions by:
- Researching stocks on demand when you're curious
- Validating your buy/sell ideas with data-driven analysis
- Finding opportunities you might have missed
- Proposing trades with full transparency
- Learning from every trade to get smarter over time

**Core Principle:** You're always in control. AI advises, you decide.

---

## 👤 User Personas

### Primary User: Christian (The Active Trader)
- **Background:** Tech-savvy, understands trading basics
- **Goals:** Make profitable trades, learn from mistakes, save time on research
- **Pain Points:** Too many stocks to research, emotional trading decisions, missing opportunities
- **Usage Pattern:** Checks app daily, reviews AI proposals, executes 3-5 trades/week

### Secondary User: Future Users (Aspirational)
- **Background:** Beginners to intermediate traders
- **Goals:** Learn trading, build confidence, grow capital slowly
- **Pain Points:** Information overload, fear of losses, don't know what to buy
- **Usage Pattern:** Checks app 2-3x/week, follows AI recommendations, executes 1-2 trades/week

---

## 🖥️ User Interface Design

### Main Navigation Structure

```
┌─────────────────────────────────────────────────────────────┐
│  FInsightAI                    🔔 Notifications    👤 User  │
├─────────────────────────────────────────────────────────────┤
│  [Dashboard] [Research] [Queue] [Portfolio] [History]       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📱 Screen-by-Screen User Flows

### 1. Dashboard (Home Screen)

**Purpose:** Quick overview of portfolio status and pending actions

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                         DASHBOARD                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Portfolio Value: $12,450                                   │
│  Daily Change: +$125 (+1.02%) ↑                            │
│  Cash Available: $2,800                                     │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔔 PENDING ACTIONS (2)                             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  [BUY] NVDA @ $145.50 - AI Confidence: 87%         │   │
│  │  Scheduled: Tomorrow 9:35am                         │   │
│  │  [Review] [Approve] [Reject]                        │   │
│  │                                                     │   │
│  │  [SELL] TSLA @ $242.00 - Profit Target Hit        │   │
│  │  Auto-executes in 2 hours                          │   │
│  │  [Review] [Cancel]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  📊 OPEN POSITIONS (4)                              │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  AAPL  120 shares  $182.50  +$450 (+2.5%)  ✅      │   │
│  │  MSFT   80 shares  $378.20  +$890 (+3.1%)  ✅      │   │
│  │  TSLA   10 shares  $242.00  +$320 (+15.2%) 🎯      │   │
│  │  GOOGL  50 shares  $142.80  -$125 (-1.8%)  ⚠️      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 AI AGENT STATUS                                 │   │
│  │  ● Active - Last scan: 5 minutes ago               │   │
│  │  Monitoring 4 positions, scanning 50 opportunities │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**User Interactions:**
- Click position → View details and AI insights
- Click pending action → Review full proposal
- Click "Approve" → Execute trade immediately
- Click "Review" → Deep dive into AI reasoning

---

### 2. Research Screen (Stock Analysis)

**Purpose:** Ask AI to research any stock

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                      STOCK RESEARCH                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Search: [NVDA___________________________] [Research]       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  NVIDIA CORPORATION (NVDA) - $145.50               │   │
│  │  +$2.30 (+1.6%) Today                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 AI RECOMMENDATION                               │   │
│  │                                                     │   │
│  │  ✅ STRONG BUY                                      │   │
│  │  Confidence: 87%                                    │   │
│  │                                                     │   │
│  │  Entry Price: $145.50                               │   │
│  │  Stop Loss: $141.15 (-3.0%)                        │   │
│  │  Profit Target: $160.00 (+10.0%)                   │   │
│  │  Position Size: $1,500 (10% of portfolio)          │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ 💡 WHY BUY NOW (OpenAI)                      │ │   │
│  │  │                                               │ │   │
│  │  │ • Strong Q4 earnings beat (+23% EPS)         │ │   │
│  │  │ • AI chip demand exceeding supply            │ │   │
│  │  │ • New H200 chip launching in Q1              │ │   │
│  │  │ • Technical breakout above $140 resistance   │ │   │
│  │  │ • Bullish MACD crossover                     │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ ✓ VERIFICATION (Claude)                      │ │   │
│  │  │                                               │ │   │
│  │  │ Confirmed: Recommendation is sound.           │ │   │
│  │  │                                               │ │   │
│  │  │ Additional considerations:                    │ │   │
│  │  │ • Valuation at 35x forward P/E is justified  │ │   │
│  │  │ • Consider scaling in if dips below $143     │ │   │
│  │  │ • Watch for profit-taking after earnings     │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ⚠️ RISKS:                                          │   │
│  │  • High volatility (50% higher than market)        │   │
│  │  • RSI at 72 (slightly overbought)                 │   │
│  │  • Sector rotation risk if rates rise              │   │
│  │                                                     │   │
│  │  📅 UPCOMING CATALYSTS:                             │   │
│  │  • Jan 15: Next earnings report                    │   │
│  │  • Jan 20: AI chip conference keynote              │   │
│  │  • Feb 1: Q1 guidance update                       │   │
│  │                                                     │   │
│  │  [Create Buy Proposal] [Save Research]             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**User Flow:**
1. User types "NVDA" and clicks "Research"
2. System shows loading animation (~3-5 seconds)
3. AI displays recommendation with reasoning
4. User reads OpenAI and Claude analyses
5. User clicks "Create Buy Proposal" if interested
6. Proposal added to Transaction Queue

**Edge Cases:**
- Stock not found: "NVDA not found. Did you mean NVDA?"
- API timeout: "Research taking longer than expected. Please try again."
- AI disagrees: Show split screen with both recommendations

---

### 3. Sell Validation Screen

**Purpose:** Validate user's decision to sell a position

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                    SELL VALIDATION                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Position: TSLA - 10 shares @ $210.00 avg cost             │
│  Current Price: $242.00 (+15.2%)                            │
│  Unrealized P&L: +$320                                      │
│                                                             │
│  Why do you want to sell?                                   │
│  [x] Profit target reached                                  │
│  [ ] Stock is overvalued                                    │
│  [ ] Need cash for another opportunity                      │
│  [ ] Bad news/concerns                                      │
│  [ ] Other: [_________________________]                     │
│                                                             │
│  [Get AI Validation]                                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🤖 AI VALIDATION                                   │   │
│  │                                                     │   │
│  │  ✅ AGREE - Good time to sell                       │   │
│  │  Confidence: 78%                                    │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ 💡 ANALYSIS (OpenAI)                         │ │   │
│  │  │                                               │ │   │
│  │  │ Your profit target logic is sound:            │ │   │
│  │  │ • +15% gain exceeds your 10% target          │ │   │
│  │  │ • Stock showing signs of exhaustion          │ │   │
│  │  │ • RSI at 78 (overbought)                     │ │   │
│  │  │ • Volume declining on recent rally           │ │   │
│  │  │                                               │ │   │
│  │  │ However, consider:                            │ │   │
│  │  │ • Earnings in 3 days (potential catalyst)    │ │   │
│  │  │ • Might wait for post-earnings move          │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ ✓ SECOND OPINION (Claude)                    │ │   │
│  │  │                                               │ │   │
│  │  │ Slight disagreement:                          │ │   │
│  │  │                                               │ │   │
│  │  │ Recommend: WAIT 3 days until after earnings  │ │   │
│  │  │                                               │ │   │
│  │  │ Reasoning:                                    │ │   │
│  │  │ • Historical pattern: +8% avg post-earnings  │ │   │
│  │  │ • Tax efficiency: Hold 3 more days for       │ │   │
│  │  │   long-term capital gains                    │ │   │
│  │  │ • Risk: Small (-2% if earnings miss)         │ │   │
│  │  │ • Reward: Large (+8% if earnings beat)       │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  💰 IF YOU SELL NOW:                                │   │
│  │  • Proceeds: $2,420                                 │   │
│  │  • Profit: $320 (+15.2%)                            │   │
│  │  • Tax Impact: ~$96 (short-term capital gains)     │   │
│  │                                                     │   │
│  │  💰 IF YOU WAIT 3 DAYS:                             │   │
│  │  • Best case: $2,613 (+24% total)                  │   │
│  │  • Worst case: $2,371 (+13% total)                 │   │
│  │  • Tax Impact: ~$48 (long-term capital gains)      │   │
│  │                                                     │   │
│  │  [Sell Now] [Wait & Reassess] [Keep Position]      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**User Flow:**
1. User navigates to position and clicks "Sell"
2. User selects reason for selling
3. User clicks "Get AI Validation"
4. AI shows both perspectives (OpenAI + Claude)
5. User decides: Sell now, wait, or keep
6. If sell: Creates proposal in Transaction Queue

---

### 4. Transaction Queue Screen

**Purpose:** Review and manage all pending trades

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                    TRANSACTION QUEUE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Filters: [All] [Buys] [Sells] [Auto-Execute] [Manual]    │
│  Sort by: [Confidence ▼] [Amount] [Scheduled Time]         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🟢 BUY - NVDA                                      │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  Proposed by: 🤖 AI Agent                           │   │
│  │  Confidence: 87% (High)                             │   │
│  │  Strategy: Earnings Play                            │   │
│  │                                                     │   │
│  │  Entry: $145.50                                     │   │
│  │  Stop Loss: $141.15 (-3.0%)                        │   │
│  │  Target: $160.00 (+10.0%)                          │   │
│  │  Amount: $1,500 (10 shares)                         │   │
│  │                                                     │   │
│  │  ⏰ Scheduled: Tomorrow at 9:35am (market open)     │   │
│  │  Status: ⏳ AWAITING YOUR APPROVAL                  │   │
│  │                                                     │   │
│  │  💡 Why AI Recommends:                              │   │
│  │  "Strong earnings beat, AI chip demand surge,      │   │
│  │   technical breakout above resistance..."          │   │
│  │   [Read Full Analysis]                              │   │
│  │                                                     │   │
│  │  [Approve & Execute] [Modify] [Reject] [Research]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🔴 SELL - TSLA                                     │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  Proposed by: 🤖 AI Agent                           │   │
│  │  Confidence: 92% (Very High)                        │   │
│  │  Reason: Profit Target Hit                          │   │
│  │                                                     │   │
│  │  Entry: $210.00 (14 days ago)                       │   │
│  │  Current: $242.00                                   │   │
│  │  P&L: +$320 (+15.2%)                               │   │
│  │  Shares: 10                                         │   │
│  │                                                     │   │
│  │  ⏰ Scheduled: Today at 2:00pm                      │   │
│  │  Status: 🤖 AUTO-EXECUTE in 1h 42m                  │   │
│  │                                                     │   │
│  │  💡 Why AI Recommends:                              │   │
│  │  "Profit target achieved, RSI overbought,          │   │
│  │   momentum weakening..." [Read Full Analysis]       │   │
│  │                                                     │   │
│  │  [Execute Now] [Hold Position] [Modify Time]       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  🟢 BUY - AAPL                                      │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  Proposed by: 👤 You (Manual Research)              │   │
│  │  Confidence: 72% (Medium)                           │   │
│  │  Strategy: User Discretion                          │   │
│  │                                                     │   │
│  │  Entry: $182.50                                     │   │
│  │  Amount: $2,000 (10 shares)                         │   │
│  │                                                     │   │
│  │  ⏰ Scheduled: User discretion                      │   │
│  │  Status: ⏳ DRAFT                                    │   │
│  │                                                     │   │
│  │  [Finalize & Submit] [Delete Draft]                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**User Interactions:**
- **Approve & Execute:** Trade executes immediately
- **Modify:** Opens dialog to change amount, price, or timing
- **Reject:** Removes from queue (with optional feedback to AI)
- **Research:** Asks AI for more detailed analysis
- **Auto-execute countdown:** Visual timer shows when trade will happen
- **Expand/collapse:** Click card to see full reasoning

**Auto-Execute Logic:**
```
IF confidence >= 85% AND amount <= $500:
  → Auto-execute after 2 hours (user can cancel)
ELSE IF confidence >= 75%:
  → Auto-execute after 4 hours (user can cancel)
ELSE:
  → Requires manual approval (no auto-execute)
```

---

### 5. Modify Transaction Dialog

**Layout:**
```
┌─────────────────────────────────────────┐
│  MODIFY TRANSACTION                     │
├─────────────────────────────────────────┤
│                                         │
│  BUY NVDA                                │
│                                         │
│  Entry Price:   [$145.50]              │
│  AI Suggested: $145.50                  │
│                                         │
│  Stop Loss:     [$141.15] (-3.0%)      │
│  AI Suggested: $141.15 (-3.0%)         │
│                                         │
│  Profit Target: [$160.00] (+10.0%)     │
│  AI Suggested: $160.00 (+10.0%)        │
│                                         │
│  Amount:        [$1,500]                │
│  AI Suggested: $1,500 (10% portfolio)   │
│  Your Choice: [___] ($ or %)           │
│                                         │
│  Execute When:                          │
│  ( ) Immediately                        │
│  (•) Tomorrow at [9:35am ▼]            │
│  ( ) When price reaches [$___]         │
│                                         │
│  [Save Changes] [Cancel]                │
│                                         │
└─────────────────────────────────────────┘
```

---

### 6. Portfolio Screen

**Purpose:** View all positions with AI insights

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                         PORTFOLIO                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Total Value: $12,450 | Cash: $2,800 | Invested: $9,650   │
│  Total P&L: +$1,250 (+10.3%) | Today: +$125 (+1.02%)      │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  POSITION  | SHARES | AVG COST | CURRENT | P&L    │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  AAPL ✅   | 120    | $182.50  | $187.40 | +$588  │   │
│  │  🤖 AI: Hold. Steady momentum continues.            │   │
│  │  [View Details] [Research] [Create Sell Proposal]   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  MSFT ✅   | 80     | $378.20  | $389.30 | +$888  │   │
│  │  🤖 AI: Hold. Strong fundamentals.                  │   │
│  │  [View Details] [Research] [Create Sell Proposal]   │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  TSLA 🎯   | 10     | $210.00  | $242.00 | +$320  │   │
│  │  🤖 AI: SELL SIGNAL - Profit target hit!            │   │
│  │  📋 Already in queue for sale at 2pm today          │   │
│  │  [View Proposal] [Cancel Sale] [Modify]             │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  GOOGL ⚠️  | 50     | $142.80  | $141.15 | -$82   │   │
│  │  🤖 AI: Monitor closely. Approaching stop loss.     │   │
│  │  [View Details] [Research] [Create Sell Proposal]   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Status Icons:**
- ✅ Green: Position healthy, no action needed
- 🎯 Target: Profit target hit, sell signal active
- ⚠️ Warning: Approaching stop loss or negative news
- 🔴 Alert: Stop loss hit, immediate action needed

---

### 7. History Screen

**Purpose:** Review past trades and learn

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                      TRADE HISTORY                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Filters: [All] [Wins] [Losses] [Last 30 Days ▼]          │
│                                                             │
│  Performance Summary:                                       │
│  • Total Trades: 24                                         │
│  • Win Rate: 62.5% (15 wins, 9 losses)                     │
│  • Average Gain: +8.3%                                      │
│  • Average Loss: -2.1%                                      │
│  • Best Trade: NVDA +23.5% ($345 profit)                   │
│  • Worst Trade: META -4.2% (-$128 loss)                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ✅ NVDA - CLOSED                                   │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  Strategy: Earnings Play                            │   │
│  │  Bought: Dec 1 @ $142.30 (10 shares)                │   │
│  │  Sold: Dec 15 @ $175.75                             │   │
│  │  P&L: +$345 (+23.5%) | Days Held: 14               │   │
│  │                                                     │   │
│  │  🤖 What AI Learned:                                │   │
│  │  "Earnings plays work well when:                   │   │
│  │   • Company beat estimates 3+ quarters in a row    │   │
│  │   • Entry 7 days before earnings                   │   │
│  │   • Exit immediately after earnings pop"           │   │
│  │   [Read Full Post-Analysis]                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ❌ META - CLOSED (LOSS)                            │   │
│  │  ─────────────────────────────────────────────────  │   │
│  │  Strategy: Technical Breakout                       │   │
│  │  Bought: Nov 20 @ $305.50 (10 shares)               │   │
│  │  Sold: Nov 28 @ $292.70 (Stop loss hit)            │   │
│  │  P&L: -$128 (-4.2%) | Days Held: 8                 │   │
│  │                                                     │   │
│  │  🤖 What AI Learned:                                │   │
│  │  "Technical breakouts failed because:               │   │
│  │   • Ignored weak sector fundamentals               │   │
│  │   • Volume on breakout was below average           │   │
│  │   • Should have waited for pullback confirmation"  │   │
│  │   [Read Full Post-Analysis]                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔔 Notification System

### Push Notification Scenarios

1. **New Trade Proposal:**
   - "🤖 AI found opportunity: BUY NVDA @ $145.50 (87% confidence)"
   - Action: Opens Transaction Queue

2. **Auto-Execute Warning:**
   - "⏰ TSLA will sell in 1 hour unless you cancel"
   - Action: Opens specific transaction

3. **Stop Loss Alert:**
   - "⚠️ GOOGL approaching stop loss ($138.50). Review position?"
   - Action: Opens position details

4. **Profit Target Hit:**
   - "🎯 AAPL hit profit target! AI recommends selling."
   - Action: Opens sell validation

5. **News Alert:**
   - "📰 Breaking news on TSLA may affect your position"
   - Action: Shows news and AI analysis

---

## 🎨 Design Principles

### Visual Design
- **Clean & Minimal:** Focus on data, not decoration
- **Color Coding:** Green = good, Red = bad/urgent, Yellow = caution, Blue = info
- **Confidence Indicators:** Visual bars for AI confidence (70% = yellow, 80% = green, 90% = dark green)
- **Status Icons:** Universal symbols (✅✓🎯⚠️🔴)

### Interaction Design
- **Progressive Disclosure:** Show summary first, details on click
- **Confirmation for Irreversible Actions:** "Are you sure you want to execute this trade?"
- **Undo/Cancel:** Always provide a way to back out
- **Keyboard Shortcuts:** Power users can navigate quickly

### Mobile Responsiveness
- **Mobile-First:** All screens work on phone (responsive design)
- **Touch Targets:** Buttons at least 44px tall
- **Swipe Actions:** Swipe to approve/reject proposals
- **Bottom Navigation:** Main nav at bottom on mobile

---

## 🚀 Progressive Feature Rollout

**Timeline:** 35 real-time hours total (4-5 days at 8h/day, or 18 days at 2h/day, or 35 days at 1h/day)

### Phase 0: Backtesting Engine (Day 0, 6h)
- ✅ Historical simulation engine
- ✅ Quick backtest presets (30d, 90d, 1y)
- ✅ Custom configuration (dates, capital, strategies)
- ✅ Performance metrics dashboard
- ✅ Trade-by-trade analysis
- **Status:** COMPLETE (implemented Dec 2025)

### Phase 1: AI Research Engine (Day 1, 4h)
- ✅ Research screen (user-initiated stock research)
- ✅ Dual AI analysis (OpenAI + Claude verification)
- ✅ BUY/WAIT/AVOID recommendations with confidence scores
- ✅ Entry/stop/target prices with reasoning

### Phase 2: Sell Validation Flow (Day 2, 3h)
- ✅ Validate user's sell decisions
- ✅ AI analysis of whether to hold or sell
- ✅ Alternative timing suggestions
- ✅ Risk/reward assessment

### Phase 3: Transaction Queue System (Day 3, 4h)
- ✅ Centralized proposal management
- ✅ Manual approval/reject/modify workflow
- ✅ Auto-execute logic (with user override)
- ✅ Scheduled execution

### Phase 4: Opportunity Scanner (Day 4-5, 5h)
- ✅ Autonomous market scanning (every 15 min)
- ✅ AI finds opportunities across watchlists
- ✅ Creates proposals automatically
- ✅ Notification system

### Phase 5: Position Monitor & Rebalancing (Day 6-7, 5h)
- ✅ AI evaluates existing positions daily
- ✅ HOLD/BUY_MORE/SELL/WATCH recommendations
- ✅ Rebalancing suggestions
- ✅ Risk monitoring

### Phase 6: Learning Engine (Day 8-9, 4h)
- ✅ Post-trade analysis
- ✅ Pattern recognition
- ✅ Improvement proposals
- ✅ Performance analytics

---

## 📺 Screen Designs

### 0. Backtesting Screen (Strategy Validation)

**Purpose:** Test trading strategies against historical data before risking real capital

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│                      BACKTESTING                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🧪 QUICK BACKTESTS                                         │
│  ┌────────┐ ┌────────┐ ┌────────┐                         │
│  │ 30 Days│ │ 90 Days│ │ 1 Year │                         │
│  └────────┘ └────────┘ └────────┘                         │
│                                                             │
│  ⚙️ CUSTOM CONFIGURATION                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Date Range:  [2024-01-01] to [2024-12-31]         │   │
│  │                                                     │   │
│  │  Initial Capital: [$100,000___]                    │   │
│  │  Position Size: [10%] of capital per trade         │   │
│  │                                                     │   │
│  │  AI Confidence: [━━━━━●━━━━] 75%                   │   │
│  │                                                     │   │
│  │  Strategies:                                        │   │
│  │  ☑ Breakouts (50-day highs)                        │   │
│  │  ☑ Earnings Momentum                               │   │
│  │  ☑ Seasonality Patterns                            │   │
│  │  ☐ Macro Catalysts                                 │   │
│  │  ☐ Social Sentiment                                │   │
│  │                                                     │   │
│  │  [x] Use AI Analysis                               │   │
│  │                                                     │   │
│  │  [Run Custom Backtest]                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  📊 RESULTS (Last 90 Days)                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │ Total Return │ │  Win Rate    │ │ Net Profit │  │   │
│  │  │    +8.7%     │ │     65%      │ │  $8,700    │  │   │
│  │  └──────────────┘ └──────────────┘ └────────────┘  │   │
│  │                                                     │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │   │
│  │  │ Total Trades │ │Profit Factor │ │  Avg Hold  │  │   │
│  │  │      23      │ │     2.34     │ │   7.3 days │  │   │
│  │  └──────────────┘ └──────────────┘ └────────────┘  │   │
│  │                                                     │   │
│  │  Performance Metrics:                               │   │
│  │  • Average Win: +12.0% ($1,200)                     │   │
│  │  • Average Loss: -5.0% ($500)                       │   │
│  │  • Largest Win: +18.0% ($1,800) - AAPL              │   │
│  │  • Largest Loss: -5.0% ($500) - TSLA                │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ 🏆 BEST TRADE                                 │ │   │
│  │  │ AAPL: +18.0% (+$1,800) in 7 days              │ │   │
│  │  │ Entry: $180.00 → Exit: $212.40 (Profit Target)│ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ 📉 WORST TRADE                                │ │   │
│  │  │ TSLA: -5.0% (-$500) in 3 days                 │ │   │
│  │  │ Entry: $250.00 → Exit: $237.50 (Stop Loss)    │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  Trade History (23 trades):                        │   │
│  │  ┌─────────────────────────────────────────────┐  │   │
│  │  │Symbol│Entry │Exit  │Days│ P&L  │ Result  │  │   │
│  │  ├─────────────────────────────────────────────┤  │   │
│  │  │AAPL  │$180.0│$212.4│ 7  │+$1800│✅ +18.0%│  │   │
│  │  │MSFT  │$380.0│$418.0│ 10 │+$1000│✅ +10.0%│  │   │
│  │  │NVDA  │$145.0│$159.5│ 8  │+$1450│✅ +10.0%│  │   │
│  │  │TSLA  │$250.0│$237.5│ 3  │ -$500│❌  -5.0%│  │   │
│  │  │GOOGL │$140.0│$133.0│ 5  │ -$700│❌  -5.0%│  │   │
│  │  │...                                          │  │   │
│  │  └─────────────────────────────────────────────┘  │   │
│  │                                                     │   │
│  │  [Download CSV] [Compare Backtests] [Save Config]  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**User Flow:**
1. **Quick Backtest (Fastest)**
   - User clicks "90 Days" button
   - System runs backtest with default settings (75% AI threshold, all strategies)
   - Shows loading animation (30-60 seconds)
   - Displays results dashboard with summary cards
   - User reviews win rate, profit factor, and trade list

2. **Custom Backtest (Full Control)**
   - User selects date range (e.g., 2024-01-01 to 2024-12-31)
   - Sets initial capital ($50k-$500k)
   - Chooses position size (5%-20%)
   - Selects specific strategies (check boxes)
   - Adjusts AI confidence threshold (50%-95%)
   - Clicks "Run Custom Backtest"
   - System polls status every 5 seconds
   - Shows progress indicator
   - Displays comprehensive results

3. **Iterative Optimization**
   - User runs baseline backtest (default settings)
   - Notes win rate: 65%, profit factor: 2.34
   - Adjusts AI threshold to 85%
   - Runs again → win rate: 71%, profit factor: 2.89 ✓
   - Saves optimal configuration
   - Applies to agent configuration

**Key Interactions:**
- **Quick presets:** One-click testing for common periods
- **Slider control:** Visual AI threshold adjustment
- **Strategy toggles:** Enable/disable specific strategies
- **Real-time status:** Updates every 5 seconds while running
- **Trade drill-down:** Click any trade for full details
- **Download CSV:** Export results for external analysis

**Performance Metrics Explained:**
- **Total Return:** % portfolio gain (green if positive)
- **Win Rate:** % of profitable trades (65% target)
- **Profit Factor:** Total wins / total losses (>2.0 is excellent)
- **Avg Hold:** Mean days per trade (helps plan capital requirements)
- **Best/Worst:** Highlight outliers for learning

**Edge Cases:**
- **No trades generated:** "No opportunities found matching criteria. Try lowering AI threshold or enabling more strategies."
- **API timeout:** "Data download taking longer than expected. Retry in 1 minute."
- **Invalid date range:** "End date must be after start date and within last 5 years."
- **Concurrent backtests:** Queue additional requests if one is running

**Integration with Agent Config:**
```
Backtest (Test) → Agent Config (Apply) → Paper Trading (Validate) → Live Trading (Execute)

Example:
1. Backtest 90d with 85% AI threshold → 71% win rate ✓
2. Navigate to Agent Config tab
3. Click "Apply Backtest Settings"
4. System auto-fills: 85% threshold, optimal strategies
5. User enables agent in Paper mode
6. Monitor live performance vs backtest expectations
```

**Success Indicators:**
- Win rate matches backtest ±5%
- Profit factor within 20% of backtest
- Trade frequency similar to historical
- No excessive drawdowns
- AI signals performing as expected

---

## 📊 Success Metrics

### User Engagement
- Daily active users: > 80%
- Average session length: > 5 minutes
- Proposals reviewed: > 90%

### User Satisfaction
- AI approval rate: > 60%
- User-initiated research: > 3 per week
- Feature satisfaction: > 4/5 stars

### Financial Performance
- User portfolio growth: > market benchmark
- Win rate: > 55%
- Average trade P&L: > 5%

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**Status:** Design Complete, Ready for Prototyping
