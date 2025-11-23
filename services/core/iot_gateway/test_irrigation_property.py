"""
Property-Based Tests for Irrigation Logic
Feature: farmtech-consolidation, Property 9: Irrigation Logic Consistency
"""
import pytest
from hypothesis import given, strategies as st
from .irrigation_logic import apply_irrigation_logic


# **Feature: farmtech-consolidation, Property 9: Irrigation Logic Consistency**
@given(
    umidade=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
    ph=st.floats(min_value=0, max_value=14, allow_nan=False, allow_infinity=False),
    fosforo=st.booleans(),
    potassio=st.booleans()
)
@pytest.mark.property
def test_irrigation_logic_is_deterministic(umidade, ph, fosforo, potassio):
    """
    Property: For any combination of sensor values, irrigation logic
    should return consistent results across multiple calls.
    **Validates: Requirements 5.3**
    """
    # Call twice with same inputs
    result1 = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    result2 = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    
    # Results must be identical (deterministic)
    assert result1 == result2, \
        f"Logic not deterministic for umidade={umidade}, ph={ph}, P={fosforo}, K={potassio}"


@given(
    umidade=st.floats(min_value=0, max_value=14.9, allow_nan=False, allow_infinity=False),
    ph=st.floats(min_value=0, max_value=14, allow_nan=False, allow_infinity=False),
    fosforo=st.booleans(),
    potassio=st.booleans()
)
@pytest.mark.property
def test_emergency_irrigation_always_activates(umidade, ph, fosforo, potassio):
    """
    Property: For any umidade < 15%, bomba must be LIGADA (emergency)
    **Validates: Requirements 5.3 - Priority 1**
    """
    bomba_ligada, decisao = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    
    assert bomba_ligada is True, \
        f"Emergency irrigation failed for umidade={umidade}"
    assert "EMERGÊNCIA" in decisao, \
        f"Emergency message missing for umidade={umidade}"


@given(
    umidade=st.floats(min_value=15, max_value=100, allow_nan=False, allow_infinity=False),
    ph=st.one_of(
        st.floats(min_value=0, max_value=4.4, allow_nan=False, allow_infinity=False),
        st.floats(min_value=7.6, max_value=14, allow_nan=False, allow_infinity=False)
    ),
    fosforo=st.booleans(),
    potassio=st.booleans()
)
@pytest.mark.property
def test_critical_ph_blocks_irrigation(umidade, ph, fosforo, potassio):
    """
    Property: For any pH < 4.5 or > 7.5 (and umidade >= 15%), bomba must be DESLIGADA
    **Validates: Requirements 5.3 - Priority 2**
    """
    bomba_ligada, decisao = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    
    assert bomba_ligada is False, \
        f"Critical pH should block irrigation for pH={ph}"
    assert "CRÍTICO" in decisao, \
        f"Critical pH message missing for pH={ph}"


@given(
    umidade=st.floats(min_value=30.1, max_value=100, allow_nan=False, allow_infinity=False),
    ph=st.floats(min_value=4.5, max_value=7.5, allow_nan=False, allow_infinity=False),
    fosforo=st.booleans(),
    potassio=st.booleans()
)
@pytest.mark.property
def test_high_humidity_stops_irrigation(umidade, ph, fosforo, potassio):
    """
    Property: For any umidade > 30%, bomba must be DESLIGADA
    **Validates: Requirements 5.3 - Priority 4**
    """
    bomba_ligada, decisao = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    
    assert bomba_ligada is False, \
        f"High humidity should stop irrigation for umidade={umidade}"
    assert "alta" in decisao.lower(), \
        f"High humidity message missing for umidade={umidade}"


@given(
    umidade=st.floats(min_value=15, max_value=19.9, allow_nan=False, allow_infinity=False),
    ph=st.floats(min_value=5.5, max_value=6.5, allow_nan=False, allow_infinity=False),
    fosforo=st.booleans(),
    potassio=st.booleans()
)
@pytest.mark.property
def test_optimal_conditions_activate_irrigation(umidade, ph, fosforo, potassio):
    """
    Property: For umidade < 20% and pH 5.5-6.5, bomba must be LIGADA
    **Validates: Requirements 5.3 - Priority 3**
    """
    bomba_ligada, decisao = apply_irrigation_logic(umidade, ph, fosforo, potassio)
    
    assert bomba_ligada is True, \
        f"Optimal conditions should activate irrigation for umidade={umidade}, pH={ph}"
    assert "otimizada" in decisao.lower(), \
        f"Optimal message missing for umidade={umidade}, pH={ph}"


def test_nutrient_modulation():
    """
    Test that nutrient presence modulates irrigation intensity
    **Validates: Requirements 5.3 - Intensity modulation**
    """
    umidade, ph = 18.0, 6.0
    
    # Both nutrients present -> normal intensity
    _, decisao_normal = apply_irrigation_logic(umidade, ph, True, True)
    assert "normal" in decisao_normal
    
    # One nutrient present -> reduced intensity
    _, decisao_reduzida = apply_irrigation_logic(umidade, ph, True, False)
    assert "reduzida" in decisao_reduzida
    
    # No nutrients -> minimal intensity
    _, decisao_minima = apply_irrigation_logic(umidade, ph, False, False)
    assert "mínima" in decisao_minima
