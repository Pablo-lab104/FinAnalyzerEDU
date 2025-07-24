import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import openai

# 🔐 Configura tu clave GPT
openai.api_key = "TU_API_KEY"

# 🧠 Función GPT para preguntas educativas
def pregunta_gpt(pregunta):
    respuesta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": pregunta}]
    )
    return respuesta.choices[0].message.content

# 📈 Indicadores técnicos
def calcular_rsi(df, periodo=14):
    delta = df['Close'].diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    avg_g = ganancia.rolling(window=periodo).mean()
    avg_p = perdida.rolling(window=periodo).mean()
    rsi = 100 - (100 / (1 + avg_g / avg_p))
    return rsi

def calcular_macd(df):
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal

# 🌟 Configuración Streamlit
st.set_page_config(page_title="FinAnalyzer EDU", page_icon="📊", layout="wide")
st.title("📊 FinAnalyzer EDU – Comparador Financiero Educativo")

# 🧩 Selección de activos
activos = st.multiselect("Selecciona activos (ej: AAPL, MSFT, TSLA):", ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN'])
periodo = st.selectbox("Periodo:", ['3mo', '6mo', '1y', '2y'])
intervalo = st.selectbox("Intervalo:", ['1d', '1wk'])

# 📊 Visualización por activo
for ticker in activos:
    df = yf.download(ticker, period=periodo, interval=intervalo)
    df['RSI'] = calcular_rsi(df)
    macd, signal = calcular_macd(df)
    df['MACD'], df['Signal'] = macd, signal

    st.subheader(f"🎯 {ticker}")
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI'))
        fig.update_layout(title='Indicador RSI', yaxis_title='RSI')
        st.plotly_chart(fig)
        st.caption("El RSI mide la fuerza del precio. RSI > 70 puede indicar sobrecompra, < 30 sobreventa.")

    with col2:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal'))
        fig_macd.update_layout(title='Indicador MACD')
        st.plotly_chart(fig_macd)
        st.caption("MACD identifica cambios de tendencia y señales de entrada/salida.")

    # 💾 Exportar CSV
    st.download_button(
        label=f"📥 Descargar CSV de {ticker}",
        data=df.to_csv().encode('utf-8'),
        file_name=f"{ticker}_finanalyzer.csv",
        mime='text/csv'
    )

# 💬 Módulo educativo GPT
st.markdown("---")
st.header("💬 Preguntas educativas sobre análisis técnico e inversión")
pregunta = st.text_input("Escribe tu pregunta:")
if pregunta:
    respuesta = pregunta_gpt(pregunta)
    st.success(respuesta)

# 👤 Créditos
st.markdown("---")
st.caption("🧠 FinAnalyzer EDU es una herramienta didáctica creada por Pablo Serrano Ruiz. Visualiza con precisión, aprende con propósito.")




  

 
        
