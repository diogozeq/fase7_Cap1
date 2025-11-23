"""
IoT Gateway Service - Handles IoT device communication and data ingestion - Fase 7 Enhanced
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import structlog
import requests

from ..database.service import DatabaseService
from .irrigation_logic import apply_irrigation_logic

logger = structlog.get_logger()


class IoTGatewayService:
    """Handles IoT device communication, data ingestion and automated alerts"""

    def __init__(self, db_service: DatabaseService, aws_service=None, alerts_service=None):
        """Initialize IoT Gateway Service"""
        self.db = db_service
        self.aws = aws_service
        self.alerts = alerts_service
        import os
        self.topic_arn = os.getenv("AWS_SNS_TOPIC_ARN", "")
        logger.info("iot_gateway_service_initialized")
    
    def ingest_reading(self, reading_data: Dict) -> int:
        """
        Process and store sensor reading
        
        Steps:
        1. Validate data
        2. Apply irrigation logic
        3. Store in database
        4. Check for alerts
        5. Return reading ID
        """
        try:
            # Extract sensor values
            umidade = reading_data.get('umidade')
            ph = reading_data.get('ph_estimado')
            fosforo = reading_data.get('fosforo_presente', False)
            potassio = reading_data.get('potassio_presente', False)
            
            # Apply irrigation logic
            bomba_ligada, decisao = apply_irrigation_logic(
                umidade=umidade,
                ph=ph,
                fosforo=fosforo,
                potassio=potassio
            )
            
            # Prepare data for storage
            ts = reading_data.get('timestamp', datetime.utcnow())
            if isinstance(ts, str):
                try:
                    from datetime import datetime as _dt
                    ts = _dt.fromisoformat(ts.replace('Z', '+00:00'))
                except Exception:
                    ts = datetime.utcnow()

            storage_data = {
                'data_hora_leitura': ts,
                'id_sensor': reading_data.get('id_sensor', 1),
                'valor_umidade': umidade,
                'valor_ph': ph,
                'valor_fosforo_p': 1.0 if fosforo else 0.0,
                'valor_potassio_k': 1.0 if potassio else 0.0,
                'temperatura': reading_data.get('temperatura'),
                'precipitacao_mm': reading_data.get('precipitacao') or reading_data.get('precipitacao_mm'),
                'bomba_ligada': bomba_ligada,
                'decisao_logica_esp32': decisao
            }
            
            # Store in database
            reading_id = self.db.create_reading(storage_data)

            # ========== FASE 7: Enviar alertas automáticos via AlertsService ==========
            if self.alerts:
                try:
                    alert_result = self.alerts.send_iot_alert({
                        'umidade': umidade,
                        'ph': ph,
                        'temperatura': temperatura,
                        'reading_id': reading_id,
                        'bomba_ligada': bomba_ligada,
                        'decisao': decisao
                    })

                    if alert_result.get('status') == 'success':
                        logger.info("iot_alert_sent_successfully",
                                   reading_id=reading_id,
                                   alert_id=alert_result.get('alert_id'))
                except Exception as e:
                    logger.error("iot_alert_send_failed", error=str(e), reading_id=reading_id)

            # Check for legacy alerts (backward compatibility)
            alerts = self.check_alerts(umidade, ph, bomba_ligada)
            if alerts and self.aws and not self.alerts:
                for alert in alerts:
                    self._send_alert(alert)

            logger.info("reading_ingested",
                       reading_id=reading_id,
                       bomba_ligada=bomba_ligada,
                       alerts_count=len(alerts))

            return reading_id
            
        except Exception as e:
            logger.exception("reading_ingestion_failed", error=str(e))
            raise
    
    def check_alerts(self, umidade: float, ph: float, bomba_ligada: bool) -> List[Dict]:
        """Check if reading triggers any alerts"""
        alerts = []
        
        # Emergency alert: umidade < 15%
        if umidade < 15.0:
            alerts.append({
                "title": "ALERTA DE EMERGÊNCIA",
                "message": f"Umidade crítica: {umidade:.1f}%",
                "severity": "critica",
                "source": "fase3"
            })
        
        # Critical pH alert
        if ph < 4.5 or ph > 7.5:
            alerts.append({
                "title": "ALERTA DE pH CRÍTICO",
                "message": f"pH fora da faixa segura: {ph:.2f}",
                "severity": "alta",
                "source": "fase3"
            })
        
        return alerts
    
    def _send_alert(self, alert: Dict):
        """Send alert via API"""
        if self.aws:
            try:
                import requests
                requests.post(
                    "http://localhost:8000/api/alerts/send",
                    json=alert,
                    timeout=5
                )
                logger.info("alert_sent", title=alert.get("title"))
            except Exception as e:
                logger.error("alert_send_failed", error=str(e))
    
    def get_device_status(self, device_id: str) -> Dict:
        """Get status of IoT device"""
        # Get latest reading for device
        latest_readings = self.db.get_latest_readings(limit=1)
        
        if not latest_readings:
            return {
                "device_id": device_id,
                "status": "no_data",
                "last_seen": None
            }
        
        latest = latest_readings[0]
        return {
            "device_id": device_id,
            "status": "online",
            "last_seen": latest.data_hora_leitura,
            "bomba_ligada": latest.bomba_ligada,
            "umidade": float(latest.valor_umidade) if latest.valor_umidade else None,
            "ph": float(latest.valor_ph) if latest.valor_ph else None
        }
