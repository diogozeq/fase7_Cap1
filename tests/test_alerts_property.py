"""
Property-Based Tests for Alerts - Fase 7
Tests correctness properties using Hypothesis
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from services.core.database.service import DatabaseService
from services.core.database.models import Base, Alert


@pytest.fixture
def db():
    """Create in-memory database for testing"""
    db = DatabaseService("sqlite:///:memory:")
    Base.metadata.create_all(db.engine)
    return db


class TestAlertsProperties:
    """Property-based tests for alerts"""
    
    @given(
        titulo=st.text(min_size=1, max_size=200),
        mensagem=st.text(min_size=1, max_size=1000),
        severidade=st.sampled_from(["baixa", "media", "alta", "critica"]),
        origem=st.sampled_from(["fase1", "fase3", "fase6"])
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_4_round_trip(self, db, titulo, mensagem, severidade, origem):
        """Property 4: Round-Trip de Alertas
        
        For any alert created, retrieving it should return identical data
        **Validates: Requirements 2.1, 2.4**
        """
        alert_data = {
            "titulo": titulo,
            "mensagem": mensagem,
            "severidade": severidade,
            "origem": origem,
            "data_hora": datetime.utcnow()
        }
        
        # Create alert
        alert_id = db.create_alert(alert_data)
        
        # Retrieve alert
        alert = db.get_alert_by_id(alert_id)
        
        # Verify data matches
        assert alert.titulo == titulo
        assert alert.mensagem == mensagem
        assert alert.severidade == severidade
        assert alert.origem == origem
    
    @given(st.lists(
        st.tuples(
            st.text(min_size=1, max_size=200),
            st.text(min_size=1, max_size=1000),
            st.sampled_from(["baixa", "media", "alta", "critica"]),
            st.sampled_from(["fase1", "fase3", "fase6"])
        ),
        min_size=1,
        max_size=20
    ))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_5_ordering(self, db, alert_tuples):
        """Property 5: Ordem de Alertas
        
        For any set of alerts, retrieving them should return in timestamp DESC order
        **Validates: Requirements 2.2, 2.5**
        """
        import time
        
        # Create alerts
        alert_ids = []
        for titulo, mensagem, severidade, origem in alert_tuples:
            alert_data = {
                "titulo": titulo,
                "mensagem": mensagem,
                "severidade": severidade,
                "origem": origem,
                "data_hora": datetime.utcnow()
            }
            alert_id = db.create_alert(alert_data)
            alert_ids.append(alert_id)
            time.sleep(0.001)  # Small delay to ensure different timestamps
        
        # Retrieve alerts
        alerts = db.get_alerts(limit=len(alert_tuples))
        
        # Should be in reverse order (newest first)
        retrieved_ids = [a.id for a in alerts]
        assert retrieved_ids == list(reversed(alert_ids))
    
    @given(
        titulo=st.text(min_size=1, max_size=200),
        mensagem=st.text(min_size=1, max_size=1000),
        severidade=st.sampled_from(["baixa", "media", "alta", "critica"]),
        origem=st.sampled_from(["fase1", "fase3", "fase6"]),
        message_id=st.one_of(st.none(), st.text(min_size=1, max_size=100))
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_property_8_metadata(self, db, titulo, mensagem, severidade, origem, message_id):
        """Property 8: Rastreabilidade de Alertas
        
        For any alert, all metadata should be present
        **Validates: Requirements 6.1, 6.2, 6.3**
        """
        alert_data = {
            "titulo": titulo,
            "mensagem": mensagem,
            "severidade": severidade,
            "origem": origem,
            "message_id": message_id,
            "data_hora": datetime.utcnow()
        }
        
        # Create alert
        alert_id = db.create_alert(alert_data)
        
        # Retrieve alert
        alert = db.get_alert_by_id(alert_id)
        
        # Verify all metadata is present
        assert alert.id is not None
        assert alert.titulo is not None
        assert alert.mensagem is not None
        assert alert.severidade is not None
        assert alert.origem is not None
        assert alert.data_hora is not None
        # message_id can be None
        if message_id is not None:
            assert alert.message_id == message_id


class TestAlertsSeverityFiltering:
    """Property-based tests for severity filtering"""
    
    @given(
        severidade=st.sampled_from(["baixa", "media", "alta", "critica"]),
        count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_severity_filter(self, db, severidade, count):
        """Property: Severity filtering returns only matching alerts
        
        For any severity, filtering should return only alerts with that severity
        """
        # Create alerts with different severities
        for i in range(count):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": severidade,
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Filter by severity
        alerts = db.get_alerts_by_severity(severidade)
        
        # All should have matching severity
        for alert in alerts:
            assert alert.severidade == severidade


class TestAlertsSourceFiltering:
    """Property-based tests for source filtering"""
    
    @given(
        origem=st.sampled_from(["fase1", "fase3", "fase6"]),
        count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_source_filter(self, db, origem, count):
        """Property: Source filtering returns only matching alerts
        
        For any source, filtering should return only alerts from that source
        """
        # Create alerts from different sources
        for i in range(count):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": origem,
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Filter by source
        alerts = db.get_alerts_by_source(origem)
        
        # All should have matching source
        for alert in alerts:
            assert alert.origem == origem


class TestAlertsPagination:
    """Property-based tests for pagination"""
    
    @given(
        total_count=st.integers(min_value=10, max_value=50),
        limit=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_pagination(self, db, total_count, limit):
        """Property: Pagination returns correct number of items
        
        For any limit, pagination should return at most limit items
        """
        # Create alerts
        for i in range(total_count):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Get first page
        alerts = db.get_alerts(limit=limit, offset=0)
        
        # Should return at most limit items
        assert len(alerts) <= limit
        
        # If total > limit, should return exactly limit
        if total_count >= limit:
            assert len(alerts) == limit


class TestAlertsCount:
    """Property-based tests for alert counting"""
    
    @given(count=st.integers(min_value=0, max_value=50))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_property_count_matches_created(self, db, count):
        """Property: Count matches number of created alerts
        
        For any number of created alerts, count should match
        """
        # Create alerts
        for i in range(count):
            alert_data = {
                "titulo": f"Alert {i}",
                "mensagem": f"Message {i}",
                "severidade": "media",
                "origem": "fase3",
                "data_hora": datetime.utcnow()
            }
            db.create_alert(alert_data)
        
        # Count should match
        total_count = db.count_alerts()
        assert total_count == count
