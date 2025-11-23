"""
Unit tests for Analytics Service - Fase 1 & 7
Tests R analysis functionality with robust error handling
"""
import pytest
from services.core.analytics.service import AnalyticsService
import json


@pytest.fixture
def analytics():
    """Create AnalyticsService instance"""
    return AnalyticsService()


class TestRAnalysisValidData:
    """Test R analysis with valid data"""
    
    def test_r_analysis_single_value(self, analytics):
        """Test R analysis with single value"""
        data = {"temperatura": [25]}
        result = analytics.run_r_analysis(data)
        
        assert result["mean_value"] == 25
        assert result["median_value"] == 25
        assert result["count"] == 1
        assert "timestamp" in result
    
    def test_r_analysis_multiple_values(self, analytics):
        """Test R analysis with multiple values"""
        data = {"temperatura": [20, 25, 30]}
        result = analytics.run_r_analysis(data)
        
        assert result["mean_value"] == 25
        assert result["median_value"] == 25
        assert result["count"] == 3
        assert result["min_value"] == 20
        assert result["max_value"] == 30
    
    def test_r_analysis_with_decimals(self, analytics):
        """Test R analysis with decimal values"""
        data = {"umidade": [60.5, 70.3, 80.1]}
        result = analytics.run_r_analysis(data)
        
        assert result["count"] == 3
        assert result["min_value"] == 60.5
        assert result["max_value"] == 80.1
    
    def test_r_analysis_deterministic(self, analytics):
        """Test that R analysis is deterministic (Property 1)"""
        data = {"temperatura": [20, 25, 30]}
        
        result1 = analytics.run_r_analysis(data)
        result2 = analytics.run_r_analysis(data)
        
        # Compare all numeric values
        assert result1["mean_value"] == result2["mean_value"]
        assert result1["median_value"] == result2["median_value"]
        assert result1["count"] == result2["count"]


class TestRAnalysisInvalidData:
    """Test R analysis with invalid data"""
    
    def test_r_analysis_empty_array(self, analytics):
        """Test R analysis rejects empty array"""
        data = {"temperatura": []}
        
        with pytest.raises(Exception):
            analytics.run_r_analysis(data)
    
    def test_r_analysis_empty_dict(self, analytics):
        """Test R analysis rejects empty dictionary"""
        data = {}
        
        with pytest.raises(ValueError):
            analytics.run_r_analysis(data)
    
    def test_r_analysis_none_input(self, analytics):
        """Test R analysis rejects None input"""
        with pytest.raises(ValueError):
            analytics.run_r_analysis(None)
    
    def test_r_analysis_nan_values(self, analytics):
        """Test R analysis handles NaN values"""
        data = {"temperatura": [20, float('nan'), 30]}
        result = analytics.run_r_analysis(data)
        
        # NaN values should be removed
        assert result["count"] == 2
        assert result["mean_value"] == 25
    
    def test_r_analysis_inf_values(self, analytics):
        """Test R analysis handles Inf values"""
        data = {"temperatura": [20, float('inf'), 30]}
        result = analytics.run_r_analysis(data)
        
        # Inf values should be removed
        assert result["count"] == 2
        assert result["mean_value"] == 25
    
    def test_r_analysis_all_nan(self, analytics):
        """Test R analysis rejects all NaN values"""
        data = {"temperatura": [float('nan'), float('nan')]}
        
        with pytest.raises(Exception):
            analytics.run_r_analysis(data)


class TestRAnalysisStatistics:
    """Test R analysis statistics calculations"""
    
    def test_r_analysis_standard_deviation(self, analytics):
        """Test standard deviation calculation"""
        data = {"valores": [1, 2, 3, 4, 5]}
        result = analytics.run_r_analysis(data)
        
        # SD of [1,2,3,4,5] should be ~1.58
        assert 1.5 < result["sd_value"] < 1.7
    
    def test_r_analysis_median_odd_count(self, analytics):
        """Test median with odd number of values"""
        data = {"valores": [1, 2, 3, 4, 5]}
        result = analytics.run_r_analysis(data)
        
        assert result["median_value"] == 3
    
    def test_r_analysis_median_even_count(self, analytics):
        """Test median with even number of values"""
        data = {"valores": [1, 2, 3, 4]}
        result = analytics.run_r_analysis(data)
        
        assert result["median_value"] == 2.5


class TestRAnalysisOutput:
    """Test R analysis output format"""
    
    def test_r_analysis_output_structure(self, analytics):
        """Test output has required fields"""
        data = {"temperatura": [20, 25, 30]}
        result = analytics.run_r_analysis(data)
        
        required_fields = ["mean_value", "median_value", "sd_value", "min_value", "max_value", "count", "timestamp"]
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_r_analysis_output_types(self, analytics):
        """Test output field types"""
        data = {"temperatura": [20, 25, 30]}
        result = analytics.run_r_analysis(data)
        
        assert isinstance(result["mean_value"], (int, float))
        assert isinstance(result["median_value"], (int, float))
        assert isinstance(result["count"], int)
        assert isinstance(result["timestamp"], str)
    
    def test_r_analysis_timestamp_format(self, analytics):
        """Test timestamp is in ISO format"""
        data = {"temperatura": [20, 25, 30]}
        result = analytics.run_r_analysis(data)
        
        # Should be ISO format: YYYY-MM-DDTHH:MM:SSZ
        assert "T" in result["timestamp"]
        assert "Z" in result["timestamp"]


class TestRAnalysisEdgeCases:
    """Test R analysis edge cases"""
    
    def test_r_analysis_negative_values(self, analytics):
        """Test R analysis with negative values"""
        data = {"temperatura": [-10, -5, 0, 5, 10]}
        result = analytics.run_r_analysis(data)
        
        assert result["mean_value"] == 0
        assert result["min_value"] == -10
        assert result["max_value"] == 10
    
    def test_r_analysis_large_values(self, analytics):
        """Test R analysis with large values"""
        data = {"valores": [1000000, 2000000, 3000000]}
        result = analytics.run_r_analysis(data)
        
        assert result["mean_value"] == 2000000
        assert result["count"] == 3
    
    def test_r_analysis_very_small_values(self, analytics):
        """Test R analysis with very small values"""
        data = {"valores": [0.001, 0.002, 0.003]}
        result = analytics.run_r_analysis(data)
        
        assert result["count"] == 3
        assert 0.001 < result["mean_value"] < 0.003
    
    def test_r_analysis_mixed_types(self, analytics):
        """Test R analysis with mixed numeric types"""
        data = {"valores": [1, 2.5, 3, 4.5, 5]}
        result = analytics.run_r_analysis(data)
        
        assert result["count"] == 5
        assert result["mean_value"] == 3.2


class TestRAnalysisMultipleFields:
    """Test R analysis with multiple data fields"""
    
    def test_r_analysis_multiple_fields(self, analytics):
        """Test R analysis combines multiple fields"""
        data = {
            "temperatura": [20, 25, 30],
            "umidade": [60, 70, 80]
        }
        result = analytics.run_r_analysis(data)
        
        # Should combine all values
        assert result["count"] == 6
        assert result["mean_value"] == 47.5  # (20+25+30+60+70+80)/6
