#!/bin/bash
# Quick Phase 4 Test Suite
# Run: bash test-phase4.sh

echo "🧪 Phase 4 API Test Suite"
echo "=========================="
echo ""

BASE_URL="http://localhost:8000"

echo "✅ TEST 1: Health Check"
curl -s $BASE_URL/ | python3 -m json.tool
echo ""

echo "✅ TEST 2: Get Agent Config"
curl -s $BASE_URL/api/agent/config | python3 -m json.tool
echo ""

echo "✅ TEST 3: Agent Status"
curl -s $BASE_URL/api/agent/status | python3 -m json.tool
echo ""

echo "✅ TEST 4: Scanner - Breakouts (Fast)"
curl -s "$BASE_URL/api/scanner/scan/breakouts?limit=3" | python3 -m json.tool
echo ""

echo "✅ TEST 5: Scanner - Earnings (Fast)"
curl -s "$BASE_URL/api/scanner/scan/earnings?limit=3" | python3 -m json.tool
echo ""

echo "=========================="
echo "🎉 Phase 4 Tests Complete!"
echo ""
echo "📝 To test manually:"
echo "  - Enable agent: curl -X POST $BASE_URL/api/agent/enable"
echo "  - Disable agent: curl -X POST $BASE_URL/api/agent/disable"
echo "  - Update config: curl -X PUT $BASE_URL/api/agent/config -H 'Content-Type: application/json' -d '{\"max_positions\": 15}'"
echo "  - Trigger scan: curl -X POST $BASE_URL/api/scanner/scan/trigger"
echo "  - Check scan status: curl $BASE_URL/api/scanner/scan/status"
