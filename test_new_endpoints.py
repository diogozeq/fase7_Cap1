"""
Script de teste para validar novos endpoints antes de reiniciar o servidor
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Configurar banco de dados
from services.core.database.service import DatabaseService
db = DatabaseService(os.getenv("DATABASE_URL"))

print("=" * 60)
print("TESTANDO NOVOS ENDPOINTS")
print("=" * 60)

# Teste 1: Verificar dados no banco
print("\n1. Verificando dados no banco...")
from services.core.database.models import LeituraSensor

with db.get_session() as session:
    total = session.query(LeituraSensor).count()
    print(f"   Total de leituras: {total}")

    with_all_data = session.query(LeituraSensor).filter(
        LeituraSensor.valor_umidade.isnot(None),
        LeituraSensor.valor_ph.isnot(None),
        LeituraSensor.temperatura.isnot(None)
    ).count()
    print(f"   Com umidade, pH e temperatura: {with_all_data}")

# Teste 2: Cluster Insights
print("\n2. Testando Cluster Insights...")
import pandas as pd
from services.core.ml_models.service import MLModelsService

with db.get_session() as session:
    rows = session.query(
        LeituraSensor.id_leitura,
        LeituraSensor.data_hora_leitura,
        LeituraSensor.valor_umidade,
        LeituraSensor.valor_ph,
        LeituraSensor.temperatura,
    ).filter(
        LeituraSensor.valor_umidade.isnot(None),
        LeituraSensor.valor_ph.isnot(None),
        LeituraSensor.temperatura.isnot(None),
    ).order_by(LeituraSensor.data_hora_leitura.desc()).limit(200).all()

    if len(rows) >= 3:
        df = pd.DataFrame(rows, columns=["id", "timestamp", "umidade", "ph", "temperatura"])
        print(f"   Registros encontrados: {len(df)}")
        print(f"   Umidade média: {df['umidade'].mean():.2f}%")
        print(f"   pH médio: {df['ph'].mean():.2f}")
        print(f"   Temperatura média: {df['temperatura'].mean():.2f}°C")

        # Testar clusterização
        ml = MLModelsService()
        data = df[["umidade", "ph", "temperatura"]]
        result = ml.cluster_data(data, n_clusters=3)

        print(f"   Clusters gerados: {len(result.get('centers', []))}")
        print(f"   Inércia: {result.get('inertia', 0):.2f}")
    else:
        print(f"   ERRO: Apenas {len(rows)} registros encontrados (mínimo: 3)")

# Teste 3: What-If Simulation
print("\n3. Testando What-If Simulation...")
with db.get_session() as session:
    rows = session.query(
        LeituraSensor.valor_umidade,
        LeituraSensor.valor_ph,
        LeituraSensor.temperatura,
    ).filter(
        LeituraSensor.valor_umidade.isnot(None),
        LeituraSensor.valor_ph.isnot(None),
        LeituraSensor.temperatura.isnot(None),
    ).order_by(LeituraSensor.data_hora_leitura.desc()).limit(50).all()

    if rows:
        df = pd.DataFrame(rows, columns=["umidade", "ph", "temperatura"])
        baseline = {
            "umidade": float(df["umidade"].mean()),
            "ph": float(df["ph"].mean()),
            "temperatura": float(df["temperatura"].mean())
        }
        print(f"   Baseline calculado:")
        print(f"   - Umidade: {baseline['umidade']:.2f}%")
        print(f"   - pH: {baseline['ph']:.2f}")
        print(f"   - Temperatura: {baseline['temperatura']:.2f}°C")

        # Testar previsão ARIMA
        history = df["umidade"].tolist()[::-1][-30:]
        ml = MLModelsService()
        forecast = ml.forecast_umidade(history, steps=7)
        print(f"   Previsões ARIMA geradas: {len(forecast.get('predictions', []))}")
    else:
        print("   ERRO: Nenhum registro encontrado")

# Teste 4: Alerts
print("\n4. Testando Alertas...")
with db.get_session() as session:
    rows = session.query(
        LeituraSensor.valor_umidade,
        LeituraSensor.valor_ph,
        LeituraSensor.temperatura,
    ).filter(
        LeituraSensor.valor_umidade.isnot(None),
    ).order_by(LeituraSensor.data_hora_leitura.desc()).limit(50).all()

    if rows:
        df = pd.DataFrame(rows, columns=["umidade", "ph", "temperatura"])
        current_umidade = float(df["umidade"].iloc[0])
        print(f"   Umidade atual: {current_umidade:.2f}%")

        if current_umidade < 30:
            print("   ⚠️ ALERTA CRÍTICO: Umidade muito baixa")
        elif current_umidade > 80:
            print("   ⚠️ ALERTA WARNING: Umidade muito alta")
        else:
            print("   ✓ Status normal")
    else:
        print("   ERRO: Nenhum registro encontrado")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
print("\nPróximo passo: Reinicie o servidor para carregar as novas rotas:")
print("   cd services/api")
print("   python -m uvicorn main:app --reload")
print("=" * 60)
