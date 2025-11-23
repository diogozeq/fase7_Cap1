@echo off
REM FarmTech AWS Setup Script for Windows
REM Creates SNS, SES, and CloudWatch resources

echo ==========================================
echo FarmTech AWS Setup
echo ==========================================
echo.

REM Configuration
set REGION=sa-east-1
set SNS_TOPIC_NAME=farmtech-alerts
set EMAIL_ADDRESS=seu-email@example.com
set SENDER_EMAIL=noreply@farmtech.com
set LOG_GROUP=/farmtech/api

echo Step 1: Creating SNS Topic...
for /f "tokens=*" %%i in ('aws sns create-topic --name %SNS_TOPIC_NAME% --region %REGION% --query "TopicArn" --output text') do set SNS_TOPIC_ARN=%%i
echo [OK] SNS Topic created: %SNS_TOPIC_ARN%
echo.

echo Step 2: Creating SNS Email Subscription...
aws sns subscribe ^
  --topic-arn %SNS_TOPIC_ARN% ^
  --protocol email ^
  --notification-endpoint %EMAIL_ADDRESS% ^
  --region %REGION%
echo [OK] Email subscription created
echo [WARNING] Check your email and confirm the subscription!
echo.

echo Step 3: Verifying SES Email...
aws ses verify-email-identity ^
  --email-address %SENDER_EMAIL% ^
  --region %REGION%
echo [OK] SES email verification sent
echo [WARNING] Check your email and confirm the verification!
echo.

echo Step 4: Creating CloudWatch Log Group...
aws logs create-log-group ^
  --log-group-name %LOG_GROUP% ^
  --region %REGION% 2>nul || echo Log group already exists
echo [OK] CloudWatch log group created
echo.

echo Step 5: Creating CloudWatch Log Stream...
aws logs create-log-stream ^
  --log-group-name %LOG_GROUP% ^
  --log-stream-name main ^
  --region %REGION% 2>nul || echo Log stream already exists
echo [OK] CloudWatch log stream created
echo.

echo ==========================================
echo AWS Setup Complete!
echo ==========================================
echo.
echo Important: Update your .env file with:
echo AWS_SNS_TOPIC_ARN=%SNS_TOPIC_ARN%
echo AWS_SES_SENDER_EMAIL=%SENDER_EMAIL%
echo AWS_CLOUDWATCH_LOG_GROUP=%LOG_GROUP%
echo.
echo Next steps:
echo 1. Confirm SNS email subscription
echo 2. Confirm SES email verification
echo 3. Update .env file
echo 4. Start the API
echo.
pause
