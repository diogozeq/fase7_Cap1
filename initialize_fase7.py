"""
Script de Inicialização - Fase 7
Cria banco de dados, tabelas e dados iniciais
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.core.database.service import DatabaseService
from services.core.database.models import Base, Cultura, Talhao, TipoSensor, Sensor, Funcionario
from datetime import datetime, date
import structlog

logger = structlog.get_logger()


def initialize_database():
    """Initialize database with tables and seed data"""
    print("=" * 60)
    print("FASE 7 - Inicializacao do Banco de Dados")
    print("=" * 60)
    print()

    # Create database service
    db = DatabaseService()

    # Create all tables
    print("[*] Criando tabelas...")
    db.create_tables()
    print("[OK] Tabelas criadas com sucesso!")
    print()

    # Check if already seeded
    with db.get_session() as session:
        existing_culturas = session.query(Cultura).count()
        if existing_culturas > 0:
            print("[!] Banco de dados ja possui dados.")
            print("[OK] Mantendo dados existentes.")
            print()
            return

    print("[*] Inserindo dados iniciais...")

    with db.get_session() as session:
        # Seed Culturas
        culturas = [
            Cultura(nome_cultura="Mandioca"),
            Cultura(nome_cultura="Cana de Açúcar"),
            Cultura(nome_cultura="Milho"),
            Cultura(nome_cultura="Soja")
        ]
        session.add_all(culturas)
        session.flush()
        print(f"  [OK] {len(culturas)} culturas")

        # Seed Talhoes
        talhoes = [
            Talhao(nome_talhao="Talhao Norte", area_hectares=10.5, id_cultura_atual=1),
            Talhao(nome_talhao="Talhao Sul", area_hectares=15.2, id_cultura_atual=2),
            Talhao(nome_talhao="Talhao Leste", area_hectares=8.7, id_cultura_atual=None)
        ]
        session.add_all(talhoes)
        session.flush()
        print(f"  [OK] {len(talhoes)} talhoes")

        # Seed TipoSensor
        tipos_sensor = [
            TipoSensor(nome_tipo_sensor="Umidade", unidade_medida_padrao="%"),
            TipoSensor(nome_tipo_sensor="pH", unidade_medida_padrao="pH"),
            TipoSensor(nome_tipo_sensor="Nutrientes P&K", unidade_medida_padrao="ppm"),
            TipoSensor(nome_tipo_sensor="Temperatura", unidade_medida_padrao="C")
        ]
        session.add_all(tipos_sensor)
        session.flush()
        print(f"  [OK] {len(tipos_sensor)} tipos de sensor")

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
        print(f"  [OK] {len(sensores)} sensores")

        # Seed Funcionarios (Fase 7)
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
        print(f"  [OK] {len(funcionarios)} funcionarios")

        session.commit()

    print()
    print("=" * 60)
    print("[OK] Banco de dados inicializado com sucesso!")
    print("=" * 60)
    print()
    print("Resumo:")
    print(f"  - Culturas: {len(culturas)}")
    print(f"  - Talhoes: {len(talhoes)}")
    print(f"  - Tipos de Sensor: {len(tipos_sensor)}")
    print(f"  - Sensores: {len(sensores)}")
    print(f"  - Funcionarios: {len(funcionarios)}")
    print()
    print("Funcionarios cadastrados para receber alertas:")
    for func in funcionarios:
        channels = []
        if func.recebe_email:
            channels.append("Email")
        if func.recebe_sms:
            channels.append("SMS")
        print(f"  - {func.nome} ({func.cargo})")
        print(f"    Canais: {', '.join(channels)}")
        levels = []
        if func.alertas_criticos:
            levels.append("CRITICO")
        if func.alertas_altos:
            levels.append("ALTO")
        if func.alertas_medios:
            levels.append("MEDIO")
        if func.alertas_baixos:
            levels.append("BAIXO")
        print(f"    Niveis: {', '.join(levels)}")
    print()


if __name__ == "__main__":
    try:
        initialize_database()
        print("[SUCCESS] Sistema pronto para uso!")
        print()
        print("Proximos passos:")
        print("  1. Inicie a API: cd services/api && uvicorn main:app --reload")
        print("  2. Acesse: http://localhost:8000/docs")
        print("  3. Teste: http://localhost:8000/api/alerts/test")
        print()
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
