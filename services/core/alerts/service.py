"""
Serviço de Alertas Proativos e Recomendações Personalizadas - Fase 7
Analisa previsões, detecta anomalias e gera ações sugeridas baseadas em ML
Envia notificações via AWS SNS/SES
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy.orm import Session
import structlog

from services.core.database.models import LeituraSensor
from services.core.database.service import DatabaseService
from services.core.aws_integration.service import AWSService
from .action_templates import ActionTemplates, ActionTemplate

logger = structlog.get_logger()


class AlertsService:
    """Serviço para gerar alertas proativos, recomendações inteligentes e notificações"""

    # Thresholds críticos
    CRITICAL_UMIDADE_MIN = 15.0  # %
    CRITICAL_UMIDADE_MAX = 85.0  # %
    CRITICAL_PH_MIN = 5.5
    CRITICAL_PH_MAX = 7.5
    CRITICAL_TEMP_MIN = 10.0  # °C
    CRITICAL_TEMP_MAX = 40.0  # °C

    def __init__(self, db_session: Session, db_service: Optional[DatabaseService] = None, aws_service: Optional[AWSService] = None):
        self.db = db_session
        self.db_service = db_service
        self.aws = aws_service or AWSService()

    def analyze_predictions(self, predictions: List[float], days: List[str]) -> List[Dict[str, Any]]:
        """
        Analisa previsões ARIMA e detecta anomalias

        Args:
            predictions: Lista de valores previstos
            days: Lista de rótulos de dias correspondentes

        Returns:
            Lista de alertas detectados
        """
        alerts = []

        for i, (pred, day) in enumerate(zip(predictions, days)):
            # Alerta crítico: umidade muito baixa
            if pred < self.CRITICAL_UMIDADE_MIN:
                alerts.append({
                    "id": f"critical_low_{i}",
                    "type": "critical",
                    "severity": "high",
                    "title": "Umidade Crítica Prevista",
                    "message": f"Dia {day}: Umidade prevista de {pred:.1f}% está abaixo do limite crítico ({self.CRITICAL_UMIDADE_MIN}%)",
                    "day": day,
                    "value": pred,
                    "icon": "alert-triangle",
                    "color": "red",
                    "action": "Ativar irrigação preventiva imediatamente"
                })

            # Alerta crítico: umidade muito alta
            elif pred > self.CRITICAL_UMIDADE_MAX:
                alerts.append({
                    "id": f"critical_high_{i}",
                    "type": "critical",
                    "severity": "high",
                    "title": "Excesso de Umidade Previsto",
                    "message": f"Dia {day}: Umidade prevista de {pred:.1f}% está acima do limite ({self.CRITICAL_UMIDADE_MAX}%)",
                    "day": day,
                    "value": pred,
                    "icon": "droplet",
                    "color": "blue",
                    "action": "Melhorar drenagem e reduzir irrigação"
                })

            # Alerta de tendência: queda acentuada
            if i > 0 and (predictions[i-1] - pred) > 10:
                alerts.append({
                    "id": f"trend_down_{i}",
                    "type": "trend",
                    "severity": "medium",
                    "title": "Queda Acentuada de Umidade",
                    "message": f"Dia {day}: Previsão de queda de {predictions[i-1]:.1f}% para {pred:.1f}%",
                    "day": day,
                    "value": pred,
                    "icon": "trending-down",
                    "color": "orange",
                    "action": "Monitorar e preparar irrigação"
                })

            # Alerta de tendência: aumento acentuado
            if i > 0 and (pred - predictions[i-1]) > 10:
                alerts.append({
                    "id": f"trend_up_{i}",
                    "type": "trend",
                    "severity": "low",
                    "title": "Aumento de Umidade Detectado",
                    "message": f"Dia {day}: Previsão de aumento de {predictions[i-1]:.1f}% para {pred:.1f}%",
                    "day": day,
                    "value": pred,
                    "icon": "trending-up",
                    "color": "green",
                    "action": "Reduzir frequência de irrigação"
                })

        return alerts

    def check_current_thresholds(self) -> List[Dict[str, Any]]:
        """
        Verifica se leitura mais recente está fora dos limites

        Returns:
            Lista de alertas para condições atuais
        """
        alerts = []

        # Buscar leitura mais recente
        latest_reading = (
            self.db.query(LeituraSensor)
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .first()
        )

        if not latest_reading:
            return alerts

        # Verificar umidade
        if latest_reading.valor_umidade:
            if latest_reading.valor_umidade < self.CRITICAL_UMIDADE_MIN:
                alerts.append({
                    "id": "current_umidade_low",
                    "type": "critical",
                    "severity": "high",
                    "title": "Umidade Atual Crítica",
                    "message": f"Umidade atual de {latest_reading.valor_umidade:.1f}% está abaixo do mínimo seguro",
                    "value": latest_reading.valor_umidade,
                    "icon": "alert-circle",
                    "color": "red",
                    "action": "Iniciar irrigação imediatamente"
                })
            elif latest_reading.valor_umidade > self.CRITICAL_UMIDADE_MAX:
                alerts.append({
                    "id": "current_umidade_high",
                    "type": "critical",
                    "severity": "high",
                    "title": "Excesso de Umidade Atual",
                    "message": f"Umidade atual de {latest_reading.valor_umidade:.1f}% está acima do máximo seguro",
                    "value": latest_reading.valor_umidade,
                    "icon": "droplet",
                    "color": "blue",
                    "action": "Verificar sistema de drenagem"
                })

        # Verificar pH
        if latest_reading.valor_ph:
            if latest_reading.valor_ph < self.CRITICAL_PH_MIN:
                alerts.append({
                    "id": "current_ph_low",
                    "type": "warning",
                    "severity": "medium",
                    "title": "pH Ácido Detectado",
                    "message": f"pH atual de {latest_reading.valor_ph:.1f} está abaixo do ideal ({self.CRITICAL_PH_MIN})",
                    "value": latest_reading.valor_ph,
                    "icon": "alert-triangle",
                    "color": "orange",
                    "action": "Aplicar calcário para correção"
                })
            elif latest_reading.valor_ph > self.CRITICAL_PH_MAX:
                alerts.append({
                    "id": "current_ph_high",
                    "type": "warning",
                    "severity": "medium",
                    "title": "pH Alcalino Detectado",
                    "message": f"pH atual de {latest_reading.valor_ph:.1f} está acima do ideal ({self.CRITICAL_PH_MAX})",
                    "value": latest_reading.valor_ph,
                    "icon": "alert-triangle",
                    "color": "orange",
                    "action": "Aplicar enxofre ou matéria orgânica"
                })

        # Verificar temperatura
        if latest_reading.temperatura:
            if latest_reading.temperatura < self.CRITICAL_TEMP_MIN:
                alerts.append({
                    "id": "current_temp_low",
                    "type": "info",
                    "severity": "low",
                    "title": "Temperatura Baixa",
                    "message": f"Temperatura de {latest_reading.temperatura:.1f}°C pode afetar o crescimento",
                    "value": latest_reading.temperatura,
                    "icon": "thermometer",
                    "color": "cyan",
                    "action": "Monitorar plantas sensíveis ao frio"
                })
            elif latest_reading.temperatura > self.CRITICAL_TEMP_MAX:
                alerts.append({
                    "id": "current_temp_high",
                    "type": "warning",
                    "severity": "medium",
                    "title": "Temperatura Elevada",
                    "message": f"Temperatura de {latest_reading.temperatura:.1f}°C pode causar estresse hídrico",
                    "value": latest_reading.temperatura,
                    "icon": "thermometer",
                    "color": "orange",
                    "action": "Aumentar frequência de irrigação"
                })

        return alerts

    def generate_cluster_recommendations(
        self,
        cluster_id: int,
        cluster_center: List[float],
        cluster_size: int
    ) -> List[Dict[str, Any]]:
        """
        Gera recomendações baseadas no cluster atual

        Args:
            cluster_id: ID do cluster
            cluster_center: Centróide [umidade, pH, temperatura]
            cluster_size: Número de registros no cluster

        Returns:
            Lista de recomendações personalizadas
        """
        recommendations = []

        umidade_avg, ph_avg, temp_avg = cluster_center

        # Análise de perfil do cluster
        profile_desc = self._get_cluster_profile_description(umidade_avg, ph_avg, temp_avg)

        # Recomendação base sobre o perfil
        recommendations.append({
            "id": f"cluster_{cluster_id}_profile",
            "priority": "info",
            "title": f"Perfil do Cluster {cluster_id + 1}",
            "description": profile_desc,
            "action": None,
            "icon": "info",
            "category": "insights"
        })

        # Recomendações baseadas em umidade
        if umidade_avg < 30:
            recommendations.append({
                "id": f"cluster_{cluster_id}_umidade_baixa",
                "priority": "high",
                "title": "Ação Recomendada: Irrigação",
                "description": f"Este cluster tem umidade média de {umidade_avg:.1f}%, indicando solo seco",
                "action": "Aumentar frequência de irrigação em 30%",
                "icon": "droplet",
                "category": "irrigation"
            })
        elif umidade_avg > 70:
            recommendations.append({
                "id": f"cluster_{cluster_id}_umidade_alta",
                "priority": "medium",
                "title": "Ação Recomendada: Drenagem",
                "description": f"Este cluster tem umidade média de {umidade_avg:.1f}%, indicando excesso de água",
                "action": "Verificar sistema de drenagem e reduzir irrigação",
                "icon": "droplet-off",
                "category": "drainage"
            })
        else:
            recommendations.append({
                "id": f"cluster_{cluster_id}_umidade_ok",
                "priority": "low",
                "title": "Umidade em Níveis Ideais",
                "description": f"Umidade média de {umidade_avg:.1f}% está na faixa ótima",
                "action": "Manter regime atual de irrigação",
                "icon": "check-circle",
                "category": "irrigation"
            })

        # Recomendações baseadas em pH
        if ph_avg < 6.0:
            recommendations.append({
                "id": f"cluster_{cluster_id}_ph_baixo",
                "priority": "high",
                "title": "Correção de pH Necessária",
                "description": f"pH médio de {ph_avg:.1f} indica solo ácido",
                "action": "Aplicar calcário dolomítico (200-300 kg/ha)",
                "icon": "flask",
                "category": "soil"
            })
        elif ph_avg > 7.0:
            recommendations.append({
                "id": f"cluster_{cluster_id}_ph_alto",
                "priority": "medium",
                "title": "Correção de pH Recomendada",
                "description": f"pH médio de {ph_avg:.1f} indica solo alcalino",
                "action": "Aplicar enxofre elementar ou matéria orgânica",
                "icon": "flask",
                "category": "soil"
            })
        else:
            recommendations.append({
                "id": f"cluster_{cluster_id}_ph_ok",
                "priority": "low",
                "title": "pH em Níveis Adequados",
                "description": f"pH médio de {ph_avg:.1f} está ideal para a maioria das culturas",
                "action": "Monitorar mensalmente",
                "icon": "check-circle",
                "category": "soil"
            })

        # Recomendações baseadas em temperatura
        if temp_avg < 18:
            recommendations.append({
                "id": f"cluster_{cluster_id}_temp_baixa",
                "priority": "medium",
                "title": "Temperatura Baixa para Crescimento",
                "description": f"Temperatura média de {temp_avg:.1f}°C pode retardar o desenvolvimento",
                "action": "Considerar culturas de clima temperado ou aguardar estação mais quente",
                "icon": "thermometer",
                "category": "climate"
            })
        elif temp_avg > 32:
            recommendations.append({
                "id": f"cluster_{cluster_id}_temp_alta",
                "priority": "high",
                "title": "Estresse Térmico Possível",
                "description": f"Temperatura média de {temp_avg:.1f}°C pode causar estresse nas plantas",
                "action": "Aumentar irrigação e considerar sombreamento parcial",
                "icon": "thermometer",
                "category": "climate"
            })

        # Recomendação de fertilização baseada no perfil completo
        if 40 <= umidade_avg <= 60 and 6.0 <= ph_avg <= 7.0 and 20 <= temp_avg <= 28:
            recommendations.append({
                "id": f"cluster_{cluster_id}_fertilizacao",
                "priority": "low",
                "title": "Oportunidade: Fertilização",
                "description": "Condições ideais para aplicação de fertilizantes",
                "action": "Aplicar NPK conforme análise de solo e cultura",
                "icon": "leaf",
                "category": "nutrition"
            })

        return recommendations

    def _get_cluster_profile_description(self, umidade: float, ph: float, temp: float) -> str:
        """Gera descrição textual do perfil do cluster"""

        # Classificar umidade
        if umidade < 30:
            umidade_desc = "baixa umidade"
        elif umidade < 50:
            umidade_desc = "umidade moderada"
        elif umidade < 70:
            umidade_desc = "umidade adequada"
        else:
            umidade_desc = "alta umidade"

        # Classificar pH
        if ph < 5.5:
            ph_desc = "solo muito ácido"
        elif ph < 6.5:
            ph_desc = "solo levemente ácido"
        elif ph < 7.5:
            ph_desc = "solo neutro"
        else:
            ph_desc = "solo alcalino"

        # Classificar temperatura
        if temp < 15:
            temp_desc = "clima frio"
        elif temp < 25:
            temp_desc = "clima ameno"
        elif temp < 32:
            temp_desc = "clima quente"
        else:
            temp_desc = "clima muito quente"

        # Identificar tipo de dia típico
        if umidade > 70 and temp < 25:
            tipo_dia = "típico de períodos chuvosos ou alta nebulosidade"
        elif umidade < 30 and temp > 28:
            tipo_dia = "típico de períodos de seca e calor"
        elif 40 <= umidade <= 60 and 20 <= temp <= 28:
            tipo_dia = "condições ideais para a maioria das culturas"
        else:
            tipo_dia = "condições variáveis"

        return f"Caracterizado por {umidade_desc} ({umidade:.1f}%), {ph_desc} (pH {ph:.1f}) e {temp_desc} ({temp:.1f}°C). {tipo_dia.capitalize()}."

    def get_all_alerts_and_recommendations(
        self,
        predictions: Optional[List[float]] = None,
        days: Optional[List[str]] = None,
        cluster_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Consolida todos os alertas e recomendações

        Args:
            predictions: Previsões ARIMA (opcional)
            days: Dias correspondentes às previsões (opcional)
            cluster_info: Informações do cluster atual (opcional)

        Returns:
            Dicionário com alertas e recomendações organizados
        """
        all_alerts = []
        all_recommendations = []

        # Alertas de condições atuais
        current_alerts = self.check_current_thresholds()
        all_alerts.extend(current_alerts)

        # Alertas de previsões
        if predictions and days:
            prediction_alerts = self.analyze_predictions(predictions, days)
            all_alerts.extend(prediction_alerts)

        # Recomendações do cluster
        if cluster_info:
            cluster_recommendations = self.generate_cluster_recommendations(
                cluster_info.get("cluster_id", 0),
                cluster_info.get("center", [50, 6.5, 25]),
                cluster_info.get("size", 0)
            )
            all_recommendations.extend(cluster_recommendations)

        # Ordenar por severidade/prioridade
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_alerts.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))

        priority_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
        all_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 4))

        return {
            "alerts": all_alerts,
            "recommendations": all_recommendations,
            "summary": {
                "total_alerts": len(all_alerts),
                "critical_alerts": len([a for a in all_alerts if a.get("severity") == "high"]),
                "total_recommendations": len(all_recommendations),
                "high_priority_recommendations": len([r for r in all_recommendations if r.get("priority") == "high"]),
                "generated_at": datetime.now().isoformat()
            }
        }

    # ========== NOVOS MÉTODOS FASE 7: NOTIFICAÇÕES ==========

    def send_alert_notification(
        self,
        titulo: str,
        mensagem: str,
        severidade: str,
        origem: str,
        alert_type: Optional[str] = None,
        dados_contexto: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Envia alerta com notificações por email e SMS

        Args:
            titulo: Título do alerta
            mensagem: Mensagem descritiva
            severidade: baixa, media, alta, critica
            origem: fase1, fase3, fase6
            alert_type: Tipo específico para buscar ações (umidade_baixa, etc)
            dados_contexto: Dados adicionais (valor lido, local, etc)

        Returns:
            Dict com resultados do envio
        """
        try:
            # Buscar ações recomendadas
            actions = []
            if alert_type:
                actions = ActionTemplates.get_actions_for_alert_type(alert_type)

            recommended_action = None
            if actions:
                # Usar primeira ação como recomendação principal
                main_action = actions[0]
                recommended_action = f"{main_action.titulo}: {main_action.descricao}"

            # Buscar funcionários que devem receber este alerta
            if not self.db_service:
                logger.warning("db_service_not_configured_skipping_notifications")
                return {"status": "warning", "message": "Database service not configured"}

            funcionarios = self.db_service.get_funcionarios_for_alert(severidade)

            if not funcionarios:
                logger.warning("no_funcionarios_for_severity", severidade=severidade)
                return {"status": "warning", "message": "No funcionarios configured for this severity"}

            # Separar emails e telefones
            emails = [f.email for f in funcionarios if f.recebe_email and f.email]
            phones = [f.telefone for f in funcionarios if f.recebe_sms and f.telefone]

            logger.info("sending_alert_notification",
                       severidade=severidade,
                       emails_count=len(emails),
                       phones_count=len(phones))

            # Enviar via AWS
            results = self.aws.send_combined_alert(
                title=titulo,
                message=mensagem,
                severity=severidade,
                emails=emails,
                phones=phones,
                recommended_action=recommended_action
            )

            # Salvar alerta no banco
            alert_id = None
            if results.get('email_ids') or results.get('sms_ids'):
                message_id = results.get('email_ids', [''])[0] or results.get('sms_ids', [''])[0]
                alert_data = {
                    "titulo": titulo,
                    "mensagem": mensagem,
                    "severidade": severidade,
                    "origem": origem,
                    "message_id": message_id,
                    "data_hora": datetime.now()
                }
                alert_id = self.db_service.create_alert(alert_data)

            # Log de auditoria (ISO 27001/27002)
            self.aws.log_alert_audit({
                "alert_id": alert_id,
                "titulo": titulo,
                "severidade": severidade,
                "origem": origem,
                "funcionarios_notificados": len(funcionarios),
                "emails_enviados": len(results.get('email_ids', [])),
                "sms_enviados": len(results.get('sms_ids', [])),
                "timestamp": datetime.now().isoformat()
            })

            logger.info("alert_notification_sent",
                       alert_id=alert_id,
                       emails_sent=len(results.get('email_ids', [])),
                       sms_sent=len(results.get('sms_ids', [])))

            return {
                "status": "success",
                "alert_id": alert_id,
                "emails_sent": len(results.get('email_ids', [])),
                "sms_sent": len(results.get('sms_ids', [])),
                "funcionarios_notificados": [f.nome for f in funcionarios],
                "actions": [
                    {
                        "titulo": a.titulo,
                        "descricao": a.descricao,
                        "prioridade": a.prioridade,
                        "responsavel": a.responsavel_sugerido,
                        "passos": a.passos
                    } for a in actions
                ]
            }

        except Exception as e:
            logger.error("alert_notification_failed", error=str(e))
            return {"status": "error", "message": str(e)}

    def send_iot_alert(self, leitura_data: Dict) -> Dict[str, Any]:
        """
        Envia alerta baseado em leitura de sensor IoT (Fase 3)

        Args:
            leitura_data: Dados da leitura do sensor

        Returns:
            Resultado do envio
        """
        umidade = leitura_data.get('umidade', 0)
        ph = leitura_data.get('ph', 7.0)
        temperatura = leitura_data.get('temperatura', 25.0)

        # Verificar condições críticas
        if umidade < self.CRITICAL_UMIDADE_MIN:
            return self.send_alert_notification(
                titulo="Umidade Crítica Detectada",
                mensagem=f"Umidade do solo está em {umidade:.1f}%, abaixo do mínimo seguro de {self.CRITICAL_UMIDADE_MIN}%. Risco de perda de plantas!",
                severidade="critica",
                origem="fase3",
                alert_type="umidade_critica_baixa",
                dados_contexto=leitura_data
            )

        elif umidade > self.CRITICAL_UMIDADE_MAX:
            return self.send_alert_notification(
                titulo="Excesso de Umidade Detectado",
                mensagem=f"Umidade do solo está em {umidade:.1f}%, acima do máximo seguro de {self.CRITICAL_UMIDADE_MAX}%. Risco de apodrecimento!",
                severidade="alta",
                origem="fase3",
                alert_type="umidade_alta",
                dados_contexto=leitura_data
            )

        elif ph < self.CRITICAL_PH_MIN:
            return self.send_alert_notification(
                titulo="pH do Solo Muito Ácido",
                mensagem=f"pH do solo está em {ph:.2f}, abaixo do mínimo recomendado de {self.CRITICAL_PH_MIN}. Aplicação de calcário necessária.",
                severidade="alta",
                origem="fase3",
                alert_type="ph_baixo",
                dados_contexto=leitura_data
            )

        elif ph > self.CRITICAL_PH_MAX:
            return self.send_alert_notification(
                titulo="pH do Solo Muito Alcalino",
                mensagem=f"pH do solo está em {ph:.2f}, acima do máximo recomendado de {self.CRITICAL_PH_MAX}. Correção necessária.",
                severidade="media",
                origem="fase3",
                alert_type="ph_alto",
                dados_contexto=leitura_data
            )

        elif temperatura > self.CRITICAL_TEMP_MAX:
            return self.send_alert_notification(
                titulo="Temperatura Elevada",
                mensagem=f"Temperatura está em {temperatura:.1f}°C, acima do limite de {self.CRITICAL_TEMP_MAX}°C. Risco de estresse térmico.",
                severidade="media",
                origem="fase3",
                alert_type="temperatura_alta",
                dados_contexto=leitura_data
            )

        elif temperatura < self.CRITICAL_TEMP_MIN:
            return self.send_alert_notification(
                titulo="Temperatura Baixa",
                mensagem=f"Temperatura está em {temperatura:.1f}°C, abaixo do limite de {self.CRITICAL_TEMP_MIN}°C. Proteção necessária.",
                severidade="media",
                origem="fase3",
                alert_type="temperatura_baixa",
                dados_contexto=leitura_data
            )

        return {"status": "ok", "message": "No alerts triggered"}

    def send_cv_alert(self, deteccao_data: Dict) -> Dict[str, Any]:
        """
        Envia alerta baseado em detecção de visão computacional (Fase 6)

        Args:
            deteccao_data: Dados da detecção (classe, confiança, etc)

        Returns:
            Resultado do envio
        """
        classe = deteccao_data.get('classe', '').lower()
        confianca = deteccao_data.get('confianca', 0)

        # Alerta se NÃO detectou capacete (segurança crítica)
        if 'capacete' in classe and confianca < 50:
            return self.send_alert_notification(
                titulo="SEGURANÇA: Capacete Não Detectado",
                mensagem=f"Funcionário detectado sem capacete de segurança. Confiança: {confianca:.1f}%. Verificação urgente necessária!",
                severidade="critica",
                origem="fase6",
                alert_type="sem_capacete",
                dados_contexto=deteccao_data
            )

        # Alerta para ferramentas em área não autorizada
        elif 'tesoura' in classe or 'ferramenta' in classe:
            return self.send_alert_notification(
                titulo="Ferramenta Detectada",
                mensagem=f"{classe.title()} detectada com {confianca:.1f}% de confiança. Verificar autorização de uso.",
                severidade="media",
                origem="fase6",
                alert_type="ferramenta_nao_autorizada",
                dados_contexto=deteccao_data
            )

        return {"status": "ok", "message": "No alerts triggered"}

    def send_weather_alert(self, previsao_data: Dict) -> Dict[str, Any]:
        """
        Envia alerta baseado em previsão meteorológica (Fase 1)

        Args:
            previsao_data: Dados da previsão do tempo

        Returns:
            Resultado do envio
        """
        condicao = previsao_data.get('condicao', '').lower()
        precipitacao = previsao_data.get('precipitacao_mm', 0)
        temperatura_min = previsao_data.get('temp_min', 25)

        # Alerta para chuva forte
        if precipitacao > 50:
            return self.send_alert_notification(
                titulo="Previsão de Chuva Forte",
                mensagem=f"Previsão de {precipitacao:.1f}mm de chuva. Proteger áreas sensíveis e verificar drenagem.",
                severidade="alta",
                origem="fase1",
                alert_type="chuva_forte",
                dados_contexto=previsao_data
            )

        # Alerta para geada
        elif temperatura_min <= 2:
            return self.send_alert_notification(
                titulo="Alerta de Geada",
                mensagem=f"Temperatura mínima prevista: {temperatura_min:.1f}°C. Risco de geada! Proteção urgente necessária.",
                severidade="critica",
                origem="fase1",
                alert_type="geada",
                dados_contexto=previsao_data
            )

        # Alerta para seca
        elif 'seco' in condicao and precipitacao == 0:
            return self.send_alert_notification(
                titulo="Período Seco Previsto",
                mensagem="Sem previsão de chuva. Verificar reservatórios e planejar irrigação.",
                severidade="media",
                origem="fase1",
                alert_type="seca",
                dados_contexto=previsao_data
            )

        return {"status": "ok", "message": "No alerts triggered"}
