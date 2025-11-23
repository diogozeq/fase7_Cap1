@echo off
REM Run this script first to set up everything

echo ==========================================
echo FarmTech - Complete Setup
echo ==========================================
echo.

REM Get current directory
set CURRENT_DIR=%cd%
echo Current directory: %CURRENT_DIR%
echo.

REM Step 1: Configure AWS CLI
echo Step 1: Configuring AWS CLI...
echo.
echo You will be asked for:
echo - AWS Access Key ID: [Your AWS Access Key ID]
echo - AWS Secret Access Key: [Your AWS Secret Access Key]
echo - Default region: sa-east-1
echo - Default output format: json
echo.
pause
aws configure

REM Step 2: Verify AWS credentials
echo.
echo Step 2: Verifying AWS credentials...
aws sts get-caller-identity
if errorlevel 1 (
    echo ERROR: AWS credentials not configured correctly
    pause
    exit /b 1
)
echo OK: AWS credentials verified
echo.

REM Step 3: Create AWS resources
echo Step 3: Creating AWS resources (SNS, SES, CloudWatch)...
echo.
call setup_aws.bat
echo.

REM Step 4: Install Python dependencies
echo Step 4: Installing Python dependencies...
if not exist "services\api\venv" (
    echo Creating virtual environment...
    cd services\api
    python -m venv venv
    cd ..\..
)

echo Activating virtual environment...
call services\api\venv\Scripts\activate.bat

echo Installing requirements...
pip install -r services\api\requirements.txt

REM Step 5: Start API
echo.
echo ==========================================
echo Step 5: Starting API...
echo ==========================================
echo.
echo API will start on http://localhost:8000
echo.
echo In another PowerShell window, run:
echo   cd "%CURRENT_DIR%"
echo   .\test_all_endpoints.bat
echo.
pause

cd services\api
python main.py
