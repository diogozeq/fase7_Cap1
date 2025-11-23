#!/bin/bash

# Test script for FarmTech Phase 7 implementation
# Tests all 6 gaps implementation

echo "=========================================="
echo "FarmTech Phase 7 - Implementation Tests"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if API is running
echo -e "${YELLOW}Test 1: Checking if API is running...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ API is running${NC}"
else
    echo -e "${RED}✗ API is not running (Status: $response)${NC}"
    echo "Start the API with: cd services/api && python main.py"
    exit 1
fi
echo ""

# Test 2: Check analytics endpoint
echo -e "${YELLOW}Test 2: Testing R Analytics endpoint...${NC}"
response=$(curl -s -X POST http://localhost:8000/api/analytics/r-analysis \
  -H "Content-Type: application/json" \
  -d '{"temperatura": [20, 25, 30], "umidade": [60, 70, 80]}')
if echo "$response" | grep -q "status"; then
    echo -e "${GREEN}✓ R Analytics endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ R Analytics endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Test 3: Check R models endpoint
echo -e "${YELLOW}Test 3: Testing R Models endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/analytics/r-models)
if echo "$response" | grep -q "models"; then
    echo -e "${GREEN}✓ R Models endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ R Models endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Test 4: Check alerts endpoint
echo -e "${YELLOW}Test 4: Testing Alerts endpoint...${NC}"
response=$(curl -s -X POST http://localhost:8000/api/alerts/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Alert",
    "message": "This is a test alert",
    "severity": "media",
    "source": "fase3"
  }')
if echo "$response" | grep -q "status"; then
    echo -e "${GREEN}✓ Alerts endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ Alerts endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Test 5: Check alert history endpoint
echo -e "${YELLOW}Test 5: Testing Alert History endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/alerts/history)
if echo "$response" | grep -q "\["; then
    echo -e "${GREEN}✓ Alert History endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ Alert History endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Test 6: Check IoT sensors endpoint
echo -e "${YELLOW}Test 6: Testing IoT Sensors endpoint...${NC}"
response=$(curl -s http://localhost:8000/api/iot/sensors)
if echo "$response" | grep -q "umidade"; then
    echo -e "${GREEN}✓ IoT Sensors endpoint working${NC}"
    echo "Response: $response"
else
    echo -e "${RED}✗ IoT Sensors endpoint failed${NC}"
    echo "Response: $response"
fi
echo ""

# Test 7: Run pytest
echo -e "${YELLOW}Test 7: Running pytest...${NC}"
cd services/api
python -m pytest ../../tests/test_alerts_integration.py -v
python -m pytest ../../tests/test_analytics_integration.py -v
cd ../..
echo ""

echo "=========================================="
echo "Tests completed!"
echo "=========================================="
