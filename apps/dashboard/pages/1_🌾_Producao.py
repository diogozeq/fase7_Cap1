import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

# DB Connection
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
DB_PATH = os.path.join(project_root, "farmtech.db")

def get_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT p.id_producao, c.nome_cultura, p.quantidade_produzida, p.data_colheita, p.valor_estimado, p.area_plantada
    FROM producao_agricola p
    JOIN culturas c ON p.id_cultura = c.id_cultura
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🌾 Fase 1: Produção Agrícola")
st.markdown("### Análise de Produtividade e Custos")

try:
    df = get_data()
    
    if df.empty:
        st.warning("Nenhum dado de produção encontrado.")
    else:
        # KPIs
        total_prod = df['quantidade_produzida'].sum()
        total_valor = df['valor_estimado'].sum()
        total_area = df['area_plantada'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Produção Total", f"{total_prod:,.1f} ton")
        c2.metric("Valor Estimado", f"R$ {total_valor:,.2f}")
        c3.metric("Área Total", f"{total_area:,.1f} ha")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Produção por Cultura")
            fig_bar = px.bar(df, x='nome_cultura', y='quantidade_produzida', color='nome_cultura', 
                             title="Toneladas por Cultura", template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("Distribuição de Valor")
            fig_pie = px.pie(df, values='valor_estimado', names='nome_cultura', 
                             title="Share de Valor Estimado", template="plotly_white")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        # Time Series
        st.subheader("Histórico de Colheitas")
        df['data_colheita'] = pd.to_datetime(df['data_colheita'])
        df_sorted = df.sort_values('data_colheita')
        fig_line = px.line(df_sorted, x='data_colheita', y='quantidade_produzida', color='nome_cultura',
                           markers=True, title="Evolução da Produção no Tempo")
        st.plotly_chart(fig_line, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
