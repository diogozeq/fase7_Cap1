"""
Database seeding script - Populate with initial data
"""
from datetime import datetime, date
from .service import DatabaseService
from .models import Cultura, Talhao, TipoSensor, Sensor, Funcionario
import structlog

logger = structlog.get_logger()


def seed_database(db_service: DatabaseService):
    """Seed database with initial data"""
    logger.info("database_seeding_started")
    
    with db_service.get_session() as session:
        # Check if already seeded
        if session.query(Cultura).count() > 0:
            logger.info("database_already_seeded")
            return
        
        # Seed Culturas
        culturas = [
            Cultura(nome_cultura="Mandioca"),
            Cultura(nome_cultura="Cana de Açúcar"),
            Cultura(nome_cultura="Milho"),
            Cultura(nome_cultura="Soja")
        ]
        session.add_all(culturas)
        session.flush()
        
        # Seed Talhoes
        talhoes = [
            Talhao(nome_talhao="Talhão Norte", area_hectares=10.5, id_cultura_atual=1),
            Talhao(nome_talhao="Talhão Sul", area_hectares=15.2, id_cultura_atual=2),
            Talhao(nome_talhao="Talhão Leste", area_hectares=8.7, id_cultura_atual=None)
        ]
        session.add_all(talhoes)
        session.flush()
        
        # Seed TipoSensor
        tipos_sensor = [
            TipoSensor(nome_tipo_sensor="Umidade", unidade_medida_padrao="%"),
            TipoSensor(nome_tipo_sensor="pH", unidade_medida_padrao="pH"),
            TipoSensor(nome_tipo_sensor="Nutrientes P&K", unidade_medida_padrao="ppm"),
            TipoSensor(nome_tipo_sensor="Temperatura", unidade_medida_padrao="°C")
        ]
        session.add_all(tipos_sensor)
        session.flush()
        
        # Seed Sensores
        sensores = [
            Sensor(
                identificacao_fabricante="DHT22-001",
                data_instalacao=date(2024, 1, 15),
                id_tipo_sensor=1,
                id_talhao=1
            ),
            Sensor(
                identificacao_fabricante="PH-SENSOR-001",
                data_instalacao=date(2024, 1, 15),
                id_tipo_sensor=2,
                id_talhao=1
            ),
            Sensor(
                identificacao_fabricante="DHT22-002",
                data_instalacao=date(2024, 1, 20),
                id_tipo_sensor=1,
                id_talhao=2
            )
        ]
        session.add_all(sensores)
        session.flush()

        # Seed Funcionários (Fase 7)
        funcionarios = [
            Funcionario(
                nome="João Silva",
                email="joao.silva@farmtech.com",
                telefone="+5511999999999",
                cargo="Supervisor de Campo",
                ativo=True,
                recebe_alertas=True,
                recebe_email=True,
                recebe_sms=True,
                alertas_criticos=True,
                alertas_altos=True,
                alertas_medios=True,
                alertas_baixos=False
            ),
            Funcionario(
                nome="Maria Santos",
                email="maria.santos@farmtech.com",
                telefone="+5511888888888",
                cargo="Gerente de Operações",
                ativo=True,
                recebe_alertas=True,
                recebe_email=True,
                recebe_sms=True,
                alertas_criticos=True,
                alertas_altos=True,
                alertas_medios=False,
                alertas_baixos=False
            ),
            Funcionario(
                nome="Pedro Oliveira",
                email="pedro.oliveira@farmtech.com",
                telefone="+5511777777777",
                cargo="Técnico Agrícola",
                ativo=True,
                recebe_alertas=True,
                recebe_email=True,
                recebe_sms=False,
                alertas_criticos=True,
                alertas_altos=True,
                alertas_medios=True,
                alertas_baixos=True
            ),
            Funcionario(
                nome="Ana Costa",
                email="ana.costa@farmtech.com",
                telefone=None,
                cargo="Analista de Dados",
                ativo=True,
                recebe_alertas=True,
                recebe_email=True,
                recebe_sms=False,
                alertas_criticos=False,
                alertas_altos=True,
                alertas_medios=True,
                alertas_baixos=True
            )
        ]
        session.add_all(funcionarios)

        session.commit()

        logger.info("database_seeding_completed",
                   culturas=len(culturas),
                   talhoes=len(talhoes),
                   tipos_sensor=len(tipos_sensor),
                   sensores=len(sensores),
                   funcionarios=len(funcionarios))


if __name__ == "__main__":
    db = DatabaseService()
    db.create_tables()
    seed_database(db)
