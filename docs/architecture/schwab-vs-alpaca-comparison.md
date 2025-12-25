# Schwab vs Alpaca: Migration Assessment

**Document Version:** 2.0  
**Created:** December 25, 2025  
**Updated:** December 25, 2025  
**Status:** ✅ **DECISION MADE: MIGRATING TO ALPACA**  
**Owner:** FInsightAI Architecture Team

---

## 🚀 MIGRATION DECISION

**✅ APPROVED: Switching from Schwab to Alpaca**

**Date:** December 25, 2025  
**Rationale:**
- No actual Schwab account usage ($300 holding only, no trades)
- No emotional or financial ties to Schwab
- Permanent API keys eliminate 7-day re-auth problem
- Better foundation for autonomous trading agent
- Simpler integration = faster Phase 4 development

**Timeline:** 4-6 hours (AI-assisted)  
**Branch:** `feature/alpaca-migration`  
**See:** `/docs/implementation/alpaca-migration-plan.md`

---

## 🎯 Executive Summary

**TL;DR:** Alpaca is **significantly easier** to integrate than Schwab. Since we have no ties to Schwab (only $300 holding, no trades), migrating is the obvious choice.

**Original Concern:** "You'd be locked into Alpaca brokerage"  
**Reality:** We were never trading on Schwab anyway - account opened solely for API access.

---

## 📊 Side-by-Side Comparison

| Feature | Schwab API | Alpaca API | Winner |
|---------|------------|------------|--------|
| **Authentication** | OAuth 2.0 (complex) | **API Keys (simple)** | 🏆 **Alpaca** |
| **Token Lifetime** | 7 days (manual re-auth) | **Permanent API keys** | 🏆 **Alpaca** |
| **Your Existing Account** | ✅ **Can trade your account** | ❌ Must open Alpaca account | 🏆 **Schwab** |
| **Paper Trading** | Limited | ✅ **Full paper trading** | 🏆 **Alpaca** |
| **Commission-Free** | ✅ Yes | ✅ Yes | 🤝 Tie |
| **Options Trading** | ✅ Yes | ✅ Yes | 🤝 Tie |
| **Crypto Trading** | ❌ No | ✅ **Yes** | 🏆 **Alpaca** |
| **Market Data** | ✅ Real-time included | ✅ Real-time included | 🤝 Tie |
| **WebSocket Streaming** | ✅ Yes | ✅ **Yes (easier)** | 🏆 **Alpaca** |
| **Python SDK** | schwabdev (community) | **alpaca-py (official)** | 🏆 **Alpaca** |
| **API Documentation** | Good | **Excellent** | 🏆 **Alpaca** |
| **Rate Limits** | 120 req/min | **200 req/min** | 🏆 **Alpaca** |
| **Account Minimum** | $0 | $0 | 🤝 Tie |
| **Margin Trading** | ✅ Yes | ✅ Yes | 🤝 Tie |
| **Fractional Shares** | ❌ No | ✅ **Yes** | 🏆 **Alpaca** |
| **After-Hours Trading** | ✅ Yes | ✅ Yes | 🤝 Tie |
| **Broker Reputation** | 🏆 **Major firm (150 years)** | Small (founded 2015) | 🏆 **Schwab** |
| **SIPC Protection** | ✅ $500k | ✅ $500k | 🤝 Tie |

**Score:** Alpaca wins 10, Schwab wins 2, Tie 8

---

## 🔑 KEY DIFFERENCE: Account Access

### ~~Schwab Approach~~ (What We Thought We Had)
```
Your Money → Your Schwab Account → Schwab API → FInsightAI
```
- ❌ **REALITY:** Only $300 holding, never traded
- ❌ No actual "existing account" to preserve
- ❌ Opened account solely for API access

### Alpaca Approach (What We're Getting)
```
Your Money → NEW Alpaca Account → Alpaca API → FInsightAI
```
- ✅ Must open Alpaca account (same as we did with Schwab)
- ✅ Transfer $300 from Schwab to Alpaca (trivial)
- ✅ **Better platform for our use case**

**The "dealbreaker" wasn't a dealbreaker** - we're in the same situation regardless:
1. ~~Open brokerage account~~ (Already did this for Schwab)
2. ~~Fund account~~ (Already funded Schwab with $300)
3. **Switch:** Close Schwab, open Alpaca, transfer funds

**Net Change:** 0 (we're just picking the better broker from the start)

---

## 🛠️ Migration Effort Estimate

### ✅ APPROVED PLAN: Replace Schwab with Alpaca

**Effort:** 4-6 hours (AI-assisted, not 3-5 days!)

**AI-Assisted Timeline:**

1. **Authentication System** (4 hours)
   - ❌ Remove: OAuth 2.0 flow, token refresh logic
   - ✅ Add: API key storage (2 lines of config)
   - ✅ Add: Header-based auth (simpler)

2. **API Client** (6 hours)
   - ❌ Remove: schwabdev library
   - ✅ Add: alpaca-py official SDK
   - ✅ Rewrite: schwab_service.py → alpaca_service.py

3. **Endpoint Mapping** (8 hours)
   - Account info: Similar
   - Positions: Similar (easier format)
   - Orders: Different order types
   - Market data: Different structure

4. **Database Models** (2 hours)
   - Minimal changes (mostly compatible)
   - Some field name updates

5. **Frontend Changes** (4 hours)
   - RealPortfolio.js: Change API calls
   - No UI changes needed

6. **Testing** (6 hours)
   - Integration testing with Alpaca sandbox
   - Paper trading verification
   - Live trading verification

**Code Diff:**
```
Files Changed: ~8 files
Lines Changed: ~800-1000 lines
New Files: 2 (alpaca_service.py, alpaca auth setup)
Deleted Files: 3 (schwab_api.py, schwab auth, tokens.json)
```

### Option 2: Support BOTH Brokers (Recommended)

**Effort:** 1-2 weeks (~40-60 hours)

**Architecture:**
```python
# /backend/app/services/broker_factory.py
class BrokerFactory:
    @staticmethod
    def get_broker(broker_type: str):
        if broker_type == "schwab":
            return SchwabBroker()
        elif broker_type == "alpaca":
            return AlpacaBroker()
        else:
            raise ValueError(f"Unknown broker: {broker_type}")

# /backend/app/services/base_broker.py
class BaseBroker(ABC):
    @abstractmethod
    async def get_account_info(self):
        pass
    
    @abstractmethod
    async def get_positions(self):
        pass
    
    @abstractmethod
    async def place_order(self, symbol, side, quantity):
        pass

# Users can choose broker per portfolio
```

**Benefits:**
- ✅ Keep your existing Schwab account
- ✅ Add Alpaca for paper trading / testing
- ✅ Users choose preferred broker
- ✅ Hedge against broker API changes

**Drawbacks:**
- More complex architecture
- Double the integration testing
- Need to maintain two broker adapters

---

## 💰 Cost Comparison

| Item | Schwab | Alpaca |
|------|--------|--------|
| **Monthly Platform Fee** | $0 | $0 |
| **Stock Trades** | $0 | $0 |
| **Options Contracts** | $0.65/contract | $0.65/contract |
| **API Access** | Free (developer app) | Free |
| **Market Data** | Free (real-time) | Free (with account) |
| **Account Minimum** | $0 | $0 |
| **Margin Rates** | 13.25% - 14.00% | 12.00% (base) |

**Winner:** Essentially identical for your use case

---

## 📈 Alpaca Advantages

### 1. **Permanent API Keys** 🔑
```python
# Schwab (pain)
- Must re-authenticate every 7 days
- OAuth flow required
- Complex token management

# Alpaca (easy)
API_KEY = "your_key_here"
API_SECRET = "your_secret_here"
# Keys never expire!
```

### 2. **Simpler Authentication**
```python
# Schwab
1. Redirect to Schwab login
2. User approves
3. Get authorization code
4. Exchange for tokens
5. Refresh token every 30 min
6. Re-auth every 7 days

# Alpaca
1. Copy API key from dashboard
2. Done
```

### 3. **Better API Design**
```python
# Alpaca has official Python SDK
from alpaca.trading.client import TradingClient

client = TradingClient(API_KEY, SECRET_KEY)
account = client.get_account()
positions = client.get_all_positions()
```

### 4. **Built for Algo Trading**
- Alpaca was **designed** for algorithmic trading
- Schwab API was added to existing retail brokerage
- Better documentation, more examples
- Active developer community

### 5. **Fractional Shares**
```python
# Alpaca: Buy $100 of AAPL
client.submit_order(
    symbol="AAPL",
    notional=100,  # Dollar amount
    side="buy"
)

# Schwab: Must buy whole shares only
```

### 6. **Crypto Trading**
- Trade crypto through same API
- BTC, ETH, and other cryptos
- Schwab doesn't offer crypto

---

## 🚨 Alpaca Disadvantages

### 1. **Smaller Broker**
- Founded 2015 (vs Schwab's 1971)
- Less regulatory track record
- Acquisition risk

### 2. **Must Move Your Money**
- Can't use existing Schwab account
- Transfer funds to Alpaca
- Maintain separate account

### 3. **Less Institutional Tools**
- No tax-loss harvesting tools (like Schwab)
- Simpler mobile app
- Fewer research tools

### 4. **No Phone Support for API Issues**
- Email/chat support only
- Community forum
- Schwab has dedicated API support line

---

## 🎯 Recommendation Matrix

### ✅ Migrate to Alpaca NOW (Our Decision)
- ✅ No real Schwab account usage ($300 holding only)
- ✅ Opened Schwab specifically for API access
- ✅ No trading history to preserve
- ✅ Weekly re-auth is permanent limitation
- ✅ Better foundation for autonomous agent
- ✅ Simpler codebase from day 1

### ~~Stick with Schwab~~ (Original recommendation before knowing account status)
- ❌ Assumed existing active Schwab account
- ❌ Assumed trading history to preserve
- ❌ Didn't know account was API-only

### ~~Support BOTH~~ (Deferred to Phase 6+)
- ⏸️ Not needed for MVP
- ⏸️ Can add multi-broker support later
- ⏸️ Current goal: ship autonomous agent fast

---

## 🚀 My Recommendation

### ✅ **DECISION: MIGRATE TO ALPACA NOW**

**Why this changed from original recommendation:**
1. **Original assumption:** "You already have money in Schwab"
   - **Reality:** Only $300 holding, never traded
2. **Original assumption:** "You want to use your existing account"
   - **Reality:** Account opened solely for API access
3. **Original concern:** "Weekly re-auth is annoying but manageable"
   - **Reality:** It's a permanent limitation we can avoid

**New recommendation:**
- ✅ Migrate to Alpaca immediately (4-6 hours)
- ✅ Build autonomous agent on solid foundation
- ✅ Never deal with 7-day re-auth in production
- ⏸️ Consider multi-broker support in Phase 6+ (nice-to-have)

**Next Steps:**
1. See `/docs/implementation/alpaca-migration-plan.md`
2. Create `feature/alpaca-migration` branch
3. Execute migration (4-6 hours)
4. Archive Schwab documentation
5. Continue Phase 4 development on Alpaca

---

### ~~Phase 4-5: Stick with Schwab~~ (Original - OUTDATED)

**Why:** [Original reasoning assumed active Schwab trading account]

### ~~Phase 6+: Add Alpaca Support~~ (Original - OUTDATED)

**Why:** [Original reasoning assumed Schwab was working well]

---

## 📝 Sample Migration Code

### Alpaca Authentication (vs Schwab)

**Schwab (Current):**
```python
# Complex OAuth setup
client = schwabdev.Client(
    app_key=APP_KEY,
    app_secret=APP_SECRET,
    callback_url=CALLBACK_URL,
    tokens_file="tokens.json",
    capture_callback=True
)
```

**Alpaca (Simpler):**
```python
# Simple API key setup
from alpaca.trading.client import TradingClient

client = TradingClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    paper=True  # or False for live
)
```

### Getting Account Info

**Schwab:**
```python
response = schwab_client.account_linked()
accounts = response.json()
```

**Alpaca:**
```python
account = alpaca_client.get_account()
# Simpler, cleaner response
```

### Placing Orders

**Schwab:**
```python
# More complex order structure
order = schwab_client.place_order(
    accountHash=account_hash,
    order={
        "orderType": "MARKET",
        "session": "NORMAL",
        "duration": "DAY",
        "orderStrategyType": "SINGLE",
        "orderLegCollection": [{
            "instruction": "BUY",
            "quantity": 10,
            "instrument": {
                "symbol": "AAPL",
                "assetType": "EQUITY"
            }
        }]
    }
)
```

**Alpaca (Simpler):**
```python
# Clean, Pythonic API
order = alpaca_client.submit_order(
    symbol="AAPL",
    qty=10,
    side="buy",
    type="market",
    time_in_force="day"
)
```

---

## ⏱️ Detailed Migration Timeline

### Week 1: Core Integration (40 hours)
- **Day 1-2:** Setup Alpaca account, test API, read docs (8h)
- **Day 3:** Build AlpacaBroker service class (8h)
- **Day 4:** Implement authentication, account info, positions (8h)
- **Day 5:** Implement order placement, market data (8h)
- **Weekend:** Testing and bug fixes (8h)

### Week 2: Integration & Testing (20 hours)
- **Day 6-7:** Frontend integration, update API calls (8h)
- **Day 8:** Paper trading testing (4h)
- **Day 9:** Live trading testing (small amounts) (4h)
- **Day 10:** Documentation and cleanup (4h)

**Total:** ~60 hours (~1.5 weeks full-time, or 3 weeks part-time)

---

## 🎬 Decision Time

### Questions to Ask Yourself:

1. **Is weekly re-auth a dealbreaker for you?**
   - If yes → Consider Alpaca
   - If no → Stick with Schwab

2. **Do you want to move money to a new broker?**
   - If yes → Alpaca is option
   - If no → Must use Schwab

3. **How important is fractional shares?**
   - Critical → Alpaca
   - Nice-to-have → Either works

4. **Timeline pressure?**
   - Need autonomous agent ASAP → Stick with Schwab (don't derail)
   - Have time for migration → Consider Alpaca

5. **Future vision?**
   - Single broker platform → Pick one
   - Multi-broker support → Plan for both

---

## 📌 Final Verdict

**For FInsightAI specifically:**

### ✅ **MIGRATE TO ALPACA NOW** (APPROVED)
- No real Schwab usage ($300 holding, no trades)
- Account opened only for API access
- 4-6 hours to migrate (AI-assisted)
- Better foundation for autonomous agent
- Permanent API keys = production-ready
- Focus energy on features, not weekly re-auth

### ⏭️ **Multi-Broker Support Later** (Phase 6+)
- Not needed for MVP
- Can add back Schwab support if users request
- Build abstraction layer when needed
- Current goal: ship autonomous agent

### ✅ **Decision Finalized**
- Migration approved: December 25, 2025
- Branch: `feature/alpaca-migration`
- Timeline: 4-6 hours
- See: `/docs/implementation/alpaca-migration-plan.md`

---

**Bottom Line:** Original recommendation was based on assumption of active Schwab trading account. Since we only have API-testing account with $300, **migrating to Alpaca is obvious choice**. Better API, permanent keys, simpler code.

---

**Document Owner:** Architecture Team  
**Status:** ✅ Decision Finalized  
**Next Action:** Execute migration plan  
**See:** `/docs/implementation/alpaca-migration-plan.md`
