# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
from datetime import datetime

# ==========================================
# 💎 網頁設定
# ==========================================
st.set_page_config(
    page_title="V32.7 戰艦指揮中心",
    page_icon="💎",
    layout="wide"
)

# ==========================================
# 🕸️ 爬蟲模組
# ==========================================
@st.cache_data(ttl=3600*12)
def get_tw_tickers(selected_industries=None):
    stock_list = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        # 上市
        url_tw = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        res = requests.get(url_tw, headers=headers)
        res.encoding = 'big5'
        df = pd.read_html(res.text)[0].iloc[2:]
        for index, row in df.iterrows():
            code_name = str(row[0]).split()
            if len(code_name) == 2:
                code, industry = code_name[0], str(row[4])
                if len(code) == 4 and (selected_industries is None or industry in selected_industries):
                    stock_list.append(f"{code}.TW")

        # 上櫃
        url_two = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
        res = requests.get(url_two, headers=headers)
        res.encoding = 'big5'
        df = pd.read_html(res.text)[0].iloc[2:]
        for index, row in df.iterrows():
            code_name = str(row[0]).split()
            if len(code_name) == 2:
                code, industry = code_name[0], str(row[4])
                if len(code) == 4 and (selected_industries is None or industry in selected_industries):
                    stock_list.append(f"{code}.TWO")
                    
        return list(set(stock_list))
    except: return []

# ==========================================
# 🛠️ 核心運算
# ==========================================
def get_stock_data_batch(tickers):
    try:
        return yf.download(tickers, period="2y", interval="1d", group_by='ticker', auto_adjust=False, progress=False)
    except: return None

def calculate_slope(series, window=5):
    try:
        if len(series) < window: return 0
        y = series.tail(window).values
        x = np.arange(len(y))
        slope, _ = np.polyfit(x, y, 1)
        return (slope / y[-1]) * 100
    except: return 0

def calculate_kd(high, low, close, n=9):
    try:
        lowest_low = low.rolling(window=n).min()
        highest_high = high.rolling(window=n).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        return k, d
    except: return pd.Series(), pd.Series()

def calculate_macd(close, fast=12, slow=26, signal=9):
    try:
        hist = close.ewm(span=fast).mean() - close.ewm(span=slow).mean()
        hist = hist - hist.ewm(span=signal).mean()
        return hist
    except: return pd.Series()

def analyze_stock(df, ticker_id):
    try:
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
        df = df.sort_index()
        if len(df) < 200 or df['Volume'].iloc[-1] < 300000: return None
        
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        df['K'], df['D'] = calculate_kd(df['High'], df['Low'], df['Close'])
        df['MACD_Hist'] = calculate_macd(df['Close'])
        
        slope5, slope20 = calculate_slope(df['MA5']), calculate_slope(df['MA20'])
        
        lookback = min(len(df), 300)
        df_300 = df.tail(lookback).copy()
        now = float(df_300['Close'].iloc[-1])
        
        score = 50
        trend = "震盪"
        if df_300['MA5'].iloc[-1] > df_300['MA10'].iloc[-1] > df_300['MA20'].iloc[-1]: score += 20
        if slope5 > 0 and slope20 > 0: 
            score += 50
            trend = "🔥🔥三線全紅"
        if df_300['MACD_Hist'].iloc[-1] > 0: score += 10
        if df_300['K'].iloc[-1] > df_300['D'].iloc[-1]: score += 10

        return {
            "ID": ticker_id,
            "Price": round(now, 2),
            "Score": score,
            "Trend_Desc": trend,
            "Technical": {
                "Slope20": round(slope20, 2),
                "MACD": "紅" if df_300['MACD_Hist'].iloc[-1] > 0 else "綠"
            },
            "Display_Info": { 
                "代號": ticker_id, "現價": round(now, 2), "評分": score, 
                "趨勢": trend, "斜率": round(slope20, 2), "預估%": round(max(slope20, 0)*10, 1)
            },
            "History_Data": { 
                "High_300D": round(df_300['High'].max(), 2),
                "Low_300D": round(df_300['Low'].min(), 2),
                "Date_Seq": [d.strftime('%m-%d') for d in df_300.index],
                "Price_Seq": [round(x, 1) for x in df_300['Close'].tolist()],
                "Vol_Seq": [int(v/1000) for v in df_300['Volume'].tolist()]
            },
            "Chart_Data": df_300 
        }
    except: return None

# ==========================================
# 🖥️ 介面邏輯 (新增 AI 戰情室)
# ==========================================
st.sidebar.title("💎 V32.7 指揮中心")

# --- 🤖 AI 傳送門 (新增功能) ---
st.sidebar.markdown("---")
st.sidebar.header("🤖 AI 戰情室")
st.sidebar.info("點擊下方按鈕，直接開啟對話視窗")
# 這裡使用 link_button 開啟新分頁，這是目前技術上最穩定的做法
st.sidebar.link_button("🧠 開啟 Gemini (Google)", "https://gemini.google.com/app", type="primary", use_container_width=True)
st.sidebar.link_button("🤖 開啟 ChatGPT", "https://chatgpt.com/", use_container_width=True)
st.sidebar.markdown("---")

# --- 模式選擇 ---
mode = st.sidebar.radio("📡 掃描模式", ["手動輸入", "全市場掃描"])

final_tickers = []
if mode == "手動輸入":
    user_input = st.sidebar.text_area("輸入代號", "2330 2317 2603 3402 8059", height=100)
    if user_input:
        raw = list(set(user_input.split()))
        for t in raw:
            if "." not in t:
                final_tickers.append(f"{t}.TW")
                final_tickers.append(f"{t}.TWO")
            else: final_tickers.append(t)
else:
    all_inds = ["半導體業", "電子零組件業", "電腦及週邊設備業", "通信網路業", "航運業", "生技醫療業"]
    selected_inds = st.sidebar.multiselect("選擇產業", all_inds, default=["半導體業", "生技醫療業"])
    if st.sidebar.button("📥 更新清單"):
        with st.spinner("連線證交所中..."):
            st.session_state['tickers'] = get_tw_tickers(selected_inds if selected_inds else None)
    if 'tickers' in st.session_state:
        final_tickers = st.session_state['tickers']
        st.sidebar.write(f"已鎖定 {len(final_tickers)} 檔")

# --- 主畫面 ---
st.title("💎 V32.7 戰艦指揮中心")

if st.button("🚀 啟動掃描運算", type="primary"):
    if not final_tickers:
        st.error("❌ 請先輸入或抓取股票代號")
    else:
        st.write(f"📡 掃描 {len(final_tickers)} 檔標的中...")
        results = []
        progress = st.progress(0)
        batch_size = 50
        
        for i in range(0, len(final_tickers), batch_size):
            batch = final_tickers[i:i+batch_size]
            try:
                data = get_stock_data_batch(batch)
                if data is not None:
                    for t in batch:
                        try:
                            df = data if len(batch)==1 else data[t]
                            if isinstance(df, pd.DataFrame) and not df.empty:
                                res = analyze_stock(df, t)
                                if res: results.append(res)
                        except: pass
            except: pass
            progress.progress(min((i+batch_size)/len(final_tickers), 1.0))
            
        if not results:
            st.error("❌ 查無符合條件股票")
        else:
            results.sort(key=lambda x: x['Score'], reverse=True)
            
            # --- 檔案生成區 ---
            st.success(f"✅ 掃描完成！共 {len(results)} 檔。")
            
            json_str = json.dumps({"Meta": "V32.7", "Data": [r['History_Data'] for r in results]}, ensure_ascii=False)
            prompt_str = f"請分析以下 V32.7 數據 (含 300 天序列):\n{json_str}"
            
            # 這裡我們做一個「工作流區塊」
            st.markdown("### 🛠️ AI 分析工作流")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.download_button("1️⃣ 下載數據 (.json)", json_str, "data.json", "application/json", use_container_width=True)
            with col2:
                st.download_button("2️⃣ 下載指令 (.txt)", prompt_str, "prompt.txt", "text/plain", use_container_width=True)
            with col3:
                # 在下載按鈕旁邊直接放 Gemini 連結，方便順手點擊
                st.link_button("3️⃣ 前往 Gemini 分析 ➤", "https://gemini.google.com/app", type="primary", use_container_width=True)
            
            st.divider()
            
            # --- 圖表區 ---
            st.subheader("📈 K 線診斷室")
            df_show = pd.DataFrame([r['Display_Info'] for r in results])
            st.dataframe(df_show, use_container_width=True)
            
            opt = st.selectbox("選擇股票:", [r['ID'] for r in results])
            tgt = next(r for r in results if r['ID'] == opt)
            df = tgt['Chart_Data']
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='blue'), name='MA20'), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Vol'), row=2, col=1)
            fig.update_layout(height=600, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
