#!/bin/bash
# Phase 1 Troubleshooting Script
# Run this to diagnose and fix issues

echo "🔍 Phase 1 Backend Diagnostics"
echo "================================"

# Check 1: PostgreSQL Service
echo ""
echo "1️⃣ Checking PostgreSQL service..."
if brew services list | grep -q "postgresql.*started"; then
    echo "   ✅ PostgreSQL is running"
else
    echo "   ❌ PostgreSQL is NOT running"
    echo "   💡 Fix: brew services start postgresql"
fi

# Check 2: Database Connection
echo ""
echo "2️⃣ Testing database connection..."
if psql postgresql://finsight:finsight123@localhost:5432/finsight -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ Database connection works"
    
    # Check if tables exist
    TABLE_COUNT=$(psql postgresql://finsight:finsight123@localhost:5432/finsight -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='strategy_parameters';" 2>/dev/null | tr -d ' ')
    if [ "$TABLE_COUNT" = "1" ]; then
        echo "   ✅ strategy_parameters table exists"
        
        # Check row count
        ROW_COUNT=$(psql postgresql://finsight:finsight123@localhost:5432/finsight -t -c "SELECT COUNT(*) FROM strategy_parameters;" 2>/dev/null | tr -d ' ')
        echo "   📊 Found $ROW_COUNT parameters in database"
    else
        echo "   ⚠️  strategy_parameters table does NOT exist"
        echo "   💡 Fix: Run migration: psql postgresql://finsight:finsight123@localhost:5432/finsight -f database/migrations/003_strategy_parameters.sql"
    fi
else
    echo "   ❌ Cannot connect to database"
    echo "   💡 Possible fixes:"
    echo "      - Check DATABASE_URL in backend/.env"
    echo "      - Create database: createdb -U finsight finsight"
    echo "      - Check password: psql -U finsight -d finsight"
fi

# Check 3: Python modules
echo ""
echo "3️⃣ Checking Python imports..."
cd backend
if python3 -c "import sys; sys.path.insert(0, '.'); from app.models.strategy_parameters import StrategyParameter; print('✅ Models import successfully')" 2>/dev/null; then
    echo "   ✅ Models import successfully"
else
    echo "   ❌ Models import FAILED"
    echo "   💡 Check for syntax errors in app/models/strategy_parameters.py"
fi

if python3 -c "import sys; sys.path.insert(0, '.'); from app.api.strategy_parameters import router; print('✅ API imports successfully')" 2>/dev/null; then
    echo "   ✅ API imports successfully"
else
    echo "   ❌ API import FAILED"
    echo "   💡 Check for syntax errors in app/api/strategy_parameters.py"
fi

# Check 4: Running processes
echo ""
echo "4️⃣ Checking for running uvicorn processes..."
PIDS=$(pgrep -f "uvicorn app.main:app")
if [ -n "$PIDS" ]; then
    echo "   ⚠️  Found running uvicorn processes: $PIDS"
    echo "   💡 Kill them: pkill -9 -f 'uvicorn app.main:app'"
else
    echo "   ✅ No hung processes found"
fi

# Check 5: Port 8000
echo ""
echo "5️⃣ Checking port 8000..."
if lsof -i :8000 > /dev/null 2>&1; then
    echo "   ⚠️  Port 8000 is in use"
    lsof -i :8000
    echo "   💡 Kill process or use different port"
else
    echo "   ✅ Port 8000 is available"
fi

# Summary
echo ""
echo "================================"
echo "📋 SUMMARY & NEXT STEPS"
echo "================================"
echo ""
echo "To start the server:"
echo "  1. cd backend"
echo "  2. pkill -9 -f uvicorn  # Kill any hung processes"
echo "  3. uvicorn app.main:app --reload"
echo ""
echo "To test the API:"
echo "  curl http://localhost:8000/"
echo "  curl http://localhost:8000/api/strategy-parameters/"
echo "  open http://localhost:8000/docs"
echo ""
