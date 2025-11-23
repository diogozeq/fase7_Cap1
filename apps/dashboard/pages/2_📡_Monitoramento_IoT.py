import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import time

# DB Connection
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
DB_PATH = os.path.join(project_root, "farmtech.db")

def get_iot_data(limit=100):
    conn = sqlite3.connect(DB_PATH)
    query = f"""
    SELECT data_hora_leitura, valor_umidade, valor_ph, temperatura, bomba_ligada
    FROM leituras_sensores
    ORDER BY data_hora_leitura DESC
    LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("📡 Fase 3: Monitoramento IoT")
st.markdown("### Sensores em Tempo Real")

# Auto-refresh
if st.checkbox("Atualização Automática (5s)", value=False):
    time.sleep(5)
    st.rerun()

try:
    df = get_iot_data(200)
    
    if df.empty:
        st.warning("Sem dados de sensores.")
    else:
        # Latest reading
        latest = df.iloc[0]
        
        # Gauges
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fig_hum = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = latest['valor_umidade'],
                title = {'text': "Umidade (%)"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "blue"}}
            ))
            fig_hum.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_hum, use_container_width=True)
            
        with col2:
            fig_temp = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = latest['temperatura'],
                title = {'text': "Temp (°C)"},
                gauge = {'axis': {'range': [0, 50]}, 'bar': {'color': "orange"}}
            ))
            fig_temp.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_temp, use_container_width=True)
            
        with col3:
            fig_ph = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = latest['valor_ph'],
                title = {'text': "pH do Solo"},
                gauge = {'axis': {'range': [0, 14]}, 'bar': {'color': "green"}}
            ))
            fig_ph.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10))
            st.plotly_chart(fig_ph, use_container_width=True)
            
        with col4:
            st.markdown("### Status Bomba")
            status = "LIGADA 💧" if latest['bomba_ligada'] else "DESLIGADA 🛑"
            color = "green" if latest['bomba_ligada'] else "red"
            st.markdown(f"<h2 style='color: {color}; text-align: center;'>{status}</h2>", unsafe_allow_html=True)
            st.info(f"Última leitura: {latest['data_hora_leitura']}")

        st.markdown("---")
        
        # Historical Charts
        st.subheader("Histórico Recente")
        df['data_hora_leitura'] = pd.to_datetime(df['data_hora_leitura'])
        
        tab1, tab2 = st.tabs(["Umidade & Temperatura", "pH"])
        
        with tab1:
            fig_hist = px.line(df, x='data_hora_leitura', y=['valor_umidade', 'temperatura'], 
                               title="Variação de Umidade e Temperatura", template="plotly_dark")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with tab2:
            fig_ph_hist = px.line(df, x='data_hora_leitura', y='valor_ph', 
                                  title="Variação de pH", template="plotly_dark")
            fig_ph_hist.update_traces(line_color='green')
            st.plotly_chart(fig_ph_hist, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar IoT: {e}")
