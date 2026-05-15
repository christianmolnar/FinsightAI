# Alpaca Paper/Live Account Separation

**Date**: 2025-12-25  
**Status**: ✅ Complete  
**Branch**: feature/alpaca-migration

## Overview
Separated Paper and Live portfolio endpoints to properly connect:
- **Paper Portfolio** → Alpaca Paper Trading Account ($100k virtual)
- **Live Portfolio** → Alpaca Live Trading Account (real money)

## Changes Made

### Backend Changes

#### 1. Updated `alpaca_service.py`
- Modified `AlpacaService.__init__()` to accept `paper` parameter
- Changed singleton pattern to support both paper and live instances
- Created separate service instances for paper and live trading

```python
class AlpacaService:
    def __init__(self, paper: bool = True):
        # Now accepts paper parameter instead of reading from env
        
def get_alpaca_service(paper: bool = True) -> AlpacaService:
    # Returns appropriate instance based on paper flag
```

#### 2. Updated `portfolio.py` API Routes
Added separate endpoints for paper and live trading:

**Paper Trading Endpoints:**
- `GET /api/v1/alpaca/paper/account`
- `GET /api/v1/alpaca/paper/positions`
- `GET /api/v1/alpaca/paper/portfolio`

**Live Trading Endpoints:**
- `GET /api/v1/alpaca/live/account`
- `GET /api/v1/alpaca/live/positions`
- `GET /api/v1/alpaca/live/portfolio`

**Backwards Compatible:**
- `GET /api/v1/alpaca/*` endpoints default to paper for compatibility

### Frontend Changes

#### 1. Updated `PaperPortfolio.js`
```javascript
// Changed from old database endpoint to Alpaca paper
const response = await fetch(`${API_BASE_URL}/api/v1/alpaca/paper/portfolio`);
```

#### 2. Updated `RealPortfolio.js`
```javascript
// Changed from generic Alpaca to live Alpaca
const response = await fetch(`${baseUrl}/api/v1/alpaca/live/portfolio`, {
  signal: AbortSignal.timeout(5000)
});
```

#### 3. Fixed Loading State Bug
Added `setLoading(false)` on successful data fetch to exit shimmer state.

## Testing

### Paper Portfolio ✅
```bash
curl http://localhost:8000/api/v1/alpaca/paper/portfolio
# Returns: $100,000 cash, 0 positions (paper account)
```

### Live Portfolio ⚠️
```bash
curl http://localhost:8000/api/v1/alpaca/live/portfolio
# Returns: 401 Not Authorized (expected - no live credentials yet)
```

## Next Steps

To enable live trading:

1. **Get Alpaca Live API Keys**
   - Log into Alpaca dashboard
   - Navigate to API Keys section
   - Generate live trading API keys
   - Note: Requires account funding and approval

2. **Configure Live Credentials**
   ```bash
   # In backend/.env (keep existing paper keys separate)
   ALPACA_LIVE_API_KEY_ID=your_live_key
   ALPACA_LIVE_API_SECRET_KEY=your_live_secret
   ```

3. **Update Service Configuration**
   - Modify `alpaca_service.py` to use separate credentials for live
   - Or use Alpaca's credential switching mechanism

## Current State

- ✅ Paper Portfolio connected to Alpaca Paper ($100k virtual)
- ✅ Live Portfolio endpoint created
- ⚠️ Live Portfolio awaits credentials
- ✅ Both UIs updated and working
- ✅ Backend server restarted and operational

## Architecture

```
Frontend:
├── Paper Portfolio (Tab) → /api/v1/alpaca/paper/portfolio
└── Live Portfolio (Tab)  → /api/v1/alpaca/live/portfolio

Backend:
├── AlpacaService(paper=True)  → Paper Trading Client
└── AlpacaService(paper=False) → Live Trading Client

Alpaca:
├── Paper Account: $100,000 virtual cash
└── Live Account: Real money (credentials pending)
```

## Notes

- Old database-based paper portfolio system (`/api/v1/paper/*`) still exists but is no longer used
- Can deprecate old system once fully migrated to Alpaca
- Live trading requires careful testing before production use
- Consider adding confirmation dialogs for live trades
