import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from PIL import Image, ImageDraw

# DB Connection
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
DB_PATH = os.path.join(project_root, "farmtech.db")

def get_detections():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT timestamp, imagem_nome, classe, confianca
    FROM deteccoes
    ORDER BY timestamp DESC
    LIMIT 50
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("👁️ Fase 6: Visão Computacional")
st.markdown("### Detecção de Pragas e Doenças")

try:
    df = get_detections()
    
    if df.empty:
        st.warning("Nenhuma detecção registrada.")
    else:
        # Stats
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Detecções", len(df))
        c2.metric("Confiança Média", f"{df['confianca'].mean()*100:.1f}%")
        most_common = df['classe'].mode()[0]
        c3.metric("Classe + Comum", most_common)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Classes Detectadas")
            fig_bar = px.bar(df['classe'].value_counts().reset_index(), x='classe', y='count', 
                             color='classe', title="Contagem por Classe")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("Confiança do Modelo")
            fig_hist = px.histogram(df, x='confianca', nbins=20, title="Distribuição de Confiança",
                                    color_discrete_sequence=['green'])
            st.plotly_chart(fig_hist, use_container_width=True)
            
        # Gallery (Simulated images since we don't have the actual files)
        st.markdown("---")
        st.subheader("Galeria de Detecções Recentes")
        
        cols = st.columns(4)
        for idx, row in df.head(4).iterrows():
            with cols[idx]:
                # Create a placeholder image
                img = Image.new('RGB', (200, 200), color = (73, 109, 137))
                d = ImageDraw.Draw(img)
                d.text((10,10), f"{row['classe']}\n{row['confianca']:.2f}", fill=(255,255,0))
                
                st.image(img, caption=f"{row['imagem_nome']}\n{row['timestamp']}", use_column_width=True)
                st.caption(f"Classe: {row['classe']}")

except Exception as e:
    st.error(f"Erro ao carregar CV: {e}")
