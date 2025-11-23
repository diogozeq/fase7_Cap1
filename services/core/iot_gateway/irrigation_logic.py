"""
Irrigation Logic from Fase 3
Implements the 4-priority decision system
"""
from typing import Tuple
import structlog

logger = structlog.get_logger()


def apply_irrigation_logic(
    umidade: float,
    ph: float,
    fosforo: bool,
    potassio: bool
) -> Tuple[bool, str]:
    """
    Apply irrigation decision logic with 4 priorities
    
    Returns: (bomba_ligada, decisao_logica)
    
    Priority 1: Emergency (umidade < 15%)
    Priority 2: Critical pH (< 4.5 or > 7.5)
    Priority 3: Optimal irrigation (umidade < 20%, pH 5.5-6.5)
    Priority 4: High umidade (> 30%)
    """
    
    # Priority 1: Emergency - Critical low umidade
    if umidade < 15.0:
        decision = "EMERGÊNCIA: Umidade crítica < 15%"
        logger.warning("irrigation_emergency", umidade=umidade, decision=decision)
        return True, decision
    
    # Priority 2: Restrictive - Critical pH
    if ph < 4.5 or ph > 7.5:
        decision = f"pH CRÍTICO: Fora da faixa segura (4.5-7.5), pH={ph:.2f}"
        logger.warning("irrigation_critical_ph", ph=ph, decision=decision)
        return False, decision
    
    # Priority 4: Stop - High umidade
    if umidade > 30.0:
        decision = f"Umidade alta > 30%: Irrigação desnecessária, umidade={umidade:.1f}%"
        logger.info("irrigation_high_humidity", umidade=umidade)
        return False, decision
    
    # Priority 3: Optimal - Low umidade + good pH
    if umidade < 20.0 and 5.5 <= ph <= 6.5:
        # Modulate intensity based on nutrients
        if fosforo and potassio:
            intensity = "normal"
        elif fosforo or potassio:
            intensity = "reduzida"
        else:
            intensity = "mínima"
        
        decision = f"Irrigação otimizada: pH ideal ({ph:.2f}), intensidade {intensity}"
        logger.info("irrigation_optimal", 
                   umidade=umidade, 
                   ph=ph, 
                   intensity=intensity,
                   fosforo=fosforo,
                   potassio=potassio)
        return True, decision
    
    # Default: No irrigation needed
    decision = f"Condições normais: Irrigação não necessária (umidade={umidade:.1f}%, pH={ph:.2f})"
    logger.info("irrigation_normal", umidade=umidade, ph=ph)
    return False, decision
