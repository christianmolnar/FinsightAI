# Phase C: Historical Data Population - Implementation Plan

**Date Started**: April 24, 2026 (Evening)  
**Goal**: Populate Railway PostgreSQL with historical stock data for backtesting  
**Status**: 🚧 In Progress

---

## Objectives

1. **Create database schema** for historical price data
2. **Download historical data** from Alpaca (2016–2026, 500+ stocks)
3. **Import Kaggle macro data** (financial events, already downloaded)
4. **Set up daily update job** (Railway cron for new daily bars)
5. **Update backtester** to use Railway DB instead of live Alpaca API calls

---

## Implementation Steps

### Step 1: Database Schema Design ✅
Create `historical_prices` table with:
- Symbol (ticker)
- Date
- Open, High, Low, Close, Volume
- Adjusted close
- Indexes for fast queries (symbol + date range)

### Step 2: Historical Data Downloader Script
Build `backend/app/services/historical_data_loader.py`:
- Connect to Alpaca API
- Download daily bars for S&P 500 stocks (2016–2026)
- Batch insert into Railway PostgreSQL
- Progress tracking and error handling
- Resume capability (skip already downloaded symbols)

### Step 3: Macro Events Import
Import Kaggle financial events from `/docs/IndexDB/30-yr-financial-events/`:
- Create `macro_events` table
- Parse CSV/JSON files
- Insert significant market events (Fed decisions, earnings, etc.)

### Step 4: Daily Update Job
Create Railway cron job:
- Runs daily at 5 PM ET (after market close)
- Downloads latest daily bar for all tracked symbols
- Updates `historical_prices` table

### Step 5: Update Backtester
Modify `backend/app/services/backtester.py`:
- Replace Alpaca API calls with Railway DB queries
- Add caching for frequently accessed date ranges
- Performance optimization (bulk queries)

---

## Database Schema

```sql
-- Historical daily prices
CREATE TABLE IF NOT EXISTS historical_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL,
    adjusted_close DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, date)
);

CREATE INDEX idx_historical_symbol_date ON historical_prices(symbol, date DESC);
CREATE INDEX idx_historical_date ON historical_prices(date DESC);

-- Macro economic events
CREATE TABLE IF NOT EXISTS macro_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    impact VARCHAR(20), -- 'high', 'medium', 'low'
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_macro_event_date ON macro_events(event_date DESC);
```

---

## Data Sources

### 1. Alpaca Markets Historical Data
- **Endpoint**: `/v2/stocks/{symbol}/bars`
- **Period**: 2016-01-01 to present
- **Timeframe**: 1Day
- **Symbols**: S&P 500 constituents (~500 stocks)
- **Rate Limit**: 200 requests/minute (paper tier)

### 2. Kaggle Macro Data
- **Location**: `/docs/IndexDB/30-yr-financial-events/`
- **Content**: Federal Reserve decisions, major earnings, market crashes
- **Format**: CSV/JSON files

---

## Implementation Progress

### ✅ Step 1: Database Schema (COMPLETE)
- Created migration script
- Tables created in Railway PostgreSQL
- Indexes optimized for date range queries

### 🚧 Step 2: Historical Data Download (IN PROGRESS)
- Script created: `historical_data_loader.py`
- Progress: 0/500 symbols downloaded
- Estimated time: 4-6 hours (overnight)

### ⏳ Step 3: Macro Events Import (PENDING)
- Awaiting Step 2 completion

### ⏳ Step 4: Daily Update Job (PENDING)
- Railway cron configuration needed

### ⏳ Step 5: Backtester Update (PENDING)
- Awaiting Step 2 completion for testing

---

## Error Handling Strategy

1. **API Rate Limits**: Sleep 60s between batches, resume on rate limit error
2. **Network Failures**: Retry 3x with exponential backoff
3. **Missing Data**: Log symbol + date, continue with next
4. **Duplicate Data**: UPSERT with `ON CONFLICT DO NOTHING`
5. **Progress Tracking**: Save checkpoint after each batch (50 symbols)

---

## Testing Plan

1. **Data Integrity Check**:
   - Query random sample (AAPL, TSLA, SPY) for 2020-2026
   - Verify no missing trading days
   - Check price consistency (high >= low, etc.)

2. **Backtester Performance Test**:
   - Run same backtest (Technical Breakout, 2020-2026)
   - Compare DB query time vs Alpaca API time
   - Verify results match (same trades, same P&L)

3. **Daily Update Test**:
   - Manually trigger cron job
   - Verify latest daily bar inserted for all symbols
   - Check for duplicates

---

## Success Criteria

- [x] Database tables created with proper indexes
- [ ] 500+ symbols downloaded (2016–2026, ~10 years)
- [ ] Macro events imported from Kaggle data
- [ ] Backtester successfully queries Railway DB
- [ ] Daily update cron job configured and tested
- [ ] Performance: Backtest runs 10x faster than before
- [ ] No missing data gaps for major symbols

---

## Rollback Plan

If issues arise:
1. Database schema changes are in migration file (can rollback)
2. Historical data download is additive (no data deleted)
3. Backtester has fallback to Alpaca API if DB query fails
4. Daily cron can be disabled in Railway dashboard

---

## Next Session Tasks (Morning Review)

1. Check download progress log
2. Verify data integrity (spot checks)
3. Test backtester with Railway DB
4. Compare performance (DB vs API)
5. Configure daily update cron job
6. Run full backtest to validate Phase C complete

---

**Started**: April 24, 2026 - 11:00 PM PT  
**Target Completion**: April 25, 2026 - 8:00 AM PT (overnight run)  
**Estimated Data Size**: ~2.5M rows (500 symbols × 10 years × 252 trading days)

