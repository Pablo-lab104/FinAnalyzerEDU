import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 🎨 Configuración general
st.set_page_config(layout="wide", page_title="FinAnalyzer EDU", page_icon="📊")

# 🖼 Encabezado institucional
st.markdown("""
<div style='text-align: center'>
    <h1 style='color:#174A7E;'>📊 FinAnalyzer EDU</h1>
    <h3 style='color:#555;'>Comparador Financiero Educativo</h3>
    <img src='https://raw.githubusercontent.com/Pablo-lab104/FinAnalyzerEDU/main/portada_finanalyzer.png' width='80%'>
    <p style='font-style: italic; color:#888;'>Analiza con precisión. Aprende con propósito.</p>
</div>
""", unsafe_allow_html=True)
st.divider()

# 📥 Inputs en columnas
col1, col2, col3 = st.columns([3,2,2])
with col1:
    tickers = st.text_input("📎 Tickers (ej: AAPL,MSFT,SPY)", "AAPL,MSFT,SPY").upper().replace(" ", "").split(",")
with col2:
    start_date = st.date_input("📅 Inicio", pd.to_datetime("2020-01-01"))
with col3:
    end_date = st.date_input("📅 Fin", pd.to_datetime("2027-01-01"))

# 🎨 Tema visual
theme = st.selectbox("🎨 Tema", ["Claro", "Oscuro"])
plotly_theme = "plotly_white" if theme == "Claro" else "plotly_dark"
colors = px.colors.qualitative.Set1

if "SPY" not in tickers:
    tickers.append("SPY")

data = yf.download(tickers, start=start_date, end=end_date)['Close'].dropna()
returns = data.pct_change().dropna()

# 📊 Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["📈 Precios", "📚 Fundamentales", "📊 Métricas", "📉 Técnico"])

# 📈 Precios
with tab1:
    fig = go.Figure()
    for i, t in enumerate(tickers):
        fig.add_trace(go.Scatter(x=data.index, y=data[t], name=t, line=dict(color=colors[i % len(colors)])))
    fig.update_layout(template=plotly_theme, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# 📚 Fundamentales
with tab2:
    fundamentals = {}
    for t in tickers:
        info = yf.Ticker(t).info
        fundamentals[t] = {
            "Nombre": info.get("longName"),
            "PER": info.get("trailingPE"),
            "Dividend (%)": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
            "ROE (%)": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None,
            "Margen (%)": info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None
        }
    df = pd.DataFrame(fundamentals).T
    st.dataframe(df)

    metric = st.selectbox("📊 Comparar métrica", df.columns[1:])
    fig = px.bar(df.reset_index(), x="index", y=metric, color="index", template=plotly_theme)
    st.plotly_chart(fig, use_container_width=True)

# 📊 Métricas
with tab3:
    annual_return = ((data.iloc[-1] / data.iloc[0]) ** (1 / ((data.index[-1] - data.index[0]).days / 365.25)) - 1) * 100
    volatility = returns.std() * (252**0.5) * 100
    sharpe = annual_return / volatility
    drawdown = ((data / data.cummax()) - 1).min() * 100

    st.markdown(f"📋 **Mejor rendimiento:** `{annual_return.idxmax()}` con {annual_return.max():.2f}%")
    for t in tickers:
        if sharpe[t] > 2:
            st.warning(f"🚨 `{t}` tiene Sharpe Ratio alto ({sharpe[t]:.2f})")

    with st.expander("ℹ️ Rendimiento anualizado"):
        st.write("Es el crecimiento medio anual del activo en el periodo analizado.")
    st.plotly_chart(px.bar(x=annual_return.index, y=annual_return.values, color=annual_return.index, template=plotly_theme), use_container_width=True)

    with st.expander("ℹ️ Volatilidad"):
        st.write("Mide cuánto varía el precio. Alta volatilidad = más riesgo.")
    st.plotly_chart(px.bar(x=volatility.index, y=volatility.values, color=volatility.index, template=plotly_theme), use_container_width=True)

    with st.expander("ℹ️ Sharpe Ratio"):
        st.write("Mide el retorno ajustado al riesgo. >1 suele indicar buen rendimiento.")
    st.plotly_chart(px.bar(x=sharpe.index, y=sharpe.values, color=sharpe.index, template=plotly_theme), use_container_width=True)

    with st.expander("ℹ️ Máximo Drawdown"):
        st.write("Máxima caída desde el valor más alto en el periodo.")
    st.plotly_chart(px.bar(x=drawdown.index, y=drawdown.values, color=drawdown.index, template=plotly_theme), use_container_width=True)

    st.subheader("🔗 Correlación entre activos")
    st.dataframe(returns.corr())

# 📉 Indicadores técnicos
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line

with tab4:
    t = st.selectbox("🧭 Selecciona activo técnico", tickers)
    td = data[t].dropna()
    sma_20 = td.rolling(20).mean()
    sma_50 = td.rolling(50).mean()
    rsi = compute_rsi(td)
    macd, signal = compute_macd(td)
    std = td.rolling(20).std()
    upper = sma_20 + 2 * std
    lower = sma_20 - 2 * std

    st.subheader("📊 Medias móviles")
    fig_sma = go.Figure()
    fig_sma.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))
    fig_sma.add_trace(go.Scatter(x=sma_20.index, y=sma_20, name="SMA 20"))
    fig_sma.add_trace(go.Scatter(x=sma_50.index, y=sma_50, name="SMA 50"))
    fig_sma.update_layout(template=plotly_theme)
    st.plotly_chart(fig_sma, use_container_width=True)

    with st.expander("ℹ️ ¿Qué es RSI?"):
        st.write("Mide fuerza relativa del precio. >70 sobrecomprado, <30 sobrevendido.")
    st.line_chart(rsi, use_container_width=True)

    with st.expander("ℹ️ ¿Qué es MACD?"):
        st.write("Cruces de medias móviles para detectar cambios de tendencia.")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=macd.index, y=macd, name="MACD"))
    fig_macd.add_trace(go.Scatter(x=signal.index, y=signal, name="Señal"))
    fig_macd.update_layout(template=plotly_theme)
    st.plotly_chart(fig_macd, use_container_width=True)

    st.subheader("📉 Bandas de Bollinger")
    fig_boll = go.Figure()
    fig_boll.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))

 
        
