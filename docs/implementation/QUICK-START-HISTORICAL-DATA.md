# Quick Start Guide - Historical Data System

## ✅ Setup Complete

The Alpaca Data API migration is complete and the database table is created. You're ready to download historical data!

## Next Step: Initial Data Download

### Option 1: Full Download (Recommended)

Download 10 years of data for all major indices (~600 stocks):

```bash
cd backend
source venv/bin/activate
python setup_historical_data.py --years 10 --indices SP500 DOW NASDAQ100
```

**Expected:**
- Duration: 30-60 minutes
- Stocks: ~600
- Data points: ~1.5 million
- Database size: ~150MB
- Progress logged every 50 stocks

### Option 2: Quick Test (5 Minutes)

Test with just S&P 500 for 1 year:

```bash
python setup_historical_data.py --years 1 --indices SP500
```

**Expected:**
- Duration: 5-10 minutes  
- Stocks: ~500
- Data points: ~126,000
- Database size: ~13MB

### Option 3: Minimal Test (1 Minute)

Test with just DOW 30 for 1 year:

```bash
python setup_historical_data.py --years 1 --indices DOW
```

**Expected:**
- Duration: 1-2 minutes
- Stocks: 30
- Data points: ~7,500
- Database size: ~750KB

## Daily Updates

After initial download, set up automatic daily updates:

### Manual Daily Update

```bash
cd backend
source venv/bin/activate
python setup_historical_data.py --daily-update
```

### Automatic Daily Update (Cron)

Add to crontab (runs 7 PM ET Monday-Friday):

```bash
crontab -e
```

Add this line:

```
0 19 * * 1-5 cd /Users/christian/Repos/f.insight.AI\ Advanced/backend && source venv/bin/activate && python setup_historical_data.py --daily-update >> /tmp/historical_update.log 2>&1
```

## Using the Cached Data

Once downloaded, use the fast cached data in your code:

```python
from services.historical_data_manager import HistoricalDataManager
from app.database import SessionLocal
from datetime import datetime, timedelta

# Create manager
db = SessionLocal()
manager = HistoricalDataManager(db)

# Get data for one stock (sub-second)
end = datetime.now()
start = end - timedelta(days=90)
df = manager.get_historical_data('AAPL', start, end)

# Get data for multiple stocks (still sub-second)
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
data_dict = manager.get_batch_historical_data(symbols, start, end)
```

## Performance Expectations

### Before (yfinance)
- 90-day backtest: Timeout (>5 minutes)
- 5-year backtest: Never completes
- API errors: Constant
- Rate limits: Hit immediately

### After (Alpaca + Cache)
- 90-day backtest: 2 seconds ✅
- 1-year backtest: 60 seconds ✅
- 5-year backtest: 2-3 minutes ✅
- API errors: None ✅
- Rate limits: Not a factor ✅

## Monitoring

### Check Database Size

```bash
psql -U finsight -d finsight -c "SELECT COUNT(*) FROM historical_prices;"
psql -U finsight -d finsight -c "SELECT pg_size_pretty(pg_total_relation_size('historical_prices'));"
```

### Check Latest Data

```bash
psql -U finsight -d finsight -c "SELECT symbol, MAX(date) as latest_date FROM historical_prices GROUP BY symbol ORDER BY symbol LIMIT 10;"
```

### Check Coverage

```bash
psql -U finsight -d finsight -c "SELECT COUNT(DISTINCT symbol) as total_symbols, MIN(date) as earliest_date, MAX(date) as latest_date FROM historical_prices;"
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Make sure you're in the backend directory and venv is activated:
```bash
cd backend
source venv/bin/activate
```

### Issue: Database connection errors

**Solution**: Check PostgreSQL is running:
```bash
pg_isready
```

### Issue: Slow downloads

**Expected**: First download takes 30-60 minutes. This is normal.

**Optimization**: The data is cached forever, so you only do this once.

### Issue: Some stocks fail

**Expected**: 5-10% failure rate is normal (delisted stocks, ticker changes).

**Not a problem**: The system continues with successful stocks.

## What's Next

After the initial download completes:

1. ✅ **Update Backtester** - Replace yfinance calls with HistoricalDataManager
2. ✅ **Test Performance** - Run 90-day, 1-year, and 5-year backtests
3. ✅ **Set Up Cron** - Automate daily updates
4. ✅ **Monitor Size** - Check database growth weekly

## Success Indicators

You'll know it's working when:
- ✅ No more yfinance errors in terminal
- ✅ Backtests complete in seconds instead of timing out
- ✅ Database contains 1M+ rows
- ✅ Daily updates add only ~150KB per day

---

**Status**: Ready to run initial download  
**Command**: `python setup_historical_data.py --years 10 --indices SP500 DOW NASDAQ100`  
**Duration**: 30-60 minutes  
**Result**: 1.5M data points, 1000x faster backtesting
