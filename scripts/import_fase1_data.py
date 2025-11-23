"""
Script para importar dados da Fase 1 (CSV) para o banco de dados consolidado
"""
import os
import sys
import csv
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.core.database.service import DatabaseService
from services.core.database.models import Cultura, InsumoCultura, ProducaoAgricola


def import_fase1_data():
    """Import data from Fase 1 CSV file"""

    # Path to Fase 1 CSV
    csv_path = Path(r"C:\Users\USUARIO\Desktop\FIAP\Fase 1 - 2025\FarmTech.DiogoLeiteZequiniPinto_RM565535_fase1_cap1\r_app\Dados para Estudo via R\TESTE 1.csv")

    if not csv_path.exists():
        print(f"❌ Arquivo CSV não encontrado: {csv_path}")
        return

    # Initialize database
    db_url = os.getenv("DATABASE_URL", "sqlite:///./farmtech.db")
    db = DatabaseService(db_url)
    db.create_tables()

    print("Importando dados da Fase 1...")

    # Read CSV data
    csv_data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('cultura'):  # Skip empty rows
                csv_data.append(row)

    print(f"   Encontrados {len(csv_data)} registros no CSV")

    with db.get_session() as session:
        # 1. Create or get cultures
        culturas_map = {}
        unique_culturas = set(row['cultura'] for row in csv_data)

        print(f"\nProcessando culturas: {unique_culturas}")

        for nome_cultura in unique_culturas:
            # Check if culture exists
            cultura = session.query(Cultura).filter(
                Cultura.nome_cultura == nome_cultura
            ).first()

            if not cultura:
                cultura = Cultura(nome_cultura=nome_cultura)
                session.add(cultura)
                session.flush()
                print(f"   [+] Criada cultura: {nome_cultura} (ID: {cultura.id_cultura})")
            else:
                print(f"   [=] Cultura ja existe: {nome_cultura} (ID: {cultura.id_cultura})")

            culturas_map[nome_cultura] = cultura

        # 2. Calculate and insert coefficients based on CSV data
        print("\nCalculando coeficientes de insumo...")

        for nome_cultura, cultura in culturas_map.items():
            # Get all records for this culture
            cultura_records = [r for r in csv_data if r['cultura'] == nome_cultura]

            # Calculate average coefficients
            total_area = sum(float(r['area']) for r in cultura_records)
            total_insumo = sum(float(r['insumo']) for r in cultura_records)
            total_custo = sum(float(r['custo_estimado']) for r in cultura_records)

            coef_insumo = total_insumo / total_area if total_area > 0 else 0
            custo_por_m2 = total_custo / total_area if total_area > 0 else 0

            # Check if InsumoCultura already exists
            insumo_cultura = session.query(InsumoCultura).filter(
                InsumoCultura.id_cultura == cultura.id_cultura
            ).first()

            if not insumo_cultura:
                insumo_cultura = InsumoCultura(
                    id_cultura=cultura.id_cultura,
                    coef_insumo_por_m2=round(coef_insumo, 4),
                    custo_por_m2=round(custo_por_m2, 2)
                )
                session.add(insumo_cultura)
                print(f"   [+] {nome_cultura}: coef_insumo={coef_insumo:.4f}, custo_m2=R${custo_por_m2:.2f}")
            else:
                # Update existing
                insumo_cultura.coef_insumo_por_m2 = round(coef_insumo, 4)
                insumo_cultura.custo_por_m2 = round(custo_por_m2, 2)
                print(f"   [*] {nome_cultura}: atualizado coef_insumo={coef_insumo:.4f}, custo_m2=R${custo_por_m2:.2f}")

        # 3. Insert production data
        print("\nInserindo dados de producao...")

        for row in csv_data:
            cultura = culturas_map[row['cultura']]

            # Parse date
            try:
                data_registro = datetime.strptime(row['data_registro'], '%Y-%m-%d %H:%M:%S')
            except:
                data_registro = datetime.now()

            producao = ProducaoAgricola(
                id_cultura=cultura.id_cultura,
                area_plantada=float(row['area']),
                quantidade_produzida=float(row['insumo']),  # Using insumo as production estimate
                valor_estimado=float(row['custo_estimado']),
                data_colheita=data_registro
            )
            session.add(producao)

        session.commit()
        print(f"   [+] Inseridos {len(csv_data)} registros de producao")

    print("\nImportacao concluida com sucesso!")
    print("\nResumo:")
    with db.get_session() as session:
        print(f"   - Culturas: {session.query(Cultura).count()}")
        print(f"   - Coeficientes de Insumo: {session.query(InsumoCultura).count()}")
        print(f"   - Registros de Producao: {session.query(ProducaoAgricola).count()}")


if __name__ == "__main__":
    import_fase1_data()
