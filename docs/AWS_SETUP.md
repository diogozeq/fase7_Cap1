# AWS Setup Guide - FarmTech Phase 7

## Prerequisites

- AWS Account
- AWS CLI configured
- Python 3.11+
- Boto3 installed

## Step 1: Create SNS Topic

```bash
# Create topic
aws sns create-topic --name farmtech-alerts --region sa-east-1

# Output:
# {
#   "TopicArn": "arn:aws:sns:sa-east-1:123456789012:farmtech-alerts"
# }

# Save the ARN
export AWS_SNS_TOPIC_ARN="arn:aws:sns:sa-east-1:123456789012:farmtech-alerts"
```

## Step 2: Create Email Subscription

```bash
# Subscribe email to topic
aws sns subscribe \
  --topic-arn $AWS_SNS_TOPIC_ARN \
  --protocol email \
  --notification-endpoint seu-email@example.com \
  --region sa-east-1

# Check your email and confirm subscription
```

## Step 3: Verify SES Email

```bash
# Verify email in SES
aws ses verify-email-identity \
  --email-address noreply@farmtech.com \
  --region sa-east-1

# Check your email and confirm verification
```

## Step 4: Create SES Template

```bash
# Create email template
aws ses create-template \
  --template '{
    "TemplateName": "FarmTechAlert",
    "SubjectPart": "FarmTech Alert: {{subject}}",
    "TextPart": "{{message}}",
    "HtmlPart": "<h1>{{subject}}</h1><p>{{message}}</p>"
  }' \
  --region sa-east-1
```

## Step 5: Create CloudWatch Log Group

```bash
# Create log group
aws logs create-log-group \
  --log-group-name /farmtech/api \
  --region sa-east-1

# Create log stream
aws logs create-log-stream \
  --log-group-name /farmtech/api \
  --log-stream-name main \
  --region sa-east-1
```

## Step 6: Configure Environment Variables

Create `.env` file:

```bash
# AWS Configuration
AWS_REGION=sa-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_SNS_TOPIC_ARN=arn:aws:sns:sa-east-1:123456789012:farmtech-alerts
AWS_SES_SENDER_EMAIL=noreply@farmtech.com
AWS_SES_REGION=sa-east-1
AWS_CLOUDWATCH_LOG_GROUP=/farmtech/api
```

## Step 7: Test SNS Alert

```bash
# Send test alert
curl -X POST http://localhost:8000/api/alerts/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Alert",
    "message": "This is a test alert from FarmTech",
    "severity": "media",
    "source": "fase3"
  }'

# Check your email for the alert
```

## Step 8: Test R Analysis

```bash
# Run R analysis
curl -X POST http://localhost:8000/api/analytics/r-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "temperatura": [20, 22, 25, 28, 30],
    "umidade": [60, 65, 70, 75, 80]
  }'
```

## Step 9: View CloudWatch Logs

```bash
# Get log events
aws logs get-log-events \
  --log-group-name /farmtech/api \
  --log-stream-name main \
  --region sa-east-1
```

## Troubleshooting

### SNS Topic Not Found

```bash
# List all topics
aws sns list-topics --region sa-east-1

# Verify ARN is correct
echo $AWS_SNS_TOPIC_ARN
```

### Email Not Received

1. Check spam folder
2. Verify email subscription in SNS console
3. Check SNS topic permissions

### SES Email Verification Failed

1. Check email in SES console
2. Verify email address is correct
3. Check SES region is sa-east-1

### CloudWatch Logs Not Appearing

1. Check log group exists
2. Check log stream exists
3. Verify IAM permissions
4. Check application logs for errors

## AWS Costs

- SNS: $0.50 per million requests
- SES: $0.10 per 1,000 emails
- CloudWatch Logs: $0.50 per GB ingested
- CloudWatch Metrics: $0.10 per metric

## Security Best Practices

1. Use IAM roles instead of access keys
2. Enable MFA on AWS account
3. Use VPC endpoints for private communication
4. Enable encryption at rest and in transit
5. Monitor CloudWatch logs for suspicious activity
6. Set up CloudWatch alarms for critical metrics

## References

- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
