from fastapi import APIRouter, Request
from datetime import timedelta, datetime
from pathlib import Path
import json
import pandas as pd
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/ml", tags=["Fase 4 - ML/Forecast"])


class WhatIfScenario(BaseModel):
    """Modelo para simulação What-If"""
    umidade: Optional[float] = None
    ph: Optional[float] = None
    temperatura: Optional[float] = None
    fosforo: Optional[float] = None
    potassio: Optional[float] = None
    precipitacao: Optional[float] = None


@router.get("/forecast")
async def forecast(request: Request, steps: int = 7):
    """Return humidity forecast using last sensor readings (fallbacks to mock data)."""
    history = []
    try:
        from services.core.database.models import LeituraSensor
        with request.app.state.db.get_session() as session:
            q = (
                session.query(LeituraSensor.valor_umidade)
                .filter(LeituraSensor.valor_umidade.isnot(None))
                .order_by(LeituraSensor.data_hora_leitura.desc())
                .limit(50)
            )
            history = [float(r[0]) for r in q.all()][::-1]
    except Exception:
        history = []

    if len(history) < 8:
        # Seed with a simple curve if the database is empty
        history = [55, 57, 56, 58, 59, 61, 60, 62, 63, 64]

    from services.core.ml_models.service import MLModelsService
    ml = MLModelsService()
    result = ml.forecast_umidade(history, steps=steps)

    base = datetime.utcnow()
    days = [(base + timedelta(days=i + 1)).strftime("%d/%m") for i in range(len(result.get("predictions", [])))]

    return {
        "history": history[-30:],
        "predictions": result.get("predictions", []),
        "confidence_intervals": result.get("confidence_intervals", []),
        "alerts": result.get("alerts", []),
        "days": days
    }


@router.get("/models")
async def list_models():
    """Lista metadados reais dos modelos treinados (usando arquivos *_metadata.json)."""
    models_dir = Path(__file__).resolve().parents[3] / "services" / "core" / "ml_models" / "models"
    models = []
    for meta_file in models_dir.glob("*_metadata.json"):
        try:
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            model_name = data.get("model_name")
            joblib_path = models_dir / f"{model_name}.joblib" if model_name else None
            status = "disponivel" if joblib_path and joblib_path.exists() else "ausente"
            metric = data.get("accuracy") or data.get("r2_score") or data.get("rmse")
            models.append(
                {
                    "name": model_name or meta_file.stem,
                    "type": data.get("model_type"),
                    "metric": metric,
                    "status": status,
                    "metadata": data,
                }
            )
        except Exception:
            continue
    return {"models": models}


@router.get("/clusters")
async def cluster_readings(request: Request, n_clusters: int = 3):
    """
    Executa K-Means em leituras reais do banco (umidade, ph, temperatura).
    """
    from services.core.database.models import LeituraSensor
    from services.core.ml_models.service import MLModelsService

    with request.app.state.db.get_session() as session:
        rows = (
            session.query(
                LeituraSensor.valor_umidade,
                LeituraSensor.valor_ph,
                LeituraSensor.temperatura,
            )
            .filter(
                LeituraSensor.valor_umidade.isnot(None),
                LeituraSensor.valor_ph.isnot(None),
                LeituraSensor.temperatura.isnot(None),
            )
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .limit(200)
            .all()
        )

    if not rows or len(rows) < n_clusters:
        return {"clusters": [], "centers": [], "inertia": 0.0, "count": len(rows)}

    df = pd.DataFrame(rows, columns=["umidade", "ph", "temperatura"])
    ml = MLModelsService()
    result = ml.cluster_data(df, n_clusters=n_clusters)
    result["count"] = len(df)
    return result


@router.get("/clusters/insights")
async def cluster_insights(request: Request, n_clusters: int = 3):
    """
    Retorna clusters com insights detalhados, registros individuais e recomendações.
    """
    from services.core.database.models import LeituraSensor
    from services.core.ml_models.service import MLModelsService
    import numpy as np

    with request.app.state.db.get_session() as session:
        rows = (
            session.query(
                LeituraSensor.id_leitura,
                LeituraSensor.data_hora_leitura,
                LeituraSensor.valor_umidade,
                LeituraSensor.valor_ph,
                LeituraSensor.temperatura,
            )
            .filter(
                LeituraSensor.valor_umidade.isnot(None),
                LeituraSensor.valor_ph.isnot(None),
                LeituraSensor.temperatura.isnot(None),
            )
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .limit(200)
            .all()
        )

    if not rows or len(rows) < n_clusters:
        return {"clusters": [], "insights": [], "count": len(rows)}

    df = pd.DataFrame(rows, columns=["id", "timestamp", "umidade", "ph", "temperatura"])
    data = df[["umidade", "ph", "temperatura"]].values

    ml = MLModelsService()
    result = ml.cluster_data(pd.DataFrame(data, columns=["umidade", "ph", "temperatura"]), n_clusters=n_clusters)

    clusters_labels = result.get("clusters", [])
    centers = result.get("centers", [])

    # Adicionar labels ao dataframe
    df["cluster"] = clusters_labels

    # Gerar insights por cluster
    cluster_insights = []
    for i in range(n_clusters):
        cluster_data = df[df["cluster"] == i]
        if len(cluster_data) == 0:
            continue

        center = centers[i]
        umidade_avg, ph_avg, temp_avg = center

        # Análise de características
        characteristics = []
        if umidade_avg > 70:
            characteristics.append("Alta umidade")
        elif umidade_avg < 40:
            characteristics.append("Baixa umidade")
        else:
            characteristics.append("Umidade moderada")

        if temp_avg > 25:
            characteristics.append("temperatura elevada")
        elif temp_avg < 15:
            characteristics.append("temperatura baixa")
        else:
            characteristics.append("temperatura amena")

        if ph_avg > 7.5:
            characteristics.append("pH alcalino")
        elif ph_avg < 6.5:
            characteristics.append("pH ácido")
        else:
            characteristics.append("pH neutro")

        # Gerar descrição automática
        description = f"Cluster {i+1} apresenta {', '.join(characteristics).lower()}"

        # Gerar recomendações
        recommendations = []
        if umidade_avg > 80:
            recommendations.append("Considere aumentar ventilação para reduzir umidade")
        elif umidade_avg < 30:
            recommendations.append("Recomenda-se aumentar irrigação ou umidificação")

        if temp_avg > 30:
            recommendations.append("Ativar sistema de resfriamento")
        elif temp_avg < 10:
            recommendations.append("Ativar sistema de aquecimento")

        if ph_avg > 8:
            recommendations.append("pH muito alcalino - adicionar corretivos ácidos")
        elif ph_avg < 6:
            recommendations.append("pH muito ácido - adicionar calcário")

        if not recommendations:
            recommendations.append("Condições dentro dos parâmetros ideais - manter monitoramento")

        # Registros do cluster (últimos 5)
        records = cluster_data.head(5).to_dict("records")
        for rec in records:
            if "timestamp" in rec and rec["timestamp"]:
                rec["timestamp"] = rec["timestamp"].isoformat() if hasattr(rec["timestamp"], "isoformat") else str(rec["timestamp"])

        cluster_insights.append({
            "id": i,
            "name": f"Cluster {i+1}",
            "size": len(cluster_data),
            "center": {
                "umidade": round(float(umidade_avg), 2),
                "ph": round(float(ph_avg), 2),
                "temperatura": round(float(temp_avg), 2)
            },
            "characteristics": characteristics,
            "description": description,
            "recommendations": recommendations,
            "sample_records": records,
            "statistics": {
                "umidade_std": round(float(cluster_data["umidade"].std()), 2),
                "ph_std": round(float(cluster_data["ph"].std()), 2),
                "temp_std": round(float(cluster_data["temperatura"].std()), 2)
            }
        })

    return {
        "clusters": cluster_insights,
        "total_records": len(df),
        "n_clusters": n_clusters,
        "inertia": result.get("inertia", 0.0)
    }


@router.post("/whatif")
async def whatif_simulation(scenario: WhatIfScenario, request: Request):
    """
    Simula cenário What-If: ajusta variáveis e vê como modelos respondem.
    """
    from services.core.database.models import LeituraSensor
    from services.core.ml_models.service import MLModelsService
    import numpy as np

    # Buscar leituras reais como baseline
    with request.app.state.db.get_session() as session:
        rows = (
            session.query(
                LeituraSensor.valor_umidade,
                LeituraSensor.valor_ph,
                LeituraSensor.temperatura,
            )
            .filter(
                LeituraSensor.valor_umidade.isnot(None),
                LeituraSensor.valor_ph.isnot(None),
                LeituraSensor.temperatura.isnot(None),
            )
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .limit(50)
            .all()
        )

    if not rows:
        # Valores padrão se não houver dados
        baseline = {"umidade": 60.0, "ph": 7.0, "temperatura": 20.0}
    else:
        df = pd.DataFrame(rows, columns=["umidade", "ph", "temperatura"])
        baseline = {
            "umidade": float(df["umidade"].mean()),
            "ph": float(df["ph"].mean()),
            "temperatura": float(df["temperatura"].mean())
        }

    # Aplicar cenário What-If
    adjusted = baseline.copy()
    if scenario.umidade is not None:
        adjusted["umidade"] = scenario.umidade
    if scenario.ph is not None:
        adjusted["ph"] = scenario.ph
    if scenario.temperatura is not None:
        adjusted["temperatura"] = scenario.temperatura

    # Simular histórico com o novo valor
    history_baseline = [baseline["umidade"]] * 10
    history_adjusted = [adjusted["umidade"]] * 10

    ml = MLModelsService()

    # Previsão ARIMA - baseline vs ajustado
    forecast_baseline = ml.forecast_umidade(history_baseline, steps=7)
    forecast_adjusted = ml.forecast_umidade(history_adjusted, steps=7)

    # Classificação de risco (usando modelo de classificação se disponível)
    risk_baseline = "Baixo"
    risk_adjusted = "Baixo"

    # Lógica simples de classificação de risco
    if adjusted["umidade"] < 30 or adjusted["umidade"] > 80:
        risk_adjusted = "Alto"
    elif adjusted["umidade"] < 40 or adjusted["umidade"] > 70:
        risk_adjusted = "Médio"

    if baseline["umidade"] < 30 or baseline["umidade"] > 80:
        risk_baseline = "Alto"
    elif baseline["umidade"] < 40 or baseline["umidade"] > 70:
        risk_baseline = "Médio"

    # Análise de impacto
    impact_analysis = []

    if scenario.umidade is not None:
        delta = scenario.umidade - baseline["umidade"]
        impact_analysis.append({
            "variable": "umidade",
            "baseline": round(baseline["umidade"], 2),
            "adjusted": round(scenario.umidade, 2),
            "delta": round(delta, 2),
            "delta_percent": round((delta / baseline["umidade"]) * 100, 2) if baseline["umidade"] != 0 else 0,
            "impact": "Aumento significativo" if delta > 10 else "Redução significativa" if delta < -10 else "Mudança moderada"
        })

    if scenario.ph is not None:
        delta = scenario.ph - baseline["ph"]
        impact_analysis.append({
            "variable": "pH",
            "baseline": round(baseline["ph"], 2),
            "adjusted": round(scenario.ph, 2),
            "delta": round(delta, 2),
            "delta_percent": round((delta / baseline["ph"]) * 100, 2) if baseline["ph"] != 0 else 0,
            "impact": "pH mais alcalino" if delta > 0.5 else "pH mais ácido" if delta < -0.5 else "pH estável"
        })

    if scenario.temperatura is not None:
        delta = scenario.temperatura - baseline["temperatura"]
        impact_analysis.append({
            "variable": "temperatura",
            "baseline": round(baseline["temperatura"], 2),
            "adjusted": round(scenario.temperatura, 2),
            "delta": round(delta, 2),
            "delta_percent": round((delta / baseline["temperatura"]) * 100, 2) if baseline["temperatura"] != 0 else 0,
            "impact": "Aquecimento" if delta > 5 else "Resfriamento" if delta < -5 else "Temperatura estável"
        })

    return {
        "baseline": baseline,
        "adjusted": adjusted,
        "impact_analysis": impact_analysis,
        "forecasts": {
            "baseline": {
                "predictions": forecast_baseline.get("predictions", []),
                "next_week_avg": round(float(np.mean(forecast_baseline.get("predictions", [0])[:7])), 2)
            },
            "adjusted": {
                "predictions": forecast_adjusted.get("predictions", []),
                "next_week_avg": round(float(np.mean(forecast_adjusted.get("predictions", [0])[:7])), 2)
            }
        },
        "risk_classification": {
            "baseline": risk_baseline,
            "adjusted": risk_adjusted,
            "changed": risk_baseline != risk_adjusted
        }
    }


@router.get("/alerts")
async def get_alerts(request: Request):
    """
    Retorna alertas proativos e recomendações personalizadas baseadas em previsões.
    """
    from services.core.database.models import LeituraSensor
    from services.core.ml_models.service import MLModelsService

    alerts = []
    recommendations = []

    # Buscar últimas leituras
    with request.app.state.db.get_session() as session:
        rows = (
            session.query(
                LeituraSensor.valor_umidade,
                LeituraSensor.valor_ph,
                LeituraSensor.temperatura,
            )
            .filter(
                LeituraSensor.valor_umidade.isnot(None),
            )
            .order_by(LeituraSensor.data_hora_leitura.desc())
            .limit(50)
            .all()
        )

    if rows:
        df = pd.DataFrame(rows, columns=["umidade", "ph", "temperatura"])

        # Análise de tendências
        current_umidade = float(df["umidade"].iloc[0])
        avg_umidade = float(df["umidade"].mean())

        # Previsão ARIMA
        history = df["umidade"].tolist()[::-1]
        ml = MLModelsService()
        forecast = ml.forecast_umidade(history[-30:], steps=7)
        predictions = forecast.get("predictions", [])

        # Alertas críticos
        if current_umidade < 30:
            alerts.append({
                "level": "critical",
                "type": "umidade_baixa",
                "message": "Umidade crítica detectada",
                "value": round(current_umidade, 2),
                "threshold": 30,
                "timestamp": datetime.utcnow().isoformat()
            })
            recommendations.append({
                "priority": "high",
                "action": "Ativar sistema de irrigação imediatamente",
                "reason": f"Umidade atual ({round(current_umidade, 2)}%) abaixo do limite seguro"
            })
        elif current_umidade > 80:
            alerts.append({
                "level": "warning",
                "type": "umidade_alta",
                "message": "Umidade elevada detectada",
                "value": round(current_umidade, 2),
                "threshold": 80,
                "timestamp": datetime.utcnow().isoformat()
            })
            recommendations.append({
                "priority": "medium",
                "action": "Aumentar ventilação do ambiente",
                "reason": f"Umidade atual ({round(current_umidade, 2)}%) acima do ideal"
            })

        # Previsões futuras
        if predictions:
            avg_forecast = sum(predictions) / len(predictions)
            if avg_forecast < 40:
                alerts.append({
                    "level": "warning",
                    "type": "previsao_umidade_baixa",
                    "message": "Previsão indica queda de umidade nos próximos dias",
                    "value": round(avg_forecast, 2),
                    "threshold": 40,
                    "timestamp": datetime.utcnow().isoformat()
                })
                recommendations.append({
                    "priority": "medium",
                    "action": "Planejar aumento de irrigação para os próximos 7 dias",
                    "reason": f"Previsão média de {round(avg_forecast, 2)}% para próxima semana"
                })
            elif avg_forecast > 75:
                alerts.append({
                    "level": "info",
                    "type": "previsao_umidade_alta",
                    "message": "Previsão indica aumento de umidade",
                    "value": round(avg_forecast, 2),
                    "threshold": 75,
                    "timestamp": datetime.utcnow().isoformat()
                })

        # Análise de clusters para recomendações contextuais
        if len(df) >= 3:
            cluster_result = ml.cluster_data(df[["umidade", "ph", "temperatura"]], n_clusters=3)
            centers = cluster_result.get("centers", [])
            clusters = cluster_result.get("clusters", [])

            if clusters:
                current_cluster = clusters[0]
                center = centers[current_cluster]

                recommendations.append({
                    "priority": "low",
                    "action": f"Ambiente classificado no Cluster {current_cluster + 1}",
                    "reason": f"Perfil: Umidade {round(center[0], 1)}%, pH {round(center[1], 1)}, Temp {round(center[2], 1)}°C"
                })

    if not alerts:
        alerts.append({
            "level": "info",
            "type": "status_normal",
            "message": "Todos os parâmetros dentro dos limites esperados",
            "timestamp": datetime.utcnow().isoformat()
        })

    if not recommendations:
        recommendations.append({
            "priority": "low",
            "action": "Manter monitoramento contínuo",
            "reason": "Condições estáveis detectadas"
        })

    return {
        "alerts": alerts,
        "recommendations": recommendations,
        "total_alerts": len([a for a in alerts if a["level"] in ["critical", "warning"]]),
        "timestamp": datetime.utcnow().isoformat()
    }
