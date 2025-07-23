import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# 🎨 Configuración general
st.set_page_config(page_title="FinAnalyzer EDU", layout="wide")
st.title("📊 FinAnalyzer EDU — Comparador Financiero Educativo")

# 🖼 Imagen institucional
st.image("portada_finanalyzer.png", use_container_width=True)

st.markdown("_Analiza con precisión. Aprende con propósito._")
st.markdown("---")

# 📥 Entrada de datos
tickers = st.text_input("📎 Introduce símbolos de activos (ej: AAPL,MSFT)", "AAPL,MSFT")
start_date = st.date_input("📅 Fecha de inicio", date(2020, 1, 1))
end_date = st.date_input("📅 Fecha de fin", date(2027, 1, 1))
selected = tickers.replace(" ", "").split(",")

col1, col2 = st.columns(2)
with col1:
    theme = st.radio("🎨 Tema de gráficos", ["Claro", "Oscuro"])
    template = "plotly_white" if theme == "Claro" else "plotly_dark"
with col2:
    show_tech = st.checkbox("📊 Mostrar análisis técnico")

# 📡 Descarga de datos
data = {}
for ticker in selected:
    df = yf.download(ticker, start=start_date, end=end_date)
    df["Ticker"] = ticker
    data[ticker] = df

st.markdown("---")
st.subheader("📈 Evolución histórica de precios")

for ticker in selected:
    df = data[ticker]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=ticker))
    fig.update_layout(template=template, title=f"Precio histórico — {ticker}")
    st.plotly_chart(fig, use_container_width=True, key=f"price_{ticker}")
    st.markdown(f"ℹ️ **{ticker}**: Este gráfico muestra el precio de cierre diario. Observa tendencias, picos y valles.")

# 📊 Indicadores técnicos
if show_tech:
    st.markdown("---")
    st.subheader("🧪 Indicadores técnicos")

    for ticker in selected:
        df = data[ticker].copy()
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["EMA12"] = df["Close"].ewm(span=12).mean()
        df["EMA26"] = df["Close"].ewm(span=26).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9).mean()
        df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
        std = df["Close"].rolling(20).std()
        df["Upper"] = df["SMA20"] + 2 * std
        df["Lower"] = df["SMA20"] - 2 * std

        st.markdown(f"### 📌 {ticker}")

        # SMA
        fig_sma = go.Figure()
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))
        fig_sma.update_layout(template=template, title="Media móvil simple")
        st.plotly_chart(fig_sma, use_container_width=True, key=f"sma_{ticker}")
        st.markdown("📏 **SMA**: Muestra la tendencia suavizada del precio. SMA20 refleja corto plazo; SMA50, medio plazo.")

        # RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
        fig_rsi.update_layout(template=template, title="Índice de Fuerza Relativa (RSI)")
        st.plotly_chart(fig_rsi, use_container_width=True, key=f"rsi_{ticker}")
        st.markdown("🧪 **RSI**: Detecta zonas de sobrecompra (>70) o sobreventa (<30). Útil para anticipar giros.")

        # MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Señal"))
        fig_macd.update_layout(template=template, title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True, key=f"macd_{ticker}")
        st.markdown("📈 **MACD**: Mide la fuerza y dirección del movimiento. Cruces con la Señal pueden indicar entradas/salidas.")

        # Bandas de Bollinger
        fig_boll = go.Figure()
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Upper"], name="Banda superior"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Lower"], name="Banda inferior"))
        fig_boll.update_layout(template=template, title="Bandas de Bollinger")
        st.plotly_chart(fig_boll, use_container_width=True, key=f"boll_{ticker}")
        st.markdown("📊 **Bollinger**: Ayudan a identificar zonas de volatilidad. Tocando los bordes puede anunciar corrección.")

# 📤 Exportar CSV
st.markdown("---")
st.subheader("📤 Exportar datos")
if st.button("Descargar CSV combinado"):
    final_df = pd.concat(data.values())
    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button("📎 Haz clic para bajar datos", data=csv, file_name="finanalyzer_edu.csv")

# 📘 Footer institucional
st.markdown("---")
st.markdown("""
📘 **FinAnalyzer EDU** ha sido desarrollado por *Pablo Serrano Ruiz* con fines educativos y académicos.  
_"Analiza con precisión. Aprende con propósito."_
""")

 
        
