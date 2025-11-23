from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/database", tags=["Database"])

class GenericRecord(BaseModel):
    table: str
    data: Dict[str, Any]

@router.get("/tables")
async def list_tables(request: Request):
    """List available tables"""
    return ["culturas", "talhoes", "tipos_sensor", "sensores", "leituras_sensores", "deteccoes", "producao_agricola", "insumos_cultura"]

@router.get("/data/{table_name}")
async def get_table_data(request: Request, table_name: str, limit: int = 100, offset: int = 0):
    """Get data from a specific table"""
    try:
        # Map table names to models
        from services.core.database.models import (
            Cultura,
            Talhao,
            TipoSensor,
            Sensor,
            LeituraSensor,
            Deteccao,
            ProducaoAgricola,
            InsumoCultura
        )
        
        models_map = {
            "culturas": Cultura,
            "talhoes": Talhao,
            "tipos_sensor": TipoSensor,
            "sensores": Sensor,
            "leituras_sensores": LeituraSensor,
            "deteccoes": Deteccao,
            "producao_agricola": ProducaoAgricola,
            "insumos_cultura": InsumoCultura
        }
        
        if table_name not in models_map:
            raise HTTPException(status_code=404, detail="Table not found")
            
        model = models_map[table_name]
        
        with request.app.state.db.get_session() as session:
            # Get columns
            columns = [c.name for c in model.__table__.columns]
            
            # Get data
            query = session.query(model).limit(limit).offset(offset)
            results = []
            for row in query.all():
                row_dict = {}
                for col in columns:
                    val = getattr(row, col)
                    # Convert dates/datetimes to string
                    if hasattr(val, 'isoformat'):
                        val = val.isoformat()
                    row_dict[col] = val
                results.append(row_dict)
                
            return {
                "columns": columns,
                "data": results,
                "total": session.query(model).count()
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/{table_name}")
async def create_record(request: Request, table_name: str, record: Dict[str, Any]):
    """Create a new record in a table"""
    try:
        from services.core.database.models import Cultura, Talhao, TipoSensor, Sensor
        
        # Only allow creation on simple tables for now to avoid complex FK issues in generic UI
        models_map = {
            "culturas": Cultura,
            "talhoes": Talhao,
            "tipos_sensor": TipoSensor,
            "sensores": Sensor
        }
        
        if table_name not in models_map:
            raise HTTPException(status_code=400, detail="Creation not supported for this table via generic view")
            
        model = models_map[table_name]
        
        with request.app.state.db.get_session() as session:
            new_obj = model(**record)
            session.add(new_obj)
            session.flush()
            return {"status": "success", "id": getattr(new_obj, list(model.__table__.primary_key.columns)[0].name)}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/data/{table_name}/{record_id}")
async def delete_record(request: Request, table_name: str, record_id: int):
    """Delete a record"""
    try:
        from services.core.database.models import Cultura, Talhao, TipoSensor, Sensor, LeituraSensor, Deteccao, ProducaoAgricola, InsumoCultura
        
        models_map = {
            "culturas": Cultura,
            "talhoes": Talhao,
            "tipos_sensor": TipoSensor,
            "sensores": Sensor,
            "leituras_sensores": LeituraSensor,
            "deteccoes": Deteccao,
            "producao_agricola": ProducaoAgricola,
            "insumos_cultura": InsumoCultura
        }
        
        if table_name not in models_map:
            raise HTTPException(status_code=404, detail="Table not found")
            
        model = models_map[table_name]
        pk_name = list(model.__table__.primary_key.columns)[0].name
        
        with request.app.state.db.get_session() as session:
            obj = session.query(model).filter(getattr(model, pk_name) == record_id).first()
            if obj:
                session.delete(obj)
                return {"status": "success"}
            else:
                raise HTTPException(status_code=404, detail="Record not found")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
