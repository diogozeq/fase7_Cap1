"""Property test for area-insumos calculation"""
import pytest
from hypothesis import given, strategies as st
from .area_insumos import calculate_area_insumos

# **Feature: farmtech-consolidation, Property 16: Area-Insumos Calculation Correctness**
@given(
    cultura=st.sampled_from(['Mandioca', 'Cana de Açúcar']),
    area=st.floats(min_value=0.1, max_value=10000, allow_nan=False, allow_infinity=False)
)
@pytest.mark.property
def test_area_insumos_calculation_correctness(cultura, area):
    """
    **Validates: Requirements 35.2, 35.3**
    """
    result = calculate_area_insumos(cultura, area)
    
    if cultura == 'Mandioca':
        expected_insumo = area * 0.05
    else:
        expected_insumo = area * 0.088
    
    assert abs(result['insumo_necessario'] - expected_insumo) < 0.01
