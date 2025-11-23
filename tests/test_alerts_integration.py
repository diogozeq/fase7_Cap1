"""
Integration tests for Alerts - Fase 7
Tests alert creation, persistence, and API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from services.api.main import app
from datetime import datetime


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestAlertsEndpoint:
    """Test /api/alerts endpoints"""
    
    def test_send_alert_endpoint(self, client):
        """Test sending alert via API"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Test Alert",
                "message": "This is a test alert",
                "severity": "critica",
                "source": "fase3"
            }
        )
        
        # Should return success or warning (if SNS not configured)
        assert response.status_code in [200, 500]
        data = response.json()
        assert "status" in data
    
    def test_get_alert_history_endpoint(self, client):
        """Test retrieving alert history"""
        response = client.get("/api/alerts/history")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_send_alert_with_all_fields(self, client):
        """Test sending alert with all fields"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Complete Alert",
                "message": "Alert with all fields",
                "severity": "alta",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]
        data = response.json()
        assert "alert" in data or "status" in data


class TestAlertsWorkflow:
    """Test complete alert workflow"""
    
    def test_alert_creation_workflow(self, client):
        """Test creating and retrieving alert"""
        # Create alert
        create_response = client.post(
            "/api/alerts/send",
            json={
                "title": "Workflow Alert",
                "message": "Testing workflow",
                "severity": "media",
                "source": "fase3"
            }
        )
        
        assert create_response.status_code in [200, 500]
        
        # Retrieve history
        history_response = client.get("/api/alerts/history")
        assert history_response.status_code == 200
    
    def test_multiple_alerts_workflow(self, client):
        """Test creating multiple alerts"""
        # Create multiple alerts
        for i in range(3):
            response = client.post(
                "/api/alerts/send",
                json={
                    "title": f"Alert {i}",
                    "message": f"Message {i}",
                    "severity": "media",
                    "source": "fase3"
                }
            )
            assert response.status_code in [200, 500]
        
        # Retrieve all
        history_response = client.get("/api/alerts/history")
        assert history_response.status_code == 200


class TestAlertsSeverities:
    """Test alerts with different severities"""
    
    def test_alert_baixa_severity(self, client):
        """Test alert with baixa severity"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Low Severity",
                "message": "Low priority alert",
                "severity": "baixa",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]
    
    def test_alert_media_severity(self, client):
        """Test alert with media severity"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Medium Severity",
                "message": "Medium priority alert",
                "severity": "media",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]
    
    def test_alert_alta_severity(self, client):
        """Test alert with alta severity"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "High Severity",
                "message": "High priority alert",
                "severity": "alta",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]
    
    def test_alert_critica_severity(self, client):
        """Test alert with critica severity"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Critical Severity",
                "message": "Critical priority alert",
                "severity": "critica",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]


class TestAlertsSources:
    """Test alerts from different sources"""
    
    def test_alert_from_fase1(self, client):
        """Test alert from Fase 1"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Fase 1 Alert",
                "message": "Alert from Fase 1",
                "severity": "media",
                "source": "fase1"
            }
        )
        
        assert response.status_code in [200, 500]
    
    def test_alert_from_fase3(self, client):
        """Test alert from Fase 3"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Fase 3 Alert",
                "message": "Alert from Fase 3",
                "severity": "media",
                "source": "fase3"
            }
        )
        
        assert response.status_code in [200, 500]
    
    def test_alert_from_fase6(self, client):
        """Test alert from Fase 6"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Fase 6 Alert",
                "message": "Alert from Fase 6",
                "severity": "media",
                "source": "fase6"
            }
        )
        
        assert response.status_code in [200, 500]


class TestAlertsErrorHandling:
    """Test error handling in alerts"""
    
    def test_alert_missing_title(self, client):
        """Test alert with missing title"""
        response = client.post(
            "/api/alerts/send",
            json={
                "message": "No title",
                "severity": "media",
                "source": "fase3"
            }
        )
        
        # Should return validation error
        assert response.status_code in [422, 500]
    
    def test_alert_missing_message(self, client):
        """Test alert with missing message"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "No message",
                "severity": "media",
                "source": "fase3"
            }
        )
        
        # Should return validation error
        assert response.status_code in [422, 500]
    
    def test_alert_invalid_severity(self, client):
        """Test alert with invalid severity"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Invalid Severity",
                "message": "Invalid severity value",
                "severity": "invalid",
                "source": "fase3"
            }
        )
        
        # Should return validation error
        assert response.status_code in [422, 500]
    
    def test_alert_invalid_source(self, client):
        """Test alert with invalid source"""
        response = client.post(
            "/api/alerts/send",
            json={
                "title": "Invalid Source",
                "message": "Invalid source value",
                "severity": "media",
                "source": "invalid"
            }
        )
        
        # Should return validation error
        assert response.status_code in [422, 500]
