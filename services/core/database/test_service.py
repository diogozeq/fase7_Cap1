"""
Unit tests for Database Service
"""
import pytest
from datetime import datetime
from .service import DatabaseService, DatabaseError
from .models import Base, LeituraSensor


@pytest.fixture
def db_service():
    """Create test database service"""
    db = DatabaseService("sqlite:///:memory:")
    db.create_tables()
    yield db


@pytest.fixture
def sample_reading_data():
    """Sample reading data"""
    return {
        "data_hora_leitura": datetime.utcnow(),
        "id_sensor": 1,
        "valor_umidade": 25.5,
        "valor_ph": 6.2,
        "valor_fosforo_p": 10.0,
        "valor_potassio_k": 15.0,
        "temperatura": 28.0,
        "bomba_ligada": False,
        "decisao_logica_esp32": "Condições normais"
    }


class TestDatabaseService:
    """Test Database Service CRUD operations"""
    
    def test_create_reading(self, db_service, sample_reading_data):
        """Test creating a reading"""
        reading_id = db_service.create_reading(sample_reading_data)
        assert reading_id is not None
        assert reading_id > 0
    
    def test_get_reading_by_id(self, db_service, sample_reading_data):
        """Test retrieving a reading by ID"""
        reading_id = db_service.create_reading(sample_reading_data)
        reading = db_service.get_reading_by_id(reading_id)
        
        assert reading is not None
        assert reading.id_leitura == reading_id
        assert float(reading.valor_umidade) == 25.5
        assert float(reading.valor_ph) == 6.2
    
    def test_get_readings_pagination(self, db_service, sample_reading_data):
        """Test paginated readings"""
        # Create multiple readings
        for i in range(5):
            data = sample_reading_data.copy()
            data["data_hora_leitura"] = datetime.utcnow()
            data["valor_umidade"] = 20.0 + i
            db_service.create_reading(data)
        
        readings = db_service.get_readings(limit=3, offset=0)
        assert len(readings) == 3
    
    def test_update_reading(self, db_service, sample_reading_data):
        """Test updating a reading"""
        reading_id = db_service.create_reading(sample_reading_data)
        
        updates = {"valor_ph": 7.0}
        success = db_service.update_reading(reading_id, updates)
        
        assert success is True
        
        updated_reading = db_service.get_reading_by_id(reading_id)
        assert updated_reading.valor_ph == 7.0
    
    def test_delete_reading(self, db_service, sample_reading_data):
        """Test deleting a reading"""
        reading_id = db_service.create_reading(sample_reading_data)
        
        success = db_service.delete_reading(reading_id)
        assert success is True
        
        deleted_reading = db_service.get_reading_by_id(reading_id)
        assert deleted_reading is None
    
    def test_count_readings(self, db_service, sample_reading_data):
        """Test counting readings"""
        initial_count = db_service.count_readings()
        
        db_service.create_reading(sample_reading_data)
        
        new_count = db_service.count_readings()
        assert new_count == initial_count + 1
    
    def test_integrity_error_duplicate_timestamp(self, db_service, sample_reading_data):
        """Test that duplicate timestamps raise error"""
        db_service.create_reading(sample_reading_data)
        
        # Try to create with same timestamp
        with pytest.raises(DatabaseError, match="integridade"):
            db_service.create_reading(sample_reading_data)
