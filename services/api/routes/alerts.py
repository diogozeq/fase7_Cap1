from fastapi import APIRouter, HTTPException, Request
from services.core.aws_integration.service import AWSService
from services.core.alerts.service import AlertsService
from services.core.alerts.action_templates import ActionTemplates
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import structlog
import os
from datetime import datetime

logger = structlog.get_logger()
router = APIRouter(prefix="/alerts", tags=["Fase 7 - Alertas"])

class AlertRequest(BaseModel):
    title: str
    message: str
    severity: str  # "baixa", "media", "alta", "critica"
    source: str    # "fase1", "fase3", "fase6"
    alert_type: Optional[str] = None  # Para buscar ação recomendada


class SendEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str


class SendSMSRequest(BaseModel):
    phone_number: str  # Formato E.164: +5511999999999
    message: str


class SendCombinedAlertRequest(BaseModel):
    title: str
    message: str
    severity: str
    emails: List[EmailStr]
    phones: List[str]
    recommended_action: Optional[str] = None


class FuncionarioCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cargo: str
    recebe_email: bool = True
    recebe_sms: bool = False
    alertas_criticos: bool = True
    alertas_altos: bool = True
    alertas_medios: bool = False
    alertas_baixos: bool = False


class IoTAlertRequest(BaseModel):
    umidade: float
    ph: Optional[float] = None
    temperatura: Optional[float] = None


class CVAlertRequest(BaseModel):
    classe: str
    confianca: float


class WeatherAlertRequest(BaseModel):
    condicao: str
    precipitacao_mm: float = 0
    temp_min: float = 25

@router.post("/send")
async def send_alert(request: Request, alert: AlertRequest):
    """Send alert via AWS SNS and SES"""
    try:
        aws = AWSService()
        
        # Format message
        formatted_message = f"""
ALERTA FARMTECH - {alert.severity.upper()}

Título: {alert.title}
Mensagem: {alert.message}
Origem: {alert.source}
Severidade: {alert.severity}

Ação Recomendada: Verificar dashboard para mais detalhes.
Timestamp: {datetime.now().isoformat()}
        """
        
        # Send via SNS
        topic_arn = os.getenv("AWS_SNS_TOPIC_ARN")
        if not topic_arn:
            logger.warning("sns_topic_not_configured")
            return {
                "status": "warning",
                "message": "SNS topic not configured",
                "alert": alert
            }
        
        message_id = aws.send_alert(
            topic_arn=topic_arn,
            message=formatted_message,
            subject=f"[{alert.severity.upper()}] {alert.title}"
        )
        
        # Save to database
        try:
            request.app.state.db.create_alert({
                "titulo": alert.title,
                "mensagem": alert.message,
                "severidade": alert.severity,
                "origem": alert.source,
                "message_id": message_id,
                "data_hora": datetime.now()
            })
        except Exception as e:
            logger.warning("alert_db_save_failed", error=str(e))
        
        logger.info("alert_sent", 
                   title=alert.title, 
                   severity=alert.severity,
                   message_id=message_id)
        
        return {
            "status": "success",
            "message_id": message_id,
            "alert": alert
        }
    except Exception as e:
        logger.error("alert_send_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_alert_history(request: Request, limit: int = 20):
    """Get alert history"""
    try:
        alerts = request.app.state.db.get_alerts(limit=limit)
        return [
            {
                "id": a.id,
                "title": a.titulo,
                "message": a.mensagem,
                "severity": a.severidade,
                "source": a.origem,
                "timestamp": a.data_hora.isoformat(),
                "message_id": a.message_id
            }
            for a in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== NOVOS ENDPOINTS FASE 7 ==========

@router.post("/send-email")
async def send_email(email_req: SendEmailRequest):
    """Send email via AWS SES"""
    try:
        aws = AWSService()
        message_id = aws.send_email(
            to_email=email_req.to_email,
            subject=email_req.subject,
            message=email_req.message
        )

        if not message_id:
            raise HTTPException(status_code=500, detail="Failed to send email")

        logger.info("email_sent_via_api", to=email_req.to_email, message_id=message_id)
        return {
            "status": "success",
            "message_id": message_id,
            "to": email_req.to_email
        }
    except Exception as e:
        logger.error("email_send_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-sms")
async def send_sms(sms_req: SendSMSRequest):
    """Send SMS via AWS SNS"""
    try:
        aws = AWSService()
        message_id = aws.send_sms(
            phone_number=sms_req.phone_number,
            message=sms_req.message
        )

        if not message_id:
            raise HTTPException(status_code=500, detail="Failed to send SMS")

        logger.info("sms_sent_via_api", phone=sms_req.phone_number, message_id=message_id)
        return {
            "status": "success",
            "message_id": message_id,
            "phone": sms_req.phone_number
        }
    except Exception as e:
        logger.error("sms_send_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-combined")
async def send_combined(combined_req: SendCombinedAlertRequest):
    """Send alert via both Email and SMS"""
    try:
        aws = AWSService()
        results = aws.send_combined_alert(
            title=combined_req.title,
            message=combined_req.message,
            severity=combined_req.severity,
            emails=combined_req.emails,
            phones=combined_req.phones,
            recommended_action=combined_req.recommended_action
        )

        logger.info("combined_alert_sent_via_api",
                   emails_sent=len(results['email_ids']),
                   sms_sent=len(results['sms_ids']))

        return {
            "status": "success",
            "emails_sent": len(results['email_ids']),
            "sms_sent": len(results['sms_ids']),
            "email_ids": results['email_ids'],
            "sms_ids": results['sms_ids']
        }
    except Exception as e:
        logger.error("combined_alert_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/iot-alert")
async def send_iot_alert(request: Request, iot_req: IoTAlertRequest):
    """Send IoT sensor alert"""
    try:
        # Criar AlertsService
        db = request.app.state.db
        aws = AWSService()

        with db.get_session() as session:
            alerts_service = AlertsService(session, db, aws)
            result = alerts_service.send_iot_alert({
                'umidade': iot_req.umidade,
                'ph': iot_req.ph,
                'temperatura': iot_req.temperatura
            })

        return result
    except Exception as e:
        logger.error("iot_alert_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cv-alert")
async def send_cv_alert(request: Request, cv_req: CVAlertRequest):
    """Send computer vision detection alert"""
    try:
        db = request.app.state.db
        aws = AWSService()

        with db.get_session() as session:
            alerts_service = AlertsService(session, db, aws)
            result = alerts_service.send_cv_alert({
                'classe': cv_req.classe,
                'confianca': cv_req.confianca
            })

        return result
    except Exception as e:
        logger.error("cv_alert_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather-alert")
async def send_weather_alert(request: Request, weather_req: WeatherAlertRequest):
    """Send weather forecast alert"""
    try:
        db = request.app.state.db
        aws = AWSService()

        with db.get_session() as session:
            alerts_service = AlertsService(session, db, aws)
            result = alerts_service.send_weather_alert({
                'condicao': weather_req.condicao,
                'precipitacao_mm': weather_req.precipitacao_mm,
                'temp_min': weather_req.temp_min
            })

        return result
    except Exception as e:
        logger.error("weather_alert_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funcionarios")
async def get_funcionarios(request: Request, apenas_ativos: bool = True):
    """Get all funcionarios"""
    try:
        funcionarios = request.app.state.db.get_funcionarios(apenas_ativos=apenas_ativos)
        return [
            {
                "id": f.id_funcionario,
                "nome": f.nome,
                "email": f.email,
                "telefone": f.telefone,
                "cargo": f.cargo,
                "ativo": f.ativo,
                "recebe_alertas": f.recebe_alertas,
                "recebe_email": f.recebe_email,
                "recebe_sms": f.recebe_sms,
                "alertas_criticos": f.alertas_criticos,
                "alertas_altos": f.alertas_altos,
                "alertas_medios": f.alertas_medios,
                "alertas_baixos": f.alertas_baixos
            }
            for f in funcionarios
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/funcionarios")
async def create_funcionario(request: Request, func: FuncionarioCreate):
    """Create new funcionario"""
    try:
        func_id = request.app.state.db.create_funcionario({
            "nome": func.nome,
            "email": func.email,
            "telefone": func.telefone,
            "cargo": func.cargo,
            "recebe_email": func.recebe_email,
            "recebe_sms": func.recebe_sms,
            "alertas_criticos": func.alertas_criticos,
            "alertas_altos": func.alertas_altos,
            "alertas_medios": func.alertas_medios,
            "alertas_baixos": func.alertas_baixos
        })

        logger.info("funcionario_created_via_api", id=func_id, nome=func.nome)
        return {
            "status": "success",
            "id": func_id,
            "nome": func.nome
        }
    except Exception as e:
        logger.error("funcionario_create_api_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions")
async def get_all_actions():
    """Get all available action templates"""
    try:
        actions = ActionTemplates.get_all_actions()
        return {
            "total": len(actions),
            "actions": [
                {
                    "code": code,
                    "titulo": action.titulo,
                    "descricao": action.descricao,
                    "prioridade": action.prioridade,
                    "tempo_estimado": action.tempo_estimado,
                    "responsavel_sugerido": action.responsavel_sugerido,
                    "passos": action.passos
                }
                for code, action in actions.items()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/actions/{alert_type}")
async def get_actions_for_alert(alert_type: str):
    """Get recommended actions for alert type"""
    try:
        actions = ActionTemplates.get_actions_for_alert_type(alert_type)
        return {
            "alert_type": alert_type,
            "actions_count": len(actions),
            "actions": [
                {
                    "titulo": a.titulo,
                    "descricao": a.descricao,
                    "prioridade": a.prioridade,
                    "tempo_estimado": a.tempo_estimado,
                    "responsavel_sugerido": a.responsavel_sugerido,
                    "passos": a.passos
                }
                for a in actions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_aws_connection():
    """Test AWS connection and services"""
    try:
        aws = AWSService()
        return {
            "status": "success",
            "region": aws.region,
            "sns_topic_arn": aws.sns_topic_arn,
            "sns_sms_topic_arn": aws.sns_sms_topic_arn,
            "ses_sender": aws.ses_sender,
            "s3_bucket": aws.s3_bucket,
            "log_group": aws.log_group,
            "message": "AWS services initialized successfully"
        }
    except Exception as e:
        logger.error("aws_test_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"AWS connection failed: {str(e)}")
