@echo off
echo ========================================
echo Testando Novos Endpoints
echo ========================================
echo.

echo [Teste 1] GET /api/ml/alerts
echo.
curl -s http://localhost:8000/api/ml/alerts
echo.
echo.

echo ========================================
echo [Teste 2] GET /api/ml/clusters/insights
echo.
curl -s "http://localhost:8000/api/ml/clusters/insights?n_clusters=3"
echo.
echo.

echo ========================================
echo [Teste 3] POST /api/ml/whatif
echo.
curl -s -X POST http://localhost:8000/api/ml/whatif -H "Content-Type: application/json" -d "{\"umidade\": 60, \"ph\": 7.0, \"temperatura\": 20}"
echo.
echo.

echo ========================================
echo Testes concluidos!
echo ========================================
pause
