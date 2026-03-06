# FInsightAI Trading Strategy Specification

**Version:** 1.0  
**Date:** December 22, 2025  
**Status:** Active Development

---

## Table of Contents

1. [Overview](#overview)
2. [Strategy Architecture](#strategy-architecture)
3. [Hold Period Intelligence](#hold-period-intelligence)
4. [Trading Strategies](#trading-strategies)
5. [IPO Strategy](#ipo-strategy)
6. [Parameters & Configuration](#parameters--configuration)
7. [Signal Detection & Scoring](#signal-detection--scoring)
8. [Entry & Exit Logic](#entry--exit-logic)
9. [Risk Management](#risk-management)
10. [AI Optimization](#ai-optimization)
11. [Learning & Analytics Engine](#learning--analytics-engine)
12. [User Interface Specifications](#user-interface-specifications)
13. [API Specifications](#api-specifications)

---

## Overview

### Philosophy
**Catalyst-Driven Value Trading** with intelligent exits and risk management.

### Core Principles
- **Holding Period:** Adaptive (1 day to multi-year holds based on stock quality)
  - **Short-term (1-30 days):** Catalyst-driven swing trades
  - **Medium-term (1-3 months):** Growth momentum plays
  - **Long-term (3-12 months):** Value accumulation positions
  - **Quality Hold (12+ months):** Blue-chip compounders
- **Risk Profile:** Conservative to moderate
- **Decision Basis:** Fundamental catalysts + technical confirmation + quality assessment
- **Exit Strategy:** Dynamic profit targets with intelligent stop-losses + quality-based holds
- **Learning System:** Every trade analyzed and logged for continuous improvement

### Key Features
- ✅ **User Configurable:** All parameters adjustable via UI
- ✅ **AI Optimization:** Independent parameter tuning per strategy
- ✅ **Granular Control:** Global OR per-strategy configuration
- ✅ **Intelligent Recommendations:** Stock-specific buy/sell/hold signals

---

## Strategy Architecture

### Strategy Lifecycle

```
┌─────────────────┐
│  Data Ingestion │
│  • Market Data  │
│  • News/Events  │
│  • Sentiment    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Signal Detection│
│  • Earnings     │
│  • Seasonality  │
│  • Macro        │
│  • Sentiment    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Technical Filter│
│  • RSI Check    │
│  • Volume       │
│  • Trend        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Risk Assessment │
│  • Position Size│
│  • Portfolio    │
│  • Correlation  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Trade Execution  │
│  • Entry Price  │
│  • Stop Loss    │
│  • Profit Target│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Position Monitor │
│  • Price Track  │
│  • Exit Signals │
│  • P&L Track    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Learning Engine  │
│  • Trade Review │
│  • Pattern Log  │
│  • AI Improve   │
└─────────────────┘
```

---

## Hold Period Intelligence

### Adaptive Hold Period System

The system intelligently determines optimal hold periods based on stock quality, catalyst type, and market conditions.

### 1. 📊 Short-Term Holds (1-30 days)

**Use Cases:**
- Earnings momentum plays
- Macro catalyst reactions
- Sentiment-driven volatility
- Technical breakouts

**Quality Indicators:**
- Catalyst-driven only (not sustainable)
- High volatility (beta >1.5)
- Event-specific opportunity
- No long-term moat

**Exit Triggers:**
- Profit target hit (8-20%)
- Catalyst resolved
- Technical breakdown
- Time limit reached

**Example Stocks:**
- Pre-earnings plays
- Fed announcement reactions
- Short squeeze candidates
- Meme stock momentum

---

### 2. 📈 Medium-Term Holds (1-3 months)

**Use Cases:**
- Growth momentum
- Sector rotation
- Product launch cycles
- Seasonal patterns

**Quality Indicators:**
- Revenue growth >20%
- Expanding margins
- Strong sector momentum
- Multiple growth catalysts

**Exit Triggers:**
- Profit target hit (15-40%)
- Growth story changes
- Sector rotation out
- Time limit reached

**Exit Strategy:**
```python
def evaluate_medium_term_hold(stock, position):
    """
    Adaptive exit for 1-3 month holds
    """
    days_held = (today - position.entry_date).days
    
    # Extend hold if conditions improving
    if stock.growth_accelerating and days_held < 90:
        return "HOLD"
    
    # Take profit if target hit
    if position.profit_pct >= target_profit:
        return "SELL"
    
    # Exit if momentum fading
    if stock.revenue_deceleration and days_held > 30:
        return "SELL"
    
    # Time-based exit
    if days_held >= 90:
        return "REVIEW"  # Manual decision
```

**Example Stocks:**
- Growth tech with positive earnings
- Biotech with pipeline catalysts
- Consumer brands with new products
- Small-caps breaking out

---

### 3. 🏆 Long-Term Holds (3-12 months)

**Use Cases:**
- Value accumulation
- Turnaround stories
- Undervalued quality
- Market recovery plays

**Quality Indicators:**
- P/E <15, strong fundamentals
- Improving margins quarter-over-quarter
- Management execution track record
- Competitive moat emerging

**Exit Triggers:**
- Valuation targets hit (30-100% gains)
- Fundamental deterioration
- Better opportunity elsewhere
- Time limit or reassessment

**Quality Assessment Matrix:**
```
Quality Score = (Financial Health × 30%) +
                (Management Quality × 25%) +
                (Competitive Position × 25%) +
                (Growth Prospects × 20%)

Score > 75: Consider long-term hold
Score 60-75: Medium-term positioning
Score < 60: Short-term only
```

**Example Stocks:**
- Undervalued blue-chips (temporary dip)
- Turnaround candidates with new CEO
- Cyclicals at bottom of cycle
- Post-merger integration plays

---

### 4. 💎 Quality Holds (12+ months, potentially multi-year)

**Use Cases:**
- Blue-chip compounders
- Market leaders with moat
- Dividend aristocrats
- Core portfolio holdings

**Quality Indicators Required:**
- Consistent profit growth (5+ years)
- ROE >15%, ROIC >12%
- Strong competitive moat (brand, network, switching costs)
- Shareholder-friendly management
- Recession-resistant business model
- Growing dividend (optional but preferred)

**Hold Conditions:**
```python
def should_hold_long_term(stock):
    """
    Determine if stock qualifies for multi-year hold
    """
    criteria = {
        "consistent_growth": stock.earnings_growth_5yr > 0.10,  # 10%+ avg
        "high_roic": stock.roic > 0.12,  # 12%+
        "strong_moat": stock.moat_rating >= 4,  # Scale 1-5
        "financial_health": stock.debt_to_equity < 0.5,
        "shareholder_friendly": stock.buyback_or_dividend,
        "market_leader": stock.market_share_rank <= 3,
        "recession_proof": stock.recession_revenue_decline < 0.15  # <15% drop
    }
    
    # Must meet 6/7 criteria
    return sum(criteria.values()) >= 6
```

**Exit Triggers (ONLY):**
- Fundamental deterioration (2+ quarters)
- Competitive moat breach
- Management change (red flag)
- Valuation extreme (P/E >40 for non-growth)
- Better quality opportunity identified
- Need to raise cash (portfolio rebalancing)

**Never Exit For:**
- ❌ Short-term price volatility
- ❌ Temporary earnings miss
- ❌ Market correction (hold through)
- ❌ Hit arbitrary profit target

**Example Stocks:**
- Microsoft, Apple, Google (mega-cap tech)
- Berkshire Hathaway (conglomerate)
- Visa, Mastercard (payment networks)
- Costco (retail moat)
- Johnson & Johnson (healthcare)

**Position Management:**
```json
{
  "symbol": "MSFT",
  "holdClassification": "quality_hold",
  "entryDate": "2024-06-15",
  "entryPrice": 425.00,
  "currentPrice": 475.00,
  "daysHeld": 190,
  "profitPercent": 11.8,
  "exitStrategy": {
    "type": "quality_based",
    "stopLoss": null,  // No stop loss for quality holds
    "profitTarget": null,  // No arbitrary target
    "reviewTriggers": [
      "quarterly_earnings_miss_2x",
      "roic_below_10_for_2_quarters",
      "competitive_threat_emerging",
      "management_turnover"
    ]
  },
  "qualityMetrics": {
    "moatRating": 5,
    "roic": 0.28,
    "earningsGrowth5yr": 0.15,
    "lastReviewDate": "2025-12-01",
    "nextReviewDate": "2026-03-01"
  }
}
```

---

### Hold Period Decision Algorithm

```python
def determine_hold_period(stock, market_data, technical_analysis):
    """
    Intelligent hold period classification
    """
    quality_score = calculate_quality_score(stock)
    catalyst_type = identify_primary_catalyst(stock)
    
    # Quality Holds (Blue-chip compounders)
    if quality_score >= 85 and stock.moat_rating >= 4:
        return {
            "classification": "quality_hold",
            "min_hold": 365,
            "max_hold": float('inf'),
            "review_frequency": "quarterly",
            "exit_strategy": "fundamental_only"
        }
    
    # Long-Term Holds (Value/Turnaround)
    elif quality_score >= 70 and catalyst_type == "fundamental":
        return {
            "classification": "long_term",
            "min_hold": 90,
            "max_hold": 365,
            "profit_target": calculate_valuation_target(stock),
            "exit_strategy": "target_or_deterioration"
        }
    
    # Medium-Term Holds (Growth Momentum)
    elif quality_score >= 55 and catalyst_type in ["growth", "sector_rotation"]:
        return {
            "classification": "medium_term",
            "min_hold": 30,
            "max_hold": 90,
            "profit_target": 0.25,  # 25%
            "exit_strategy": "momentum_fade"
        }
    
    # Short-Term Holds (Catalyst Plays)
    else:
        return {
            "classification": "short_term",
            "min_hold": 1,
            "max_hold": 30,
            "profit_target": 0.12,  # 12%
            "exit_strategy": "catalyst_resolution"
        }
```

---

## Trading Strategies

**Note:** The following strategies apply primarily to **short-term and medium-term holds**. Quality holds are identified through separate fundamental screening.

### 1. 📊 Earnings Momentum Strategy

**Catalyst:** Companies with strong earnings projections

#### Signal Criteria
- Earnings announcement: 3-7 days away (configurable)
- EPS growth: >15% YoY (configurable)
- Revenue growth: >10% YoY (configurable)
- Earnings revisions: Upgrades in last 30 days
- Historical beat rate: >70% (configurable)

#### Entry Rules
- **Timing:** Enter 3-7 days before earnings
- **Price:** Market price or limit order
- **Volume:** Must exceed 1.5x 20-day average (configurable)

#### Exit Rules
- **Profit Target:** +8-15% (user configurable per stock)
- **Stop Loss:** -5% from entry (configurable)
- **Time Exit:** Day after earnings OR 14 days max
- **Event Exit:** Immediate on earnings miss

#### Configuration Parameters
```json
{
  "enabled": true,
  "daysBeforeEarnings": {
    "min": 3,
    "max": 7,
    "default": 5,
    "aiOptimizable": true
  },
  "minEpsGrowth": {
    "min": 10.0,
    "max": 30.0,
    "default": 15.0,
    "aiOptimizable": true
  },
  "minRevenueGrowth": {
    "min": 5.0,
    "max": 20.0,
    "default": 10.0,
    "aiOptimizable": true
  },
  "historicalBeatRate": {
    "min": 60.0,
    "max": 90.0,
    "default": 70.0,
    "aiOptimizable": true
  },
  "profitTarget": {
    "min": 5.0,
    "max": 25.0,
    "default": 12.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "stopLoss": {
    "min": 3.0,
    "max": 10.0,
    "default": 5.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "maxPortfolioWeight": {
    "min": 5.0,
    "max": 30.0,
    "default": 20.0,
    "aiOptimizable": true
  }
}
```

---

### 2. 📅 Seasonality & Calendar Strategy

**Catalyst:** Historical seasonal performance patterns

#### Signal Criteria
- Historical pattern: 5+ years of data
- Seasonal strength: >60% win rate (configurable)
- Current year alignment: Sector/market conditions match
- Pattern types:
  - Holiday retail (Oct-Dec)
  - Tax season (Jan-Apr)
  - Summer travel (May-Aug)
  - Back-to-school (Aug-Sep)
  - Quarterly rebalancing (Mar, Jun, Sep, Dec)

#### Entry Rules
- **Timing:** 2-4 weeks before seasonal peak (configurable)
- **Confirmation:** Technical trend alignment required
- **Volume:** Normal or above average

#### Exit Rules
- **Profit Target:** +10-20% (user configurable per stock)
- **Stop Loss:** -7% from entry (configurable)
- **Time Exit:** End of seasonal period
- **Pattern Break:** Exit if historical pattern fails

#### Configuration Parameters
```json
{
  "enabled": true,
  "weeksBeforePeak": {
    "min": 1,
    "max": 6,
    "default": 3,
    "aiOptimizable": true
  },
  "minHistoricalWinRate": {
    "min": 50.0,
    "max": 80.0,
    "default": 60.0,
    "aiOptimizable": true
  },
  "profitTarget": {
    "min": 8.0,
    "max": 30.0,
    "default": 15.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "stopLoss": {
    "min": 5.0,
    "max": 10.0,
    "default": 7.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "maxHoldDays": {
    "min": 14,
    "max": 60,
    "default": 30,
    "aiOptimizable": true
  }
}
```

---

### 3. 🌍 Macro & Economic Catalyst Strategy

**Catalyst:** Economic/world events affecting specific sectors

#### Signal Criteria
- **Event Types:**
  - Interest rate changes (Fed meetings)
  - Commodity price movements
  - GDP/unemployment/inflation releases
  - Geopolitical events
  - Regulatory changes
  
- **Strength Rating:** 70-100 (high impact events only)
- **Sector Alignment:** Clear beneficiaries identified
- **Timing:** Within 48 hours of event

#### Entry Rules
- **Timing:** Within 24-48 hours post-announcement (configurable)
- **Confirmation:** Sector ETF moving in expected direction
- **Multiple Confirmations:** News + price action + volume

#### Exit Rules
- **Profit Target:** +5-12% (depends on catalyst strength)
- **Stop Loss:** -6% from entry (configurable)
- **Time Exit:** 30 days maximum
- **Event Fade:** Exit if catalyst impact fades

#### Configuration Parameters
```json
{
  "enabled": true,
  "entryTimeframe": {
    "min": 12,
    "max": 72,
    "default": 48,
    "unit": "hours",
    "aiOptimizable": true
  },
  "catalystStrengthMin": {
    "min": 60,
    "max": 90,
    "default": 70,
    "aiOptimizable": true
  },
  "profitTarget": {
    "min": 3.0,
    "max": 15.0,
    "default": 8.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "stopLoss": {
    "min": 4.0,
    "max": 10.0,
    "default": 6.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "maxHoldDays": {
    "min": 14,
    "max": 45,
    "default": 30,
    "aiOptimizable": true
  }
}
```

---

### 4. 📱 Social Sentiment & Alternative Data Strategy

**Catalyst:** Sentiment shifts with volume confirmation

#### Signal Criteria
- Social sentiment: >70% positive (configurable)
- Sources: Twitter, Reddit, StockTwits, news
- Sentiment trend: Rising over 48 hours
- Volume confirmation: >150% of 20-day average (configurable)
- Institutional signals: Upgrades, insider buying, 13F filings
- Search trends: >50% increase (Google Trends)

#### Entry Rules
- **Timing:** When sentiment spike + volume align
- **Confirmation:** Multiple data sources agree
- **Quality Filter:** Exclude pump-and-dump patterns

#### Exit Rules
- **Profit Target:** +6-10% (user configurable per stock)
- **Stop Loss:** -4% from entry (tight, volatile strategy)
- **Sentiment Reversal:** Exit if sentiment drops below 50%
- **Volume Dry-Up:** Exit if volume drops <80% average for 2 days

#### Configuration Parameters
```json
{
  "enabled": true,
  "minSentimentScore": {
    "min": 60.0,
    "max": 85.0,
    "default": 70.0,
    "aiOptimizable": true
  },
  "volumeMultiplier": {
    "min": 1.2,
    "max": 2.5,
    "default": 1.5,
    "aiOptimizable": true
  },
  "profitTarget": {
    "min": 4.0,
    "max": 15.0,
    "default": 8.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "stopLoss": {
    "min": 2.0,
    "max": 6.0,
    "default": 4.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "sentimentExitThreshold": {
    "min": 40.0,
    "max": 60.0,
    "default": 50.0,
    "aiOptimizable": true
  }
}
```

---

## IPO Strategy

### 5. 🚀 Initial Public Offering (IPO) Strategy

**Catalyst:** New companies going public with strong fundamentals

#### IPO Intelligence System

The system continuously monitors upcoming IPOs and evaluates them for investment opportunities.

#### Signal Criteria

**Pre-IPO Research (30-90 days before):**
- Company background check
- Financial health analysis (S-1 filing review)
- Market opportunity assessment
- Competitive positioning
- Management team evaluation
- Underwriter quality (tier 1 banks = higher confidence)
- Lock-up period analysis

**Key Metrics:**
- Revenue growth trajectory: >30% YoY preferred
- Path to profitability: Clear or already profitable
- Market size: TAM >$10B
- Valuation: P/S ratio vs comparable companies
- Insider ownership: >20% post-IPO (skin in the game)
- Share structure: Avoid dual-class if possible

**Social & News Sentiment:**
- Media coverage analysis (30 days pre-IPO)
- Social media buzz tracking
- Industry analyst opinions
- Competitor reactions
- Customer feedback/reviews

#### Entry Rules

**IPO Day Considerations:**
- **Timing:** First day or wait for 2-5 day stabilization?
- **Price Target:** Entry at IPO price, below, or above based on demand
- **Allocation:** Smaller position size (higher risk)
- **Lock-up Awareness:** Note when insiders can sell (typically 180 days)

**Decision Matrix:**
```python
def evaluate_ipo_entry(ipo_data, market_conditions):
    """
    Determine if and when to enter IPO
    """
    # High-quality IPOs: Enter day 1
    if (ipo_data.quality_score >= 80 and 
        ipo_data.valuation_fair and
        market_conditions.sentiment > 70):
        return {
            "action": "BUY",
            "timing": "IPO_DAY",
            "price_limit": ipo_data.ipo_price * 1.10  # Up to 10% premium
        }
    
    # Medium-quality: Wait for stabilization
    elif ipo_data.quality_score >= 60:
        return {
            "action": "WATCH",
            "timing": "WAIT_5_DAYS",
            "entry_trigger": "price_stabilization_below_ipo"
        }
    
    # Low-quality or overvalued: Skip
    else:
        return {
            "action": "PASS",
            "reasoning": ipo_data.red_flags
        }
```

#### Hold Period for IPOs

**Typical Hold:** 3-12 months (medium to long-term)

**Rationale:**
- IPOs need time to establish trading patterns
- Lock-up expiration can cause volatility (180 days)
- First 2-4 earnings reports critical for trajectory
- Institutional accumulation takes 6-12 months

**Quality-Based Extension:**
- If IPO proves to be quality compounder → Convert to quality hold
- Monitor quarterly earnings for growth sustainability

#### Exit Rules

**Profit Targets:**
- **First 90 days:** +25-50% (if momentum strong)
- **90-180 days:** Hold through lock-up expiration
- **180-365 days:** +50-100% or convert to long-term

**Stop Loss:**
- **First 30 days:** -15% from entry (IPOs are volatile)
- **After 30 days:** -10% from entry
- **Lock-up expiration:** Tighten to -8% (insider selling risk)

**Mandatory Exits:**
- CEO/CFO departure in first year
- Revenue miss >10% in first 2 quarters
- Guidance reduction
- Lock-up selling exceeds 30% of shares
- Accounting irregularities

#### IPO Stages & Strategy

**Stage 1: Pre-IPO (30-90 days before)**
```json
{
  "stage": "research",
  "activities": [
    "Read S-1 filing completely",
    "Analyze financials and growth metrics",
    "Research management backgrounds",
    "Assess competitive landscape",
    "Monitor media coverage",
    "Track social sentiment trends",
    "Evaluate underwriter quality"
  ],
  "output": {
    "quality_score": 0-100,
    "recommendation": "strong_buy | buy | watch | pass",
    "entry_strategy": "ipo_day | wait_5d | wait_lock_up | skip"
  }
}
```

**Stage 2: IPO Day**
```json
{
  "stage": "execution",
  "checks": [
    "Market conditions favorable?",
    "Opening price vs IPO price?",
    "Volume and demand signals?",
    "Underwriter support evident?"
  ],
  "execution": {
    "if_strong_quality": "Market order at open or limit +10%",
    "if_medium_quality": "Wait for intraday dip",
    "if_weak_quality": "Skip"
  }
}
```

**Stage 3: First 30 Days**
```json
{
  "stage": "early_monitoring",
  "watch_for": [
    "Price stabilization pattern",
    "Volume normalization",
    "Analyst coverage initiation",
    "First guidance/business update"
  ],
  "actions": {
    "if_momentum_strong": "Hold or add to position",
    "if_breaking_down": "Exit at -15% stop loss",
    "if_consolidating": "Continue holding"
  }
}
```

**Stage 4: 30-180 Days (Pre-Lock-up)**
```json
{
  "stage": "establishment",
  "key_events": [
    "First earnings report (critical!)",
    "Second earnings report",
    "Analyst revisions",
    "Lock-up expiration date"
  ],
  "hold_strategy": {
    "if_exceeding_expectations": "Hold through lock-up",
    "if_meeting_expectations": "Take partial profits before lock-up",
    "if_missing_expectations": "Exit immediately"
  }
}
```

**Stage 5: 180+ Days (Post-Lock-up)**
```json
{
  "stage": "maturation",
  "evaluation": "Convert to standard strategy or exit",
  "quality_assessment": {
    "if_quality_hold_criteria": "Migrate to quality hold (unlimited)",
    "if_growth_story_intact": "Hold as medium/long-term (3-12 months)",
    "if_story_broken": "Exit position"
  }
}
```

#### IPO Configuration Parameters

```json
{
  "enabled": true,
  "minMarketCap": {
    "min": 500000000,  // $500M
    "max": 10000000000,  // $10B
    "default": 1000000000,  // $1B
    "description": "Minimum IPO market cap"
  },
  "minRevenueGrowth": {
    "min": 20.0,
    "max": 100.0,
    "default": 30.0,
    "description": "Minimum YoY revenue growth %"
  },
  "maxPSRatio": {
    "min": 5.0,
    "max": 20.0,
    "default": 10.0,
    "description": "Maximum price-to-sales ratio"
  },
  "minQualityScore": {
    "min": 50,
    "max": 90,
    "default": 65,
    "description": "Minimum quality score to consider"
  },
  "profitTarget": {
    "min": 20.0,
    "max": 100.0,
    "default": 50.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "stopLoss": {
    "min": 10.0,
    "max": 20.0,
    "default": 15.0,
    "perStockOverride": true,
    "aiOptimizable": true
  },
  "maxPositionSize": {
    "min": 2.0,
    "max": 10.0,
    "default": 5.0,
    "description": "Max % of portfolio (IPOs are higher risk)"
  },
  "waitPeriod": {
    "min": 0,
    "max": 30,
    "default": 5,
    "description": "Days to wait after IPO before entering"
  }
}
```

#### IPO Research Checklist

**Automated Analysis:**
- [ ] Parse S-1 filing for financials
- [ ] Calculate growth rates (revenue, user, ARR)
- [ ] Assess profitability path
- [ ] Identify risk factors
- [ ] Analyze use of proceeds
- [ ] Check insider ownership %
- [ ] Evaluate underwriter tier
- [ ] Compare valuation to peers
- [ ] Scrape news articles (30 days)
- [ ] Track social media sentiment
- [ ] Monitor Reddit/Twitter discussion volume

**Manual Review (AI-Assisted):**
- [ ] Management team quality check
- [ ] Product/service differentiation
- [ ] Competitive moat assessment
- [ ] TAM (Total Addressable Market) validation
- [ ] Customer concentration risk
- [ ] Regulatory/legal risks
- [ ] Technology/IP strength

#### Example IPO Evaluation

```json
{
  "symbol": "NEWCO",
  "name": "New Company Inc.",
  "ipoDate": "2026-01-15",
  "ipoPrice": 25.00,
  "marketCap": 5000000000,
  "analysis": {
    "quality_score": 78,
    "financials": {
      "revenue_2024": 500000000,
      "revenue_growth_yoy": 0.45,  // 45%
      "gross_margin": 0.65,
      "net_income": -50000000,  // Not profitable yet
      "cash_burn_months": 24  // 2 years runway
    },
    "valuation": {
      "ps_ratio": 10.0,
      "peer_average_ps": 12.0,
      "assessment": "fairly_valued"
    },
    "management": {
      "ceo_experience": "Veteran (15+ years)",
      "insider_ownership_post_ipo": 0.25,
      "quality_rating": 4  // out of 5
    },
    "underwriters": ["Goldman Sachs", "Morgan Stanley"],
    "sentiment": {
      "news_score": 75,
      "social_score": 68,
      "analyst_coverage": "positive"
    }
  },
  "recommendation": {
    "action": "STRONG_BUY",
    "timing": "IPO_DAY",
    "rationale": [
      "High revenue growth (45% YoY)",
      "Fairly valued vs peers",
      "Strong management team",
      "Top-tier underwriters",
      "Positive sentiment",
      "24 months cash runway"
    ],
    "risks": [
      "Not yet profitable",
      "Competitive market"
    ],
    "entry": {
      "price_limit": 27.50,  // Up to 10% premium
      "position_size": 3.0,  // 3% of portfolio
      "stop_loss": 21.25,  // -15%
      "profit_target": 37.50  // +50%
    },
    "hold_classification": "medium_term",
    "expected_hold_days": 180,
    "review_schedule": "after_first_earnings"
  }
}
```

---

## Backtesting & Validation Engine

### 🧪 Backtesting System

**Core Principle:** Test before you trade. Validate strategies with historical data.

The Backtesting Engine allows you to simulate trading strategies against historical market data to validate effectiveness before risking real capital.

#### Purpose & Benefits

**Why Backtest?**
- Validate strategy parameters before live trading
- Identify optimal entry/exit thresholds
- Test different strategy combinations
- Understand historical win rates and profit factors
- Build confidence in AI-driven decisions
- Optimize risk management rules

**Key Features:**
- Simulates complete Scanner → AI Analyzer → Trade Execution workflow
- Uses real historical price data from yfinance
- Tests all strategies: Breakouts, Earnings, Seasonality, Macro, Sentiment
- Applies configurable exit rules: Profit targets, stop losses, max hold time
- Generates comprehensive performance metrics
- Provides trade-by-trade analysis

#### Architecture

**Backend Components:**
```
backend/services/backtester.py (579 lines)
├── Backtester Class
│   ├── run_backtest() - Main execution engine
│   ├── _get_historical_candidates() - Scanner simulation
│   ├── _scan_breakouts_historical() - 50-day high detection
│   ├── _scan_earnings_historical() - Earnings opportunity simulation
│   ├── _scan_seasonal_historical() - Seasonal pattern detection
│   ├── _analyze_with_ai() - AI confidence simulation
│   └── _simulate_trade() - Full trade lifecycle with exit logic
├── BacktestResult Class - Individual trade container
└── BacktestMetrics Class - Performance calculator

backend/api/backtest.py (312 lines)
├── POST /api/backtest/run - Custom backtest
├── POST /api/backtest/quick/{period} - Quick presets (30d, 90d, 1y)
├── GET /api/backtest/status/{id} - Status polling
├── GET /api/backtest/results/{id} - Full results
├── GET /api/backtest/results/{id}/trades - Paginated trades
└── GET /api/backtest/list - List all backtests
```

**Frontend Components:**
```
frontend/src/components/Backtesting.js (588 lines)
├── Quick Backtest Buttons (30d, 90d, 1y)
├── Custom Configuration Form
│   ├── Date range pickers
│   ├── Capital settings
│   ├── AI confidence threshold slider
│   ├── Strategy selection checkboxes
│   └── Use AI toggle
├── Status Polling (5-second intervals)
└── Results Dashboard
    ├── Summary cards (total return, win rate, net profit)
    ├── Performance metrics (profit factor, avg win/loss)
    ├── Best/worst trade analysis
    └── Trade history table
```

#### How It Works

**Step 1: Historical Data Collection**
```python
# Download historical prices for date range
for date in date_range:
    historical_prices = yfinance.download(
        symbols=stock_universe,
        start=date - lookback_period,
        end=date
    )
```

**Step 2: Scanner Simulation**
```python
# Apply scanner strategies to historical data
candidates = []

# Breakouts: Find stocks breaking 50-day highs
if 'breakouts' in strategies:
    breakout_stocks = _scan_breakouts_historical(date, prices)
    candidates.extend(breakout_stocks)

# Earnings: Simulate earnings opportunities (20% random selection)
if 'earnings' in strategies:
    earnings_stocks = _scan_earnings_historical(date, prices)
    candidates.extend(earnings_stocks)

# Seasonality: Check monthly seasonal patterns
if 'seasonality' in strategies:
    seasonal_stocks = _scan_seasonal_historical(date, prices)
    candidates.extend(seasonal_stocks)
```

**Step 3: AI Analysis Simulation**
```python
if use_ai:
    # Simulate AI confidence scoring
    base_confidence = 65.0  # Base score
    variance = random.uniform(-15, 15)  # Random variance
    ai_confidence = base_confidence + variance
    
    # Filter by threshold
    if ai_confidence >= confidence_threshold:
        candidates.append(opportunity)
```

**Step 4: Trade Execution Simulation**
```python
# Enter trade at next day's open price
entry_price = next_day_open
position_size = capital * position_size_pct

# Simulate holding period
for date in future_dates:
    current_price = historical_prices[date][symbol]
    
    # Check exit conditions
    profit_pct = (current_price - entry_price) / entry_price
    
    if profit_pct >= profit_target:  # +10% default
        exit_trade(reason='PROFIT_TARGET', price=current_price)
    elif profit_pct <= -stop_loss:  # -5% default
        exit_trade(reason='STOP_LOSS', price=current_price)
    elif days_held >= max_hold_days:  # 14 days default
        exit_trade(reason='MAX_HOLD', price=current_price)
```

**Step 5: Performance Analysis**
```python
# Calculate comprehensive metrics
metrics = BacktestMetrics(
    total_trades=len(trades),
    winning_trades=len([t for t in trades if t.profit_loss > 0]),
    losing_trades=len([t for t in trades if t.profit_loss < 0]),
    win_rate=winning_trades / total_trades,
    total_return=(final_capital - initial_capital) / initial_capital,
    profit_factor=total_wins / abs(total_losses),
    avg_win=mean([t.profit_loss for t in winning_trades]),
    avg_loss=mean([t.profit_loss for t in losing_trades]),
    avg_hold_days=mean([t.days_held for t in trades]),
    best_trade=max(trades, key=lambda t: t.profit_loss_pct),
    worst_trade=min(trades, key=lambda t: t.profit_loss_pct)
)
```

#### API Endpoints

**1. POST /api/backtest/run - Custom Backtest**
```json
Request:
{
  "start_date": "2025-01-01",
  "end_date": "2025-03-01",
  "initial_capital": 100000,
  "position_size_pct": 0.10,
  "strategies": ["breakouts", "earnings", "seasonality"],
  "confidence_threshold": 0.75,
  "use_ai": true
}

Response:
{
  "backtest_id": "bt_20250301_143025",
  "status": "running",
  "message": "Backtest started"
}
```

**2. POST /api/backtest/quick/{period} - Quick Presets**
```
POST /api/backtest/quick/30d  → Last 30 days
POST /api/backtest/quick/90d  → Last 90 days
POST /api/backtest/quick/1y   → Last 1 year

Returns: Same as custom backtest
```

**3. GET /api/backtest/status/{backtest_id} - Poll Status**
```json
Response:
{
  "backtest_id": "bt_20250301_143025",
  "status": "completed",
  "progress": 100,
  "start_time": "2025-03-01T14:30:25Z",
  "end_time": "2025-03-01T14:32:18Z"
}
```

**4. GET /api/backtest/results/{backtest_id} - Full Results**
```json
Response:
{
  "backtest_id": "bt_20250301_143025",
  "status": "completed",
  "config": { /* original config */ },
  "summary": {
    "total_return": 0.087,  // 8.7%
    "total_return_dollars": 8700.00,
    "win_rate": 0.65,  // 65%
    "total_trades": 23,
    "winning_trades": 15,
    "losing_trades": 8,
    "profit_factor": 2.34,
    "avg_win_pct": 0.12,
    "avg_loss_pct": -0.05,
    "avg_hold_days": 7.3,
    "best_trade": {
      "symbol": "AAPL",
      "profit_pct": 0.18,  // +18%
      "profit_dollars": 1800.00
    },
    "worst_trade": {
      "symbol": "TSLA",
      "profit_pct": -0.05,  // -5%
      "profit_dollars": -500.00
    }
  },
  "trades": [ /* array of all trades */ ]
}
```

**5. GET /api/backtest/results/{backtest_id}/trades - Paginated Trades**
```json
Response:
{
  "backtest_id": "bt_20250301_143025",
  "total_trades": 23,
  "page": 1,
  "limit": 10,
  "trades": [
    {
      "symbol": "AAPL",
      "strategy": "BREAKOUTS",
      "entry_date": "2025-01-15",
      "entry_price": 180.00,
      "exit_date": "2025-01-22",
      "exit_price": 194.40,
      "exit_reason": "PROFIT_TARGET",
      "days_held": 7,
      "profit_loss": 1440.00,
      "profit_loss_pct": 0.08
    },
    // ...more trades
  ]
}
```

#### Performance Metrics Explained

**Win Rate:** Percentage of profitable trades
```
Win Rate = Winning Trades / Total Trades
Example: 15 wins / 23 total = 65%
```

**Total Return:** Overall portfolio gain/loss
```
Total Return = (Final Capital - Initial Capital) / Initial Capital
Example: ($108,700 - $100,000) / $100,000 = 8.7%
```

**Profit Factor:** Ratio of total wins to total losses
```
Profit Factor = Total $ Won / Total $ Lost
Example: $12,500 / $3,800 = 3.29
(Higher is better; >2.0 is excellent)
```

**Average Win/Loss:** Mean profit/loss per trade
```
Avg Win = Sum of Winning Trade $ / Number of Wins
Avg Loss = Sum of Losing Trade $ / Number of Losses
```

**Average Hold Days:** Mean days per trade
```
Avg Hold Days = Sum of Days Held / Total Trades
Example: 168 days / 23 trades = 7.3 days
```

#### Configuration Options

**Date Range:**
- Custom: Any historical date range
- Quick presets: 30d, 90d, 1y

**Capital Settings:**
- Initial capital: Any amount (default $100,000)
- Position size: % of capital per trade (default 10%)

**Strategy Selection:**
- Breakouts: 50-day high detection
- Earnings: Earnings opportunity simulation
- Seasonality: Monthly seasonal patterns
- Can enable any combination

**AI Configuration:**
- Use AI: Enable/disable AI filtering
- Confidence threshold: 50%-95% (default 75%)

**Exit Rules (Fixed):**
- Profit target: +10%
- Stop loss: -5%
- Max hold time: 14 days

#### Usage Workflow

**1. Quick Backtest (Fastest)**
```
1. Navigate to Backtesting tab
2. Click "90 Days" button
3. Wait 30-60 seconds
4. Review results
```

**2. Custom Backtest (Full Control)**
```
1. Select date range (e.g., 2024-01-01 to 2024-12-31)
2. Set initial capital ($50,000 - $500,000)
3. Choose position size (5% - 20%)
4. Select strategies (check all that apply)
5. Set AI threshold (50% - 95%)
6. Click "Run Custom Backtest"
7. Monitor status (updates every 5 seconds)
8. Review detailed results
```

**3. Iterative Optimization**
```
1. Run baseline backtest with default settings
2. Note win rate and profit factor
3. Adjust one parameter (e.g., AI threshold)
4. Run again and compare results
5. Keep better configuration
6. Repeat with other parameters
7. Document optimal settings
```

#### Integration with Agent Configuration

**Workflow: Backtest → Configure → Deploy**

```
Step 1: Backtest with different thresholds
- Run with 65% AI threshold → 58% win rate
- Run with 75% AI threshold → 65% win rate ✓
- Run with 85% AI threshold → 71% win rate ✓✓

Step 2: Identify optimal settings
- Best win rate: 85% threshold
- Best profit factor: 85% threshold
- Decision: Use 85% for live agent

Step 3: Apply to agent configuration
- Navigate to Agent Config tab
- Set AI Confidence Threshold: 85%
- Enable strategies: Breakouts, Earnings, Seasonality
- Set position size: 10%
- Save configuration

Step 4: Monitor live performance
- Compare live results to backtest
- Adjust if significant deviation
- Run new backtests monthly
```

#### Limitations & Best Practices

**Limitations:**
- Historical data != future performance
- Simplified AI confidence simulation (not real AI analysis)
- No slippage or commissions modeled
- No market impact (assumes perfect execution)
- In-memory storage (results lost on restart)
- Limited stock universe (top 100 by volume)

**Best Practices:**
- Run multiple time periods (bull, bear, sideways markets)
- Test parameter sensitivity (don't overfit)
- Compare to buy-and-hold benchmark
- Account for survivorship bias
- Use 90+ day backtests for statistical significance
- Validate with paper trading before live
- Rerun backtests quarterly as markets evolve

#### Future Enhancements

**Phase 1 (Current): Basic Backtesting**
- ✅ Historical price data simulation
- ✅ Scanner strategy simulation
- ✅ AI confidence simulation
- ✅ Fixed exit rules
- ✅ Performance metrics
- ✅ React UI with visualizations

**Phase 2: Advanced Analytics**
- Monthly/quarterly performance breakdowns
- Strategy-specific win rates
- Drawdown analysis (max, average)
- Sharpe ratio calculation
- Benchmark comparison (SPY)
- Sector performance analysis

**Phase 3: Real AI Integration**
- Use actual AI model for analysis
- Test AI improvements over time
- A/B test different AI models
- Confidence calibration

**Phase 4: Database Persistence**
- Store backtest results in PostgreSQL
- Historical backtest tracking
- Compare backtest versions
- Share backtest results

**Phase 5: Optimization Engine**
- Auto-optimize parameters
- Grid search for best settings
- Walk-forward analysis
- Monte Carlo simulation

#### Documentation & Testing

**Complete Documentation:**
- `/docs/implementation/BACKTESTING-COMPLETE.md` - Full technical reference
- `/docs/implementation/BACKTESTING-QUICKSTART.md` - 5-minute quick start

**Test Script:**
- `backend/test-backtest.sh` - Automated endpoint testing

**Status:**
- ✅ Backend complete (891 lines)
- ✅ Frontend complete (588 lines)
- ✅ API integrated into main.py
- ✅ UI integrated into App.js
- ✅ Documentation complete (900+ lines)
- ⏳ Pending real-world validation testing

---

## Learning & Analytics Engine

### 📊 Trade Learning System

**Core Principle:** Every trade is an opportunity to learn and improve

The Learning & Analytics Engine captures the complete context of every trade decision, analyzes outcomes, identifies patterns, and proposes improvements to trading logic.

#### 1. Trade Storage with Full Context

**Database Schema:**

```python
class TradeLog:
    """Complete record of every trade with AI rationale"""
    id: UUID
    timestamp: DateTime
    
    # Basic Trade Info
    symbol: str
    action: str  # BUY | SELL
    shares: int
    price: float
    total_value: float
    portfolio_percent: float
    
    # Strategy Context
    strategy: str  # EARNINGS | SEASONALITY | MACRO | SENTIMENT | IPO
    hold_classification: str  # SHORT | MEDIUM | LONG | QUALITY
    expected_hold_days: int
    
    # Entry Signals (for BUY)
    entry_signals: JSON
    """
    {
      "earnings": {"score": 78, "signals": [...]},
      "seasonality": {"score": 65, "signals": [...]},
      "macro": {"score": 82, "signals": [...]},
      "sentiment": {"score": 70, "signals": [...]},
      "combined_score": 74
    }
    """
    
    # Market Conditions
    market_conditions: JSON
    """
    {
      "spy_trend": "uptrend",
      "vix": 15.2,
      "sector_strength": 68,
      "market_phase": "expansion"
    }
    """
    
    # Technical Analysis
    technicals: JSON
    """
    {
      "rsi": 58,
      "macd": "bullish_cross",
      "price_vs_sma50": 1.05,
      "volume_ratio": 1.8,
      "support": 150.0,
      "resistance": 165.0
    }
    """
    
    # AI Rationale (CRITICAL)
    ai_rationale: TEXT
    """
    Full natural language explanation:
    - Why this stock was selected
    - Which signals triggered the entry
    - What the AI expects to happen
    - Risk factors considered
    - Alternative stocks that were rejected and why
    """
    
    # Configuration Used
    parameters_used: JSON
    """
    Snapshot of all strategy parameters at time of trade
    """
    
    # Exit Info (for SELL)
    exit_reason: str  # PROFIT_TARGET | STOP_LOSS | TIME_BASED | SIGNAL_REVERSAL | MANUAL
    exit_signals: JSON
    days_held: int
    
    # Outcome
    profit_loss: float
    profit_loss_percent: float
    outcome: str  # WIN | LOSS | BREAKEVEN
    
    # Post-Trade Analysis (added after close)
    analysis: JSON
    lessons_learned: TEXT
    what_went_right: TEXT
    what_went_wrong: TEXT
    improvement_proposals: JSON

class Position:
    """Active position tracking"""
    # ...existing fields...
    trade_log_id: UUID  # Link to entry trade
    peak_profit: float  # Highest profit reached
    max_drawdown: float  # Worst drawdown from entry
    days_held: int
    current_signals: JSON  # Updated daily
```

#### 2. Post-Trade Analysis Framework

**Triggered automatically when position is closed:**

```python
def analyze_trade(trade_log: TradeLog):
    """
    Comprehensive trade analysis
    """
    analysis = {
        "outcome_type": classify_outcome(trade_log),
        "performance_vs_expectation": compare_to_expectation(trade_log),
        "signal_accuracy": evaluate_signals(trade_log),
        "timing_analysis": analyze_entry_exit_timing(trade_log),
        "hold_period_analysis": evaluate_hold_decision(trade_log),
        "parameter_effectiveness": assess_parameters(trade_log)
    }
    
    # Generate natural language lessons
    lessons = generate_lessons(trade_log, analysis)
    
    # Identify improvement opportunities
    proposals = generate_improvement_proposals(trade_log, analysis)
    
    return {
        "analysis": analysis,
        "lessons_learned": lessons,
        "improvement_proposals": proposals
    }

def classify_outcome(trade):
    """Detailed outcome classification"""
    
    if trade.outcome == "WIN":
        if trade.profit_loss_percent >= trade.expected_profit:
            return "EXCELLENT_WIN"  # Met or exceeded target
        elif trade.profit_loss_percent >= trade.expected_profit * 0.7:
            return "GOOD_WIN"  # 70%+ of target
        else:
            return "SMALL_WIN"  # Profit but below expectations
    
    elif trade.outcome == "LOSS":
        if abs(trade.profit_loss_percent) <= trade.stop_loss * 0.5:
            return "CONTROLLED_LOSS"  # Small loss, good exit
        elif abs(trade.profit_loss_percent) <= trade.stop_loss:
            return "ACCEPTABLE_LOSS"  # Stop loss worked
        else:
            return "EXCESSIVE_LOSS"  # Failed to exit properly
    
    else:
        if trade.days_held > trade.expected_hold_days:
            return "STAGNANT"  # Held too long for no gain
        else:
            return "NEUTRAL_EXIT"  # Exited at breakeven appropriately

def evaluate_signals(trade):
    """Analyze signal accuracy"""
    
    # Compare entry signals to what actually happened
    signal_performance = {}
    
    for strategy, data in trade.entry_signals.items():
        score = data['score']
        
        # Did the stock move as this signal predicted?
        actual_movement = calculate_directional_accuracy(trade)
        
        signal_performance[strategy] = {
            "entry_score": score,
            "predictive_accuracy": actual_movement,
            "contribution_to_outcome": score * actual_movement
        }
    
    # Identify best and worst signals
    best_signal = max(signal_performance, key=lambda x: signal_performance[x]['contribution_to_outcome'])
    worst_signal = min(signal_performance, key=lambda x: signal_performance[x]['contribution_to_outcome'])
    
    return {
        "signal_performance": signal_performance,
        "best_signal": best_signal,
        "worst_signal": worst_signal,
        "overall_accuracy": sum(s['predictive_accuracy'] for s in signal_performance.values()) / len(signal_performance)
    }
```

#### 3. Pattern Recognition Engine

**Identify recurring patterns across trades:**

```python
def identify_patterns(trade_history: List[TradeLog]):
    """
    Find patterns in wins and losses
    """
    
    patterns = {}
    
    # Win patterns
    wins = [t for t in trade_history if t.outcome == "WIN"]
    patterns['winning_patterns'] = {
        "best_strategies": find_highest_win_rate_strategies(wins),
        "best_hold_periods": find_optimal_hold_periods(wins),
        "best_market_conditions": find_favorable_conditions(wins),
        "best_entry_scores": find_optimal_entry_thresholds(wins),
        "winning_sectors": find_best_sectors(wins)
    }
    
    # Loss patterns
    losses = [t for t in trade_history if t.outcome == "LOSS"]
    patterns['losing_patterns'] = {
        "problematic_strategies": find_highest_loss_rate_strategies(losses),
        "dangerous_conditions": find_unfavorable_conditions(losses),
        "poor_entry_scores": find_problematic_entry_thresholds(losses),
        "losing_sectors": find_worst_sectors(losses),
        "common_mistakes": identify_repeated_mistakes(losses)
    }
    
    # Timing patterns
    patterns['timing_insights'] = {
        "best_entry_days": find_best_days_to_enter(wins),
        "best_exit_days": find_best_days_to_exit(wins),
        "optimal_hold_length": calculate_optimal_hold_by_strategy(trade_history)
    }
    
    return patterns

def find_optimal_entry_thresholds(wins):
    """
    What signal scores lead to best outcomes?
    """
    # Analyze: Does higher entry score = better win?
    # Find sweet spot for each strategy
    
    results = {}
    for strategy in ['earnings', 'seasonality', 'macro', 'sentiment', 'ipo']:
        strategy_wins = [t for t in wins if t.strategy == strategy.upper()]
        
        if len(strategy_wins) < 5:  # Not enough data
            continue
        
        # Bucket by entry score ranges
        score_buckets = {
            "60-70": [],
            "70-80": [],
            "80-90": [],
            "90-100": []
        }
        
        for trade in strategy_wins:
            score = trade.entry_signals.get(strategy, {}).get('score', 0)
            if 60 <= score < 70:
                score_buckets["60-70"].append(trade)
            elif 70 <= score < 80:
                score_buckets["70-80"].append(trade)
            elif 80 <= score < 90:
                score_buckets["80-90"].append(trade)
            elif 90 <= score <= 100:
                score_buckets["90-100"].append(trade)
        
        # Calculate avg profit for each bucket
        bucket_performance = {}
        for bucket, trades in score_buckets.items():
            if trades:
                avg_profit = sum(t.profit_loss_percent for t in trades) / len(trades)
                bucket_performance[bucket] = {
                    "avg_profit": avg_profit,
                    "trade_count": len(trades)
                }
        
        # Find optimal range
        best_bucket = max(bucket_performance, key=lambda x: bucket_performance[x]['avg_profit'])
        
        results[strategy] = {
            "optimal_range": best_bucket,
            "bucket_performance": bucket_performance,
            "recommendation": f"Best results with {strategy} score in {best_bucket} range"
        }
    
    return results
```

#### 4. Improvement Proposal System

**AI generates proposals to improve logic:**

```python
class ImprovementProposal:
    """Proposed change to trading logic"""
    id: UUID
    timestamp: DateTime
    
    proposal_type: str  # PARAMETER_ADJUST | NEW_RULE | REMOVE_RULE | STRATEGY_WEIGHT
    
    strategy: str  # Which strategy to modify
    
    current_state: JSON
    """
    What the current logic/parameter is
    """
    
    proposed_state: JSON
    """
    What it should be changed to
    """
    
    rationale: TEXT
    """
    Why this change would improve performance
    """
    
    supporting_evidence: JSON
    """
    Trade examples, statistics, patterns that support this change
    """
    
    expected_impact: JSON
    """
    {
      "win_rate_change": +5%,
      "avg_profit_change": +2%,
      "risk_change": "lower",
      "trade_frequency_change": -10%
    }
    """
    
    confidence: float  # 0-100, how confident AI is in this proposal
    
    status: str  # PENDING | APPROVED | REJECTED | IMPLEMENTED
    user_decision: str
    user_feedback: TEXT

def generate_improvement_proposals(patterns, trade_history):
    """
    Generate actionable improvement proposals
    """
    proposals = []
    
    # Example 1: Parameter adjustment
    if patterns['winning_patterns']['best_entry_scores']['earnings']['optimal_range'] == "80-90":
        current_threshold = get_current_parameter('earnings', 'minSignalScore')
        if current_threshold < 80:
            proposals.append({
                "type": "PARAMETER_ADJUST",
                "strategy": "EARNINGS",
                "parameter": "minSignalScore",
                "current_value": current_threshold,
                "proposed_value": 80,
                "rationale": "Analysis of 47 earnings trades shows optimal results with signal score 80-90. Current threshold of 70 resulted in 12 losing trades that would have been avoided.",
                "evidence": {
                    "trades_analyzed": 47,
                    "win_rate_60-70": 0.45,
                    "win_rate_70-80": 0.62,
                    "win_rate_80-90": 0.78,
                    "avg_profit_improvement": "+3.2%"
                },
                "confidence": 85
            })
    
    # Example 2: New rule suggestion
    if patterns['losing_patterns']['dangerous_conditions']['high_vix']:
        proposals.append({
            "type": "NEW_RULE",
            "strategy": "ALL",
            "rule": "Skip entries when VIX > 25",
            "rationale": "18 of 23 losses (78%) occurred when VIX was above 25. These high-volatility periods led to stop-outs even when signals were strong.",
            "evidence": {
                "losses_with_high_vix": 18,
                "losses_with_low_vix": 5,
                "avg_loss_high_vix": -12.3,
                "avg_loss_low_vix": -6.2
            },
            "confidence": 92
            })
    
    # Example 3: Strategy weight adjustment
    earnings_win_rate = calculate_win_rate(trade_history, 'EARNINGS')
    sentiment_win_rate = calculate_win_rate(trade_history, 'SENTIMENT')
    
    if earnings_win_rate > sentiment_win_rate + 0.15:  # 15% better
        proposals.append({
            "type": "STRATEGY_WEIGHT",
            "change": "Increase earnings weight, decrease sentiment weight",
            "rationale": f"Earnings strategy has {earnings_win_rate:.1%} win rate vs sentiment's {sentiment_win_rate:.1%}. Should allocate more capital to higher-performing strategy.",
            "current_weights": {
                "earnings": 0.25,
                "sentiment": 0.25
            },
            "proposed_weights": {
                "earnings": 0.35,
                "sentiment": 0.15
            },
            "confidence": 75
        })
    
    return proposals

def calculate_win_rate(trades, strategy):
    """Calculate win rate for specific strategy"""
    strategy_trades = [t for t in trades if t.strategy == strategy]
    if not strategy_trades:
        return 0.0
    wins = [t for t in strategy_trades if t.outcome == "WIN"]
    return len(wins) / len(strategy_trades)
```

#### 5. User Approval Workflow

**Proposals require user review:**

```python
class ApprovalWorkflow:
    """
    User reviews and approves/rejects proposals
    """
    
    def present_proposal(proposal: ImprovementProposal):
        """
        Show proposal to user in Learning & Analytics tab
        """
        return {
            "summary": generate_summary(proposal),
            "detailed_rationale": proposal.rationale,
            "evidence": format_evidence(proposal.supporting_evidence),
            "before_after": show_before_after(proposal),
            "risk_assessment": evaluate_risk(proposal),
            "actions": ["APPROVE", "REJECT", "MODIFY", "TEST_FIRST"]
        }
    
    def handle_user_decision(proposal_id, decision, feedback):
        """
        Process user's decision
        """
        proposal = get_proposal(proposal_id)
        
        if decision == "APPROVE":
            # Implement the change
            apply_proposal(proposal)
            proposal.status = "IMPLEMENTED"
            log_change(proposal, "User approved and implemented")
            
        elif decision == "TEST_FIRST":
            # Run backtest with proposed change
            backtest_results = backtest_proposal(proposal, historical_data=last_90_days)
            return {
                "backtest_results": backtest_results,
                "recommendation": "Proceed" if backtest_results.improvement > 0 else "Reconsider"
            }
            
        elif decision == "MODIFY":
            # User wants to tweak the proposal
            proposal.status = "PENDING_MODIFICATION"
            proposal.user_feedback = feedback
            
        elif decision == "REJECT":
            proposal.status = "REJECTED"
            proposal.user_feedback = feedback
            log_change(proposal, f"User rejected: {feedback}")
```

#### 6. Learning Database Schema

```sql
-- Trade logs with full context
CREATE TABLE trade_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    action VARCHAR(4) NOT NULL,  -- BUY/SELL
    shares INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_value DECIMAL(12,2) NOT NULL,
    portfolio_percent DECIMAL(5,2),
    
    strategy VARCHAR(20) NOT NULL,
    hold_classification VARCHAR(20),
    expected_hold_days INTEGER,
    
    entry_signals JSONB,
    market_conditions JSONB,
    technicals JSONB,
    ai_rationale TEXT NOT NULL,  -- CRITICAL: Full reasoning
    parameters_used JSONB,
    
    exit_reason VARCHAR(50),
    exit_signals JSONB,
    days_held INTEGER,
    
    profit_loss DECIMAL(10,2),
    profit_loss_percent DECIMAL(6,2),
    outcome VARCHAR(20),  -- WIN/LOSS/BREAKEVEN
    
    analysis JSONB,
    lessons_learned TEXT,
    what_went_right TEXT,
    what_went_wrong TEXT,
    improvement_proposals JSONB,
    
    INDEX idx_symbol (symbol),
    INDEX idx_strategy (strategy),
    INDEX idx_outcome (outcome),
    INDEX idx_timestamp (timestamp)
);

-- Improvement proposals
CREATE TABLE improvement_proposals (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    proposal_type VARCHAR(30) NOT NULL,
    strategy VARCHAR(20),
    current_state JSONB NOT NULL,
    proposed_state JSONB NOT NULL,
    rationale TEXT NOT NULL,
    supporting_evidence JSONB,
    expected_impact JSONB,
    confidence DECIMAL(5,2),
    
    status VARCHAR(20) DEFAULT 'PENDING',
    user_decision VARCHAR(20),
    user_feedback TEXT,
    implemented_at TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_strategy (strategy)
);

-- Pattern cache (for performance)
CREATE TABLE pattern_cache (
    id UUID PRIMARY KEY,
    analysis_date DATE NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    trade_count INTEGER,
    confidence DECIMAL(5,2),
    
    INDEX idx_date (analysis_date),
    INDEX idx_type (pattern_type)
);
```

#### 7. API Endpoints

```python
# Trade logging
POST /api/v1/trades/log
"""
Log a trade with full AI rationale
Body: TradeLog object
"""

GET /api/v1/trades/history
"""
Get trade history with filters
Query params: symbol, strategy, outcome, start_date, end_date
"""

# Analysis
GET /api/v1/learning/analysis
"""
Get overall performance analysis
Returns: Win rates, best strategies, patterns
"""

GET /api/v1/learning/patterns
"""
Get identified patterns
Returns: Winning patterns, losing patterns, timing insights
"""

POST /api/v1/learning/analyze-trade/{trade_id}
"""
Trigger post-trade analysis for specific trade
Returns: Analysis results, lessons, proposals
"""

# Proposals
GET /api/v1/learning/proposals
"""
Get pending improvement proposals
Query params: status, strategy
"""

POST /api/v1/learning/proposals/{id}/decision
"""
Approve/reject/modify a proposal
Body: {decision: "APPROVE|REJECT|MODIFY|TEST", feedback: "..."}
"""

POST /api/v1/learning/proposals/{id}/backtest
"""
Backtest a proposal before implementing
Returns: Simulated results
"""

# Insights
GET /api/v1/learning/insights
"""
Get actionable insights
Returns: Top lessons, recommended changes, performance metrics
"""
```

---
