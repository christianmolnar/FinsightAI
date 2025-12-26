# Schwab Portfolio Integration Architecture

**Document Version:** 1.0  
**Created:** December 25, 2025  
**Status:** Active - Phase 3 Complete  
**Owner:** FInsightAI Backend Team

---

## 📋 Table of Contents

1. [Component Overview](#component-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Data Flow](#data-flow)
4. [API Mapping](#api-mapping)
5. [Data Models](#data-models)
6. [Authentication & Security](#authentication--security)
7. [Error Handling](#error-handling)
8. [Performance & Caching](#performance--caching)
9. [Rate Limiting](#rate-limiting)
10. [Testing Strategy](#testing-strategy)
11. [Future Enhancements](#future-enhancements)

---

## Component Overview

### Purpose
The Schwab Portfolio Integration provides real-time access to user's Charles Schwab brokerage accounts, enabling:
- Live portfolio viewing (positions, balances, P&L)
- Real-time market data for holdings
- Account information and trading restrictions
- Multi-account aggregation and consolidation

### Responsibilities
1. **Authentication Management** - OAuth token lifecycle, refresh logic
2. **Account Data Retrieval** - Fetch accounts, positions, balances from Schwab API
3. **Data Transformation** - Map Schwab API responses to our internal schemas
4. **Error Handling** - Graceful degradation when Schwab API unavailable
5. **Performance Optimization** - Minimize API calls, implement intelligent caching

### Non-Responsibilities
- Trade execution (Phase 5+)
- Historical data analysis (separate service)
- Tax calculation (handled by sell validation service)
- Paper trading (separate portfolio service)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  ┌────────────────────┐  ┌────────────────────┐                 │
│  │  RealPortfolio.js  │  │   Dashboard.js     │                 │
│  │  (Schwab Portfolio)│  │   (Overview)       │                 │
│  └─────────┬──────────┘  └──────────┬─────────┘                 │
│            │                         │                          │
│            │   API Requests          │                          │
│            │   (axios/fetch)         │                          │
└────────────┼─────────────────────────┼──────────────────────────┘
             │                         │
             │                         │
             ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         API Router: /api/v1/schwab/*                     │   │
│  │  (/backend/app/api/portfolio.py lines 218-550)           │   │
│  │                                                          │   │
│  │  GET /schwab/accounts                                    │   │
│  │  GET /schwab/accounts/{hash}/positions                   │   │
│  │  GET /schwab/accounts/{hash}/summary                     │   │
│  │  GET /schwab/portfolio/overview                          │   │
│  │  GET /schwab/positions/all                               │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                         │
│                       ▼                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Schwab Service (schwab_service)                  │   │
│  │  (/backend/app/schwab_api.py)                            │   │
│  │                                                          │   │
│  │  - initialize_client()                                   │   │
│  │  - get_account_info()                                    │   │
│  │  - Token management (access + refresh)                   │   │
│  │  - Error handling & retries                              │   │
│  └────────────────────┬─────────────────────────────────────┘   │
│                       │                                         │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        │ HTTPS/OAuth
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              Charles Schwab API (External)                      │
│  https://api.schwabapi.com/trader/v1/                           │
│                                                                 │
│  - GET /accounts                                                │
│  - GET /accounts/{accountHash}                                  │
│  - OAuth 2.0 Authentication                                     │
│  - Rate Limit: 120 req/min per app                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Initial Account Load Flow

```
User Opens Schwab Tab
        ↓
Frontend: RealPortfolio.js componentDidMount()
        ↓
API Request: GET /api/v1/schwab/portfolio/overview
        ↓
Backend: get_schwab_portfolio_overview()
        ↓
┌──────────────────────────────────────────┐
│ Sequential API Calls:                    │
│ 1. get_schwab_accounts()                 │
│    └→ schwab_service.get_account_info()  │
│                                          │
│ 2. For each account:                     │
│    ├→ get_schwab_account_positions()     │
│    │  └→ schwab_client.account_details() │
│    └→ get_schwab_account_summary()       │
│       └→ schwab_client.account_details() │ 
└──────────────────────────────────────────┘
        ↓
Data Transformation & Aggregation
        ↓
JSON Response to Frontend
        ↓
React State Update & Render
```

**Performance Notes:**
- For N accounts, makes 1 + (2×N) Schwab API calls
- Average response time: 800ms - 1.5s (depends on Schwab API)
- No caching currently implemented (all real-time)

### 2. Token Refresh Flow

```
API Call with Expired Access Token
        ↓
Schwab API Returns 401 Unauthorized
        ↓
schwab_service detects expired token
        ↓
Automatic Token Refresh
├─ Check refresh_token expiry
├─ Call Schwab OAuth endpoint
├─ Update tokens.json file
└─ Retry original request
        ↓
Success or Error Response
```

**Token Lifecycle:**
- Access Token: 30 minutes validity
- Refresh Token: **7 days validity (Schwab's official policy)**
- Auto-refresh implemented: ✅ (via schwabdev library)
- **Production Reality:** ⚠️ Manual re-auth required every 7 days
  - **This is Schwab's actual OAuth policy, not worst-case**
  - **Current Impact:** User must manually re-authenticate weekly
  - **Mitigations Being Researched (Phase 6):**
    1. Persistent refresh token rotation (if Schwab allows)
    2. Service account authentication (if available for individual developer apps)
    3. Automated re-auth notification system (alert user 24h before expiry)
    4. Multi-device auth fallback (re-auth from phone when needed)

---

## API Mapping

### Endpoint: GET /api/v1/schwab/accounts

**Purpose:** Fetch all linked Schwab accounts for the authenticated user

**Request:**
```http
GET /api/v1/schwab/accounts HTTP/1.1
Host: localhost:8000
```

**Schwab API Called:**
```python
schwab_service.get_account_info()
# Internally calls Schwab API: GET /trader/v1/accounts
```

**Response Schema:**
```json
{
  "success": true,
  "accounts": [
    {
      "accountNumber": "****1234",
      "hashValue": "A1B2C3D4E5F6...",
      "type": "MARGIN",
      "status": "ACTIVE"
    }
  ],
  "account_count": 1
}
```

**Error Responses:**
- `503 Service Unavailable` - Schwab API not configured (missing APP_KEY/APP_SECRET)
- `401 Unauthorized` - Authentication failed, re-auth required
- `500 Internal Server Error` - Unexpected error

---

### Endpoint: GET /api/v1/schwab/accounts/{account_hash}/positions

**Purpose:** Get all positions (stocks, options, etc.) for a specific account

**Request:**
```http
GET /api/v1/schwab/accounts/A1B2C3D4E5F6.../positions HTTP/1.1
```

**Schwab API Called:**
```python
schwab_client.account_details(
    accountHash=account_hash,
    fields="positions"
)
# Schwab API: GET /trader/v1/accounts/{accountHash}?fields=positions
```

**Response Schema:**
```json
{
  "success": true,
  "account_hash": "A1B2C3D4E5F6...",
  "positions": [
    {
      "symbol": "AAPL",
      "cusip": "037833100",
      "description": "Apple Inc",
      "assetType": "EQUITY",
      "quantity": 100,
      "marketValue": 18500.00,
      "averagePrice": 175.00,
      "currentPrice": 185.00,
      "dayPL": 500.00,
      "totalPL": 1000.00,
      "dayPLPercent": 2.78,
      "totalPLPercent": 5.71
    }
  ],
  "position_count": 1,
  "total_market_value": 18500.00
}
```

**Data Transformations Applied:**
1. **Net Quantity Calculation:** `longQuantity - shortQuantity`
2. **Current Price Derived:** `marketValue / netQuantity` (when available)
3. **Total P&L Calculation:** `marketValue - (averagePrice × netQuantity)`
4. **Percentage Calculations:** `(P&L / cost_basis) × 100`
5. **Zero-Quantity Filtering:** Positions with net quantity = 0 are excluded

---

### Endpoint: GET /api/v1/schwab/accounts/{account_hash}/summary

**Purpose:** Get account balances, buying power, day trading status

**Request:**
```http
GET /api/v1/schwab/accounts/A1B2C3D4E5F6.../summary HTTP/1.1
```

**Schwab API Called:**
```python
schwab_client.account_details(
    accountHash=account_hash,
    fields="positions"  # Returns full account details including balances
)
```

**Response Schema:**
```json
{
  "success": true,
  "summary": {
    "accountId": "123456789",
    "accountHash": "A1B2C3D4E5F6...",
    "type": "MARGIN",
    "roundTrips": 2,
    "isDayTrader": false,
    "isClosingOnlyRestricted": false,
    "currentBalances": {
      "cashBalance": 25000.00,
      "liquidationValue": 125000.00,
      "equity": 125000.00,
      "buyingPower": 200000.00,
      "moneyMarketFund": 0.00
    },
    "projectedBalances": {
      "cashBalance": 25000.00,
      "buyingPower": 200000.00
    },
    "positionCount": 8,
    "totalMarketValue": 100000.00,
    "totalDayPL": 1250.00
  }
}
```

**Key Fields:**
- `isDayTrader`: Pattern day trader flag (4+ day trades in 5 days with <$25k)
- `isClosingOnlyRestricted`: Account restricted to closing positions only
- `roundTrips`: Day trade count in current 5-day period
- `buyingPower`: Available buying power (includes margin)

---

### Endpoint: GET /api/v1/schwab/portfolio/overview

**Purpose:** Aggregate view of ALL accounts with positions and totals

**Request:**
```http
GET /api/v1/schwab/portfolio/overview HTTP/1.1
```

**Internal Flow:**
1. Call `get_schwab_accounts()` - Get all accounts
2. For each account:
   - Call `get_schwab_account_positions()` - Get positions
   - Call `get_schwab_account_summary()` - Get balances
3. Aggregate data across accounts
4. Calculate portfolio-wide totals

**Response Schema:**
```json
{
  "success": true,
  "total_accounts": 2,
  "total_market_value": 225000.00,
  "total_day_pl": 2750.00,
  "day_pl_percent": 1.23,
  "accounts": [
    {
      "accountNumber": "****1234",
      "accountHash": "A1B2C3D4E5F6...",
      "type": "MARGIN",
      "marketValue": 125000.00,
      "dayPL": 1500.00,
      "positionCount": 8,
      "cashBalance": 25000.00,
      "buyingPower": 200000.00,
      "isDayTrader": false,
      "positions": [ /* Position objects */ ]
    },
    {
      "accountNumber": "****5678",
      "accountHash": "Z9Y8X7W6V5U4...",
      "type": "CASH",
      "marketValue": 100000.00,
      "dayPL": 1250.00,
      "positionCount": 5,
      "cashBalance": 50000.00,
      "buyingPower": 50000.00,
      "isDayTrader": false,
      "positions": [ /* Position objects */ ]
    }
  ]
}
```

**Performance Characteristics:**
- API Calls: 1 + (2 × account_count)
- Response Time: 800ms - 2.5s (for 1-3 accounts)
- Error Handling: Individual account failures logged as warnings, continue with remaining accounts

---

### Endpoint: GET /api/v1/schwab/positions/all

**Purpose:** Consolidated view of positions across all accounts, grouped by symbol

**Request:**
```http
GET /api/v1/schwab/positions/all HTTP/1.1
```

**Internal Flow:**
1. Call `get_schwab_portfolio_overview()` - Get all accounts with positions
2. Flatten positions from all accounts
3. Group positions by symbol
4. Calculate aggregated totals per symbol
5. Compute weighted average prices

**Response Schema:**
```json
{
  "success": true,
  "all_positions": [
    {
      "symbol": "AAPL",
      "description": "Apple Inc",
      "assetType": "EQUITY",
      "quantity": 50,
      "marketValue": 9250.00,
      "averagePrice": 175.00,
      "currentPrice": 185.00,
      "dayPL": 250.00,
      "totalPL": 500.00,
      "accountHash": "A1B2C3D4E5F6...",
      "accountNumber": "****1234",
      "accountType": "MARGIN"
    },
    {
      "symbol": "AAPL",
      "description": "Apple Inc",
      "assetType": "EQUITY",
      "quantity": 50,
      "marketValue": 9250.00,
      "averagePrice": 180.00,
      "currentPrice": 185.00,
      "dayPL": 250.00,
      "totalPL": 250.00,
      "accountHash": "Z9Y8X7W6V5U4...",
      "accountNumber": "****5678",
      "accountType": "CASH"
    }
  ],
  "consolidated_positions": [
    {
      "symbol": "AAPL",
      "description": "Apple Inc",
      "assetType": "EQUITY",
      "totalQuantity": 100,
      "totalMarketValue": 18500.00,
      "totalDayPL": 500.00,
      "totalPL": 750.00,
      "averagePrice": 185.00,
      "dayPLPercent": 2.78,
      "totalPLPercent": 4.23,
      "accounts": [
        {"accountNumber": "****1234", "quantity": 50, "marketValue": 9250.00},
        {"accountNumber": "****5678", "quantity": 50, "marketValue": 9250.00}
      ]
    }
  ],
  "total_positions": 2,
  "unique_symbols": 1
}
```

**Use Cases:**
- Portfolio-wide position analysis
- Multi-account position tracking
- Risk aggregation across accounts
- Symbol-level performance reporting

---

## Data Models

### Internal Data Models (SQLAlchemy)

**Note:** Schwab data is NOT persisted to our database. All data is fetched real-time from Schwab API.

### Paper Portfolio Models (For Comparison)

```python
# /backend/app/models/portfolio.py
class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    portfolio_type = Column(Enum(PortfolioType), nullable=False)
    # "PAPER" or "LIVE"
    
    total_value = Column(Numeric(15, 2), default=0.0)
    current_cash = Column(Numeric(15, 2), nullable=False)
    invested_value = Column(Numeric(15, 2), default=0.0)

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"))
    symbol = Column(String(10), nullable=False)
    shares = Column(Numeric(12, 4), nullable=False)
    avg_cost = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    market_value = Column(Numeric(15, 2), nullable=False)
    unrealized_pnl = Column(Numeric(15, 2), nullable=False)
```

### Schwab API Response Models

**Account Object (from Schwab):**
```typescript
interface SchwabAccount {
  accountNumber: string;      // Masked: "****1234"
  hashValue: string;          // Unique account identifier
  type: "CASH" | "MARGIN" | "IRA" | "401K";
  status: "ACTIVE" | "CLOSED" | "RESTRICTED";
}
```

**Position Object (from Schwab):**
```typescript
interface SchwabPosition {
  instrument: {
    symbol: string;
    cusip: string;
    description: string;
    assetType: "EQUITY" | "OPTION" | "MUTUAL_FUND" | "FIXED_INCOME";
  };
  longQuantity: number;
  shortQuantity: number;
  averagePrice: number;
  currentDayProfitLoss: number;
  marketValue: number;
}
```

**Account Balances (from Schwab):**
```typescript
interface SchwabBalances {
  cashBalance: number;
  liquidationValue: number;
  equity: number;
  buyingPower: number;
  moneyMarketFund: number;
}
```

---

## Authentication & Security

### OAuth 2.0 Flow

```
┌─────────────┐                                    ┌─────────────┐
│   Backend   │                                    │   Schwab    │
│  (FastAPI)  │                                    │ OAuth Server│
└──────┬──────┘                                    └──────┬──────┘
       │                                                  │
       │ 1. Redirect user to Schwab login                 │
       ├─────────────────────────────────────────────-───>│
       │    https://api.schwabapi.com/oauth/authorize     │ 
       │    ?client_id=APP_KEY                            │
       │    &redirect_uri=https://localhost:8000/callback │
       │                                                  │
       │ 2. User authenticates & approves                 │
       │                                                  │
       │ 3. Redirect with authorization code              │
       │<─────────────────────────────────────────────────┤
       │    ?code=AUTHORIZATION_CODE                      │
       │                                                  │
       │ 4. Exchange code for tokens                      │
       ├─────────────────────────────────────────────-───>│
       │    POST /oauth/token                             │
       │    {code, client_id, client_secret}              │
       │                                                  │
       │ 5. Return access + refresh tokens                │
       │<─────────────────────────────────────────────────┤
       │    {access_token, refresh_token,                 │
       │     expires_in: 1800}                            │
       │                                                  │
       │ 6. Store tokens securely                         │
       │    (tokens.json - NOT in git)                    │
       │                                                  │
```

### Token Storage

**File:** `/backend/tokens.json` (git-ignored)

```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "def502...",
  "token_type": "Bearer",
  "expires_in": 1800,
  "expires_at": 1735123456.789,
  "refresh_expires_at": 1735728256.789
}
```

**Security Measures:**
1. ✅ Tokens stored in `.gitignore`d file
2. ✅ File permissions restricted (600) - owner read/write only
3. ✅ No tokens in environment variables
4. ✅ No tokens logged or printed
5. ⚠️  Future: Encrypt tokens at rest (Phase 6+)
6. ⚠️  Future: Move to secure credential store (AWS Secrets Manager, etc.)

### Token Refresh Logic

**Location:** `/backend/app/schwab_api.py` - `SchwabService` class

```python
def _refresh_token_if_needed(self):
    """Auto-refresh access token if expired or expiring soon"""
    if not self.tokens:
        return False
    
    # Refresh if token expires in < 5 minutes
    expires_at = self.tokens.get("expires_at", 0)
    if time.time() >= expires_at - 300:
        return self._refresh_access_token()
    
    return True

def _refresh_access_token(self):
    """Use refresh token to get new access token"""
    try:
        new_tokens = self.client.refresh_access_token(
            self.tokens["refresh_token"]
        )
        self._save_tokens(new_tokens)
        return True
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return False
```

**Refresh Strategy:**
- Automatic refresh when access token expires in < 5 minutes
- Retry original request after successful refresh
- **Refresh token expires after 7 days (cannot be extended)**
- Manual re-authentication required when refresh token expires

### Known Production Limitations

**⚠️ Weekly Re-Authentication Requirement**

**The Issue:**
- Schwab's OAuth refresh tokens expire after exactly 7 days
- There is **no way** to extend refresh token lifetime via API
- Once expired, user **must** manually re-authenticate through OAuth flow

**Why This Matters:**
- Autonomous agent cannot operate for >7 days without human intervention
- Production deployment requires weekly user action
- Not suitable for "set-and-forget" autonomous trading

**Possible Workarounds (Under Investigation):**

1. **Pro-active Re-Auth Notification** (Easiest)
   - Monitor refresh token expiry
   - Send email/push notification 24h before expiry
   - Provide one-click re-auth link
   - Status: Can implement in Phase 6

2. **Schwab Business/Institutional Account** (Uncertain)
   - Research if Schwab offers longer-lived tokens for business accounts
   - May require upgrading from individual developer account
   - Status: Needs research

3. **Alternative Broker APIs** (Nuclear Option)
   - Interactive Brokers: 24-hour tokens (worse)
   - TD Ameritrade: Was acquired by Schwab, API being phased out
   - Alpaca: Permanent API keys (but limited to Alpaca brokerage)
   - Status: Would require complete rewrite

**Current Recommendation:**
- Accept 7-day limitation for MVP
- Implement proactive notification system
- Monitor if Schwab policy changes
- Consider this when setting user expectations

**User Communication:**
- Be transparent: "You'll need to re-authenticate weekly"
- Make re-auth process **seamless** (one-click from email)
- Consider it a security feature (limited token lifetime)

---

## Error Handling

### Error Classification

| Error Type | HTTP Code | Handling Strategy | User Message |
|------------|-----------|-------------------|--------------|
| **API Not Configured** | 503 | Return error immediately | "Schwab API not configured. Please set APP_KEY and APP_SECRET." |
| **Client Init Failed** | 503 | Log error, return 503 | "Failed to initialize Schwab client. Check credentials." |
| **Authentication Failed** | 401 | Log warning, return 401 | "Authentication failed. Please re-authenticate with Schwab." |
| **Token Expired** | 401 | Auto-refresh → Retry | (Transparent to user if refresh succeeds) |
| **Rate Limited** | 429 | Log warning, return 429 | "Schwab API rate limit exceeded. Please try again in 60 seconds." |
| **Account Not Found** | 404 | Log warning, return 404 | "Account not found. It may have been closed." |
| **Schwab API Error** | 500+ | Log full error, return 500 | "Schwab API error. Please try again later." |
| **Network Timeout** | 504 | Log error, return 504 | "Request to Schwab timed out. Please try again." |
| **Unexpected Error** | 500 | Log full traceback, return 500 | "Internal server error. Contact support if persists." |

### Error Response Format

```json
{
  "detail": "Human-readable error message",
  "error_code": "SCHWAB_AUTH_FAILED",
  "timestamp": "2025-12-25T10:30:00Z",
  "request_id": "abc123def456"
}
```

### Retry Logic

**Current Implementation:**
- **No automatic retries** for Schwab API calls
- Token refresh triggers manual retry of original request
- Network timeouts fail immediately

**Future Enhancement (Phase 6):**
```python
# Exponential backoff for transient errors
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # seconds

for attempt in range(MAX_RETRIES):
    try:
        response = schwab_client.account_details(...)
        if response.ok:
            return response.json()
    except NetworkError:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAYS[attempt])
            continue
        raise
```

### Graceful Degradation

**Scenario:** Individual account fails, others succeed

```python
# Current implementation in get_schwab_portfolio_overview()
for account in accounts:
    try:
        # Fetch account positions and summary
        positions_response = await get_schwab_account_positions(account_hash)
        # ... process account data
        portfolio_overview.append(account_overview)
    except Exception as e:
        logger.warning(f"Could not fetch details for account {account_hash}: {e}")
        continue  # Skip failed account, continue with others

# Return partial results
return {
    "success": True,
    "total_accounts": len(portfolio_overview),  # Only successful accounts
    "accounts": portfolio_overview
}
```

**Benefit:** User sees data for working accounts even if one account fails

---

## Performance & Caching

### Current State: No Caching

**All requests fetch real-time data from Schwab API**

**Pros:**
- ✅ Always up-to-date
- ✅ No stale data issues
- ✅ Simple implementation

**Cons:**
- ❌ Slower response times (800ms - 2.5s)
- ❌ More API calls → Higher rate limit risk
- ❌ Higher latency on page load

### Performance Metrics (Current)

| Endpoint | Schwab API Calls | Avg Response Time | Use Case |
|----------|------------------|-------------------|----------|
| `/schwab/accounts` | 1 | 300-500ms | Initial load |
| `/schwab/accounts/{hash}/positions` | 1 | 400-700ms | Per account |
| `/schwab/accounts/{hash}/summary` | 1 | 400-700ms | Per account |
| `/schwab/portfolio/overview` | 1 + (2×N) | 800ms - 2.5s | Full portfolio (N accounts) |
| `/schwab/positions/all` | 1 + (2×N) | 800ms - 2.5s | Consolidated view |

**Example:** User with 2 accounts loading overview page:
- API Calls: 1 + (2×2) = 5 Schwab API requests
- Total Time: ~1.5 seconds

### Proposed Caching Strategy (Phase 5+)

#### Level 1: In-Memory Cache (Redis)

```python
# Cache positions for 30 seconds
CACHE_TTL_POSITIONS = 30

@cache(ttl=CACHE_TTL_POSITIONS, key="schwab:positions:{account_hash}")
async def get_schwab_account_positions(account_hash: str):
    # ... existing implementation
```

**Cache Keys:**
- `schwab:accounts:{user_id}` - TTL: 5 minutes
- `schwab:positions:{account_hash}` - TTL: 30 seconds
- `schwab:summary:{account_hash}` - TTL: 60 seconds
- `schwab:quotes:{symbol}` - TTL: 15 seconds

#### Level 2: Conditional Requests (ETags)

```python
# Use Schwab API ETags if supported
headers = {
    "If-None-Match": cached_etag
}
response = schwab_client.account_details(..., headers=headers)

if response.status_code == 304:
    # Not modified, use cached data
    return cached_data
```

#### Level 3: Background Refresh

```python
# Pre-fetch data in background before cache expires
@background_task
async def refresh_portfolio_cache(user_id: str):
    accounts = await get_schwab_accounts()
    for account in accounts:
        # Warm cache before expiry
        await get_schwab_account_positions(account["hashValue"])
```

**Expected Improvements:**
- 80% reduction in API calls (cache hits)
- 70% faster response times (cached)
- Lower rate limit consumption

---

## Rate Limiting

### Schwab API Limits

**Official Limits (per application):**
- **120 requests per minute** per APP_KEY
- **2 requests per second** burst limit
- Limits apply across all users of the application

**Rate Limit Headers (from Schwab):**
```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 115
X-RateLimit-Reset: 1735123500
```

### Current Rate Limit Handling

**Status:** ⚠️ No rate limiting implemented

**Risks:**
- Multiple concurrent users could exceed limits
- No backoff on 429 responses
- No queue for pending requests

### Proposed Rate Limiting Strategy (Phase 5+)

#### Client-Side Rate Limiter

```python
# /backend/app/services/rate_limiter.py
from ratelimit import RateLimiter

# 100 req/min (20% buffer below Schwab's 120/min)
schwab_limiter = RateLimiter(max_calls=100, period=60)

@schwab_limiter
async def call_schwab_api(endpoint, **kwargs):
    """Rate-limited wrapper for all Schwab API calls"""
    return await schwab_client.request(endpoint, **kwargs)
```

#### Request Queue

```python
# Queue requests when rate limit approached
if schwab_limiter.remaining < 10:
    logger.warning("Approaching rate limit, queueing request")
    await request_queue.enqueue(request)
    return {"success": False, "queued": True}
```

#### Exponential Backoff on 429

```python
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    logger.warning(f"Rate limited, retrying after {retry_after}s")
    await asyncio.sleep(retry_after)
    return await call_schwab_api_with_retry(endpoint, **kwargs)
```

---

## Testing Strategy

### Current Testing Status

**Manual Testing:** ✅ Complete
- All endpoints tested with `curl`
- Frontend integration tested with real Schwab accounts
- Token refresh tested (expired access token scenario)

**Automated Testing:** ❌ Not implemented

### Proposed Testing Approach

#### Unit Tests

```python
# /backend/tests/test_portfolio_api.py
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_get_schwab_accounts_success():
    """Test successful account retrieval"""
    mock_service = Mock()
    mock_service.get_account_info.return_value = [
        {"accountNumber": "****1234", "hashValue": "ABC123"}
    ]
    
    with patch("app.api.portfolio.schwab_service", mock_service):
        response = await get_schwab_accounts()
        
    assert response["success"] is True
    assert response["account_count"] == 1

@pytest.mark.asyncio
async def test_get_schwab_accounts_not_configured():
    """Test error when Schwab API not configured"""
    mock_service = Mock()
    mock_service.is_configured.return_value = False
    
    with patch("app.api.portfolio.schwab_service", mock_service):
        with pytest.raises(HTTPException) as exc:
            await get_schwab_accounts()
    
    assert exc.value.status_code == 503
```

#### Integration Tests

```python
# /backend/tests/integration/test_schwab_integration.py
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_portfolio_flow():
    """Test complete portfolio retrieval flow"""
    # Use test credentials with Schwab sandbox
    client = SchwabService(test_mode=True)
    
    # Test authentication
    assert client.is_configured()
    assert client.initialize_client()
    
    # Test account retrieval
    accounts = client.get_account_info()
    assert len(accounts) > 0
    
    # Test position retrieval
    account_hash = accounts[0]["hashValue"]
    response = await get_schwab_account_positions(account_hash)
    assert response["success"] is True
```

#### Mock Data Strategy

**Create fixture files:**
```python
# /backend/tests/fixtures/schwab_responses.py
MOCK_ACCOUNT_RESPONSE = {
    "accountNumber": "****9999",
    "hashValue": "TEST123456",
    "type": "MARGIN",
    "status": "ACTIVE"
}

MOCK_POSITIONS_RESPONSE = {
    "securitiesAccount": {
        "positions": [
            {
                "instrument": {
                    "symbol": "AAPL",
                    "cusip": "037833100",
                    "description": "Apple Inc",
                    "assetType": "EQUITY"
                },
                "longQuantity": 100,
                "shortQuantity": 0,
                "averagePrice": 175.00,
                "marketValue": 18500.00,
                "currentDayProfitLoss": 500.00
            }
        ]
    }
}
```

#### Schwab Sandbox Environment

**Schwab provides a sandbox API for testing:**
- Base URL: `https://api.schwabapi.com/sandbox/`
- Test credentials separate from production
- Mock data for testing without real accounts

**Configuration:**
```python
# /backend/app/config.py
SCHWAB_API_BASE = os.getenv(
    "SCHWAB_API_BASE",
    "https://api.schwabapi.com/trader/v1"  # Production
)

if os.getenv("TESTING"):
    SCHWAB_API_BASE = "https://api.schwabapi.com/sandbox/trader/v1"
```

---

## Future Enhancements

### Phase 4: Autonomous Trading Agent (CURRENT FOCUS)

**Vision:** AI-powered autonomous agent that runs 24/7 to manage portfolio

**Core Components Needed:**

1. **Portfolio Analysis Engine**
   - ❌ Continuous monitoring of held positions
   - ❌ AI analysis: Should we hold, sell, or adjust position size?
   - ❌ Risk assessment for each position
   - ❌ Performance tracking against benchmarks

2. **Opportunity Scanner Service**
   - ❌ Background process scanning for new opportunities
   - ❌ Technical analysis (RSI, MACD, Bollinger Bands, volume)
   - ❌ Fundamental screening (P/E, growth, margins)
   - ❌ AI signal generation with confidence scores
   - ❌ Multi-factor opportunity scoring system

3. **Decision & Execution Framework**
   - ❌ Autonomous bounds: What can agent do without approval?
     - Example: Rebalance within 5% of target allocations
     - Example: Close positions with stop-loss triggered
   - ❌ User approval required: What needs human decision?
     - Example: New position > 5% of portfolio
     - Example: Selling at loss > $X
   - ❌ Transaction queue auto-population
   - ❌ Automated execution within bounds

4. **Notification & Alerting System**
   - ❌ Real-time alerts for opportunities requiring approval
   - ❌ Daily portfolio summary emails
   - ❌ Performance reports (weekly/monthly)
   - ❌ Risk alerts (concentration, volatility spikes)

**What We Have Today (Phase 3):**
- ✅ Real-time Schwab portfolio data
- ✅ Market hours indicator (open/closed)
- ✅ Manual trade execution (paper + live routing)
- ✅ Transaction queue system
- ✅ AI research on-demand (GPT-4 + Claude)
- ✅ Sell validation with tax analysis

**What's Missing for Autonomous Operation:**
- ❌ Background agent process running 24/7
- ❌ Continuous opportunity scanning
- ❌ Automated decision logic
- ❌ Position monitoring & alerts
- ❌ Auto-execution within defined bounds

---

### Phase 5: Performance & Scalability

**Current State:**
- ❌ No Redis caching (all requests hit Schwab API)
- ❌ No request batching
- ❌ No WebSocket support
- ❌ No background pre-fetching
- ❌ No client-side rate limiting

**Performance Optimizations Needed:**
- Redis caching layer (30s TTL for positions, 60s for balances)
- Request batching and queuing
- WebSocket support for real-time updates
- Background data pre-fetching
- Client-side rate limiting (buffer below Schwab's 120 req/min)

**Why These Matter:**
- Current: 1.5s load time, 5 API calls for 2-account portfolio
- With caching: 200ms load time, 80% reduction in API calls
- With WebSocket: Real-time position updates without polling

---

### Phase 6: Advanced Trading Features

- **Trade Execution via Schwab API**
  - Place limit/market orders
  - Stop-loss and take-profit orders
  - Options trading
- **Order Management**
  - View open orders
  - Modify pending orders
  - Cancel orders
- **Multi-User Support**
  - User-specific token storage (encrypted)
  - Account linking per user
  - Role-based access control

---

### Phase 7: Security & Production Hardening

**Current Security Issues:**
- ⚠️ Tokens stored as plain JSON (backend/tokens.json)
- ⚠️ Manual re-auth required every 7 days (production blocker)
- ⚠️ No audit logging of API calls
- ⚠️ No multi-factor authentication

**Security Enhancements:**
- Encrypt tokens at rest (AES-256)
- Move to AWS Secrets Manager / Azure Key Vault
- Implement persistent token refresh strategy
- Add comprehensive audit logging
- Multi-factor auth for sensitive operations
- Automated re-authentication flow with user notification

---

### Phase 8: Monitoring & Observability

- Datadog/New Relic integration
- API latency metrics & dashboards
- Error rate tracking & alerting
- Rate limit consumption monitoring
- Authentication failure alerts
- Trading activity dashboards

---

## Appendix A: Schwab API Endpoints Used

| Endpoint | Purpose | Documentation |
|----------|---------|---------------|
| `GET /trader/v1/accounts` | List all accounts | [Schwab Docs](https://developer.schwab.com) |
| `GET /trader/v1/accounts/{accountHash}` | Account details | [Schwab Docs](https://developer.schwab.com) |
| `POST /oauth/token` | Token exchange/refresh | [OAuth Docs](https://developer.schwab.com/oauth) |

## Appendix B: Environment Variables

```bash
# Required for Schwab API
SCHWAB_APP_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
SCHWAB_REDIRECT_URI=https://localhost:8000/callback

# Optional
SCHWAB_API_BASE=https://api.schwabapi.com/trader/v1
SCHWAB_TOKEN_FILE=/backend/tokens.json
```

## Appendix C: Troubleshooting

### Common Issues

**Issue:** `401 Unauthorized` on API calls
- **Cause:** Access token expired
- **Solution:** Check token expiry, manually re-authenticate if refresh token expired

**Issue:** `503 Service Unavailable` on startup
- **Cause:** Missing `SCHWAB_APP_KEY` or `SCHWAB_APP_SECRET`
- **Solution:** Set environment variables in `.env` file

**Issue:** Slow response times (>3 seconds)
- **Cause:** Multiple sequential API calls
- **Solution:** Implement caching (Phase 5)

**Issue:** Empty positions array despite having positions
- **Cause:** Zero net quantity filter (long - short = 0)
- **Solution:** Check `longQuantity` and `shortQuantity` in Schwab response

---

## Document Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-12-25 | 1.0 | Initial architecture specification | AI Development Team |

---

**Next Steps:**
1. Review and approve this specification
2. Implement automated testing (Phase 4)
3. Add caching layer (Phase 5)
4. Enhance error handling and retry logic
5. Implement rate limiting (Phase 5)

**Questions or feedback?** Update this document and commit changes.
