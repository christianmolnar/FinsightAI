# Quick Test Commands - Copy & Paste Ready

## Server Management
```bash
# Start Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Frontend  
cd frontend && npm start

# Kill Backend
lsof -ti :8000 | xargs kill -9

# Kill Frontend
lsof -ti :3000 | xargs kill -9
```

## Health Checks (Fast - 1 second)
```bash
# Backend health
curl http://localhost:8000/

# Account status
curl http://localhost:8000/api/v1/alpaca/account

# Get quotes
curl "http://localhost:8000/api/market/quotes/AAPL,MSFT,GOOGL"
```

## Scanner Tests (Medium - 10-30 seconds)
```bash
# Breakout scan
curl http://localhost:8000/api/scanner/scan/breakouts

# Earnings scan  
curl http://localhost:8000/api/scanner/scan/earnings

# Seasonal scan
curl http://localhost:8000/api/scanner/scan/seasonal
```

## AI Analyzer (Slow - 2-3 minutes, costs $$$)
```bash
# Find opportunities (lower threshold for testing)
curl "http://localhost:8000/api/scanner/opportunities?max_results=3&confidence_threshold=0.70"

# Trigger background scan job
curl -X POST "http://localhost:8000/api/scanner/scan/trigger"

# Check scan status
curl http://localhost:8000/api/scanner/scan/status

# View created proposals
curl http://localhost:8000/api/queue/proposals
```

## Standalone Tests
```bash
# Test scanner only
cd backend && python3 test_scanner.py

# Test analyzer (2-3 min, $$$)
cd backend && python3 test_analyzer.py

# Test background job (2-3 min, $$$)
cd backend && python3 jobs/scan_opportunities.py
```

## Open Frontend
```bash
open http://localhost:3000
```

## Notes
- ⚡ = Fast (1-5 seconds)
- ⏱️ = Medium (10-30 seconds)  
- 🐌 = Slow (2-3 minutes)
- 💰 = Costs money (OpenAI + Claude API calls)

## Common Issues
```bash
# Backend won't start - port already in use
lsof -ti :8000 | xargs kill -9

# Frontend won't start - port already in use  
lsof -ti :3000 | xargs kill -9

# Check if servers are running
lsof -i :8000 | grep LISTEN  # Backend
lsof -i :3000 | grep LISTEN  # Frontend

# View backend logs
cd backend && tail -f logs/scanner.log
```
