from fastapi import APIRouter, HTTPException, Request
from services.core.analytics.service import AnalyticsService
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger()
router = APIRouter(prefix="/analytics", tags=["Fase 1 - Analytics"])

@router.post("/r-analysis")
async def run_r_analysis(request: Request, data: dict):
    """Run R analysis on weather data"""
    try:
        analytics = AnalyticsService()
        result = analytics.run_r_analysis(data)
        
        logger.info("r_analysis_complete", result=result)
        
        return {
            "status": "success",
            "analysis": result
        }
    except Exception as e:
        logger.error("r_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/r-models")
async def get_r_models():
    """Get available R models"""
    return {
        "models": [
            "linear_regression",
            "polynomial_regression",
            "time_series"
        ]
    }


@router.get("/overview")
async def analytics_overview(request: Request) -> Dict[str, Any]:
    """
    Consolida métricas reais do banco para alimentar a UI das fases 1/3/4.
    Inclui último sensor, médias, produção e estatísticas de detecção.
    """
    from sqlalchemy import func
    from services.core.database.models import (
        LeituraSensor,
        Deteccao,
        ProducaoAgricola,
        Cultura,
    )

    # Weather (API real) com fallback silencioso
    weather = {}
    try:
        from services.core.weather.cptec_client import CPTECClient

        weather = CPTECClient().get_weather_data()
    except Exception as e:
        logger.warning("weather_unavailable", error=str(e))
        weather = {"error": "weather_unavailable"}

    latest_payload = None

    with request.app.state.db.get_session() as session:
        latest = (
            session.query(LeituraSensor)
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .first()
        )
        avg_umidade = session.query(func.avg(LeituraSensor.valor_umidade)).scalar()
        avg_temp = session.query(func.avg(LeituraSensor.temperatura)).scalar()
        total_readings = session.query(func.count(LeituraSensor.id_leitura)).scalar()

        detections_total = session.query(func.count(Deteccao.id_deteccao)).scalar()
        avg_conf = session.query(func.avg(Deteccao.confianca)).scalar()
        top_classes = (
            session.query(Deteccao.classe, func.count(Deteccao.classe).label("c"))
            .group_by(Deteccao.classe)
            .order_by(func.count(Deteccao.classe).desc())
            .limit(3)
            .all()
        )

        prod_total = session.query(func.sum(ProducaoAgricola.quantidade_produzida)).scalar()
        valor_total = session.query(func.sum(ProducaoAgricola.valor_estimado)).scalar()
        prod_by_culture = (
            session.query(
                Cultura.nome_cultura,
                func.sum(ProducaoAgricola.quantidade_produzida).label("qtd"),
            )
            .join(Cultura, ProducaoAgricola.id_cultura == Cultura.id_cultura)
            .group_by(Cultura.nome_cultura)
            .order_by(func.sum(ProducaoAgricola.quantidade_produzida).desc())
            .limit(5)
            .all()
        )
        if latest:
            latest_payload = {
                "umidade": float(latest.valor_umidade) if latest.valor_umidade is not None else None,
                "temperatura": float(latest.temperatura) if latest.temperatura is not None else None,
                "ph": float(latest.valor_ph) if latest.valor_ph is not None else None,
                "precipitacao": float(latest.precipitacao_mm) if latest.precipitacao_mm is not None else None,
                "timestamp": latest.data_hora_leitura.isoformat() if latest.data_hora_leitura else None,
                "decisao": latest.decisao_logica_esp32,
                "bomba_ligada": bool(latest.bomba_ligada),
            }

    return {
        "weather": weather,
        "sensors": {
            "latest": latest_payload,
            "avg_umidade": float(avg_umidade) if avg_umidade is not None else None,
            "avg_temperatura": float(avg_temp) if avg_temp is not None else None,
            "total": int(total_readings or 0),
        },
        "detections": {
            "total": int(detections_total or 0),
            "avg_confidence": float(avg_conf) if avg_conf is not None else None,
            "top_classes": [{"classe": c, "count": int(cnt)} for c, cnt in top_classes],
        },
        "producao": {
            "total_quantidade": float(prod_total) if prod_total is not None else None,
            "valor_total": float(valor_total) if valor_total is not None else None,
            "por_cultura": [
                {"cultura": nome, "quantidade": float(qtd)} for nome, qtd in prod_by_culture
            ],
        },
    }
