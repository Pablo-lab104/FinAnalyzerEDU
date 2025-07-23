import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# 🎨 Configuración general
st.set_page_config(page_title="FinAnalyzer EDU", layout="wide")
st.title("📊 FinAnalyzer EDU — Comparador Financiero Educativo")

# 🖼 Imagen institucional
st.image("portada_finanalyzer.png", use_column_width=True)

st.markdown("_Analiza con precisión. Aprende con propósito._")
st.markdown("---")


# 📥 Entrada de datos
tickers = st.text_input("📎 Introduce los símbolos de los activos (ej: AAPL, MSFT):", "AAPL,MSFT")
start_date = st.date_input("📅 Fecha de inicio", date(2020, 1, 1))
end_date = st.date_input("📅 Fecha de fin", date(2027, 1, 1))
selected = tickers.replace(" ", "").split(",")

col_theme, col_tech = st.columns([1,1])
with col_theme:
    theme = st.radio("🎨 Tema de gráficos", ["Claro", "Oscuro"])
    template = "plotly_white" if theme == "Claro" else "plotly_dark"
with col_tech:
    show_technical = st.checkbox("📊 Mostrar análisis técnico")

# 📡 Descarga de datos
data = {}
for ticker in selected:
    df = yf.download(ticker, start=start_date, end=end_date)
    df["Ticker"] = ticker
    data[ticker] = df

st.markdown("---")

# 📈 Visualización de precios
st.subheader("📈 Evolución histórica de precios")
for ticker in selected:
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=data[ticker].index, y=data[ticker]["Close"], name=f"{ticker}"))
    fig_price.update_layout(template=template, title=f"Precio histórico — {ticker}")
    st.plotly_chart(fig_price, use_container_width=True, key=f"price_{ticker}")

# 🧠 Explicación educativa
    st.markdown(f"ℹ️ **{ticker}**: Este gráfico representa la evolución del precio de cierre diario del activo. Observa patrones, tendencias y períodos de volatilidad.")

st.markdown("---")

# 📊 Módulo de análisis técnico
if show_technical:
    st.subheader("🧪 Indicadores técnicos")

    for ticker in selected:
        df = data[ticker]
        df["SMA20"] = df["Close"].rolling(window=20).mean()
        df["SMA50"] = df["Close"].rolling(window=50).mean()
        df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
        df["EMA12"] = df["Close"].ewm(span=12).mean()
        df["EMA26"] = df["Close"].ewm(span=26).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9).mean()
        df["Upper"] = df["SMA20"] + 2 * df["Close"].rolling(window=20).std()
        df["Lower"] = df["SMA20"] - 2 * df["Close"].rolling(window=20).std()

        st.markdown(f"### 📌 {ticker}")

        # SMA
        fig_sma = go.Figure()
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))
        fig_sma.update_layout(template=template, title="Media móvil simple")
        st.plotly_chart(fig_sma, use_container_width=True, key=f"sma_{ticker}")
        st.markdown("🔎 **SMA**: La media móvil suaviza el precio para identificar tendencias. SMA20 responde al corto plazo, SMA50 al medio plazo.")

        # RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
        fig_rsi.update_layout(template=template, title="Índice de Fuerza Relativa")
        st.plotly_chart(fig_rsi, use_container_width=True, key=f"rsi_{ticker}")
        st.markdown("🧪 **RSI**: Indica si un activo está sobrecomprado (>70) o sobrevendido (<30). Puede anticipar giros de tendencia.")

        # MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Señal"))
        fig_macd.update_layout(template=template, title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True, key=f"macd_{ticker}")
        st.markdown("📈 **MACD**: Mide el impulso del mercado. Cruces entre MACD y la Señal pueden indicar puntos de entrada o salida.")

        # Bollinger Bands
        fig_boll = go.Figure()
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Upper"], name="Banda superior"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Lower"], name="Banda inferior"))
        fig_boll.update_layout(template=template, title="Bandas de Bollinger")
        st.plotly_chart(fig_boll, use_container_width=True, key=f"boll_{ticker}")
        st.markdown("📊 **Bandas de Bollinger**: Ayudan a identificar niveles de volatilidad. Cuando el precio toca los extremos, puede haber corrección.")

st.markdown("---")

# 📤 Exportar datos
st.subheader("📤 Exportar resultados")
if st.button("Descargar CSV combinado"):
    final_df = pd.concat(data.values())
    csv = final_df.to_csv(index=False).encode("utf-8")
    st.download_button("Haz clic aquí para bajar los datos", data=csv, file_name="finanalyzer_edu_export.csv")

st.markdown("---")

# 🧠 Pie educativo
st.markdown("""
---
📘 **FinAnalyzer EDU** ha sido creado por *Pablo Serrano Ruiz* con fines académicos y de divulgación financiera.  
Lema: _“Analiza con precisión. Aprende con propósito.”_
""")
 
        
