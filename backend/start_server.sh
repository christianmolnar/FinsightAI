#!/bin/bash
# Start FInsightAI Backend Server
# Run this manually to see any errors

echo "=== FInsightAI Backend Startup Script ==="
echo ""

cd "$(dirname "$0")"

echo "1. Activating virtual environment..."
source ../.venv/bin/activate

echo "2. Checking database connection..."
python3 << 'PYEOF'
from sqlalchemy import create_engine, text
try:
    engine = create_engine("postgresql+psycopg://finsight:finsight123@/finsight?host=/tmp")
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("   ✓ Database connection OK")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
PYEOF

echo "3. Starting uvicorn server..."
echo "   Server will start on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
