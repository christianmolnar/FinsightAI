# Alpaca Trading Integration Architecture

**Date**: 2025-12-25  
**Status**: ✅ Active  
**Version**: 1.0

## Overview

f.insight.AI uses Alpaca Markets as its primary broker integration, providing both paper trading ($100k virtual) and live trading capabilities through a clean REST API.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       Frontend (React)                       │
│                     http://localhost:3000                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐          ┌──────────────────┐          │
│  │  Paper Portfolio │          │  Live Portfolio  │          │
│  │  (Tab)          │          │  (Tab)           │          │
│  └────────┬─────────┘          └────────┬─────────┘          │
│           │                              │                    │
│           ▼                              ▼                    │
│  GET /api/v1/alpaca/paper/    GET /api/v1/alpaca/live/      │
│      portfolio                     portfolio                  │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
            │   Backend (FastAPI)        │
            │   http://localhost:8000    │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Layer                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  📁 app/api/portfolio.py                                     │
│                                                               │
│  @router.get("/alpaca/paper/portfolio")                      │
│    └─► get_alpaca_service(paper=True)                       │
│                                                               │
│  @router.get("/alpaca/live/portfolio")                       │
│    └─► get_alpaca_service(paper=False)                      │
│                                                               │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
            │  📁 app/services/          │
            │     alpaca_service.py      │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   AlpacaService Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  class AlpacaService:                                        │
│    def __init__(self, paper: bool = True):                  │
│      if paper:                                               │
│        base_url = ALPACA_PAPER_BASE_URL                     │
│      else:                                                   │
│        base_url = ALPACA_LIVE_BASE_URL                      │
│                                                               │
│  # Singleton pattern (separate instances)                   │
│  _alpaca_paper_service = AlpacaService(paper=True)          │
│  _alpaca_live_service = AlpacaService(paper=False)          │
│                                                               │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
            │   Alpaca SDK (alpaca-py)   │
            ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Alpaca Markets API                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Paper Trading:  https://paper-api.alpaca.markets           │
│    ├─ Account: $100,000 virtual cash                        │
│    ├─ Real-time market data                                 │
│    └─ Risk-free testing                                     │
│                                                               │
│  Live Trading:   https://api.alpaca.markets                 │
│    ├─ Real money account                                    │
│    ├─ Real-time execution                                   │
│    └─ Requires funding & verification                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Components

#### PaperPortfolio.js
```javascript
// Location: frontend/src/components/PaperPortfolio.js
const fetchPortfolio = async () => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/alpaca/paper/portfolio`
  );
  const data = await response.json();
  
  // Transform Alpaca format to UI format
  const transformedData = {
    total_value: data.account?.portfolio_value || 0,
    cash_balance: data.account?.cash || 0,
    invested_value: data.metrics?.total_market_value || 0,
    unrealized_pnl: data.metrics?.total_unrealized_pl || 0,
    positions: data.positions || []
  };
};
```

#### RealPortfolio.js
```javascript
// Location: frontend/src/RealPortfolio.js
const fetchPortfolioData = async () => {
  const response = await fetch(
    `${baseUrl}/api/v1/alpaca/live/portfolio`,
    { signal: AbortSignal.timeout(5000) }
  );
  // Currently temporary - points to paper until live credentials ready
};
```

### 2. Backend API Layer

#### portfolio.py Routes
```python
# Location: backend/app/api/portfolio.py
from app.services.alpaca_service import get_alpaca_service

@router.get("/alpaca/paper/portfolio")
async def get_paper_portfolio():
    """Paper trading portfolio ($100k virtual)"""
    alpaca = get_alpaca_service(paper=True)
    return {
        "account": alpaca.get_account(),
        "positions": alpaca.get_positions(),
        "metrics": alpaca.get_portfolio_metrics()
    }

@router.get("/alpaca/live/portfolio")
async def get_live_portfolio():
    """Live trading portfolio (real money)"""
    alpaca = get_alpaca_service(paper=False)
    return {
        "account": alpaca.get_account(),
        "positions": alpaca.get_positions(),
        "metrics": alpaca.get_portfolio_metrics()
    }
```

**Additional Endpoints:**
- `GET /api/v1/alpaca/paper/account` - Paper account details
- `GET /api/v1/alpaca/paper/positions` - Paper positions
- `GET /api/v1/alpaca/live/account` - Live account details
- `GET /api/v1/alpaca/live/positions` - Live positions

### 3. Service Layer

#### alpaca_service.py
```python
# Location: backend/app/services/alpaca_service.py
from alpaca.trading.client import TradingClient

class AlpacaService:
    def __init__(self, paper: bool = True):
        """Initialize Alpaca client
        
        Args:
            paper: If True, use paper trading. If False, use live trading.
        """
        self.paper = paper
        
        # Use same API keys - base URL determines paper vs live
        self.client = TradingClient(
            api_key=os.getenv("ALPACA_API_KEY_ID"),
            secret_key=os.getenv("ALPACA_API_SECRET_KEY"),
            paper=paper  # This flag switches the endpoint
        )
    
    def get_account(self):
        """Get account information"""
        return self.client.get_account()
    
    def get_positions(self):
        """Get all open positions"""
        return self.client.get_all_positions()
    
    def get_portfolio_metrics(self):
        """Calculate portfolio metrics"""
        account = self.get_account()
        positions = self.get_positions()
        
        return {
            "total_market_value": sum(float(p.market_value) for p in positions),
            "total_unrealized_pl": sum(float(p.unrealized_pl) for p in positions),
            "total_unrealized_plpc": account.portfolio_value / account.equity * 100
        }

# Singleton instances
_alpaca_paper_service = None
_alpaca_live_service = None

def get_alpaca_service(paper: bool = True) -> AlpacaService:
    """Get or create Alpaca service instance"""
    global _alpaca_paper_service, _alpaca_live_service
    
    if paper:
        if _alpaca_paper_service is None:
            _alpaca_paper_service = AlpacaService(paper=True)
        return _alpaca_paper_service
    else:
        if _alpaca_live_service is None:
            _alpaca_live_service = AlpacaService(paper=False)
        return _alpaca_live_service
```

## Configuration

### Environment Variables

#### Backend (.env)
```bash
# Alpaca API Credentials (same keys for both paper and live)
ALPACA_API_KEY_ID=your_key_here
ALPACA_API_SECRET_KEY=your_secret_here

# Base URLs (handled automatically by alpaca-py SDK)
# paper=True  → https://paper-api.alpaca.markets
# paper=False → https://api.alpaca.markets
```

#### Frontend (.env)
```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000

# Standard ports (user-mandated)
# Frontend: 3000
# Backend: 8000
```

## Data Flow

### Paper Portfolio Request Flow

1. **User opens Paper Portfolio tab**
2. **Frontend** → `GET http://localhost:8000/api/v1/alpaca/paper/portfolio`
3. **Backend API** → Calls `get_alpaca_service(paper=True)`
4. **Service Layer** → Returns singleton `_alpaca_paper_service`
5. **Alpaca Client** → Requests `https://paper-api.alpaca.markets/v2/account`
6. **Alpaca API** → Returns account data ($100k, positions, metrics)
7. **Backend** → Transforms to standard format
8. **Frontend** → Displays portfolio data

### Live Portfolio Request Flow

1. **User opens Live Portfolio tab**
2. **Frontend** → `GET http://localhost:8000/api/v1/alpaca/live/portfolio`
3. **Backend API** → Calls `get_alpaca_service(paper=False)`
4. **Service Layer** → Returns singleton `_alpaca_live_service`
5. **Alpaca Client** → Requests `https://api.alpaca.markets/v2/account`
6. **Alpaca API** → Returns live account data (real money)
7. **Backend** → Transforms to standard format
8. **Frontend** → Displays portfolio data

## API Response Format

### Alpaca Account Object
```json
{
  "id": "46e199f7-da1b-4856-824f-74130c124ca7",
  "account_number": "PA3R6RNJHP85",
  "status": "ACTIVE",
  "currency": "USD",
  "buying_power": "100000.00",
  "cash": "100000.00",
  "portfolio_value": "100000.00",
  "pattern_day_trader": false,
  "trading_blocked": false,
  "transfers_blocked": false,
  "account_blocked": false,
  "created_at": "2025-12-24T00:00:00Z",
  "shorting_enabled": false,
  "multiplier": "1",
  "equity": "100000.00",
  "last_equity": "100000.00",
  "initial_margin": "0",
  "maintenance_margin": "0",
  "sma": "0",
  "daytrade_count": 0
}
```

### Position Object
```json
{
  "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "asset_class": "us_equity",
  "qty": "10",
  "avg_entry_price": "150.00",
  "side": "long",
  "market_value": "1500.00",
  "cost_basis": "1500.00",
  "unrealized_pl": "0.00",
  "unrealized_plpc": "0.00",
  "current_price": "150.00",
  "lastday_price": "149.50",
  "change_today": "0.33"
}
```

### Backend Response Format
```json
{
  "account": {
    "portfolio_value": 100000.00,
    "cash": 100000.00,
    "buying_power": 100000.00,
    "equity": 100000.00
  },
  "positions": [
    {
      "symbol": "AAPL",
      "qty": 10,
      "avg_entry_price": 150.00,
      "market_value": 1500.00,
      "unrealized_pl": 0.00,
      "unrealized_plpc": 0.00,
      "current_price": 150.00
    }
  ],
  "metrics": {
    "total_market_value": 1500.00,
    "total_unrealized_pl": 0.00,
    "total_unrealized_plpc": 0.00
  }
}
```

## Authentication

**Alpaca uses API Key authentication** - no OAuth complexity!

### Key Features
- ✅ **Permanent keys** - Never expire
- ✅ **Same keys** for paper and live (base URL determines mode)
- ✅ **Simple .env config** - Just add keys
- ✅ **No browser flow** - Pure API authentication

### Security Best Practices
1. **Never commit** API keys to git
2. **Use .env** files (added to .gitignore)
3. **Rotate keys** if compromised
4. **Restrict permissions** in Alpaca dashboard (if available)

## Current Status

### Paper Trading ✅
- **Status**: Fully operational
- **Account**: $100,000 virtual cash
- **Account ID**: `46e199f7-da1b-4856-824f-74130c124ca7`
- **Endpoint**: `https://paper-api.alpaca.markets`
- **Frontend**: Paper Portfolio tab working
- **Positions**: 0 (clean slate)

### Live Trading ⏸️
- **Status**: Endpoint created, awaiting credentials
- **Account**: Not yet funded/verified
- **Endpoint**: `https://api.alpaca.markets`
- **Frontend**: Live Portfolio tab temporarily points to paper
- **Next Step**: Complete Alpaca live account approval and funding

## Testing

### Test Paper Portfolio
```bash
# Backend must be running on port 8000
curl http://localhost:8000/api/v1/alpaca/paper/portfolio

# Expected response: 200 OK with $100k account data
```

### Test Live Portfolio
```bash
curl http://localhost:8000/api/v1/alpaca/live/portfolio

# Current: 401 Not Authorized (expected - no live credentials)
# After setup: 200 OK with live account data
```

### Frontend Testing
1. Start backend: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm start` (runs on port 3000)
3. Open browser: `http://localhost:3000`
4. Click "Paper Portfolio" tab → Should show $100k
5. Click "Live Portfolio" tab → Currently shows paper data (temporary)

## Migration from Schwab

This integration replaced the previous Schwab integration. Key improvements:

| Aspect | Schwab | Alpaca |
|--------|--------|--------|
| **Auth** | OAuth 2.0 (7-day refresh) | API Keys (permanent) |
| **Setup** | Complex browser flow | Simple .env config |
| **Paper Trading** | Limited | Full-featured ($100k) |
| **Live Trading** | Required real account | Separate endpoints |
| **Developer Experience** | Frustrating | Excellent |
| **Documentation** | Scattered | Comprehensive |

See: `../schwab/architecture/schwab-vs-alpaca-comparison.md` for detailed comparison.

## Next Steps

1. **Complete live account setup**
   - Fund Alpaca live account
   - Complete verification process
   - Test live endpoint

2. **Implement order placement**
   - POST /api/v1/alpaca/paper/orders
   - POST /api/v1/alpaca/live/orders
   - Order validation and confirmation

3. **Add transaction history**
   - GET /api/v1/alpaca/paper/orders
   - GET /api/v1/alpaca/live/orders
   - Display in frontend

4. **Implement market data**
   - Real-time quotes
   - Historical data
   - Market status

## References

- **Alpaca API Docs**: https://docs.alpaca.markets/
- **alpaca-py SDK**: https://github.com/alpacahq/alpaca-py
- **Migration Plan**: `../implementation/alpaca-migration-plan.md`
- **Migration Status**: `../implementation/alpaca-migration-status.md`
- **Recent Changes**: `../implementation/2025-12-25-alpaca-paper-live-separation.md`

---

**Last Updated**: 2025-12-25  
**Version**: 1.0  
**Status**: ✅ Active and operational
