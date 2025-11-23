@echo off
echo ========================================
echo Reiniciando Servidor Backend
echo ========================================
echo.

echo [1/3] Parando processos na porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Matando processo %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo [2/3] Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Iniciando servidor com novas rotas...
echo.
echo ========================================
echo Servidor rodando em http://127.0.0.1:8000
echo Pressione Ctrl+C para parar
echo ========================================
echo.

python -m uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000
