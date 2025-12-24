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

### MVP (Week 1-2)
- ✅ Dashboard with portfolio summary
- ✅ Research screen (user-initiated)
- ✅ Transaction queue (manual approval only)
- ✅ Basic buy/sell execution (paper trading)

### V1.1 (Week 3-4)
- ✅ Autonomous opportunity scanner
- ✅ Auto-execute logic (with user override)
- ✅ Sell validation flow
- ✅ Enhanced AI reasoning display

### V1.2 (Week 5-6)
- ✅ Learning engine (post-trade analysis)
- ✅ History screen with insights
- ✅ Notification system
- ✅ Mobile optimizations

### V2.0 (Week 7-9)
- ✅ Multi-user authentication
- ✅ Live trading (Schwab integration)
- ✅ Advanced strategies
- ✅ Performance analytics

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
