"""
Unit tests for Alerts - Fase 7
Tests alert creation, persistence, and retrieval
"""
import pytest
from datetime import datetime
from services.core.database.service import DatabaseService
from services.core.database.models import Base, Alert


@pytest.fixture
def db():
    """Create in-memory database for testing"""
    db = DatabaseService("sqlite:///:memory:")
    Base.metadata.create_all(db.engine)
    return db


class TestAlertCreation:
    """Test alert creation"""
    
    def test_create_alert(self, db):
        """Test creating an alert"""
        alert_data = {
            "titulo": "Test Alert",
            "mensagem": "This is a test alert",
            "severidade": "critica",
            "origem": "fase3",
            "data_hora": datetime.utcnow()
        }
        alert_id = db.create_alert(alert_data)
        
        assert alert_id > 0
    
    def test_create_alert_with_message_id(self, db):
        """Test creating alert with SNS message ID"""
        alert_data = {
            "titulo": "SNS Alert",
            "mensagem": "Alert sent via SNS",
            "severidade": "alta",
            "origem": "fase3",
            "message_id": "sns-12345",
            "data_hora": datetime.utcnow()
        }
        alert_id = db.create_alert(alert_data)
        
        alert = db.get_alert_by_id(alert_id)
        assert alert.message_id == "sns-12345"
    
    def test_create_multiple_alerts(self, db):
        """Test creating multiple alerts"""
        for i in range(5):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        alerts = db.get_alerts(limit=10)
        assert len(alerts) == 5


class TestAlertRetrieval:
    """Test alert retrieval"""
    
    def test_get_alerts(self, db):
        """Test retrieving alerts"""
        # Create test alerts
        for i in range(3):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        alerts = db.get_alerts(limit=10)
        assert len(alerts) == 3
    
    def test_get_alerts_ordering(self, db):
        """Test alerts are ordered by timestamp DESC (Property 5)"""
        import time
        
        # Create alerts with slight delays
        alert_ids = []
        for i in range(3):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            alert_id = db.create_alert(alert_data)
            alert_ids.append(alert_id)
            time.sleep(0.01)
        
        alerts = db.get_alerts(limit=10)
        
        # Should be in reverse order (newest first)
        assert alerts[0].id == alert_ids[2]
        assert alerts[1].id == alert_ids[1]
        assert alerts[2].id == alert_ids[0]
    
    def test_get_alert_by_id(self, db):
        """Test retrieving specific alert"""
        alert_data = {
            "titulo": "Specific Alert",
            "mensagem": "Find me",
            "severidade": "alta",
            "origem": "fase3",
            "data_hora": datetime.utcnow()
        }
        alert_id = db.create_alert(alert_data)
        
        alert = db.get_alert_by_id(alert_id)
        assert alert is not None
        assert alert.titulo == "Specific Alert"
    
    def test_get_alerts_pagination(self, db):
        """Test alert pagination"""
        # Create 25 alerts
        for i in range(25):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Get first page (limit 10)
        page1 = db.get_alerts(limit=10, offset=0)
        assert len(page1) == 10
        
        # Get second page
        page2 = db.get_alerts(limit=10, offset=10)
        assert len(page2) == 10
        
        # Get third page
        page3 = db.get_alerts(limit=10, offset=20)
        assert len(page3) == 5


class TestAlertFiltering:
    """Test alert filtering"""
    
    def test_get_alerts_by_severity(self, db):
        """Test filtering alerts by severity"""
        # Create alerts with different severities
        severities = ["baixa", "media", "alta", "critica"]
        for severity in severities:
            alert_data = {
                "titulo": f"Alert {severity}",
                "mensagem": f"Message {severity}",
                "severidade": severity,
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Filter by severity
        critica_alerts = db.get_alerts_by_severity("critica")
        assert len(critica_alerts) == 1
        assert critica_alerts[0].severidade == "critica"
    
    def test_get_alerts_by_source(self, db):
        """Test filtering alerts by source"""
        # Create alerts from different sources
        sources = ["fase1", "fase3", "fase6"]
        for source in sources:
            alert_data = {
                "titulo": f"Alert {source}",
                "mensagem": f"Message {source}",
                "severidade": "media",
                "origem": source,
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Filter by source
        fase3_alerts = db.get_alerts_by_source("fase3")
        assert len(fase3_alerts) == 1
        assert fase3_alerts[0].origem == "fase3"


class TestAlertRoundTrip:
    """Test alert round-trip (Property 4)"""
    
    def test_alert_round_trip(self, db):
        """Test creating and retrieving alert returns identical data"""
        original_data = {
            "titulo": "Round Trip Alert",
            "mensagem": "Test round trip",
            "severidade": "alta",
            "origem": "fase3",
            "message_id": "msg-123",
            "data_hora": datetime.utcnow()
        }
        
        # Create alert
        alert_id = db.create_alert(original_data)
        
        # Retrieve alert
        alert = db.get_alert_by_id(alert_id)
        
        # Verify data matches
        assert alert.titulo == original_data["titulo"]
        assert alert.mensagem == original_data["mensagem"]
        assert alert.severidade == original_data["severidade"]
        assert alert.origem == original_data["origem"]
        assert alert.message_id == original_data["message_id"]


class TestAlertMetadata:
    """Test alert metadata (Property 8)"""
    
    def test_alert_has_all_metadata(self, db):
        """Test alert contains all required metadata"""
        alert_data = {
            "titulo": "Metadata Alert",
            "mensagem": "Test metadata",
            "severidade": "critica",
            "origem": "fase3",
            "message_id": "sns-456",
            "data_hora": datetime.utcnow()
        }
        
        alert_id = db.create_alert(alert_data)
        alert = db.get_alert_by_id(alert_id)
        
        # Verify all metadata is present
        assert alert.id is not None
        assert alert.titulo is not None
        assert alert.mensagem is not None
        assert alert.severidade is not None
        assert alert.origem is not None
        assert alert.message_id is not None
        assert alert.data_hora is not None


class TestAlertCounting:
    """Test alert counting"""
    
    def test_count_alerts(self, db):
        """Test counting total alerts"""
        # Create 5 alerts
        for i in range(5):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        count = db.count_alerts()
        assert count == 5
