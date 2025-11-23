"""
Pytest configuration and shared fixtures
"""
import pytest
import os
from datetime import datetime


@pytest.fixture(scope="session")
def test_env():
    """Set up test environment"""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["TESTING"] = "true"
    yield
    # Cleanup
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing"""
    return {
        "titulo": "Test Alert",
        "mensagem": "This is a test alert",
        "severidade": "critica",
        "origem": "fase3",
        "message_id": "test-123",
        "data_hora": datetime.utcnow()
    }


@pytest.fixture
def sample_analytics_data():
    """Sample analytics data for testing"""
    return {
        "temperatura": [20, 25, 30],
        "umidade": [60, 70, 80],
        "pressao": [1010, 1012, 1014]
    }


@pytest.fixture
def sample_sensor_data():
    """Sample sensor data for testing"""
    return {
        "umidade": [45.2, 46.1, 47.3, 48.5, 49.2],
        "ph": [6.2, 6.3, 6.4, 6.5, 6.6],
        "temperatura": [22.5, 23.1, 23.8, 24.2, 24.9]
    }


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing"""
    return {
        "temperatura": [18.5, 19.2, 20.1, 21.3, 22.0],
        "umidade": [65, 68, 70, 72, 75],
        "pressao": [1013, 1012, 1011, 1010, 1009],
        "velocidade_vento": [5.2, 6.1, 5.8, 7.2, 6.5]
    }


@pytest.fixture
def alert_severities():
    """Valid alert severities"""
    return ["baixa", "media", "alta", "critica"]


@pytest.fixture
def alert_sources():
    """Valid alert sources"""
    return ["fase1", "fase3", "fase6"]


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "property: mark test as a property-based test"
    )
