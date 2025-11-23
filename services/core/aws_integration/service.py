"""AWS Integration Service - Fase 7 Completo"""
import boto3
from typing import Dict, List, Optional
import structlog
from datetime import datetime
import os
import re

logger = structlog.get_logger()

class AWSService:
    """Handles all AWS service integrations with SMS, Email and monitoring"""

    def __init__(self, region: str = 'sa-east-1'):
        self.region = region
        self.sns_topic_arn = os.getenv("AWS_SNS_TOPIC_ARN", "")
        self.sns_sms_topic_arn = os.getenv("AWS_SNS_SMS_TOPIC_ARN", "")
        self.ses_sender = os.getenv("AWS_SES_SENDER_EMAIL", "noreply@farmtech.com")
        self.s3_bucket = os.getenv("AWS_S3_BUCKET", "farmtech-storage")
        self.log_group = os.getenv("AWS_CLOUDWATCH_LOG_GROUP", "/farmtech/logs")

        try:
            # Inicializar clientes AWS
            self.sns_client = boto3.client('sns', region_name=region)
            self.s3_client = boto3.client('s3', region_name=region)
            self.cloudwatch_client = boto3.client('cloudwatch', region_name=region)
            self.logs_client = boto3.client('logs', region_name=region)
            self.ses_client = boto3.client('ses', region_name=region)
            logger.info("aws_service_initialized", region=region)
        except Exception as e:
            logger.warning("aws_service_init_failed", error=str(e))
    
    def send_alert(self, topic_arn: str, message: str, subject: str) -> str:
        """Send alert via SNS"""
        try:
            response = self.sns_client.publish(
                TopicArn=topic_arn,
                Message=message,
                Subject=subject
            )
            logger.info("sns_alert_sent", message_id=response['MessageId'])
            return response['MessageId']
        except Exception as e:
            logger.error("sns_alert_failed", error=str(e))
            return ""
    
    def send_email(self, to_email: str, subject: str, message: str) -> str:
        """Send email via SES"""
        try:
            sender = os.getenv("AWS_SES_SENDER_EMAIL", "noreply@farmtech.com")
            response = self.ses_client.send_email(
                Source=sender,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': message}}
                }
            )
            logger.info("ses_email_sent", message_id=response['MessageId'])
            return response['MessageId']
        except Exception as e:
            logger.error("ses_email_failed", error=str(e))
            return ""
    
    def upload_to_s3(self, bucket: str, key: str, data: bytes) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.put_object(Bucket=bucket, Key=key, Body=data)
            url = f"https://{bucket}.s3.{self.region}.amazonaws.com/{key}"
            logger.info("s3_upload_success", url=url)
            return url
        except Exception as e:
            logger.error("s3_upload_failed", error=str(e))
            return ""
    
    def log_metric(self, namespace: str, metric_name: str, value: float) -> None:
        """Log metric to CloudWatch"""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=[{
                    'MetricName': metric_name,
                    'Value': value,
                    'Timestamp': datetime.now()
                }]
            )
            logger.info("cloudwatch_metric_logged", metric=metric_name, value=value)
        except Exception as e:
            logger.error("cloudwatch_metric_failed", error=str(e))
    
    def send_logs_to_cloudwatch(self, log_group: str, log_stream: str, logs: List[Dict]) -> None:
        """Send logs to CloudWatch"""
        try:
            # Create log group if not exists
            try:
                self.logs_client.create_log_group(logGroupName=log_group)
            except self.logs_client.exceptions.ResourceAlreadyExistsException:
                pass
            except Exception:
                pass
            
            # Create log stream if not exists
            try:
                self.logs_client.create_log_stream(
                    logGroupName=log_group,
                    logStreamName=log_stream
                )
            except self.logs_client.exceptions.ResourceAlreadyExistsException:
                pass
            except Exception:
                pass
            
            # Put log events
            log_events = [
                {
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'message': log.get('message', str(log))
                }
                for log in logs
            ]
            
            if log_events:
                self.logs_client.put_log_events(
                    logGroupName=log_group,
                    logStreamName=log_stream,
                    logEvents=log_events
                )
            
            logger.info("cloudwatch_logs_sent", count=len(logs))
        except Exception as e:
            logger.error("cloudwatch_logs_failed", error=str(e))
    
    def put_metric(self, namespace: str, metric_name: str, value: float, unit: str = 'None') -> None:
        """Put metric to CloudWatch"""
        try:
            self.cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.now()
                    }
                ]
            )
            logger.info("cloudwatch_metric_sent", metric=metric_name, value=value)
        except Exception as e:
            logger.error("cloudwatch_metric_failed", error=str(e))

    # ========== NOVOS MÉTODOS FASE 7 ==========

    def send_sms(self, phone_number: str, message: str) -> str:
        """
        Send SMS via SNS

        Args:
            phone_number: Phone number in E.164 format (+5511999999999)
            message: SMS message (max 160 chars recommended)

        Returns:
            SNS Message ID or empty string on failure
        """
        try:
            # Validar formato de telefone brasileiro
            if not self._validate_phone_number(phone_number):
                logger.error("invalid_phone_number", phone=phone_number)
                return ""

            # Truncar mensagem se muito longa
            if len(message) > 160:
                message = message[:157] + "..."
                logger.warning("sms_message_truncated", original_length=len(message))

            # Enviar SMS via SNS
            response = self.sns_client.publish(
                PhoneNumber=phone_number,
                Message=message,
                MessageAttributes={
                    'AWS.SNS.SMS.SenderID': {
                        'DataType': 'String',
                        'StringValue': 'FarmTech'
                    },
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'  # Maior prioridade
                    }
                }
            )

            message_id = response.get('MessageId', '')
            logger.info("sms_sent", phone=phone_number, message_id=message_id)

            # Registrar métrica
            self.put_metric('FarmTech/Alerts', 'SMSSent', 1, 'Count')

            return message_id

        except Exception as e:
            logger.error("sms_send_failed", error=str(e), phone=phone_number)
            self.put_metric('FarmTech/Alerts', 'SMSFailed', 1, 'Count')
            return ""

    def send_sms_to_topic(self, message: str) -> str:
        """
        Send SMS to SNS Topic (multiple subscribers)

        Args:
            message: SMS message

        Returns:
            SNS Message ID or empty string
        """
        try:
            if not self.sns_sms_topic_arn:
                logger.warning("sns_sms_topic_not_configured")
                return ""

            response = self.sns_client.publish(
                TopicArn=self.sns_sms_topic_arn,
                Message=message[:160],  # SMS limit
                Subject="FarmTech Alert"
            )

            message_id = response.get('MessageId', '')
            logger.info("sms_topic_sent", message_id=message_id)
            return message_id

        except Exception as e:
            logger.error("sms_topic_failed", error=str(e))
            return ""

    def send_email_html(self, to_email: str, subject: str, html_body: str, text_body: Optional[str] = None) -> str:
        """
        Send HTML email via SES

        Args:
            to_email: Recipient email
            subject: Email subject
            html_body: HTML content
            text_body: Plain text fallback (optional)

        Returns:
            SES Message ID or empty string
        """
        try:
            message_body = {
                'Html': {'Data': html_body, 'Charset': 'UTF-8'}
            }

            if text_body:
                message_body['Text'] = {'Data': text_body, 'Charset': 'UTF-8'}

            response = self.ses_client.send_email(
                Source=self.ses_sender,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': message_body
                }
            )

            message_id = response.get('MessageId', '')
            logger.info("email_html_sent", to=to_email, message_id=message_id)
            self.put_metric('FarmTech/Alerts', 'EmailSent', 1, 'Count')

            return message_id

        except Exception as e:
            logger.error("email_html_failed", error=str(e), to=to_email)
            self.put_metric('FarmTech/Alerts', 'EmailFailed', 1, 'Count')
            return ""

    def send_combined_alert(
        self,
        title: str,
        message: str,
        severity: str,
        emails: List[str],
        phones: List[str],
        recommended_action: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Send alert via both Email and SMS

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (baixa, media, alta, critica)
            emails: List of email addresses
            phones: List of phone numbers
            recommended_action: Suggested corrective action

        Returns:
            Dict with 'email_ids' and 'sms_ids' lists
        """
        results = {
            'email_ids': [],
            'sms_ids': []
        }

        # Definir emoji e cor por severidade
        severity_config = {
            'baixa': {'emoji': 'ℹ️', 'color': '#17a2b8'},
            'media': {'emoji': '⚠️', 'color': '#ffc107'},
            'alta': {'emoji': '🚨', 'color': '#fd7e14'},
            'critica': {'emoji': '🆘', 'color': '#dc3545'}
        }

        config = severity_config.get(severity.lower(), severity_config['media'])

        # Criar corpo HTML do email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {config['color']}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .action {{ background: #e8f4f8; padding: 15px; margin: 15px 0; border-left: 4px solid #0066cc; }}
                .footer {{ text-align: center; padding: 10px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{config['emoji']} {title}</h2>
                    <p>Severidade: {severity.upper()}</p>
                </div>
                <div class="content">
                    <p><strong>Mensagem:</strong></p>
                    <p>{message}</p>

                    {f'<div class="action"><strong>Ação Recomendada:</strong><br/>{recommended_action}</div>' if recommended_action else ''}

                    <p><small>Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</small></p>
                </div>
                <div class="footer">
                    <p>FarmTech Monitoring System | ISO 27001 Compliant</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Texto simples para fallback
        text_body = f"""
{config['emoji']} {title}

Severidade: {severity.upper()}

{message}

{f'Ação Recomendada: {recommended_action}' if recommended_action else ''}

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

---
FarmTech Monitoring System
        """

        # Enviar emails
        for email in emails:
            if self._validate_email(email):
                msg_id = self.send_email_html(email, f"[{severity.upper()}] {title}", html_body, text_body)
                if msg_id:
                    results['email_ids'].append(msg_id)

        # Criar mensagem SMS (curta)
        sms_text = f"{config['emoji']} {title[:30]}: {message[:100]}"
        if recommended_action:
            sms_text += f" | Ação: {recommended_action[:40]}"

        # Enviar SMS
        for phone in phones:
            if self._validate_phone_number(phone):
                msg_id = self.send_sms(phone, sms_text)
                if msg_id:
                    results['sms_ids'].append(msg_id)

        logger.info("combined_alert_sent",
                   title=title,
                   emails_sent=len(results['email_ids']),
                   sms_sent=len(results['sms_ids']))

        return results

    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _validate_phone_number(self, phone: str) -> bool:
        """
        Validate Brazilian phone number in E.164 format
        Examples: +5511999999999, +551133334444
        """
        pattern = r'^\+55[1-9]{2}9?\d{8}$'
        return bool(re.match(pattern, phone))

    def log_alert_audit(self, alert_data: Dict) -> None:
        """
        Log alert to CloudWatch for ISO 27001/27002 compliance

        Args:
            alert_data: Alert information for audit trail
        """
        try:
            log_stream = f"alerts-{datetime.now().strftime('%Y-%m-%d')}"

            # Criar log stream se não existir
            try:
                self.logs_client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=log_stream
                )
            except self.logs_client.exceptions.ResourceAlreadyExistsException:
                pass

            # Preparar evento de log
            log_event = {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'message': f"[ALERT_AUDIT] {alert_data}"
            }

            # Enviar para CloudWatch
            self.logs_client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=log_stream,
                logEvents=[log_event]
            )

            logger.info("alert_audit_logged", log_stream=log_stream)

        except Exception as e:
            logger.error("alert_audit_failed", error=str(e))
