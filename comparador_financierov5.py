import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 🔧 Configuración general
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
st.markdown("<hr style='border-top: 1px solid #BBB;'>", unsafe_allow_html=True)

# 🎛 Inputs organizados
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

# 📉 Descarga de datos
data = yf.download(tickers, start=start_date, end=end_date)['Close'].dropna()
returns = data.pct_change().dropna()

# 📊 Pestañas organizadas
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Precios", "📚 Fundamentales", "📊 Métricas", "📉 Técnico", "📘 Explicaciones"])

# 📈 TAB 1 - Precios históricos
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

# 📊 TAB 3 - Métricas financieras
with tab3:
    st.markdown("## 📊 Métricas de rendimiento")
    annual_return = ((data.iloc[-1] / data.iloc[0]) ** (1 / ((data.index[-1] - data.index[0]).days / 365.25)) - 1) * 100
    volatility = returns.std() * (252**0.5) * 100
    sharpe = annual_return / volatility
    drawdown = ((data / data.cummax()) - 1).min() * 100

    st.markdown(f"📋 **Mejor rendimiento:** `{annual_return.idxmax()}` con {annual_return.max():.2f}%")
    for t in tickers:
        if sharpe[t] > 2:
            st.warning(f"🚨 `{t}` tiene Sharpe Ratio alto ({sharpe[t]:.2f})")

    st.plotly_chart(px.bar(x=annual_return.index, y=annual_return.values, color=annual_return.index, template=plotly_theme), use_container_width=True)
    st.plotly_chart(px.bar(x=volatility.index, y=volatility.values, color=volatility.index, template=plotly_theme), use_container_width=True)
    st.plotly_chart(px.bar(x=sharpe.index, y=sharpe.values, color=sharpe.index, template=plotly_theme), use_container_width=True)
    st.plotly_chart(px.bar(x=drawdown.index, y=drawdown.values, color=drawdown.index, template=plotly_theme), use_container_width=True)

    st.subheader("🔗 Correlación entre activos")
    st.dataframe(returns.corr())

# 📉 TAB 4 - Indicadores técnicos
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
    st.markdown("## 📉 Análisis técnico")
    t = st.selectbox("🧭 Selecciona activo técnico", tickers)
    td = data[t].dropna()
    sma_20 = td.rolling(20).mean()
    sma_50 = td.rolling(50).mean()
    rsi = compute_rsi(td)
    macd, signal = compute_macd(td)
    std = td.rolling(20).std()
    upper = sma_20 + 2 * std
    lower = sma_20 - 2 * std

    fig_sma = go.Figure()
    fig_sma.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))
    fig_sma.add_trace(go.Scatter(x=sma_20.index, y=sma_20, name="SMA 20"))
    fig_sma.add_trace(go.Scatter(x=sma_50.index, y=sma_50, name="SMA 50"))
    fig_sma.update_layout(template=plotly_theme)
    st.plotly_chart(fig_sma, use_container_width=True)

    st.line_chart(rsi, use_container_width=True)

    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=macd.index, y=macd, name="MACD"))
    fig_macd.add_trace(go.Scatter(x=signal.index, y=signal, name="Señal"))
    fig_macd.update_layout(template=plotly_theme)
    st.plotly_chart(fig_macd, use_container_width=True)

    fig_boll = go.Figure()
    fig_boll.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))
    fig_boll.add_trace(go.Scatter(x=upper.index, y=upper, name="Banda superior"))
    fig_boll.add_trace(go.Scatter(x=lower.index, y=lower, name="Banda inferior"))
    fig_boll.update_layout(template=plotly_theme)
    st.plotly_chart(fig_boll, use_container_width=True)

    st.download_button("📥 Descargar datos", data.to_csv().encode(), file_name="datos.csv", mime="text/csv")

# 📘 TAB 5 - Explicaciones
with tab5:
    st.markdown("## 📘 Análisis y conclusiones")

    st.markdown("### 📈 Precios históricos")
    st.write("El gráfico permite visualizar la evolución temporal de cada activo. Tendencias sostenidas reflejan crecimiento estructural; caídas bruscas indican correcciones o eventos externos.")

    st.markdown("### 📚 Indicadores fundamentales")
    st.write("- **PER <15:** valoración razonable o infravalorada.")
    # 💬 Chat Educativo Financiero (GPT)
import openai
openai.api_key = "TU_API_KEY"  # ← reemplaza con tu clave API

def consulta_chatbot(pregunta):
    client = openai.OpenAI()  # si estás en v1
chat_response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": pregunta}]
)
return chat_response.choices[0].message.content

st.markdown("---")
st.markdown("## 💬 Chat educativo sobre finanzas y análisis técnico")
user_question = st.text_input("Escribe tu pregunta financiera o sobre inversión:")

if user_question:
    respuesta = consulta_chatbot(user_question)
    st.info(respuesta)
    # 💬 Chat Educativo Financiero (GPT)
import openai

client = openai.OpenAI(api_key="TU_API_KEY")  # ← Reemplaza TU_API_KEY con tu clave real

def consulta_chatbot(pregunta):
    chat_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": pregunta}]
    )
    return chat_response.choices[0].message.content

st.markdown("---")
st.markdown("## 💬 Chat educativo sobre finanzas y análisis técnico")

user_question = st.text_input("Escribe tu pregunta financiera o sobre inversión:")

if user_question:
    try:
        respuesta = consulta_chatbot(user_question)
        st.info(respuesta)
    except Exception as e:
        st.error("❌ Hubo un error al consultar el chatbot. Verifica tu clave API o conexión.")






  

 
        
