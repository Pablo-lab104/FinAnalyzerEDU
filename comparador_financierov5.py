import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import openai

# ⚙️ Configuración general
st.set_page_config(layout="wide", page_title="FinAnalyzer EDU", page_icon="📊")

# 🎨 Encabezado institucional
st.markdown("""
<div style='text-align: center'>
<h1 style='color:#174A7E;'>📊 FinAnalyzer EDU</h1>
<h3 style='color:#555;'>Comparador Financiero Educativo</h3>
<img src='https://raw.githubusercontent.com/Pablo-lab104/FinAnalyzerEDU/main/portada_finanalyzer.png' width='80%'>
<p style='font-style: italic; color:#888;'>Analiza con precisión. Aprende con propósito.</p>
</div>
""", unsafe_allow_html=True)
st.markdown("<hr style='border-top: 1px solid #BBB;'>", unsafe_allow_html=True)

# 🎯 Inputs principales
col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    tickers = st.text_input("📎 Tickers (ej: AAPL,MSFT,SPY)", "AAPL,MSFT,SPY").upper().replace(" ", "").split(",")
with col2:
    start_date = st.date_input("📅 Fecha de inicio", pd.to_datetime("2020-01-01"))
with col3:
    end_date = st.date_input("📅 Fecha de fin", pd.to_datetime("2027-01-01"))
theme = st.selectbox("🎨 Tema visual", ["Claro", "Oscuro"])
plotly_theme = "plotly_white" if theme == "Claro" else "plotly_dark"
colors = px.colors.qualitative.Set1
if "SPY" not in tickers:
    tickers.append("SPY")

# 📉 Descarga de precios históricos
data = yf.download(tickers, start=start_date, end=end_date)['Close'].dropna()
returns = data.pct_change().dropna()

# 🧭 Tabs organizados
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Precios", "📚 Fundamentales", "📊 Métricas", "📉 Técnico", "📘 Explicaciones"])

# 📈 TAB 1 - Evolución histórica
with tab1:
    st.markdown("## 📈 Evolución histórica de precios")
    fig = go.Figure()
    for i, t in enumerate(tickers):
        fig.add_trace(go.Scatter(x=data.index, y=data[t], name=t, line=dict(color=colors[i % len(colors)])))
    fig.update_layout(template=plotly_theme, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# 📚 TAB 2 - Fundamentales
with tab2:
    st.markdown("## 📚 Información fundamental")
    fundamentals = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).fast_info
            fundamentals[t] = {
                "Ticker": t,
                "Precio actual": info.get("last_price"),
                "PER": info.get("pe_ratio"),
                "Dividend (%)": info.get("dividend_rate"),
                "ROE (%)": None,
                "Margen (%)": None
            }
        except Exception:
            fundamentals[t] = {
                "Ticker": t,
                "Precio actual": "Error",
                "PER": "Error",
                "Dividend (%)": "Error",
                "ROE (%)": "Error",
                "Margen (%)": "Error"
            }
    df = pd.DataFrame(fundamentals).T
    st.dataframe(df)
    metric = st.selectbox("📊 Comparar métrica", df.columns[1:])
    fig = px.bar(df.reset_index().rename(columns={"index": "Ticker"}), x="Ticker", y=metric, color="Ticker", template=plotly_theme)
    st.plotly_chart(fig, use_container_width=True)

# 📊 TAB 3 - Métricas financieras
with tab3:
    st.markdown("## 📊 Métricas de rendimiento")
    sharpe_ratio = returns.mean() / returns.std()
    volatilities = returns.std()
    metrics_df = pd.DataFrame({
        "Sharpe Ratio": sharpe_ratio,
        "Volatilidad": volatilities,
    }).dropna()
    st.dataframe(metrics_df)
    chart_type = st.selectbox("📊 Mostrar gráfico", ["Sharpe Ratio", "Volatilidad"])
    fig = px.bar(metrics_df.reset_index().rename(columns={"index": "Ticker"}), x="Ticker", y=chart_type, color="Ticker", template=plotly_theme)
    st.plotly_chart(fig, use_container_width=True)

# 📉 TAB 4 - Indicadores técnicos
with tab4:
    st.markdown("## 📉 Indicadores técnicos: RSI y medias móviles")
    for t in tickers:
        df = data[t].dropna()
        df_ma50 = df.rolling(window=50).mean()
        df_ma200 = df.rolling(window=200).mean()
        delta = df.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df, name="Precio"))
        fig.add_trace(go.Scatter(x=df_ma50.index, y=df_ma50, name="MA50"))
        fig.add_trace(go.Scatter(x=df_ma200.index, y=df_ma200, name="MA200"))
        fig.update_layout(title=f"{t} - Medias móviles", template=plotly_theme)
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=rsi.index, y=rsi, name="RSI"))
        fig2.update_layout(title=f"{t} - RSI", template=plotly_theme, yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig2, use_container_width=True)

# 📘 TAB 5 - Explicaciones educativas
with tab5:
    st.markdown("## 📘 Explicaciones educativas")
    st.info("🧠 Este comparador se creó con fines educativos. Los indicadores financieros como el PER, la volatilidad o el RSI pueden ayudarte a tomar decisiones más informadas, pero no garantizan resultados.")
    st.markdown("""
**¿Cómo interpretar algunas métricas?**
- **PER (Price to Earnings Ratio)**: indica cuántas veces los beneficios están reflejados en el precio actual.
- **Dividend Yield**: porcentaje de retorno por dividendos. Interesante para ingresos pasivos.
- **Sharpe Ratio**: mide el rendimiento ajustado por riesgo. Cuanto más alto, mejor.
- **RSI (Relative Strength Index)**: indica si el activo está sobrecomprado (>70) o sobrevendido (<30).

Recuerda complementar tus análisis con contexto económico, análisis cualitativos y tus propios criterios. 📘
""")











  

 
        
