import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# 🎨 Configuración
st.set_page_config(page_title="FinAnalyzer EDU", layout="wide")
st.title("📊 FinAnalyzer EDU — Comparador Financiero Educativo")

# 🖼 Imagen institucional
st.image("portada_finanalyzer.png", use_container_width=True)
st.markdown("_Analiza con precisión. Aprende con propósito._")
st.markdown("---")

# 📥 Entrada de datos
tickers = st.text_input("📎 Activos (ej: AAPL, MSFT)", "AAPL,MSFT")
start = st.date_input("📅 Fecha inicio", date(2020,1,1))
end = st.date_input("📅 Fecha fin", date(2027,1,1))
selected = tickers.replace(" ", "").split(",")

col1, col2 = st.columns(2)
with col1:
    theme = st.radio("🎨 Tema", ["Claro", "Oscuro"])
    template = "plotly_white" if theme=="Claro" else "plotly_dark"
with col2:
    show_tech = st.checkbox("📊 Análisis técnico")

# 📡 Descarga de datos
data = {}
for t in selected:
    df = yf.download(t, start=start, end=end)
    df["Ticker"] = t
    data[t] = df

st.markdown("---")
st.subheader("📈 Evolución histórica")

for t in selected:
    df = data[t]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=t))
    fig.update_layout(template=template, title=f"Precio — {t}")
    st.plotly_chart(fig, use_container_width=True, key=f"precio_{t}")
    st.markdown(f"ℹ️ **{t}**: Precio de cierre diario. Observa la tendencia y movimientos clave.")

# 🧪 Indicadores técnicos
if show_tech:
    st.markdown("---")
    st.subheader("🧪 Indicadores técnicos")

    for t in selected:
        df = data[t].copy()
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["SMA50"] = df["Close"].rolling(50).mean()
        df["EMA12"] = df["Close"].ewm(span=12).mean()
        df["EMA26"] = df["Close"].ewm(span=26).mean()
        df["MACD"] = df["EMA12"] - df["EMA26"]
        df["Signal"] = df["MACD"].ewm(span=9).mean()
        df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
        std = df["Close"].rolling(20).std()
        boll_mean = df["Close"].rolling(20).mean()
        df["Upper"] = boll_mean + 2 * std
        df["Lower"] = boll_mean - 2 * std

        st.markdown(f"### 📌 {t}")

        # SMA
        fig_sma = go.Figure()
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA20"], name="SMA20"))
        fig_sma.add_trace(go.Scatter(x=df.index, y=df["SMA50"], name="SMA50"))
        fig_sma.update_layout(template=template, title="Media móvil")
        st.plotly_chart(fig_sma, use_container_width=True, key=f"sma_{t}")
        st.markdown("📏 **SMA**: La media móvil suaviza el precio para ver tendencias.")

        # RSI
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
        fig_rsi.update_layout(template=template, title="RSI")
        st.plotly_chart(fig_rsi, use_container_width=True, key=f"rsi_{t}")
        st.markdown("🧪 **RSI**: Identifica zonas de sobrecompra/sobreventa para posibles giros.")

        # MACD
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Señal"))
        fig_macd.update_layout(template=template, title="MACD")
        st.plotly_chart(fig_macd, use_container_width=True, key=f"macd_{t}")
        st.markdown("📈 **MACD**: Mide el impulso. Cruces entre líneas indican señales técnicas.")

        # Bollinger
        fig_boll = go.Figure()
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Precio"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Upper"], name="Banda superior"))
        fig_boll.add_trace(go.Scatter(x=df.index, y=df["Lower"], name="Banda inferior"))
        fig_boll.update_layout(template=template, title="Bandas de Bollinger")
        st.plotly_chart(fig_boll, use_container_width=True, key=f"boll_{t}")
        st.markdown("📊 **Bollinger**: Visualizan zonas de alta volatilidad. Los extremos sugieren corrección.")

# 📤 Exportación
st.markdown("---")
st.subheader("📤 Exportar datos")
if st.button("Descargar CSV"):
    all_data = pd.concat(data.values())
    csv = all_data.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", data=csv, file_name="FinAnalyzerEDU.csv")

# 📘 Firma institucional
st.markdown("---")
st.markdown("""
📘 **FinAnalyzer EDU** desarrollado por *Pablo Serrano Ruiz* con fines educativos y académicos.  
_"Analiza con precisión. Aprende con propósito."_
""")


 
        
