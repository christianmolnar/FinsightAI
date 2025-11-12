# FInsightAI Configuration Interface Specification
**Intelligent Parameter Configuration with AI Recommendations**

## Configuration Tab Architecture

### 📊 **Strategy Configuration Tab**
*Complete user control over all trading parameters with AI recommendations*

---

## 1. 📊 **Earnings Momentum Configuration**

### **Detection Criteria**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 EARNINGS MOMENTUM STRATEGY                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Earnings Window:        [1] to [14] days before announcement        │
│                        ├─────────────────────────────────────────┤   │
│                        │ 🤖 Get AI Recommendation                │   │
│                        └─────────────────────────────────────────┘   │
│                                                                     │
│ EPS Growth Threshold:   [15]% YoY minimum                          │
│                        ├─────────────────────────────────────────┤   │
│                        │ 🤖 Optimize for Market Conditions       │   │
│                        └─────────────────────────────────────────┘   │
│                                                                     │
│ Revenue Growth:         [10]% YoY minimum                          │
│ Beat Rate Required:     [70]% historical success                   │
│ Revision Window:        [30] days for analyst upgrades             │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🧠 AI OPTIMIZATION                                              │ │
│ │                                                                 │ │
│ │ Market Regime: [Bull Market] ▼                                  │ │
│ │ Risk Tolerance: [●●●○○] Moderate                               │ │
│ │ Portfolio Size: [$300] Current Balance                         │ │
│ │                                                                 │ │
│ │ [🤖 Get AI Recommendation for All Parameters]                   │ │
│ │ [📊 Backtest Current Settings] [💾 Save Configuration]         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### **Entry & Exit Rules**
```
┌─────────────────────────────────────────────────────────────────────┐
│ ENTRY/EXIT CONFIGURATION                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Entry Timing:       [3] to [7] days before earnings                │
│ Position Size:      [5]% max of portfolio                          │
│ Portfolio Limit:    [20]% max in earnings plays                    │
│                                                                     │
│ Profit Targets:     Conservative: [8]%  Aggressive: [15]%          │
│ Stop Loss:          [-5]% from entry                               │
│ Time Exit:          [✓] Day after earnings regardless              │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🎯 AI EXIT STRATEGY OPTIMIZER                                   │ │
│ │                                                                 │ │
│ │ Historical Win Rate: 68% with current settings                 │ │
│ │ Avg Winner: +11.2% | Avg Loser: -3.8%                         │ │
│ │ Profit Factor: 1.74 (Good)                                     │ │
│ │                                                                 │ │
│ │ [🤖 Optimize Profit Targets] [🤖 Optimize Stop Loss]           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 📅 **Seasonality Configuration**

### **Seasonal Patterns Setup**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📅 SEASONALITY STRATEGY                                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Holiday Retail (Oct-Dec):                                          │
│ ├ Sectors: [Consumer Discretionary] [Retail] [E-commerce]          │
│ ├ Entry Window: [2-4] weeks before peak                            │
│ ├ Min Historical Years: [5] years of data required                 │
│ └ Expected Return: [10-20]% target range                           │
│                                                                     │
│ Summer Driving (May-Aug):                                          │
│ ├ Sectors: [Energy] [Travel] [Airlines] [Auto]                    │
│ ├ Oil Price Correlation: [✓] Factor in crude prices               │
│ └ Weather Data: [✓] Include temperature forecasts                 │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🧠 SEASONAL AI ANALYZER                                         │ │
│ │                                                                 │ │
│ │ Current Date: November 11, 2025                                │ │
│ │ Next Opportunity: Holiday Retail Season (Starting)             │ │
│ │ Strength: ●●●●○ Strong (Based on economic indicators)          │ │
│ │                                                                 │ │
│ │ Top AI Picks for This Season:                                  │ │
│ │ • AMZN (E-commerce leader, Prime benefits)                     │ │
│ │ • TJX (Off-price retail strength)                              │ │
│ │ • DIS (Holiday theme parks, streaming)                         │ │
│ │                                                                 │ │
│ │ [🤖 Get Full Seasonal Analysis] [📊 Historical Performance]     │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 🌍 **Macro & Economic Configuration**

### **Economic Indicators Setup**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🌍 MACRO & ECONOMIC CATALYSTS                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Interest Rate Sensitivity:                                          │
│ ├ Rate Increase Threshold: [0.25]% for trigger                     │
│ ├ Banking Sector Weight: [●●●○○] High sensitivity                  │
│ ├ REIT Inverse Weight: [●●●●○] Very high sensitivity               │
│ └ Entry Timing: Within [48] hours of Fed announcement              │
│                                                                     │
│ Commodity Price Triggers:                                          │
│ ├ Oil Price Change: [±5]% weekly move                             │
│ ├ Gold Correlation: [✓] Include precious metals                   │
│ ├ Agriculture: [✓] Weather + supply chain factors                 │
│ └ Currency Impact: [✓] USD strength factor                        │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🎯 CURRENT MACRO ENVIRONMENT                                    │ │
│ │                                                                 │ │
│ │ Fed Policy: Neutral-to-Hawkish (Rate cuts unlikely)            │ │
│ │ Inflation: 2.8% (Slightly elevated)                            │ │
│ │ USD Strength: Strong (DXY: 106.2)                              │ │
│ │ Geopolitical Risk: Medium (Multiple conflicts)                 │ │
│ │                                                                 │ │
│ │ AI Recommended Focus:                                           │ │
│ │ • Dollar-strong exporters (tech, defense)                      │ │
│ │ • Inflation-resistant businesses                                │ │
│ │ • Energy stability plays                                        │ │
│ │                                                                 │ │
│ │ [🤖 Get Macro Analysis] [🔄 Update Economic Data]              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. 📱 **Social Sentiment Configuration**

### **Alternative Data Sources**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📱 SOCIAL SENTIMENT & ALTERNATIVE DATA                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Social Media Sentiment:                                            │
│ ├ Positive Threshold: [70]% minimum sentiment score               │ │
│ ├ Sources: [✓] Twitter [✓] Reddit [✓] StockTwits [✓] Discord      │
│ ├ Volume Requirement: [150]% of 20-day average                    │
│ └ Sentiment Change: [+20]% improvement required                   │
│                                                                     │
│ News & Analyst Data:                                               │
│ ├ News Positivity: [80]% positive sentiment                       │
│ ├ Analyst Upgrades: [2+] upgrades in [30] days                   │
│ ├ Price Target Increase: [10]% minimum raise                      │
│ └ Institutional Activity: [✓] Include 13F filings                 │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 📊 CURRENT SENTIMENT LEADERS                                    │ │
│ │                                                                 │ │
│ │ Most Bullish Sentiment (Last 24h):                             │ │
│ │ 1. NVDA (AI optimism) - 89% positive                           │ │
│ │ 2. TSLA (FSD progress) - 76% positive                          │ │
│ │ 3. AAPL (iPhone cycle) - 74% positive                          │ │
│ │                                                                 │ │
│ │ Sentiment Reversals (Bullish Turn):                            │ │
│ │ 1. META (+34% sentiment in 3 days)                             │ │
│ │ 2. GOOGL (+28% sentiment recovery)                             │ │
│ │                                                                 │ │
│ │ [🤖 Analyze Current Sentiment] [📈 Sentiment Trends]           │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. ⚙️ **Technical Analysis Configuration**

### **Indicator Thresholds**
```
┌─────────────────────────────────────────────────────────────────────┐
│ ⚙️ TECHNICAL ANALYSIS CONFIRMATION FILTERS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Required Confirmations: [3] of [5] must pass                       │
│                                                                     │
│ 1. Trend Analysis:                                                  │
│    ├ Above 20-day MA: [✓] Required                                │
│    ├ 20-day > 50-day MA: [✓] Required                             │
│    └ Price > 200-day MA: [5]% minimum above                       │
│                                                                     │
│ 2. Momentum Indicators:                                             │
│    ├ RSI Range: [40] to [70] (avoid extremes)                     │
│    ├ MACD Signal: [✓] Line above signal required                  │
│    └ Stochastic: [✓] %K above %D required                         │
│                                                                     │
│ 3. Volume Analysis:                                                 │
│    ├ Min Daily Volume: [500K] shares                              │
│    ├ Volume Increase: [120]% of 20-day average                    │
│    └ OBV Trend: [✓] On-balance volume rising                      │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🔧 AI TECHNICAL OPTIMIZER                                       │ │
│ │                                                                 │ │
│ │ Current Market Regime: Bull Market (Trending Higher)           │ │
│ │                                                                 │ │
│ │ AI Recommendations:                                             │ │
│ │ • RSI: Lower to 35-65 (more opportunities)                     │ │
│ │ • Volume: Increase to 130% (higher conviction)                 │ │
│ │ • Add: Relative Strength filter (outperform SPY)               │ │
│ │                                                                 │ │
│ │ Win Rate Impact: +8% with these changes                        │ │
│ │                                                                 │ │
│ │ [🤖 Apply AI Recommendations] [🧪 Backtest Changes]            │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. 🎯 **Risk Management Configuration**

### **Portfolio Risk Controls**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🎯 RISK MANAGEMENT CONTROLS                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Position Sizing:                                                    │
│ ├ Max Single Position: [5]% of portfolio                          │
│ ├ Max Sector Exposure: [25]% of portfolio                         │
│ ├ Cash Reserve: [10]% minimum cash level                          │
│ └ Correlation Limit: [0.7] max correlation between positions      │
│                                                                     │
│ Risk Limits:                                                        │
│ ├ Max Portfolio Drawdown: [15]% from peak                         │
│ ├ Daily Loss Limit: [3]% of portfolio value                       │
│ ├ Consecutive Losses: [5] trades before pause                     │
│ └ VIX Threshold: [25] reduce sizes by 50%                         │
│                                                                     │
│ Stop Loss Configuration:                                            │
│ ├ Standard Stop: [-5]% from entry                                 │
│ ├ Tight Stop (High Vol): [-3]% from entry                        │
│ ├ Wide Stop (High Conv): [-8]% from entry                        │
│ └ Trailing Stop: [✓] Enable for winning positions                 │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🛡️ AI RISK OPTIMIZER                                           │ │
│ │                                                                 │ │
│ │ Current Portfolio Risk: 12% (Low)                               │ │
│ │ Sharpe Ratio Projection: 1.4 (Good)                           │ │
│ │ Max Drawdown Estimate: 11% (Within limits)                     │ │
│ │                                                                 │ │
│ │ AI Risk Assessment:                                             │ │
│ │ "Portfolio is well-diversified. Can increase position sizes    │ │
│ │ to 6% for high-conviction trades given low correlation."        │ │
│ │                                                                 │ │
│ │ Recommended Adjustments:                                        │ │
│ │ • Increase max position to 6% (from 5%)                        │ │
│ │ • Add sector rotation based on seasonality                      │ │
│ │ • Implement volatility-adjusted position sizing                 │ │
│ │                                                                 │ │
│ │ [🤖 Apply Risk Optimization] [📊 Risk Simulation]              │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 7. 🤖 **AI Model Configuration**

### **LLM Integration Setup**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 🤖 AI MODEL CONFIGURATION                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Primary AI Models:                                                  │
│ ├ OpenAI: [○ Not Configured] [🔧 Setup API Key]                   │
│ ├ Anthropic (Claude): [○ Not Configured] [🔧 Setup API Key]       │
│ ├ Local Model: [○ Not Available] [📥 Download Llama]              │
│ └ Backup Service: [✓] Use Schwab Fundamental Data                  │
│                                                                     │
│ AI Recommendation Settings:                                         │
│ ├ Risk Tolerance: [●●●○○] Moderate (User Profile)                 │
│ ├ Market Experience: [●●○○○] Intermediate                          │
│ ├ Time Horizon: [●●●●○] Short-Medium Term (1-30 days)             │
│ └ Capital Amount: [$300] Current Portfolio Size                    │
│                                                                     │
│ Update Frequency:                                                   │
│ ├ Parameter Optimization: [Weekly] Review                          │
│ ├ Market Regime Analysis: [Daily] Assessment                       │
│ ├ Strategy Performance: [After each trade] Learning               │
│ └ Economic Updates: [Real-time] On major events                   │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🚀 QUICK SETUP                                                  │ │
│ │                                                                 │ │
│ │ [🔑 Add OpenAI API Key] [🔑 Add Anthropic API Key]             │ │
│ │                                                                 │ │
│ │ Or start with basic configuration:                              │ │
│ │ [🎯 Use Conservative Defaults] [📊 Use Aggressive Defaults]     │ │
│ │ [🧠 Run Initial AI Analysis] [📋 Export Configuration]         │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 8. 📊 **Global Configuration Actions**

### **Master Controls**
```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 MASTER CONFIGURATION PANEL                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ 🧠 AI MASTER OPTIMIZER                                          │ │
│ │                                                                 │ │
│ │ "Analyze my portfolio, current market conditions, and my        │ │
│ │ risk tolerance to recommend optimal settings for ALL            │ │
│ │ trading strategies and parameters."                              │ │
│ │                                                                 │ │
│ │ Current Context:                                                │ │
│ │ • Portfolio: $300 (Small, need efficient deployment)           │ │
│ │ • Market: Bull market with high valuations                     │ │
│ │ • Season: Holiday season approaching                           │ │
│ │ • Risk: Moderate (learning phase)                              │ │
│ │                                                                 │ │
│ │ [🤖 GET COMPREHENSIVE AI RECOMMENDATIONS]                       │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ Quick Actions:                                                      │
│ ├ [📊 Backtest All Strategies] - Test current settings             │
│ ├ [🔄 Reset to Defaults] - Conservative baseline                   │
│ ├ [📥 Import Configuration] - Load saved setup                     │
│ ├ [📤 Export Configuration] - Save current setup                   │
│ ├ [🎯 Market Regime Adjust] - Adapt to current conditions         │
│ └ [🚫 Emergency Stop All] - Halt all trading immediately           │
│                                                                     │
│ Configuration Status:                                               │
│ ├ Strategies: [4/5] Configured                                     │
│ ├ Technical: [✓] Complete                                          │
│ ├ Risk Management: [✓] Complete                                    │
│ ├ AI Integration: [⚠] Need API Keys                               │
│ └ Backtesting: [○] Not Run                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Requirements

### Backend API Endpoints Needed:
```python
POST /api/config/strategy/{strategy_type}  # Update strategy parameters
GET  /api/config/strategy/{strategy_type}   # Get current config
POST /api/ai/recommend/strategy            # Get AI recommendations
POST /api/ai/optimize/all                  # Master AI optimization
POST /api/config/backtest                  # Run backtest with settings
GET  /api/config/export                    # Export configuration
POST /api/config/import                    # Import configuration
```

### LLM Integration Setup:
```python
# Add to .env file
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
AI_MODEL_PREFERENCE=openai  # or anthropic or local

# AI Service Configuration
AI_TEMPERATURE=0.2          # Lower = more conservative recommendations
AI_MAX_TOKENS=2000         # Response length limit
AI_MODEL_NAME=gpt-4-turbo  # or claude-3-sonnet
```

### Database Schema for Configuration:
```sql
-- Store user configurations
CREATE TABLE strategy_configurations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    strategy_type VARCHAR(50),
    parameters JSONB,
    ai_optimized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Store AI recommendations history
CREATE TABLE ai_recommendations (
    id SERIAL PRIMARY KEY,
    config_id INTEGER REFERENCES strategy_configurations(id),
    recommendation_text TEXT,
    confidence_score FLOAT,
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

This configuration interface gives you complete control over every trading parameter while leveraging AI to optimize settings based on market conditions, your risk tolerance, and portfolio size. Each parameter can be manually adjusted or AI-optimized with a single click.
