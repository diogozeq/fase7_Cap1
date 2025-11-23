@echo off
REM Start FarmTech API

echo ==========================================
echo FarmTech API Startup
echo ==========================================
echo.

REM Check if venv exists
if not exist "services\api\venv" (
    echo Creating virtual environment...
    cd services\api
    python -m venv venv
    cd ..\..
)

REM Activate venv
echo Activating virtual environment...
call services\api\venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r services\api\requirements.txt

REM Start API
echo.
echo ==========================================
echo Starting API on http://localhost:8000
echo ==========================================
echo.
echo Press Ctrl+C to stop the server
echo.

cd services\api
python main.py
