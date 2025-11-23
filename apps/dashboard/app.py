import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# Page config
st.set_page_config(
    page_title="FarmTech Consolidação",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "farmtech.db"


# Helpers ----------------------------------------------------------------------
def load_df(query: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            return pd.read_sql(query, conn)
    except Exception:
        return pd.DataFrame()


def fmt(num, suffix=""):
    try:
        return f"{num:,.1f}{suffix}".replace(",", ".")
    except Exception:
        return "—"


# Sidebar ----------------------------------------------------------------------
st.sidebar.title("FarmTech 4.0")
st.sidebar.success("Sistema Integrado de Gestão Agrícola")
st.sidebar.markdown("**Banco:** " + ("ok" if DB_PATH.exists() else "indisponível"))
st.sidebar.markdown(f"`{DB_PATH.name}`")

# Header -----------------------------------------------------------------------
st.title("🚜 Dashboard Consolidado FarmTech")
st.caption("Centro de controle da fazenda inteligente")

# Top metrics ------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Culturas", fmt(load_df("select count(*) c from culturas").squeeze() or 0))
with col2:
    st.metric("Talhões", fmt(load_df("select count(*) c from talhoes").squeeze() or 0))
with col3:
    st.metric("Sensores", fmt(load_df("select count(*) c from sensores").squeeze() or 0))
with col4:
    latest_bomba = load_df(
        """
        select bomba_ligada from leituras_sensores
        order by data_hora_leitura desc limit 1
        """
    )
    st.metric("Bomba", "Ligada" if not latest_bomba.empty and latest_bomba.iloc[0, 0] else "Desligada")

st.markdown("---")

# Fase 1: Produção (quick view) -------------------------------------------------
st.subheader("🌾 Fase 1: Produção Agrícola")
col_p1a, col_p1b, col_p1c = st.columns(3)

talhoes = load_df("select nome_talhao, area_hectares from talhoes")
with col_p1a:
    area_total = talhoes["area_hectares"].sum() if not talhoes.empty else 0
    st.metric("Área Total (ha)", fmt(area_total))
with col_p1b:
    st.metric("Culturas cadastradas", fmt(len(load_df("select * from culturas"))))
with col_p1c:
    st.metric("Aplicações registradas", fmt(len(load_df("select * from ajustes_aplicacao"))))

if not talhoes.empty:
    st.bar_chart(talhoes.set_index("nome_talhao"), use_container_width=True)

# Fase 3: IoT ------------------------------------------------------------------
st.subheader("📡 Fase 3: Monitoramento IoT")
iot_df = load_df(
    """
    select data_hora_leitura, valor_umidade, valor_ph, temperatura, bomba_ligada
    from leituras_sensores
    order by data_hora_leitura desc
    limit 200
    """
)

col_iot1, col_iot2, col_iot3 = st.columns(3)
if not iot_df.empty:
    last_row = iot_df.iloc[0]
    col_iot1.metric("Umidade (%)", fmt(last_row["valor_umidade"]))
    col_iot2.metric("pH", fmt(last_row["valor_ph"]))
    col_iot3.metric("Temperatura (°C)", fmt(last_row["temperatura"]))

    st.line_chart(
        iot_df.set_index("data_hora_leitura")[["valor_umidade", "temperatura"]],
        use_container_width=True,
    )
else:
    st.info("Sem leituras em `leituras_sensores` ainda.")

# Fase 4: Analytics / Forecast -------------------------------------------------
st.subheader("🤖 Fase 4: Previsão de Umidade (ARIMA)")
hist = iot_df["valor_umidade"].dropna().tolist() if not iot_df.empty else []
forecast_vals = []
if len(hist) >= 8:
    from statsmodels.tsa.arima.model import ARIMA

    try:
        model = ARIMA(hist, order=(1, 1, 1)).fit()
        forecast_vals = model.forecast(steps=7).tolist()
    except Exception:
        forecast_vals = []

if forecast_vals:
    days = [(datetime.now() + timedelta(days=i + 1)).strftime("%d/%m") for i in range(len(forecast_vals))]
    chart_df = pd.DataFrame({"Previsão": forecast_vals}, index=days)
    st.line_chart(chart_df, use_container_width=True)
else:
    st.info("Sem dados suficientes para prever. Adicione leituras de umidade.")

# Fase 6: Visão Computacional --------------------------------------------------
st.subheader("👁️ Fase 6: Detecções (YOLOv8)")
det_df = load_df(
    """
    select timestamp, imagem_nome, classe, confianca
    from deteccoes
    order by timestamp desc
    limit 10
    """
)

col_cv1, col_cv2, col_cv3 = st.columns(3)
col_cv1.metric("Total detecções", fmt(len(det_df)))
col_cv2.metric("Confiança média", fmt(det_df["confianca"].mean() * 100 if not det_df.empty else 0, "%"))
top_class = det_df["classe"].mode()[0] if not det_df.empty else "—"
col_cv3.metric("Classe mais comum", top_class)

if not det_df.empty:
    st.table(det_df.rename(columns={
        "timestamp": "Data/Hora",
        "imagem_nome": "Imagem",
        "classe": "Classe",
        "confianca": "Confiança",
    }))
else:
    st.info("Nenhuma detecção registrada em `deteccoes`.")

# Footer -----------------------------------------------------------------------
st.markdown("---")
st.caption("Dados carregados de `farmtech.db`. Caso veja avisos, confira se o banco contém as tabelas necessárias.")
