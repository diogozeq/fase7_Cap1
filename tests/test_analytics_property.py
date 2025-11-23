"""
Property-Based Tests for Analytics - Fase 1 & 7
Tests correctness properties using Hypothesis
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from services.core.analytics.service import AnalyticsService
import math


@pytest.fixture
def analytics():
    """Create AnalyticsService instance"""
    return AnalyticsService()


class TestAnalyticsProperties:
    """Property-based tests for analytics"""
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_1_deterministic(self, analytics, values):
        """Property 1: Análise R Determinística
        
        For any valid dataset, running analysis twice should produce identical results
        **Validates: Requirements 1.1, 1.4**
        """
        data = {"valores": values}
        
        result1 = analytics.run_r_analysis(data)
        result2 = analytics.run_r_analysis(data)
        
        # Results should be identical
        assert result1["mean_value"] == result2["mean_value"]
        assert result1["median_value"] == result2["median_value"]
        assert result1["count"] == result2["count"]
        assert result1["min_value"] == result2["min_value"]
        assert result1["max_value"] == result2["max_value"]
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_mean_in_range(self, analytics, values):
        """Property: Mean is within min and max
        
        For any valid dataset, mean should be between min and max
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Mean should be between min and max
        assert result["min_value"] <= result["mean_value"] <= result["max_value"]
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_count_matches_length(self, analytics, values):
        """Property: Count matches input length
        
        For any valid dataset, count should equal number of values
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Count should match input length
        assert result["count"] == len(values)
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_min_max_correct(self, analytics, values):
        """Property: Min and max are correct
        
        For any valid dataset, min and max should match actual values
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Min and max should match
        assert result["min_value"] == min(values)
        assert result["max_value"] == max(values)
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_mean_calculation(self, analytics, values):
        """Property: Mean calculation is correct
        
        For any valid dataset, mean should equal sum/count
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        expected_mean = sum(values) / len(values)
        # Allow small floating point error
        assert abs(result["mean_value"] - expected_mean) < 1e-6
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=2,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_std_dev_non_negative(self, analytics, values):
        """Property: Standard deviation is non-negative
        
        For any valid dataset, std dev should be >= 0
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Std dev should be non-negative
        assert result["sd_value"] >= 0
    
    @given(st.lists(
        st.floats(
            min_value=-1e6,
            max_value=1e6,
            allow_nan=False,
            allow_infinity=False
        ),
        min_size=1,
        max_size=1000
    ))
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_output_has_timestamp(self, analytics, values):
        """Property: Output always has timestamp
        
        For any valid dataset, result should include timestamp
        """
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Should have timestamp
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)
        assert "T" in result["timestamp"]
        assert "Z" in result["timestamp"]


class TestAnalyticsInputValidation:
    """Property-based tests for input validation"""
    
    @given(st.just([]))
    def test_property_6_empty_array_rejected(self, analytics):
        """Property 6: Validação de Entrada R
        
        For empty array, system should reject with error
        **Validates: Requirements 1.3, 5.1**
        """
        data = {"valores": []}
        
        with pytest.raises(Exception):
            analytics.run_r_analysis(data)
    
    @given(st.just(None))
    def test_property_none_rejected(self, analytics):
        """Property: None input rejected
        
        For None input, system should reject with error
        """
        with pytest.raises(ValueError):
            analytics.run_r_analysis(None)
    
    @given(st.just({}))
    def test_property_empty_dict_rejected(self, analytics):
        """Property: Empty dict rejected
        
        For empty dictionary, system should reject with error
        """
        with pytest.raises(ValueError):
            analytics.run_r_analysis({})


class TestAnalyticsNaNHandling:
    """Property-based tests for NaN handling"""
    
    @given(st.lists(
        st.one_of(
            st.floats(
                min_value=-1e6,
                max_value=1e6,
                allow_nan=False,
                allow_infinity=False
            ),
            st.just(float('nan'))
        ),
        min_size=2,
        max_size=100
    ))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_nan_removed(self, analytics, values):
        """Property: NaN values are removed
        
        For dataset with NaN, NaN should be removed before analysis
        """
        # Only test if there's at least one non-NaN value
        non_nan_values = [v for v in values if not math.isnan(v)]
        if len(non_nan_values) == 0:
            pytest.skip("No non-NaN values")
        
        data = {"valores": values}
        result = analytics.run_r_analysis(data)
        
        # Count should match non-NaN values
        assert result["count"] == len(non_nan_values)
