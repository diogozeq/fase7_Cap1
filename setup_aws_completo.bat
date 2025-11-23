@echo off
REM FarmTech AWS Setup Completo - Fase 7
REM Cria todos os recursos AWS necessários para o sistema de mensageria

echo ==========================================
echo FarmTech AWS Setup Completo - Fase 7
echo ==========================================
echo.

REM Configuração
set REGION=sa-east-1
set SNS_TOPIC_EMAIL=farmtech-alerts-email
set SNS_TOPIC_SMS=farmtech-alerts-sms
set EMAIL_ADDRESS=seu-email@example.com
set SENDER_EMAIL=noreply@farmtech.com
set PHONE_NUMBER=+5511999999999
set LOG_GROUP=/farmtech/logs
set S3_BUCKET=farmtech-storage-%RANDOM%

echo Configuracao:
echo - Regiao: %REGION%
echo - Email: %EMAIL_ADDRESS%
echo - Telefone: %PHONE_NUMBER%
echo.
echo IMPORTANTE: Edite este arquivo e altere EMAIL_ADDRESS e PHONE_NUMBER antes de executar!
echo.
pause

echo.
echo ==========================================
echo Step 1: Criando SNS Topic para EMAIL
echo ==========================================
for /f "tokens=*" %%i in ('aws sns create-topic --name %SNS_TOPIC_EMAIL% --region %REGION% --query "TopicArn" --output text') do set SNS_EMAIL_ARN=%%i
if errorlevel 1 (
    echo [ERRO] Falha ao criar SNS Topic para email
    pause
    exit /b 1
)
echo [OK] SNS Topic Email: %SNS_EMAIL_ARN%
echo.

echo ==========================================
echo Step 2: Criando SNS Topic para SMS
echo ==========================================
for /f "tokens=*" %%i in ('aws sns create-topic --name %SNS_TOPIC_SMS% --region %REGION% --query "TopicArn" --output text') do set SNS_SMS_ARN=%%i
if errorlevel 1 (
    echo [ERRO] Falha ao criar SNS Topic para SMS
    pause
    exit /b 1
)
echo [OK] SNS Topic SMS: %SNS_SMS_ARN%
echo.

echo ==========================================
echo Step 3: Criando Subscricao EMAIL
echo ==========================================
aws sns subscribe ^
  --topic-arn %SNS_EMAIL_ARN% ^
  --protocol email ^
  --notification-endpoint %EMAIL_ADDRESS% ^
  --region %REGION%
if errorlevel 1 (
    echo [ERRO] Falha ao criar subscricao email
) else (
    echo [OK] Subscricao email criada
    echo [AVISO] Confirme a subscricao no seu email!
)
echo.

echo ==========================================
echo Step 4: Criando Subscricao SMS
echo ==========================================
aws sns subscribe ^
  --topic-arn %SNS_SMS_ARN% ^
  --protocol sms ^
  --notification-endpoint %PHONE_NUMBER% ^
  --region %REGION%
if errorlevel 1 (
    echo [ERRO] Falha ao criar subscricao SMS
    echo [NOTA] SMS pode nao estar disponivel em todas as regioes
) else (
    echo [OK] Subscricao SMS criada
)
echo.

echo ==========================================
echo Step 5: Verificando Email SES
echo ==========================================
aws ses verify-email-identity ^
  --email-address %SENDER_EMAIL% ^
  --region %REGION%
if errorlevel 1 (
    echo [ERRO] Falha ao verificar email SES
) else (
    echo [OK] Email SES enviado para verificacao
    echo [AVISO] Confirme o email de verificacao!
)
echo.

echo ==========================================
echo Step 6: Criando CloudWatch Log Group
echo ==========================================
aws logs create-log-group ^
  --log-group-name %LOG_GROUP% ^
  --region %REGION% 2>nul
if errorlevel 1 (
    echo [INFO] Log group ja existe ou erro ao criar
) else (
    echo [OK] CloudWatch Log Group criado
)
echo.

echo ==========================================
echo Step 7: Criando CloudWatch Log Streams
echo ==========================================
aws logs create-log-stream ^
  --log-group-name %LOG_GROUP% ^
  --log-stream-name api ^
  --region %REGION% 2>nul

aws logs create-log-stream ^
  --log-group-name %LOG_GROUP% ^
  --log-stream-name alerts ^
  --region %REGION% 2>nul

aws logs create-log-stream ^
  --log-group-name %LOG_GROUP% ^
  --log-stream-name iot ^
  --region %REGION% 2>nul

echo [OK] Log streams criados (api, alerts, iot)
echo.

echo ==========================================
echo Step 8: Criando S3 Bucket
echo ==========================================
aws s3api create-bucket ^
  --bucket %S3_BUCKET% ^
  --region %REGION% ^
  --create-bucket-configuration LocationConstraint=%REGION% 2>nul
if errorlevel 1 (
    echo [INFO] Bucket ja existe ou erro ao criar
) else (
    echo [OK] S3 Bucket criado: %S3_BUCKET%
)
echo.

echo ==========================================
echo Step 9: Configurando Politica de Retenção (ISO 27001)
echo ==========================================
aws logs put-retention-policy ^
  --log-group-name %LOG_GROUP% ^
  --retention-in-days 90 ^
  --region %REGION%
echo [OK] Politica de retencao: 90 dias
echo.

echo ==========================================
echo Step 10: Habilitando Criptografia S3
echo ==========================================
aws s3api put-bucket-encryption ^
  --bucket %S3_BUCKET% ^
  --server-side-encryption-configuration "{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}" ^
  --region %REGION% 2>nul
echo [OK] Criptografia S3 habilitada (AES256)
echo.

echo ==========================================
echo Setup AWS Concluido!
echo ==========================================
echo.
echo Recursos criados:
echo - SNS Topic Email: %SNS_EMAIL_ARN%
echo - SNS Topic SMS: %SNS_SMS_ARN%
echo - SES Sender: %SENDER_EMAIL%
echo - CloudWatch Logs: %LOG_GROUP%
echo - S3 Bucket: %S3_BUCKET%
echo.
echo ==========================================
echo Atualize seu arquivo .env com:
echo ==========================================
echo AWS_REGION=%REGION%
echo AWS_SNS_TOPIC_ARN=%SNS_EMAIL_ARN%
echo AWS_SNS_SMS_TOPIC_ARN=%SNS_SMS_ARN%
echo AWS_SES_SENDER_EMAIL=%SENDER_EMAIL%
echo AWS_CLOUDWATCH_LOG_GROUP=%LOG_GROUP%
echo AWS_S3_BUCKET=%S3_BUCKET%
echo.
echo Proximos passos:
echo 1. Confirme a subscricao SNS no email: %EMAIL_ADDRESS%
echo 2. Confirme a verificacao SES
echo 3. Atualize o arquivo .env
echo 4. Inicie a aplicacao
echo.
pause
