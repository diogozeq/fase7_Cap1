"""
Property-based tests for alert triggering
**Feature: farmtech-consolidation, Property 10 & 11: Alert Triggers**
"""
import pytest
from hypothesis import given, strategies as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.core.iot_gateway.service import IoTGatewayService

# **Feature: farmtech-consolidation, Property 10: Emergency Alert Trigger**
# **Validates: Requirements 8.1**
@given(
    umidade=st.floats(min_value=0, max_value=14.9),
    ph=st.floats(min_value=4.5, max_value=7.5)
)
@pytest.mark.property
def test_emergency_alert_triggered_on_low_humidity(umidade, ph):
    """
    Property: For any reading with umidade < 15%, 
    the system should trigger an emergency alert.
    **Validates: Requirements 8.1**
    """
    service = IoTGatewayService(db_service=None, aws_service=None)
    
    alerts = service.check_alerts(umidade, ph, bomba_ligada=True)
    
    # Should have at least one alert
    assert len(alerts) > 0
    # Alert should mention emergency or critical humidity
    assert any("EMERGÊNCIA" in alert or "crítica" in alert for alert in alerts)


# **Feature: farmtech-consolidation, Property 11: Critical pH Alert Trigger**
# **Validates: Requirements 8.2**
@given(
    ph=st.one_of(
        st.floats(min_value=0, max_value=4.4),  # Below critical
        st.floats(min_value=7.6, max_value=14)  # Above critical
    ),
    umidade=st.floats(min_value=15, max_value=100)
)
@pytest.mark.property
def test_critical_ph_alert_triggered(ph, umidade):
    """
    Property: For any reading with pH < 4.5 or pH > 7.5,
    the system should trigger a critical pH alert.
    **Validates: Requirements 8.2**
    """
    service = IoTGatewayService(db_service=None, aws_service=None)
    
    alerts = service.check_alerts(umidade, ph, bomba_ligada=False)
    
    # Should have at least one alert
    assert len(alerts) > 0
    # Alert should mention pH
    assert any("pH" in alert for alert in alerts)


@given(
    umidade=st.floats(min_value=15, max_value=100),
    ph=st.floats(min_value=4.5, max_value=7.5)
)
@pytest.mark.property
def test_no_alerts_on_normal_conditions(umidade, ph):
    """
    Property: For normal conditions (umidade >= 15%, pH 4.5-7.5),
    no alerts should be triggered.
    """
    service = IoTGatewayService(db_service=None, aws_service=None)
    
    alerts = service.check_alerts(umidade, ph, bomba_ligada=False)
    
    # Should have no alerts
    assert len(alerts) == 0


@given(
    umidade=st.floats(min_value=0, max_value=14.9),
    ph=st.one_of(
        st.floats(min_value=0, max_value=4.4),
        st.floats(min_value=7.6, max_value=14)
    )
)
@pytest.mark.property
def test_multiple_alerts_on_multiple_critical_conditions(umidade, ph):
    """
    Property: When multiple critical conditions exist,
    multiple alerts should be triggered.
    """
    service = IoTGatewayService(db_service=None, aws_service=None)
    
    alerts = service.check_alerts(umidade, ph, bomba_ligada=True)
    
    # Should have at least 2 alerts (emergency + pH)
    assert len(alerts) >= 2
