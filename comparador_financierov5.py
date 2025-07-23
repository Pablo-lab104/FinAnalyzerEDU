
import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Comparador Financiero Avanzado")

# Inputs
tickers = [t.strip().upper() for t in st.text_input("Introduce tickers separados por coma:", "AAPL,MSFT,SPY").split(",")]
start_date = st.date_input("Fecha de inicio", pd.to_datetime("2020-01-01"))
end_date = st.date_input("Fecha de fin", pd.to_datetime("2027-01-01"))
theme = st.selectbox("🎨 Tema de gráficos", ["Claro", "Oscuro"])
plotly_theme = "plotly_white" if theme == "Claro" else "plotly_dark"
colors = px.colors.qualitative.Set1

if "SPY" not in tickers:
    tickers.append("SPY")

if "comparaciones" not in st.session_state:
    st.session_state.comparaciones = []

data = yf.download(tickers, start=start_date, end=end_date)['Close'].dropna()
returns = data.pct_change().dropna()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Precios", "📚 Fundamentales", "📊 Métricas", "📉 Técnico"])

# 📈 Precios
with tab1:
    fig = go.Figure()
    for i, t in enumerate(tickers):
        fig.add_trace(go.Scatter(x=data.index, y=data[t], name=t, line=dict(color=colors[i % len(colors)])))
    fig.update_layout(template=plotly_theme, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, key="precio_chart")

# 📚 Fundamentales
with tab2:
    if st.checkbox("Mostrar fundamentales"):
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

        if st.checkbox("📊 Comparar métrica"):
            metric = st.selectbox("Selecciona métrica", df.columns[1:])
            fig = px.bar(df.reset_index(), x="index", y=metric, color="index", template=plotly_theme)
            st.plotly_chart(fig, use_container_width=True, key="fundamentales_chart")

# 📊 Métricas avanzadas
with tab3:
    if st.checkbox("Mostrar métricas"):
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
        st.plotly_chart(px.bar(x=annual_return.index, y=annual_return.values, color=annual_return.index, template=plotly_theme), use_container_width=True, key="rendimiento_chart")

        with st.expander("ℹ️ Volatilidad"):
            st.write("Mide cuánto varía el precio. Alta volatilidad = más riesgo.")
        st.plotly_chart(px.bar(x=volatility.index, y=volatility.values, color=volatility.index, template=plotly_theme), use_container_width=True, key="volatilidad_chart")

        with st.expander("ℹ️ Sharpe Ratio"):
            st.write("Mide el retorno ajustado al riesgo. >1 suele indicar buen rendimiento.")
        st.plotly_chart(px.bar(x=sharpe.index, y=sharpe.values, color=sharpe.index, template=plotly_theme), use_container_width=True, key="sharpe_chart")

        with st.expander("ℹ️ Máximo Drawdown"):
            st.write("Máxima caída desde el valor más alto en el periodo.")
        st.plotly_chart(px.bar(x=drawdown.index, y=drawdown.values, color=drawdown.index, template=plotly_theme), use_container_width=True, key="drawdown_chart")

        st.subheader("🔗 Correlación")
        st.dataframe(returns.corr())

# 📉 Técnico
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
    if st.checkbox("Mostrar análisis técnico"):
        t = st.selectbox("Ticker técnico", tickers)
        td = data[t].dropna()
        sma_20 = td.rolling(20).mean()
        sma_50 = td.rolling(50).mean()
        rsi = compute_rsi(td)
        macd, signal = compute_macd(td)

        st.subheader("📊 Medias móviles")
        fig_sma = go.Figure()
        fig_sma.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))
        fig_sma.add_trace(go.Scatter(x=sma_20.index, y=sma_20, name="SMA 20"))
        fig_sma.add_trace(go.Scatter(x=sma_50.index, y=sma_50, name="SMA 50"))
        fig_sma.update_layout(template=plotly_theme)
        st.plotly_chart(fig_sma, use_container_width=True, key="sma_chart")

        with st.expander("ℹ️ ¿Qué es RSI?"):
            st.write("Mide fuerza relativa del precio. >70 sobrecomprado, <30 sobrevendido.")
        st.line_chart(rsi, use_container_width=True)

        with st.expander("ℹ️ ¿Qué es MACD?"):
            st.write("Cruces de medias móviles para detectar cambios de tendencia.")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=macd.index, y=macd, name="MACD"))
        fig_macd.add_trace(go.Scatter(x=signal.index, y=signal, name="Señal"))
        fig_macd.update_layout(template=plotly_theme)
        st.plotly_chart(fig_macd, use_container_width=True, key="macd_chart")

        st.subheader("📉 Bandas de Bollinger")
        std = td.rolling(20).std()
        upper = sma_20 + 2 * std
        lower = sma_20 - 2 * std
        fig_boll = go.Figure()
        fig_boll.add_trace(go.Scatter(x=td.index, y=td, name="Precio"))
        fig_boll.add_trace(go.Scatter(x=upper.index, y=upper, name="Banda superior"))
        fig_boll.add_trace(go.Scatter(x=lower.index, y=lower, name="Banda inferior"))
        fig_boll.update_layout(template=plotly_theme)
        st.plotly_chart(fig_boll, use_container_width=True, key="bollinger_chart")

        with st.expander("ℹ️ ¿Qué son Bandas de Bollinger?"):
            st.write("Indican si el activo está sobrecomprado o sobrevendido según volatilidad.")
        st.download_button("📥 Descargar datos", data.to_csv().encode(), file_name="datos.csv", mime="text/csv")
        st.subheader("🔗 Correlaciones") 
        
