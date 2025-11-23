from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from services.core.calculations.area_insumos import calculate_area_insumos

router = APIRouter(prefix="/calculations", tags=["Fase 1 - Cálculos"])


class CalculationRequest(BaseModel):
    cultura: str
    area: float


@router.post("/insumos")
async def calculate_inputs(request: Request, payload: CalculationRequest):
    try:
        # Map frontend culture names to backend expected names
        culture_map = {
            "milho": "Milho",
            "soja": "Soja",
            "trigo": "Mandioca",  # Fallback
            "mandioca": "Mandioca",
            "cana": "Cana de Acucar",
            "cana de açucar": "Cana de Acucar",
            "cana de acucar": "Cana de Acucar",
        }

        cultura_real = culture_map.get(payload.cultura.lower(), "Mandioca")

        db_service = getattr(request.app.state, "db", None)
        result = calculate_area_insumos(cultura_real, payload.area, db_service=db_service)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/producao-agricola")
async def get_producao_agricola(request: Request, limit: int = 10):
    """Get agricultural production data from Fase 1 CSV"""
    try:
        from services.core.database.models import ProducaoAgricola, Cultura

        with request.app.state.db.get_session() as session:
            # Query production data with culture names
            query = (
                session.query(ProducaoAgricola, Cultura)
                .join(Cultura, ProducaoAgricola.id_cultura == Cultura.id_cultura)
                .order_by(ProducaoAgricola.data_colheita.desc())
                .limit(limit)
            )

            results = []
            for producao, cultura in query.all():
                results.append({
                    "id": producao.id_producao,
                    "cultura": cultura.nome_cultura,
                    "area_plantada": float(producao.area_plantada) if producao.area_plantada else 0,
                    "quantidade_produzida": float(producao.quantidade_produzida) if producao.quantidade_produzida else 0,
                    "valor_estimado": float(producao.valor_estimado) if producao.valor_estimado else 0,
                    "data_colheita": producao.data_colheita.isoformat() if producao.data_colheita else None
                })

            return {
                "total": session.query(ProducaoAgricola).count(),
                "data": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/culturas")
async def get_culturas_with_coefficients(request: Request):
    """Get all cultures with their input coefficients"""
    try:
        from services.core.database.models import Cultura, InsumoCultura

        with request.app.state.db.get_session() as session:
            query = (
                session.query(Cultura, InsumoCultura)
                .outerjoin(InsumoCultura, Cultura.id_cultura == InsumoCultura.id_cultura)
                .all()
            )

            results = []
            for cultura, insumo in query:
                results.append({
                    "id": cultura.id_cultura,
                    "nome": cultura.nome_cultura,
                    "coef_insumo_por_m2": float(insumo.coef_insumo_por_m2) if insumo else None,
                    "custo_por_m2": float(insumo.custo_por_m2) if insumo else None
                })

            return {"culturas": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
