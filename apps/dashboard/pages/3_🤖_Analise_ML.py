import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sqlite3
import os
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# DB Connection
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
DB_PATH = os.path.join(project_root, "farmtech.db")

def get_ml_data():
    conn = sqlite3.connect(DB_PATH)
    # Get sensor data for regression
    query = """
    SELECT valor_umidade, temperatura, valor_ph
    FROM leituras_sensores
    WHERE valor_umidade IS NOT NULL AND temperatura IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.title("🤖 Fase 4: Análise de Machine Learning")
st.markdown("### Modelos Preditivos e Insights")

try:
    df = get_ml_data()
    
    if len(df) < 10:
        st.warning("Dados insuficientes para ML (mínimo 10 leituras).")
    else:
        # Correlation Matrix
        st.subheader("Correlação entre Variáveis")
        corr = df.corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', 
                             title="Matriz de Correlação")
        st.plotly_chart(fig_corr, use_container_width=True)
        
        st.markdown("---")
        
        # Regression Model
        st.subheader("Regressão Linear: Umidade vs Temperatura")
        
        X = df[['temperatura']]
        y = df['valor_umidade']
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Predictions
        y_pred = model.predict(X)
        r2 = model.score(X, y)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.info(f"**R² Score:** {r2:.4f}")
            st.write("Coeficiente:", model.coef_[0])
            st.write("Intercepto:", model.intercept_)
            
        with col2:
            fig_reg = px.scatter(df, x='temperatura', y='valor_umidade', opacity=0.65, 
                                 title="Regressão Linear Simples")
            fig_reg.add_traces(go.Scatter(x=df['temperatura'], y=y_pred, name='Regressão', mode='lines', line=dict(color='red')))
            st.plotly_chart(fig_reg, use_container_width=True)
            
        # Forecast Simulation (ARIMA-like visual)
        st.markdown("---")
        st.subheader("Previsão de Umidade (Simulação ARIMA)")
        
        # Generate dummy forecast data based on recent trend
        last_val = df['valor_umidade'].iloc[-1]
        future_steps = 24
        future_index = pd.date_range(start=pd.Timestamp.now(), periods=future_steps, freq='H')
        
        # Simple random walk for visual demo
        noise = np.random.normal(0, 2, future_steps)
        forecast_values = [last_val]
        for n in noise:
            forecast_values.append(forecast_values[-1] + n)
        forecast_values = forecast_values[1:]
        
        df_forecast = pd.DataFrame({'Data': future_index, 'Previsão Umidade': forecast_values})
        
        fig_forecast = px.line(df_forecast, x='Data', y='Previsão Umidade', 
                               title="Previsão para as Próximas 24h", markers=True)
        fig_forecast.add_hline(y=30, line_dash="dash", line_color="red", annotation_text="Nível Crítico")
        st.plotly_chart(fig_forecast, use_container_width=True)

except Exception as e:
    st.error(f"Erro na análise ML: {e}")
