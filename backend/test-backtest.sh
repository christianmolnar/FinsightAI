#!/bin/bash

# Backtesting API Test Script
# Tests all backtesting endpoints

BASE_URL="http://localhost:8000/api/backtest"

echo "🧪 BACKTESTING API TEST SUITE"
echo "================================"
echo ""

# Test 1: Quick Backtest (30 days)
echo "Test 1: Quick Backtest - Last 30 Days"
echo "--------------------------------------"
curl -X POST "$BASE_URL/quick/30d?confidence_threshold=0.75" \
     -H "Content-Type: application/json" \
     -s | python3 -m json.tool
echo ""
echo ""

# Test 2: Custom Backtest
echo "Test 2: Custom Backtest (2025-01-01 to 2026-03-01)"
echo "---------------------------------------------------"
BACKTEST_ID=$(curl -X POST "$BASE_URL/run" \
     -H "Content-Type: application/json" \
     -d '{
       "start_date": "2025-01-01",
       "end_date": "2026-03-01",
       "strategies": null,
       "confidence_threshold": 0.75,
       "use_ai": true,
       "initial_capital": 10000,
       "position_size": 1000,
       "max_hold_days": 14
     }' \
     -s | python3 -c "import sys, json; print(json.load(sys.stdin).get('backtest_id', ''))")

if [ -n "$BACKTEST_ID" ]; then
    echo "✅ Backtest started: $BACKTEST_ID"
    echo ""
    
    # Test 3: Check Status
    echo "Test 3: Check Backtest Status"
    echo "------------------------------"
    sleep 5
    curl -s "$BASE_URL/status/$BACKTEST_ID" | python3 -m json.tool
    echo ""
    echo ""
    
    # Test 4: Wait for completion and get results
    echo "Test 4: Wait for completion (max 60 seconds)..."
    echo "------------------------------------------------"
    
    for i in {1..12}; do
        STATUS=$(curl -s "$BASE_URL/status/$BACKTEST_ID" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', ''))")
        
        if [ "$STATUS" == "complete" ]; then
            echo "✅ Backtest completed!"
            echo ""
            
            echo "Test 5: Get Results"
            echo "-------------------"
            curl -s "$BASE_URL/results/$BACKTEST_ID" | python3 -m json.tool
            echo ""
            echo ""
            
            echo "Test 6: Get Trade List"
            echo "----------------------"
            curl -s "$BASE_URL/results/$BACKTEST_ID/trades?limit=5" | python3 -m json.tool
            echo ""
            echo ""
            
            break
        elif [ "$STATUS" == "failed" ]; then
            echo "❌ Backtest failed"
            curl -s "$BASE_URL/status/$BACKTEST_ID" | python3 -m json.tool
            break
        else
            echo "⏳ Still running... (attempt $i/12)"
            sleep 5
        fi
    done
else
    echo "❌ Failed to start backtest"
fi

# Test 7: List All Backtests
echo "Test 7: List All Backtests"
echo "--------------------------"
curl -s "$BASE_URL/list" | python3 -m json.tool
echo ""

echo ""
echo "✅ ALL TESTS COMPLETE"
