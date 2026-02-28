# FInsightAI Testing Plan

**Complete Testing Guide for Phase 4 - Opportunity Scanner**

---

## Quick Start Test Commands

Copy and paste these commands to test each component:

### 1. Backend Health Check
```bash
curl http://localhost:8000/ | python3 -m json.tool
```
**Expected**: 
```json
{
  "message": "FInsightAI Trading Agent",
  "status": "active",
  "version": "1.0.0"
}
```

---

### 2. Account Status Test
```bash
curl http://localhost:8000/api/v1/alpaca/account | python3 -m json.tool
```
**Expected**: 
- Account ID displayed
- Status: "ACTIVE"
- Cash: $100,000
- No errors

---

### 3. Market Quotes Test
```bash
curl "http://localhost:8000/api/market/quotes/AAPL,MSFT,GOOGL" | python3 -m json.tool
```
**Expected**:
- Real bid/ask prices for each symbol
- Current timestamps
- No "N/A" values

---

### 4. Market Scanner - Breakouts
```bash
curl http://localhost:8000/api/scanner/scan/breakouts | python3 -m json.tool
```
**Expected**:
```json
{
  "success": true,
  "strategy": "technical_breakout",
  "candidates": [...],
  "total_found": 0-5
}
```
**Note**: May return 0 candidates if yfinance has rate limits - this is normal.

---

### 5. Market Scanner - Earnings
```bash
curl http://localhost:8000/api/scanner/scan/earnings | python3 -m json.tool
```
**Expected**:
```json
{
  "success": true,
  "strategy": "earnings_play",
  "candidates": [...],
  "total_found": 0-10
}
```

---

### 6. Market Scanner - Seasonal
```bash
curl http://localhost:8000/api/scanner/scan/seasonal | python3 -m json.tool
```
**Expected**:
```json
{
  "success": true,
  "strategy": "seasonality",
  "candidates": [...],
  "total_found": 0-5
}
```

---

### 7. Opportunity Analyzer (Full AI Analysis)
```bash
curl "http://localhost:8000/api/scanner/opportunities?max_results=3&confidence_threshold=0.70" | python3 -m json.tool
```
**Expected**:
```json
{
  "success": true,
  "opportunities": [
    {
      "symbol": "AAPL",
      "scanner_strategy": "technical_breakout",
      "scanner_score": 75,
      "ai_recommendation": "BUY",
      "ai_confidence": 0.85,
      "ai_reasoning": "Strong fundamentals...",
      "entry_price": 257.50,
      "stop_loss": 245.00,
      "target_price": 285.00,
      "final_score": 85
    }
  ],
  "total_found": 1,
  "confidence_threshold": 0.70
}
```
**Note**: 
- This calls OpenAI + Claude APIs (costs ~$0.10-0.20 per stock)
- Takes 2-3 minutes for full analysis
- May return 0 results if no high-confidence opportunities found

---

### 8. Trigger Background Scan Job
```bash
curl -X POST "http://localhost:8000/api/scanner/scan/trigger?confidence_threshold=0.75&max_opportunities=5" | python3 -m json.tool
```
**Expected**:
```json
{
  "success": true,
  "message": "Scan job started in background",
  "scan_id": 1,
  "estimated_duration": "2-3 minutes",
  "check_status_at": "/api/scanner/scan/status"
}
```

---

### 9. Check Scan Job Status
```bash
curl http://localhost:8000/api/scanner/scan/status | python3 -m json.tool
```
**Expected** (after scan completes):
```json
{
  "success": true,
  "last_scan": {
    "scan_id": 1,
    "timestamp": "2026-02-15T10:30:00Z",
    "opportunities_found": 3,
    "proposals_created": 2,
    "duration_seconds": 45.3,
    "status": "success"
  }
}
```

---

### 10. Transaction Queue Test
```bash
curl http://localhost:8000/api/queue/proposals | python3 -m json.tool
```
**Expected**:
- List of pending proposals
- Shows proposals created by autonomous scanner
- Includes AI confidence and reasoning

---

## Frontend Tests

### 1. Open Frontend
```bash
open http://localhost:3000
```

### 2. Check Auto-Refresh
- **Expected**: Green dot indicator when auto-refresh is on
- **Expected**: "Last updated" timestamp updates every 60 seconds
- **Expected**: Quote prices update without page reload

### 3. Test Auto-Refresh Controls
- Toggle auto-refresh on/off
- Change refresh interval (15s, 30s, 1min, 2min, 5min)
- Verify green dot shows/hides correctly

---

## Manual Tests

### Test 1: Scanner Standalone
```bash
cd backend
source venv/bin/activate
python3 test_scanner.py
```
**Expected**:
- "Testing Market Scanner..."
- "✓ Scanner created - 50 stocks in universe"
- "Found X technical breakout candidates"
- Sample candidates displayed

---

### Test 2: Analyzer Standalone  
```bash
cd backend
source venv/bin/activate
python3 test_analyzer.py
```
**Expected**:
- "Testing Opportunity Analyzer..."
- "✓ Analyzer created (threshold=60%)"
- "🔍 Finding opportunities..."
- "✅ Found X opportunities"
- Top opportunities listed with scores

**Note**: This takes 2-3 minutes due to AI API calls

---

### Test 3: Background Job Standalone
```bash
cd backend
source venv/bin/activate
python3 jobs/scan_opportunities.py
```
**Expected**:
- "AUTOMATED OPPORTUNITY SCANNER"
- "🔍 Starting opportunity scan #1"
- "📊 Found X opportunities"
- "✅ Created X trade proposals"
- "SCAN SUMMARY" with results

---

## Integration Tests

### Full Flow Test (Scanner → Analyzer → Proposals)

1. **Trigger scan**:
   ```bash
   curl -X POST "http://localhost:8000/api/scanner/scan/trigger" | python3 -m json.tool
   ```

2. **Wait 2-3 minutes** for AI analysis

3. **Check status**:
   ```bash
   curl http://localhost:8000/api/scanner/scan/status | python3 -m json.tool
   ```

4. **Verify proposals created**:
   ```bash
   curl http://localhost:8000/api/queue/proposals | python3 -m json.tool
   ```

5. **Expected**: Proposals appear in queue with:
   - Symbol, entry price, stop loss, target
   - AI confidence and reasoning
   - Scanner strategy
   - Status: "pending"
   - Source: "autonomous_scanner"

---

### Multi-Strategy Scan Test

**Test different strategy combinations**:

```bash
# Test earnings only
curl "http://localhost:8000/api/scanner/opportunities?strategies=earnings&max_results=2" | python3 -m json.tool

# Test breakout only
curl "http://localhost:8000/api/scanner/opportunities?strategies=breakout&max_results=2" | python3 -m json.tool

# Test seasonal only
curl "http://localhost:8000/api/scanner/opportunities?strategies=seasonal&max_results=2" | python3 -m json.tool

# Test multiple strategies
curl "http://localhost:8000/api/scanner/opportunities?strategies=earnings,breakout&max_results=3" | python3 -m json.tool
```

**Expected**: Each returns opportunities specific to requested strategies only.

---

### Confidence Threshold Test

**Test different confidence levels**:

```bash
# Strict (80%)
curl "http://localhost:8000/api/scanner/opportunities?confidence_threshold=0.80&max_results=5" | python3 -m json.tool

# Moderate (75%)
curl "http://localhost:8000/api/scanner/opportunities?confidence_threshold=0.75&max_results=5" | python3 -m json.tool

# Relaxed (60%)
curl "http://localhost:8000/api/scanner/opportunities?confidence_threshold=0.60&max_results=5" | python3 -m json.tool
```

**Expected**: Lower thresholds return more opportunities (less strict filtering).

---

### Background Job Test

**Test automated scanning**:

```bash
# Trigger background scan
curl -X POST "http://localhost:8000/api/scanner/scan/trigger?confidence_threshold=0.75&max_opportunities=5"

# Immediate check (should show "in progress" or "no scans")
curl http://localhost:8000/api/scanner/scan/status | python3 -m json.tool

# Wait 2-3 minutes...

# Check again (should show results)
curl http://localhost:8000/api/scanner/scan/status | python3 -m json.tool

# Verify proposals were created
curl http://localhost:8000/api/queue/proposals | python3 -m json.tool | grep -A 5 "autonomous_scanner"
```

**Expected**:
1. First status check: No results yet or previous scan
2. Second status check: Complete scan with opportunities_found > 0
3. Proposals: Should include proposals with source="autonomous_scanner"

---

### Error Handling Test

**Test system handles errors gracefully**:

```bash
# Test invalid confidence threshold
curl "http://localhost:8000/api/scanner/opportunities?confidence_threshold=2.0" 
# Expected: 422 Validation Error

# Test invalid strategy name
curl "http://localhost:8000/api/scanner/opportunities?strategies=invalid_strategy"
# Expected: Should skip invalid strategy or return empty results

# Test max_results=0
curl "http://localhost:8000/api/scanner/opportunities?max_results=0"
# Expected: Returns empty array

# Test negative max_results
curl "http://localhost:8000/api/scanner/opportunities?max_results=-5"
# Expected: 422 Validation Error or returns 0 results
```

---

## Performance Tests

### Scanner Performance Benchmark

```bash
# Time the scanner (should be <30 seconds)
time curl -s http://localhost:8000/api/scanner/scan/breakouts > /dev/null
```

**Expected**: 
- Breakout: 5-15 seconds
- Earnings: 3-8 seconds
- Seasonal: <2 seconds

---

### Analyzer Performance Benchmark

```bash
# Time full analysis (should be 2-4 minutes for 5 stocks)
time curl -s "http://localhost:8000/api/scanner/opportunities?max_results=5&confidence_threshold=0.70" > /dev/null
```

**Expected**: 
- 1 stock: 15-30 seconds
- 5 stocks: 2-3 minutes
- 10 stocks: 4-5 minutes

---

### Concurrent Request Test

**Test system handles multiple simultaneous requests**:

```bash
# Open 3 terminals and run these simultaneously:

# Terminal 1:
curl http://localhost:8000/api/scanner/scan/breakouts

# Terminal 2:
curl http://localhost:8000/api/scanner/scan/earnings

# Terminal 3:
curl http://localhost:8000/api/market/quotes/AAPL,MSFT,GOOGL
```

**Expected**: All requests complete successfully without blocking each other.

---

## Data Validation Tests

### Proposal Data Quality Test

```bash
# Get proposals
curl http://localhost:8000/api/queue/proposals | python3 -m json.tool > proposals.json

# Check the file manually for:
```

**Verify each proposal has**:
- ✅ Valid symbol (3-5 uppercase letters)
- ✅ Action = "BUY"
- ✅ Quantity > 0
- ✅ Entry price > 0
- ✅ Stop loss < Entry price (proper risk management)
- ✅ Target price > Entry price (profit target set)
- ✅ AI confidence between 0.0-1.0
- ✅ AI reasoning is not empty string
- ✅ Scanner strategy is valid ("technical_breakout", "earnings_play", "seasonality")
- ✅ Final score between 0-100
- ✅ Status = "pending"
- ✅ Source = "autonomous_scanner"

---

### Opportunity Data Quality Test

```bash
# Get opportunities
curl "http://localhost:8000/api/scanner/opportunities?max_results=5" | python3 -m json.tool > opportunities.json

# Check the file manually for:
```

**Verify each opportunity has**:
- ✅ Symbol matches scanner candidate
- ✅ Scanner score 0-100
- ✅ AI recommendation is "BUY", "WAIT", or "AVOID"
- ✅ AI confidence >= threshold used
- ✅ Entry/stop/target prices are reasonable (target > entry > stop)
- ✅ Final score >= AI confidence * 70 + scanner score * 30
- ✅ Current price and volume are present

---

## Regression Tests

### After Code Changes, Run These:

```bash
# 1. Quick health check (30 seconds)
curl http://localhost:8000/ && \
curl http://localhost:8000/api/v1/alpaca/account && \
curl http://localhost:8000/api/market/quotes/AAPL

# 2. Scanner integrity check (1 minute)
curl http://localhost:8000/api/scanner/scan/breakouts && \
curl http://localhost:8000/api/scanner/scan/earnings && \
curl http://localhost:8000/api/scanner/scan/seasonal

# 3. Backend logs check
# Look for errors in terminal where backend is running
# Should see no ERROR or CRITICAL logs

# 4. Frontend smoke test
open http://localhost:3000
# Verify: Quotes display, auto-refresh works, no console errors
```

---

## Expected Behaviors

### ✅ Normal Behaviors
- Scanner returns 0 candidates (market conditions may not show opportunities)
- Analyzer returns 0 opportunities (confidence threshold not met)
- yfinance rate limit errors (free tier limitation)
- AI analysis takes 2-3 minutes (normal API latency)
- Some symbols fail to fetch data (delisted, API issues)

### ⚠️ Warning Signs
- Backend returns 500 errors consistently
- All API calls timeout
- Database connection errors
- OpenAI/Claude API key errors

### ❌ Errors Requiring Investigation
- Frontend shows "N/A" for all quotes after auto-refresh
- Scanner endpoint returns 404
- Proposals not created after successful scan
- Backend crashes during scan

---

## Troubleshooting

### Issue: "yfinance rate limit" errors
**Solution**: Normal for free tier. Use Alpaca market data API in production.

### Issue: "No opportunities found"
**Reason**: Either no scanner candidates, or none met confidence threshold.
**Solution**: Lower confidence threshold to 0.60 or 0.65 for testing.

### Issue: "OpenAI API key not set"
**Solution**: Check `.env` file has `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`.

### Issue: Backend not reloading after code changes
**Solution**: Restart backend manually:
```bash
cd backend
lsof -ti :8000 | xargs kill -9
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Frontend quotes showing N/A
**Reason**: Alpaca API may be returning different field names.
**Solution**: Check browser console for errors, verify API response format.

---

## Performance Benchmarks

### Scanner Performance
- **Breakout scan**: 5-10 seconds (fetches 1-year history for 50 stocks)
- **Earnings scan**: 3-5 seconds (checks calendar data)
- **Seasonal scan**: <1 second (pattern matching)
- **All strategies**: 10-15 seconds

### Analyzer Performance (with AI)
- **Per stock**: 15-30 seconds (research + dual AI calls)
- **5 stocks**: 2-3 minutes total
- **10 stocks**: 4-5 minutes total

### Background Job Performance
- **Full scan (5 opportunities)**: 2-4 minutes
- **With proposal creation**: +5-10 seconds
- **Memory usage**: <500MB

---

## Test Schedule Recommendations

### During Development
- **Manual tests**: After each code change
- **API tests**: Every 30 minutes during active development
- **Full flow test**: Once per session

### Production Schedule
- **Background scan**: Every 15 minutes (via cron)
- **Health check**: Every 5 minutes
- **Full system test**: Daily at market open

---

## Success Criteria

### Phase 4 Complete When:
- ✅ All scanner strategies return results
- ✅ Opportunity analyzer completes without errors
- ✅ Background job creates proposals in database
- ✅ API endpoints respond correctly
- ✅ Frontend displays real-time quotes
- ✅ Auto-refresh works without page reload
- ✅ Manual scan trigger works via API

---

## Next Phase Testing

### Phase 5: Portfolio Management
- Test position tracking
- Verify portfolio value calculations
- Test position limits and risk management

### Phase 6: Trade Execution
- Paper trading order placement
- Order status tracking
- Fill confirmation

### Phase 7: Risk Management
- Stop loss triggers
- Position size limits
- Drawdown monitoring

### Phase 8: Monitoring & Alerts
- Performance dashboards
- Email/SMS notifications
- Trade logging

---

**Last Updated**: 2026-02-15  
**Version**: 1.0  
**Phase**: 4.3 Complete
