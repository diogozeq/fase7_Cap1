#!/bin/bash

# FarmTech AWS Setup Script
# Creates SNS, SES, and CloudWatch resources

echo "=========================================="
echo "FarmTech AWS Setup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
REGION="sa-east-1"
SNS_TOPIC_NAME="farmtech-alerts"
EMAIL_ADDRESS="seu-email@example.com"
SENDER_EMAIL="noreply@farmtech.com"
LOG_GROUP="/farmtech/api"

echo -e "${YELLOW}Step 1: Creating SNS Topic...${NC}"
SNS_RESPONSE=$(aws sns create-topic --name $SNS_TOPIC_NAME --region $REGION)
SNS_TOPIC_ARN=$(echo $SNS_RESPONSE | grep -o 'arn:aws:sns:[^"]*')
echo -e "${GREEN}✓ SNS Topic created: $SNS_TOPIC_ARN${NC}"
echo ""

echo -e "${YELLOW}Step 2: Creating SNS Email Subscription...${NC}"
aws sns subscribe \
  --topic-arn $SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint $EMAIL_ADDRESS \
  --region $REGION
echo -e "${GREEN}✓ Email subscription created${NC}"
echo -e "${YELLOW}⚠ Check your email and confirm the subscription!${NC}"
echo ""

echo -e "${YELLOW}Step 3: Verifying SES Email...${NC}"
aws ses verify-email-identity \
  --email-address $SENDER_EMAIL \
  --region $REGION
echo -e "${GREEN}✓ SES email verification sent${NC}"
echo -e "${YELLOW}⚠ Check your email and confirm the verification!${NC}"
echo ""

echo -e "${YELLOW}Step 4: Creating CloudWatch Log Group...${NC}"
aws logs create-log-group \
  --log-group-name $LOG_GROUP \
  --region $REGION 2>/dev/null || echo "Log group already exists"
echo -e "${GREEN}✓ CloudWatch log group created${NC}"
echo ""

echo -e "${YELLOW}Step 5: Creating CloudWatch Log Stream...${NC}"
aws logs create-log-stream \
  --log-group-name $LOG_GROUP \
  --log-stream-name main \
  --region $REGION 2>/dev/null || echo "Log stream already exists"
echo -e "${GREEN}✓ CloudWatch log stream created${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}AWS Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Important: Update your .env file with:"
echo "AWS_SNS_TOPIC_ARN=$SNS_TOPIC_ARN"
echo "AWS_SES_SENDER_EMAIL=$SENDER_EMAIL"
echo "AWS_CLOUDWATCH_LOG_GROUP=$LOG_GROUP"
echo ""
echo "Next steps:"
echo "1. Confirm SNS email subscription"
echo "2. Confirm SES email verification"
echo "3. Update .env file"
echo "4. Start the API"
echo ""
