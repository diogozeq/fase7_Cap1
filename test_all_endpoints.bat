@echo off
REM Test all FarmTech endpoints

echo ==========================================
echo FarmTech Endpoint Tests
echo ==========================================
echo.

REM Colors (using echo with special characters)
setlocal enabledelayedexpansion

REM Test 1: Health Check
echo [TEST 1] Health Check
echo URL: http://localhost:8000/health
curl http://localhost:8000/health
echo.
echo.

REM Test 2: API Health
echo [TEST 2] API Health
echo URL: http://localhost:8000/api/health
curl http://localhost:8000/api/health
echo.
echo.

REM Test 3: R Models
echo [TEST 3] R Models List
echo URL: http://localhost:8000/api/analytics/r-models
curl http://localhost:8000/api/analytics/r-models
echo.
echo.

REM Test 4: R Analysis
echo [TEST 4] R Analysis
echo URL: http://localhost:8000/api/analytics/r-analysis
echo Data: temperatura=[20,25,30], umidade=[60,70,80]
curl -X POST http://localhost:8000/api/analytics/r-analysis ^
  -H "Content-Type: application/json" ^
  -d "{\"temperatura\": [20, 25, 30], \"umidade\": [60, 70, 80]}"
echo.
echo.

REM Test 5: Send Alert
echo [TEST 5] Send Alert
echo URL: http://localhost:8000/api/alerts/send
echo Data: title=Test Alert, severity=media
curl -X POST http://localhost:8000/api/alerts/send ^
  -H "Content-Type: application/json" ^
  -d "{\"title\": \"Test Alert\", \"message\": \"This is a test alert\", \"severity\": \"media\", \"source\": \"fase3\"}"
echo.
echo.

REM Test 6: Alert History
echo [TEST 6] Alert History
echo URL: http://localhost:8000/api/alerts/history
curl http://localhost:8000/api/alerts/history
echo.
echo.

REM Test 7: IoT Sensors
echo [TEST 7] IoT Sensors
echo URL: http://localhost:8000/api/iot/sensors
curl http://localhost:8000/api/iot/sensors
echo.
echo.

echo ==========================================
echo Tests completed!
echo ==========================================
echo.
echo Check your email for the alert!
echo.
pause
