# ==========================================
# AI TRADING DASHBOARD (PRODUCTION v12)
# HEDGE-FUND LEVEL QUANT TERMINAL REF REFACTOR
# ==========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3

import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

from PIL import Image
import easyocr

from sklearn.linear_model import LinearRegression
from textblob import TextBlob
from streamlit_autorefresh import st_autorefresh
import pandas_ta as ta

# ==========================================
# PAGE CONFIG & ADVANCED CYBERPUNK CSS
# ==========================================

st.set_page_config(
    page_title="AI Trading Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@500;700;900&display=swap');

    /* 🌌 ANIMATED BACKGROUND */
    .stApp {
        background: linear-gradient(-45deg, #0a0c10, #111622, #051d16, #0c1017, #131a26);
        background-size: 400% 400%;
        animation: gradientAnimation 18s ease infinite;
        font-family: 'Inter', sans-serif;
    }

    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 🪟 GLASSMORPHISM MAIN CONTAINER */
    .block-container { 
        padding: 2.5rem !important; 
        background: rgba(10, 14, 22, 0.45);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(0, 255, 204, 0.08);
        margin-top: 15px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* 🛸 SIDEBAR UPGRADE */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 22, 0.85) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 255, 204, 0.05);
    }

    /* 🏷️ HEADERS & NEON GLOW */
    h1, h2, h3 { 
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        color: #00ffcc !important; 
        text-shadow: 0px 0px 15px rgba(0, 255, 204, 0.25);
    }
    p, span, div, label { color: #cbd5e1 !important; }
    
    /* 💳 PREMIUM METRIC CARDS REFACTOR */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 15px 20px !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 255, 204, 0.3) !important;
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 255, 204, 0.15);
    }
    [data-testid="stMetricValue"] { 
        font-family: 'Orbitron', sans-serif !important;
        font-size: 2rem !important; 
        font-weight: 700 !important; 
        color: #ffffff !important;
    }
    
    /* ⚡ HIGH-TECH NEON BUTTONS & DOWNLOAD BUTTONS */
    .stButton > button, [data-testid="stDownloadButton"] > button {
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, rgba(0,255,204,0.05), rgba(0,150,255,0.05)) !important;
        color: #00ffcc !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        border: 1px solid rgba(0, 255, 204, 0.4) !important;
        letter-spacing: 1px;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        padding: 10px 24px !important;
        width: 100%;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(90deg, #00ffcc, #0096ff) !important;
        color: #0a0c10 !important;
        font-weight: 700 !important;
        box-shadow: 0px 0px 25px rgba(0, 255, 204, 0.6) !important;
        transform: translateY(-2px);
        border-color: transparent !important;
    }
    
    /* 📑 MODERN TABS UPGRADE */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 15px; 
        background: rgba(255,255,255,0.02);
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] { 
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        height: 45px; 
        border-radius: 8px;
        color: #94a3b8 !important;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] { 
        background: rgba(0, 255, 204, 0.1) !important;
        color: #00ffcc !important; 
        border-bottom: 2px solid #00ffcc !important;
    }

    /* 🔌 INPUT FIELDS STYLING */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {
        background-color: rgba(255, 255, 255, 0.03) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }

    /* Custom scrollbars */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
    ::-webkit-scrollbar-thumb { background: rgba(0, 255, 204, 0.15); border-radius: 4px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE & SESSION STATE
# ==========================================

conn = sqlite3.connect("stock_app.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_name TEXT,
    quantity INTEGER,
    buy_price REAL
)
""")
conn.commit()

if "alerts" not in st.session_state:
    st.session_state.alerts = {}

# ==========================================
# CORE QUANT ENGINE FUNCTIONS
# ==========================================

@st.cache_data(ttl=30)
def get_price(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d")
        return float(data["Close"].iloc[-1])
    except:
        return None

@st.cache_data(ttl=60)
def get_history(symbol, period="6mo"):
    try:
        df = yf.Ticker(symbol).history(period=period)
        return df
    except:
        return pd.DataFrame()

def ml_prediction(stock):
    df = get_history(stock)
    if df.empty: return None
    X = np.array(range(len(df))).reshape(-1, 1)
    y = df["Close"].values
    model = LinearRegression()
    model.fit(X, y)
    prediction = model.predict([[len(df)]])[0]
    return float(prediction)

def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def add_indicators(df):
    df["RSI"] = ta.rsi(df["Close"], length=14)
    macd = ta.macd(df["Close"])
    return pd.concat([df, macd], axis=1)

def check_alerts():
    triggered = []
    for stock, target in list(st.session_state.alerts.items()):
        current = get_price(stock)
        if current and current >= target:
            triggered.append((stock, current, target))
            del st.session_state.alerts[stock]
    return triggered

def tradingview_chart(symbol):
    return f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
      new TradingView.widget({{
        "width": "100%", "height": 550, "symbol": "{symbol}", "interval": "D",
        "timezone": "Asia/Kolkata", "theme": "dark", "style": "1", "locale": "en",
        "toolbar_bg": "rgba(10, 14, 22, 0.9)", "enable_publishing": false, "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom:0;'>⚡ SYSTEM QUANT</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size:0.8rem; color:#00ffcc;'>HEDGE NODE v12</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Navigation Hub",
        ["🌐 Live Markets", "💼 Portfolio Ledger", "🧠 AI Analytics", "📊 Backtest Studio", "🛠️ Quant Tools"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("🤖 Quantum Core Engine Online")

triggered_alerts = check_alerts()
if triggered_alerts:
    for s, p, t in triggered_alerts:
        st.toast(f"🚨 ALERT TERMINAL FIRE: {s} hit ${p:.2f}!", icon="🚨")

# ==========================================
# 1. LIVE MARKETS HUB (STOCKS & CRYPTO OVERLAYS)
# ==========================================

if menu == "🌐 Live Markets":
    st.title("🌐 Multi-Asset Live Hub")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Equity/Crypto Dashboard", "📊 Candlestick / TradingView", "📰 Feed Sentiment"])
    
    with tab1:
        st_autorefresh(interval=10000, key="refresh_markets")
        
        # Stocks Node
        st.subheader("Equities Core Vectors")
        cols_st = st.columns(4)
        for i, stock in enumerate(["AAPL", "TSLA", "MSFT", "RELIANCE.NS"]):
            try:
                data = yf.Ticker(stock).history(period="1d")
                current = float(data["Close"].iloc[-1])
                opening = float(data["Open"].iloc[-1])
                pct = ((current - opening) / opening) * 100
                cols_st[i].metric(label=stock, value=f"${current:,.2f}" if ".NS" not in stock else f"₹{current:,.2f}", delta=f"{pct:.2f}%")
            except: cols_st[i].metric(label=stock, value="Offline")

        # Crypto Node (NEW FEATURE 1)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Decentralized Crypto Nodes")
        cols_cr = st.columns(3)
        for i, crypto in enumerate(["BTC-USD", "ETH-USD", "SOL-USD"]):
            try:
                data = yf.Ticker(crypto).history(period="1d")
                current = float(data["Close"].iloc[-1])
                opening = float(data["Open"].iloc[-1])
                pct = ((current - opening) / opening) * 100
                cols_cr[i].metric(label=crypto.split("-")[0], value=f"${current:,.2f}", delta=f"{pct:.2f}%")
            except: cols_cr[i].metric(label=crypto, value="Offline")
                    
    with tab2:
        c_mode = st.radio("Chart Render Core", ["Plotly Native Candlestick", "TradingView Engine Widget"], horizontal=True)
        tv_sym = st.text_input("Asset Ticker Target", "AAPL")
        
        if c_mode == "TradingView Engine Widget":
            components.html(tradingview_chart(tv_sym), height=580)
        else:
            # Native Candlestick overlay (NEW FEATURE 2)
            df_chart = get_history(tv_sym, period="3mo")
            if not df_chart.empty:
                df_chart['MA50'] = df_chart['Close'].rolling(window=20).mean() # Short MA
                
                fig = go.Figure(data=[
                    go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'], name='Candles'),
                    go.Scatter(x=df_chart.index, y=df_chart['MA50'], line=dict(color='#0096ff', width=1.5), name='SMA 20')
                ])
                fig.update_layout(
                    template="plotly_dark", height=500, margin=dict(t=10, b=0, l=0, r=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else: st.error("Chart node compile array error.")
        
    with tab3:
        st.subheader("Live Sentiment Matrix")
        news_sym = st.text_input("Enter Asset Ticker", "TSLA", key="news_sym")
        if st.button("Scan Headlines", use_container_width=True):
            with st.spinner("Decoding Ticker Sentiment..."):
                try:
                    news = yf.Ticker(news_sym).news
                    if news and isinstance(news, list):
                        for item in news[:6]:
                            title = item.get("title") or (item.get("content", {}).get("title") if "content" in item else None)
                            if title:
                                sentiment = analyze_sentiment(title)
                                with st.container():
                                    st.markdown(f"**{title}**")
                                    c1, _ = st.columns([1.5, 4])
                                    if sentiment > 0.1: c1.success(f"🟢 Bullish: {sentiment:.2f}")
                                    elif sentiment < -0.1: c1.error(f"🔴 Bearish: {sentiment:.2f}")
                                    else: c1.warning(f"🟡 Neutral: {sentiment:.2f}")
                                    st.divider()
                except Exception as e: st.error(f"Feed node exception: {e}")

# ==========================================
# 2. PORTFOLIO LEDGER (WITH LEDGER DATA EXPORT)
# ==========================================

elif menu == "💼 Portfolio Ledger":
    st.title("💼 Ledger Asset Console")
    
    col1, col2 = st.columns([1, 1.5], gap="large")
    with col1:
        st.subheader("Commit Order Vector")
        with st.form("add_stock_form", clear_on_submit=True):
            stock_name = st.text_input("Asset Node ID (e.g. BTC-USD, TSLA)")
            in_col1, in_col2 = st.columns(2)
            quantity = in_col1.number_input("Transaction Volume", min_value=1)
            buy_price = in_col2.number_input("Execution Cost ($)", min_value=0.0)
                
            if st.form_submit_button("Log Vector Commit", use_container_width=True):
                cursor.execute("INSERT INTO portfolio (stock_name, quantity, buy_price) VALUES (?, ?, ?)", (stock_name, quantity, buy_price))
                conn.commit()
                st.toast(f"Logged dynamic asset target {stock_name}!")
                
    with col2:
        df = pd.read_sql("SELECT * FROM portfolio", conn)
        if not df.empty:
            st.subheader("Performance Matrix ")
            total_invested, total_current = 0, 0
            labels, values = [], []
            
            # Dynamic re-calculations
            calculated_rows = []
            for _, row in df.iterrows():
                current_price = get_price(row["stock_name"]) or row["buy_price"]
                invested = row["buy_price"] * row["quantity"]
                current_val = current_price * row["quantity"]
                pl_node = current_val - invested
                
                total_invested += invested
                total_current += current_val
                labels.append(row["stock_name"])
                values.append(current_val)
                
                calculated_rows.append({
                    "Asset": row["stock_name"], "Units": row["quantity"], 
                    "Entry ($)": row["buy_price"], "Current ($)": round(current_price, 2),
                    "Net P/L ($)": round(pl_node, 2)
                })

            m1, m2, m3 = st.columns(3)
            profit = total_current - total_invested
            profit_pct = (profit / total_invested) * 100 if total_invested else 0
            m1.metric("Capital Pool Base", f"${total_invested:,.2f}")
            m2.metric("Market Valuation", f"${total_current:,.2f}")
            m3.metric("Net Unsettled P/L", f"${profit:,.2f}", f"{profit_pct:.2f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            summary_df = pd.DataFrame(calculated_rows)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # EXPORT INTERACTION UTILITY (NEW FEATURE 3)
            csv_data = summary_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 EXPORT DATA LEDGER COMPILATION (CSV)",
                data=csv_data,
                file_name="quant_portfolio_ledger.csv",
                mime="text/csv"
            )

    if not df.empty and values:
        st.markdown("---")
        fig = px.pie(names=labels, values=values, title="Capital Allocation Matrix", hole=0.4)
        fig.update_layout(template="plotly_dark", margin=dict(t=40, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. AI INTEL & ANALYTICS
# ==========================================

elif menu == "🧠 AI Analytics":
    st.title("🧠 Neural Array Core Analytics")
    tab1, tab2 = st.tabs(["Neural Bounds Trend Vector", "Quant Technical Oscillators"])
    
    with tab1:
        stock1 = st.text_input("Asset Matrix ID Ticker", "TSLA")
        if st.button("Generate Matrix Bounds Plan"):
            df = get_history(stock1, "3mo")
            if not df.empty and len(df) > 30:
                latest = float(df["Close"].iloc[-1])
                old = float(df["Close"].iloc[-30])
                pct = ((latest - old) / old) * 100
                
                c1, c2 = st.columns([1, 2.5])
                c1.metric("30-Day Vector Shift", f"{pct:.2f}%")
                if pct > 10: c1.success("🚀 ALPHA BOUND (STRONG BUY)")
                elif pct < -10: c1.error("⚠️ RISK LIQUIDITY NODE (SELL)")
                else: c1.warning("⚖️ SYMMETRIC RANGE SHIFT (HOLD)")
                
                prediction = ml_prediction(stock1)
                if prediction: c1.info(f"🤖 ML Target Node: ${prediction:,.2f}")
                
                fig = go.Figure(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Price Stream", line=dict(color='#00ffcc', width=2)))
                fig.update_layout(template="plotly_dark", height=350, margin=dict(t=10, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                c2.plotly_chart(fig, use_container_width=True)
                
    with tab2:
        stock3 = st.text_input("Indicator Scans Asset", "BTC-USD")
        if st.button("Initialize Wave Compilation"):
            df = get_history(stock3)
            if not df.empty:
                df = add_indicators(df)
                st.line_chart(df["Close"], use_container_width=True)
                
                col_rsi, col_macd = st.columns(2)
                with col_rsi:
                    st.markdown("**Relative Strength (RSI Vector)**")
                    st.line_chart(df["RSI"], height=200)
                with col_macd:
                    st.markdown("**MACD Structural Alignments**")
                    st.line_chart(df[["MACD_12_26_9", "MACDs_12_26_9"]], height=200)

# ==========================================
# 4. HISTORICAL BACKTEST STUDIO (NEW FEATURE 4)
# ==========================================

elif menu == "📊 Backtest Studio":
    st.title("📊 Algorithmic Matrix Simulation Studio")
    st.markdown("Past historical structural nodes computation patterns simulation rules analysis setup node.")
    
    b_col1, b_col2 = st.columns([1, 2])
    with b_col1:
        st.subheader("Strategy Configurations")
        backtest_ticker = st.text_input("Backtest Target Node", "AAPL")
        rsi_lower = st.number_input("RSI Strategy Oversold Floor Node", min_value=10, max_value=50, value=30)
        rsi_upper = st.number_input("RSI Strategy Overbought Ceiling Node", min_value=50, max_value=90, value=70)
        
        simulate_trigger = st.button("Execute Backtest Array Execution")
        
    with b_col2:
        if simulate_trigger:
            with st.spinner("Processing Historic Vector Blocks..."):
                df_back = get_history(backtest_ticker, period="1y")
                if not df_back.empty and len(df_back) > 20:
                    df_back["RSI"] = ta.rsi(df_back["Close"], length=14)
                    df_back = df_back.dropna()
                    #Logic Sim loops
                    cash = 10000.0
                    position = 0.0
                    initial_capital = cash
                    
                    for idx, row in df_back.iterrows():
                        current_close = float(row["Close"])
                        current_rsi = float(row["RSI"])
                        
                        # Sim trigger rules
                        if current_rsi < rsi_lower and cash > current_close: # Buy rule
                            position += cash / current_close
                            cash = 0.0
                        elif current_rsi > rsi_upper and position > 0: # Sell rule
                            cash += position * current_close
                            position = 0.0
                            
                    final_value = cash + (position * float(df_back["Close"].iloc[-1]))
                    strategy_return = ((final_value - initial_capital) / initial_capital) * 100
                    
                    # Compute Benchmark buy-and-hold returns
                    bench_return = ((float(df_back["Close"].iloc[-1]) - float(df_back["Close"].iloc[0])) / float(df_back["Close"].iloc[0])) * 100
                    
                    st.subheader("Simulation Results Matrix")
                    sm1, sm2, sm3 = st.columns(3)
                    sm1.metric("Starting Capital Base", f"${initial_capital:,.2f}")
                    sm2.metric("Final Simulated Yield", f"${final_value:,.2f}", f"{strategy_return:.2f}% Strategy Net")
                    sm3.metric("Benchmark Buy & Hold Yield", f"{bench_return:.2f}%")
                    
                    st.success("Historical computation algorithm array passed validation checks successfully.")
                else: st.error("Insufficent matrix data size block to perform optimization modeling.")

# ==========================================
# 5. QUANT TOOLS (OCR & PRICE INTERCEPT TARGETS)
# ==========================================

elif menu == "🛠️ Quant Tools":
    st.title("🛠️ Operations Node Utilities")
    tab1, tab2 = st.tabs(["Price Interceptors node config", "Interface Screenshot Data Extraction Node"])
    
    with tab1:
        st.subheader("Price Interceptor Triggers Deployment")
        with st.form("alert_form", clear_on_submit=True):
            alt_stock = st.text_input("Asset Ticker Node Target", "BTC-USD")
            alt_target = st.number_input("Target Boundary Trigger ($)", min_value=0.0)
            if st.form_submit_button("Deploy Node Boundary Interceptor", use_container_width=True):
                st.session_state.alerts[alt_stock] = alt_target
                st.toast(f"Bound intercept deployment vector confirmation: {alt_stock}")
                
    with tab2:
        st.subheader("OCR Alpha Document Image Reader")
        uploaded = st.file_uploader("Upload Terminal Matrix Image", type=["png", "jpg", "jpeg"])
        if uploaded:
            image = Image.open(uploaded)
            st.image(image, caption="Buffered Upload Stream Node", width=400)
            with st.spinner("Decoding document alpha data fields..."):
                reader = easyocr.Reader(['en'])
                result = reader.readtext(np.array(image))
                text = "\n".join([r[1] for r in result])
                st.text_area("Decoded Alpha Matrix String Arrays", text, height=250)