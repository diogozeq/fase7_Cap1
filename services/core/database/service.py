"""
Database Service - Encapsulates all database operations
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, OperationalError
from contextlib import contextmanager
from typing import List, Optional, Dict, Any
import structlog

from .models import Base, Cultura, Talhao, TipoSensor, Sensor, LeituraSensor, AjusteAplicacao, Deteccao, Alert, ProducaoAgricola, InsumoCultura, Funcionario

logger = structlog.get_logger()


class DatabaseError(Exception):
    """Custom database error"""
    pass


class DatabaseService:
    """Encapsulates all database operations using SQLAlchemy ORM"""
    
    def __init__(self, connection_string: str | None = None):
        """Initialize database service"""
        import os
        conn = connection_string or os.getenv("DATABASE_URL", "sqlite:///./farmtech.db")
        conn = self._normalize_sqlite_url(conn)
        self.engine = create_engine(
            conn,
            connect_args={"check_same_thread": False} if "sqlite" in conn else {},
            pool_pre_ping=True,
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        logger.info("database_service_initialized", connection=conn)

    def _normalize_sqlite_url(self, conn: str) -> str:
        """Ensure SQLite URLs always point to the real project database."""
        if not conn.startswith("sqlite"):
            return conn

        prefix = "sqlite:///"
        raw_path = conn.replace(prefix, "", 1)
        path_obj = Path(raw_path)

        # Prefer the root database (project root / farmtech.db) when a relative path is provided
        if not path_obj.is_absolute():
            repo_root = Path(__file__).resolve().parents[3]
            candidates = [
                (repo_root / path_obj).resolve(),
                (Path.cwd() / path_obj).resolve()
            ]
            target = next((c for c in candidates if c.exists()), candidates[0])
        else:
            target = path_obj

        normalized = f"{prefix}{target.as_posix()}"
        if target.exists():
            logger.info("database_file_resolved", path=str(target))
        else:
            logger.warning("database_file_missing", attempted_path=str(target))
        return normalized
    
    def create_tables(self):
        """Create all tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("database_tables_created")
        except Exception as e:
            logger.error("database_tables_creation_failed", error=str(e))
            raise DatabaseError(f"Failed to create tables: {str(e)}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Get database session with context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logger.error("integrity_error", error=str(e))
            raise DatabaseError("Violação de integridade: timestamp duplicado ou FK inválida")
        except OperationalError as e:
            session.rollback()
            logger.error("operational_error", error=str(e))
            raise DatabaseError("Erro de operação no banco de dados")
        except Exception as e:
            session.rollback()
            logger.exception("unexpected_db_error", error=str(e))
            raise DatabaseError("Erro inesperado no banco de dados")
        finally:
            session.close()
    
    # CRUD Operations for LeituraSensor
    def create_reading(self, reading_data: Dict[str, Any]) -> int:
        """Insert new sensor reading"""
        with self.get_session() as session:
            reading = LeituraSensor(**reading_data)
            session.add(reading)
            session.flush()
            logger.info("reading_created", reading_id=reading.id_leitura)
            return reading.id_leitura
    
    def get_readings(self, limit: int = 100, offset: int = 0) -> List[LeituraSensor]:
        """Get paginated readings"""
        with self.get_session() as session:
            readings = session.query(LeituraSensor)\
                .order_by(LeituraSensor.data_hora_leitura.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            # Expunge objects from session to avoid DetachedInstanceError
            for reading in readings:
                session.expunge(reading)
            return readings
    
    def get_reading_by_id(self, reading_id: int) -> Optional[LeituraSensor]:
        """Get specific reading"""
        with self.get_session() as session:
            reading = session.query(LeituraSensor)\
                .filter(LeituraSensor.id_leitura == reading_id)\
                .first()
            if reading:
                # Expunge object from session to avoid DetachedInstanceError
                session.expunge(reading)
            return reading
    
    def update_reading(self, reading_id: int, updates: Dict[str, Any]) -> bool:
        """Update reading fields"""
        with self.get_session() as session:
            reading = session.query(LeituraSensor)\
                .filter(LeituraSensor.id_leitura == reading_id)\
                .first()
            if not reading:
                return False
            
            for key, value in updates.items():
                if hasattr(reading, key):
                    setattr(reading, key, value)
            
            logger.info("reading_updated", reading_id=reading_id)
            return True
    
    def delete_reading(self, reading_id: int) -> bool:
        """Delete reading"""
        with self.get_session() as session:
            reading = session.query(LeituraSensor)\
                .filter(LeituraSensor.id_leitura == reading_id)\
                .first()
            if not reading:
                return False
            
            session.delete(reading)
            logger.info("reading_deleted", reading_id=reading_id)
            return True
    
    # Utility methods
    def get_latest_readings(self, limit: int = 10) -> List[LeituraSensor]:
        """Get latest readings"""
        return self.get_readings(limit=limit, offset=0)

    # CRUD Operations for Deteccao
    def create_detection(self, detection_data: Dict[str, Any]) -> int:
        """Insert new detection"""
        with self.get_session() as session:
            detection = Deteccao(**detection_data)
            session.add(detection)
            session.flush()
            logger.info("detection_created", detection_id=detection.id_deteccao)
            return detection.id_deteccao
    
    def get_detections(self, limit: int = 100, offset: int = 0) -> List[Deteccao]:
        """Get paginated detections"""
        with self.get_session() as session:
            detections = session.query(Deteccao)\
                .order_by(Deteccao.timestamp.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            for d in detections:
                session.expunge(d)
            return detections

    def reset_detections(self) -> int:
        """Delete all detections to ensure we only serve real inferences."""
        with self.get_session() as session:
            deleted = session.query(Deteccao).delete()
            logger.info("detections_reset", deleted=deleted)
            return deleted

    def bulk_create_detections(self, detections: List[Dict[str, Any]]) -> int:
        """Insert multiple detections efficiently."""
        with self.get_session() as session:
            objs = [Deteccao(**d) for d in detections]
            session.add_all(objs)
            session.flush()
            logger.info("detections_bulk_created", count=len(objs))
            return len(objs)

    # CRUD Operations for Alert (Fase 7)
    def create_alert(self, alert_data: Dict[str, Any]) -> int:
        """Create a new alert"""
        try:
            with self.get_session() as session:
                alert = Alert(**alert_data)
                session.add(alert)
                session.flush()
                logger.info("alert_created", alert_id=alert.id, titulo=alert.titulo)
                return alert.id
        except IntegrityError as e:
            logger.error("alert_integrity_error", error=str(e))
            raise DatabaseError("Violação de integridade ao criar alerta")
        except Exception as e:
            logger.error("alert_creation_failed", error=str(e))
            raise DatabaseError(f"Falha ao criar alerta: {str(e)}")
    
    def get_alerts(self, limit: int = 20, offset: int = 0) -> List[Alert]:
        """Get recent alerts"""
        try:
            with self.get_session() as session:
                alerts = session.query(Alert)\
                    .order_by(Alert.data_hora.desc())\
                    .limit(limit)\
                    .offset(offset)\
                    .all()
                # Expunge objects from session
                for alert in alerts:
                    session.expunge(alert)
                logger.info("alerts_retrieved", count=len(alerts))
                return alerts
        except Exception as e:
            logger.error("get_alerts_failed", error=str(e))
            return []
    
    def get_alert_by_id(self, alert_id: int) -> Optional[Alert]:
        """Get specific alert"""
        try:
            with self.get_session() as session:
                alert = session.query(Alert)\
                    .filter(Alert.id == alert_id)\
                    .first()
                if alert:
                    session.expunge(alert)
                return alert
        except Exception as e:
            logger.error("get_alert_failed", alert_id=alert_id, error=str(e))
            return None
    
    def get_alerts_by_severity(self, severity: str, limit: int = 20) -> List[Alert]:
        """Get alerts filtered by severity"""
        try:
            with self.get_session() as session:
                alerts = session.query(Alert)\
                    .filter(Alert.severidade == severity)\
                    .order_by(Alert.data_hora.desc())\
                    .limit(limit)\
                    .all()
                for alert in alerts:
                    session.expunge(alert)
                return alerts
        except Exception as e:
            logger.error("get_alerts_by_severity_failed", severity=severity, error=str(e))
            return []
    
    def get_alerts_by_source(self, source: str, limit: int = 20) -> List[Alert]:
        """Get alerts filtered by source"""
        try:
            with self.get_session() as session:
                alerts = session.query(Alert)\
                    .filter(Alert.origem == source)\
                    .order_by(Alert.data_hora.desc())\
                    .limit(limit)\
                    .all()
                for alert in alerts:
                    session.expunge(alert)
                return alerts
        except Exception as e:
            logger.error("get_alerts_by_source_failed", source=source, error=str(e))
            return []
    
    def count_alerts(self) -> int:
        """Count total alerts"""
        try:
            with self.get_session() as session:
                count = session.query(Alert).count()
                logger.info("alerts_counted", count=count)
                return count
        except Exception as e:
            logger.error("count_alerts_failed", error=str(e))
            return 0

    # ========== FUNCIONÁRIOS (FASE 7) ==========

    def create_funcionario(self, funcionario_data: Dict[str, Any]) -> int:
        """Create new funcionario"""
        try:
            with self.get_session() as session:
                funcionario = Funcionario(**funcionario_data)
                session.add(funcionario)
                session.commit()
                session.refresh(funcionario)
                func_id = funcionario.id_funcionario
                logger.info("funcionario_created", id=func_id, nome=funcionario.nome)
                return func_id
        except Exception as e:
            logger.error("create_funcionario_failed", error=str(e))
            raise DatabaseError(f"Failed to create funcionario: {str(e)}")

    def get_funcionarios(self, apenas_ativos: bool = True) -> List[Funcionario]:
        """Get all funcionarios"""
        try:
            with self.get_session() as session:
                query = session.query(Funcionario)
                if apenas_ativos:
                    query = query.filter(Funcionario.ativo == True)
                funcionarios = query.all()
                for func in funcionarios:
                    session.expunge(func)
                logger.info("funcionarios_retrieved", count=len(funcionarios))
                return funcionarios
        except Exception as e:
            logger.error("get_funcionarios_failed", error=str(e))
            return []

    def get_funcionario_by_id(self, funcionario_id: int) -> Optional[Funcionario]:
        """Get funcionario by ID"""
        try:
            with self.get_session() as session:
                funcionario = session.query(Funcionario).filter(Funcionario.id_funcionario == funcionario_id).first()
                if funcionario:
                    session.expunge(funcionario)
                return funcionario
        except Exception as e:
            logger.error("get_funcionario_by_id_failed", id=funcionario_id, error=str(e))
            return None

    def get_funcionarios_for_alert(self, severidade: str) -> List[Funcionario]:
        """
        Get funcionarios that should receive alerts of given severity

        Args:
            severidade: baixa, media, alta, critica

        Returns:
            List of funcionarios configured to receive this severity level
        """
        try:
            with self.get_session() as session:
                query = session.query(Funcionario).filter(
                    Funcionario.ativo == True,
                    Funcionario.recebe_alertas == True
                )

                # Filtrar por nível de severidade
                if severidade == 'critica':
                    query = query.filter(Funcionario.alertas_criticos == True)
                elif severidade == 'alta':
                    query = query.filter(Funcionario.alertas_altos == True)
                elif severidade == 'media':
                    query = query.filter(Funcionario.alertas_medios == True)
                elif severidade == 'baixa':
                    query = query.filter(Funcionario.alertas_baixos == True)

                funcionarios = query.all()
                for func in funcionarios:
                    session.expunge(func)

                logger.info("funcionarios_for_alert_retrieved",
                           severidade=severidade,
                           count=len(funcionarios))
                return funcionarios

        except Exception as e:
            logger.error("get_funcionarios_for_alert_failed",
                        severidade=severidade,
                        error=str(e))
            return []

    def update_funcionario(self, funcionario_id: int, update_data: Dict[str, Any]) -> bool:
        """Update funcionario"""
        try:
            with self.get_session() as session:
                funcionario = session.query(Funcionario).filter(
                    Funcionario.id_funcionario == funcionario_id
                ).first()

                if not funcionario:
                    logger.warning("funcionario_not_found", id=funcionario_id)
                    return False

                for key, value in update_data.items():
                    if hasattr(funcionario, key):
                        setattr(funcionario, key, value)

                session.commit()
                logger.info("funcionario_updated", id=funcionario_id)
                return True

        except Exception as e:
            logger.error("update_funcionario_failed", id=funcionario_id, error=str(e))
            return False

    def delete_funcionario(self, funcionario_id: int) -> bool:
        """Soft delete funcionario (set ativo=False)"""
        try:
            return self.update_funcionario(funcionario_id, {'ativo': False})
        except Exception as e:
            logger.error("delete_funcionario_failed", id=funcionario_id, error=str(e))
            return False
