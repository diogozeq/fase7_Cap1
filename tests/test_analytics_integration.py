"""
Integration tests for Analytics - Fase 1 & 7
Tests R analysis endpoint and full workflow
"""
import pytest
from fastapi.testclient import TestClient
from services.api.main import app
import json


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestAnalyticsEndpoint:
    """Test /api/analytics/r-analysis endpoint"""
    
    def test_r_analysis_endpoint_valid_data(self, client):
        """Test endpoint with valid data"""
        response = client.post(
            "/api/analytics/r-analysis",
            json={"temperatura": [20, 25, 30]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "analysis" in data
        assert data["analysis"]["mean_value"] == 25
    
    def test_r_analysis_endpoint_multiple_fields(self, client):
        """Test endpoint with multiple data fields"""
        response = client.post(
            "/api/analytics/r-analysis",
            json={
                "temperatura": [20, 25, 30],
                "umidade": [60, 70, 80]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["analysis"]["count"] == 6
    
    def test_r_analysis_endpoint_empty_data(self, client):
        """Test endpoint with empty data"""
        response = client.post(
            "/api/analytics/r-analysis",
            json={}
        )
        
        assert response.status_code == 500
    
    def test_r_analysis_endpoint_invalid_json(self, client):
        """Test endpoint with invalid JSON"""
        response = client.post(
            "/api/analytics/r-analysis",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]


class TestAnalyticsWorkflow:
    """Test complete analytics workflow"""
    
    def test_analytics_workflow_weather_data(self, client):
        """Test analytics with weather data"""
        # Simulate weather data from API
        weather_data = {
            "temperatura": [18.5, 19.2, 20.1, 21.3, 22.0],
            "umidade": [65, 68, 70, 72, 75],
            "pressao": [1013, 1012, 1011, 1010, 1009]
        }
        
        response = client.post(
            "/api/analytics/r-analysis",
            json=weather_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["analysis"]["count"] == 15  # 5 values * 3 fields
    
    def test_analytics_workflow_sensor_data(self, client):
        """Test analytics with sensor data"""
        # Simulate sensor readings
        sensor_data = {
            "umidade": [45.2, 46.1, 47.3, 48.5, 49.2],
            "ph": [6.2, 6.3, 6.4, 6.5, 6.6]
        }
        
        response = client.post(
            "/api/analytics/r-analysis",
            json=sensor_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["mean_value"] > 0


class TestAnalyticsErrorHandling:
    """Test error handling in analytics"""
    
    def test_analytics_with_nan_values(self, client):
        """Test analytics handles NaN values"""
        response = client.post(
            "/api/analytics/r-analysis",
            json={"valores": [1, 2, float('nan'), 4, 5]}
        )
        
        # Should handle NaN gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["count"] == 4  # NaN removed
    
    def test_analytics_with_inf_values(self, client):
        """Test analytics handles Inf values"""
        response = client.post(
            "/api/analytics/r-analysis",
            json={"valores": [1, 2, float('inf'), 4, 5]}
        )
        
        # Should handle Inf gracefully
        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["count"] == 4  # Inf removed


class TestAnalyticsPerformance:
    """Test analytics performance"""
    
    def test_analytics_large_dataset(self, client):
        """Test analytics with large dataset"""
        # Create large dataset
        large_data = {
            "valores": list(range(1, 1001))  # 1000 values
        }
        
        response = client.post(
            "/api/analytics/r-analysis",
            json=large_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis"]["count"] == 1000
    
    def test_analytics_response_time(self, client):
        """Test analytics response time"""
        import time
        
        data = {"valores": list(range(1, 101))}
        
        start = time.time()
        response = client.post(
            "/api/analytics/r-analysis",
            json=data
        )
        elapsed = time.time() - start
        
        assert response.status_code == 200
        # Should complete in less than 5 seconds
        assert elapsed < 5.0
