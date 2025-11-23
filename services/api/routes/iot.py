from fastapi import APIRouter, Request, HTTPException
from services.core.iot_gateway.irrigation_logic import apply_irrigation_logic
from datetime import datetime
import structlog

router = APIRouter(prefix="/iot", tags=["Fase 3 - IoT"])
logger = structlog.get_logger()


@router.get("/sensors")
async def get_sensor_data(request: Request):
    """
    Retorna a última leitura real do banco (leituras_sensores).
    Se não houver dados, gera uma leitura simples para não quebrar a UI.
    """
    precipitacao = None
    try:
        from services.core.database.models import LeituraSensor

        with request.app.state.db.get_session() as session:
            reading = (
                session.query(LeituraSensor)
                .order_by(LeituraSensor.data_hora_leitura.desc())
                .first()
            )

            if reading:
                umidade = float(reading.valor_umidade) if reading.valor_umidade is not None else None
                ph = float(reading.valor_ph) if reading.valor_ph is not None else None
                temperatura = float(reading.temperatura) if reading.temperatura is not None else None
                precipitacao = float(reading.precipitacao_mm) if reading.precipitacao_mm is not None else None
                bomba_ligada = bool(reading.bomba_ligada)
                decisao = reading.decisao_logica_esp32 or "Sem decisão registrada"
                ts = reading.data_hora_leitura or datetime.utcnow()
            else:
                umidade = 45.0
                ph = 6.0
                temperatura = 27.0
                precipitacao = 0.0
                bomba_ligada, decisao = apply_irrigation_logic(
                    umidade=umidade, ph=ph, fosforo=True, potassio=True
                )
                ts = datetime.utcnow()

    except Exception as e:
        logger.error("iot_read_failed", error=str(e))
        # fallback simples
        umidade = 45.0
        ph = 6.0
        temperatura = 27.0
        precipitacao = 0.0
        bomba_ligada, decisao = apply_irrigation_logic(
            umidade=umidade, ph=ph, fosforo=True, potassio=True
        )
        ts = datetime.utcnow()

    return {
        "umidade": round(umidade, 1) if umidade is not None else None,
        "temperatura": round(temperatura, 1) if temperatura is not None else None,
        "ph": ph,
        "precipitacao": precipitacao,
        "bomba_ligada": bomba_ligada,
        "decisao": decisao,
        "timestamp": ts.isoformat(),
    }


@router.post("/pump/toggle")
async def toggle_pump(request: Request):
    """
    Alterna o estado da bomba persistindo no último registro e reprocessando a lógica.
    """
    from services.core.database.models import LeituraSensor

    db_service = getattr(request.app.state, "db", None)
    if not db_service:
        raise HTTPException(status_code=500, detail="DB não inicializado")

    with db_service.get_session() as session:
        latest = (
            session.query(LeituraSensor)
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .first()
        )
        if not latest:
            raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para alternar bomba")

        umidade = float(latest.valor_umidade) if latest.valor_umidade is not None else 0.0
        ph = float(latest.valor_ph) if latest.valor_ph is not None else 6.0
        fosforo = bool(latest.valor_fosforo_p) if latest.valor_fosforo_p is not None else True
        potassio = bool(latest.valor_potassio_k) if latest.valor_potassio_k is not None else True

        # Reprocessa a lógica com dados armazenados
        _, decisao_logica = apply_irrigation_logic(
            umidade=umidade,
            ph=ph,
            fosforo=fosforo,
            potassio=potassio,
        )

        latest.bomba_ligada = not bool(latest.bomba_ligada)
        latest.decisao_logica_esp32 = f"{decisao_logica} | override_manual"

        return {
            "status": "success",
            "bomba_ligada": latest.bomba_ligada,
            "decisao": latest.decisao_logica_esp32,
            "reading_id": latest.id_leitura,
        }
