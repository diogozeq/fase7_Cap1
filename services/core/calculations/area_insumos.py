"""
Area and Insumos Calculation - DB-backed with fallback coefficients
"""
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()

# Default coefficients as fallback
DEFAULT_COEFFICIENTS = {
    "Mandioca": {"insumo": 0.05, "custo_por_m2": 4.5},
    "Cana de Açúcar": {"insumo": 0.088, "custo_por_m2": 13.2},
    "Cana de Acucar": {"insumo": 0.088, "custo_por_m2": 13.2},
    "Milho": {"insumo": 0.070, "custo_por_m2": 5.8},
    "Soja": {"insumo": 0.060, "custo_por_m2": 5.0},
    "Café": {"insumo": 0.040, "custo_por_m2": 6.5},
    "Cafe": {"insumo": 0.040, "custo_por_m2": 6.5},
}


def _load_coef_from_db(cultura: str, db_service) -> Optional[Dict]:
    """Try to load coefficients from insumos_cultura table."""
    def _normalize(text: str) -> str:
        mapping = str.maketrans("çáàâãéêíóôõúüÇÁÀÂÃÉÊÍÓÔÕÚÜ", "caaaaeeiooouuCAAAAEEIOOOUU")
        return text.translate(mapping).lower()

    try:
        from services.core.database.models import Cultura, InsumoCultura

        with db_service.get_session() as session:
            cult = (
                session.query(Cultura)
                .filter(Cultura.nome_cultura.ilike(cultura))
                .first()
            )
            if not cult:
                target_norm = _normalize(cultura)
                cult = next(
                    (c for c in session.query(Cultura).all() if _normalize(c.nome_cultura) == target_norm),
                    None,
                )
            if not cult:
                return None
            insumo = (
                session.query(InsumoCultura)
                .filter(InsumoCultura.id_cultura == cult.id_cultura)
                .first()
            )
            if insumo:
                return {
                    "insumo": float(insumo.coef_insumo_por_m2),
                    "custo_por_m2": float(insumo.custo_por_m2),
                }
    except Exception as e:
        logger.warning("load_coef_from_db_failed", error=str(e))
    return None


def calculate_area_insumos(cultura: str, area: float, db_service=None) -> Dict:
    """
    Calculate insumos and costs for given cultura and area.
    Prefer DB coefficients; fallback to defaults.
    """
    coef = None
    if db_service:
        coef = _load_coef_from_db(cultura, db_service)
    if not coef:
        coef = DEFAULT_COEFFICIENTS.get(cultura)

    if not coef:
        raise ValueError(f"Cultura '{cultura}' não suportada")
    if area <= 0:
        raise ValueError("Área deve ser maior que zero")

    insumo = area * coef["insumo"]
    custo = area * coef["custo_por_m2"]

    result = {
        "cultura": cultura,
        "area": area,
        "insumo_necessario": round(insumo, 2),
        "custo_estimado": round(custo, 2),
        "breakdown": {
            "coeficiente_insumo": coef["insumo"],
            "custo_por_m2": coef["custo_por_m2"],
            "fonte": "db" if db_service and coef else "default",
        },
    }

    logger.info("calculation_complete", cultura=cultura, area=area, insumo=insumo)
    return result
