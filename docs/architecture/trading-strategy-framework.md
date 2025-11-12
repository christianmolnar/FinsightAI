# FInsightAI Trading Strategy Framework
**Intelligent Medium-Term Trading Agent**

## Trading Philosophy

### Core Approach: "Catalyst-Driven Value Trading"
- **Holding Period**: 1-30 days (swing/position trading)
- **Risk Profile**: Conservative to moderate (no aggressive day trading)
- **Decision Basis**: Fundamental catalysts backed by technical confirmation
- **Exit Strategy**: Intelligent profit targets with risk management

---

## Primary Trading Signals (Fundamental Catalysts)

### 1. 📊 **Earnings Momentum Strategy**
**Signal**: Companies with projected strong earnings announcements

**Criteria**:
- Earnings announcement within 1-14 days
- Consensus EPS growth >15% YoY
- Revenue growth >10% YoY
- Positive earnings revisions (upgrades in last 30 days)
- Historical earnings beat rate >70%

**Entry Timing**: 3-7 days before earnings announcement
**Exit Strategy**: 
- Target: +8-15% or day after earnings (whichever comes first)
- Stop Loss: -5% from entry

**Risk Mitigation**: Max 20% of portfolio in pre-earnings positions

---

### 2. 📅 **Seasonality & Calendar Effects**
**Signal**: Stocks with historically strong performance in specific periods

**Criteria**:
- Christmas/Holiday retail boost (Oct-Dec): Consumer discretionary
- Tax season software (Jan-Apr): Financial software
- Summer driving season (May-Aug): Oil & travel
- Back-to-school (Aug-Sep): Education & tech
- Quarterly rebalancing (Mar, Jun, Sep, Dec): Index additions

**Entry Timing**: 2-4 weeks before seasonal peak
**Exit Strategy**:
- Target: +10-20% or end of seasonal period
- Stop Loss: -7% from entry

**Historical Analysis**: Requires 5+ years of seasonal performance data

---

### 3. 🌍 **Macro & Economic Catalysts**
**Signal**: Companies positioned to benefit from economic/world events

**Criteria**:
- **Interest Rate Changes**: Banks (rising rates), REITs (falling rates)
- **Commodity Price Movements**: Energy, materials, agriculture stocks
- **Economic Indicators**: GDP growth, unemployment, inflation data
- **Geopolitical Events**: Defense, energy, supply chain impacts
- **Regulatory Changes**: Healthcare, tech, financial sector impacts

**Entry Timing**: Within 48 hours of catalyst announcement
**Exit Strategy**:
- Target: +5-12% depending on catalyst strength
- Stop Loss: -6% from entry
- Time Stop: 30 days maximum hold

---

### 4. 📱 **Social Sentiment & Alternative Data**
**Signal**: Positive sentiment shift with volume confirmation

**Criteria**:
- Social media sentiment score >70% positive (Twitter, Reddit, StockTwits)
- Institutional buying pressure (13F filings, insider buying)
- Analyst upgrades with price target increases
- News sentiment analysis >80% positive
- Search trend volume increase >50% (Google Trends)

**Volume Confirmation**: Daily volume >150% of 20-day average
**Entry Timing**: When sentiment + volume align
**Exit Strategy**:
- Target: +6-10% or sentiment reversal
- Stop Loss: -4% from entry

---

### 5. 🎯 **Additional Strategy Categories**

#### **5a. Merger & Acquisition Arbitrage**
- Announced M&A deals with spread >2%
- High probability of completion (regulatory approval likely)
- Target: Close the spread (2-8% typical)

#### **5b. Earnings Surprise Follow-Through** 
- Stocks that beat earnings by >10%
- Strong guidance raises
- Entry day after earnings if gap up <5%

#### **5c. Breakout & Technical Catalysts**
- 52-week high breakouts with volume
- Chart pattern completions (triangles, flags)
- Key resistance level breaks

#### **5d. Dividend & Corporate Action Plays**
- Special dividend announcements
- Stock buyback programs >5% of float
- Spin-off situations with undervalued assets

#### **5e. ETF Inclusion Plays**
- Stocks being added to major indices (S&P 500, Russell)
- Expected forced buying from index funds
- Entry before inclusion date

---

## Technical Analysis Backup (Confirmation Filters)

### Required Technical Confirmation (All Signals Must Pass 3 of 5):

1. **Trend Analysis**
   - Stock above 20-day moving average
   - 20-day MA above 50-day MA (uptrend)
   - Price >5% above 200-day MA (bull market confirmation)

2. **Momentum Indicators**
   - RSI between 40-70 (not overbought/oversold)
   - MACD line above signal line
   - Stochastic %K above %D

3. **Volume Analysis**
   - Average daily volume >500K shares
   - Recent volume >120% of 20-day average
   - On-balance volume trending up

4. **Support & Resistance**
   - Price above key support level
   - No major resistance within 10% above current price
   - Bollinger Bands not severely contracted

5. **Relative Strength**
   - Outperforming S&P 500 over last 30 days
   - Sector relative strength >1.0
   - Price performance ranking top 50% in sector

---

## Exit Strategy Framework

### Profit Targets (Automatically Set Limit Orders)

**Conservative Targets (70% of position)**:
- Earnings plays: +8%
- Seasonality: +10%
- Macro events: +5%
- Sentiment: +6%

**Aggressive Targets (30% of position)**:
- Earnings plays: +15%
- Seasonality: +20%
- Macro events: +12%
- Sentiment: +10%

### Stop Loss Rules (Automatically Set)

**Standard Stop Loss**: -5% from entry price
**Tight Stop Loss** (high volatility): -3% from entry
**Wide Stop Loss** (strong conviction): -8% from entry

### Time-Based Exits
- **Maximum Hold**: 30 calendar days
- **Earnings Plays**: Exit day after earnings regardless of profit/loss
- **Event-Driven**: Exit 2 days after event conclusion

### Dynamic Exit Conditions
- **Sentiment Reversal**: Exit if social sentiment drops below 40%
- **Volume Dry-Up**: Exit if volume drops below 50% of 20-day average for 3 days
- **Technical Breakdown**: Exit if price breaks below entry-day low

---

## Risk Management Rules

### Position Sizing
- **Maximum Single Position**: 5% of portfolio
- **Maximum Sector Exposure**: 25% of portfolio  
- **Maximum Strategy Exposure**: 
  - Earnings plays: 20%
  - Seasonality: 15%
  - Macro events: 10%
  - Sentiment: 15%

### Portfolio Risk Limits
- **Maximum Drawdown**: 15% from peak
- **Daily Loss Limit**: 3% of portfolio value
- **Consecutive Losing Trades**: Stop after 5 losses, review strategy

### Market Condition Filters
- **VIX >25**: Reduce position sizes by 50%
- **Market Downtrend**: No new entries if S&P 500 below 50-day MA
- **Low Liquidity Periods**: No entries during major holidays

---

## Decision Engine Logic

### Trade Scoring Algorithm

**Signal Strength Score (0-100)**:
- Primary catalyst strength: 40 points
- Technical confirmation: 30 points
- Volume confirmation: 15 points
- Market conditions: 10 points
- Risk/reward ratio: 5 points

**Minimum Score for Entry**: 70/100

### Confidence Levels
- **95-100**: Maximum position size (5% of portfolio)
- **85-94**: Large position (3-4% of portfolio)
- **75-84**: Medium position (2-3% of portfolio)
- **70-74**: Small position (1-2% of portfolio)

### AI Learning Components
- **Success Rate Tracking**: Monitor win rate by strategy type
- **Adaptive Scoring**: Adjust weights based on historical performance
- **Market Regime Detection**: Modify strategies for bull/bear/sideways markets

---

## Implementation Requirements

### Data Sources Needed
1. **Financial Data**: Earnings, revenue, growth rates
2. **Economic Data**: Fed rates, GDP, inflation, unemployment
3. **News & Sentiment**: Financial news, social media, analyst reports
4. **Technical Data**: Price, volume, indicators
5. **Corporate Actions**: Dividends, M&A, buybacks, spin-offs
6. **Insider Trading**: Director/officer transactions
7. **Institutional Flow**: 13F filings, ETF flows

### Trading Infrastructure
1. **Order Management**: Automatic limit/stop order placement
2. **Portfolio Tracking**: Real-time P&L, risk metrics
3. **Alert System**: Trade signals, exit triggers, risk warnings
4. **Backtesting Engine**: Strategy validation and optimization
5. **Paper Trading**: Risk-free strategy testing

### Dashboard Requirements
1. **Portfolio Overview**: Performance, allocation, risk metrics
2. **Individual Stock Analysis**: Charts, indicators, catalysts
3. **Trade Journal**: Entry/exit logs, performance analysis
4. **Market Scanner**: Real-time signal detection
5. **Risk Monitor**: Portfolio heat map, exposure analysis

---

## Success Metrics

### Performance Targets
- **Annual Return**: 15-25% (beating S&P 500 by 5-10%)
- **Win Rate**: >55% of trades profitable
- **Average Win**: >+8%
- **Average Loss**: <-4%
- **Profit Factor**: >1.5 (gross profit / gross loss)
- **Sharpe Ratio**: >1.2
- **Maximum Drawdown**: <15%

### Risk Metrics
- **Beta**: 0.8-1.2 (market correlation)
- **Volatility**: <20% annualized
- **Value at Risk (1%)**: <3% daily loss
- **Correlation to Market**: <0.85 during downturns

---

*This framework combines fundamental catalyst identification with technical analysis confirmation to create an intelligent, risk-managed trading system optimized for 1-30 day holding periods.*
