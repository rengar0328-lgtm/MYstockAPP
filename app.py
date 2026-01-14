# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
import warnings
from datetime import datetime

# 忽略 SSL 警告 (這是穿透防護的關鍵)
warnings.filterwarnings("ignore")

# ==========================================
# 💎 網頁設定
# ==========================================
st.set_page_config(
    page_title="V32.10 強力穿透版",
    page_icon="💎",
    layout="wide"
)

# ==========================================
# 🛡️ 離線資料庫 (最後一道防線)
# ==========================================
OFFLINE_LIST = [
    "2330.TW", "2454.TW", "2317.TW", "2603.TW", "2609.TW", "2615.TW", "2303.TW", "3711.TW", "3443.TW", "6669.TW",
    "3035.TW", "3037.TW", "2382.TW", "3231.TW", "2356.TW", "2376.TW", "2308.TW", "2881.TW", "2882.TW", "5871.TW",
    "4743.TWO", "6446.TWO", "6472.TWO", "6547.TWO", "8069.TWO", "8299.TWO", "3529.TWO", "3293.TWO", "3034.TW",
    "3533.TW", "3661.TW", "6531.TW", "5274.TW", "8046.TW", "6223.TWO", "3105.TWO", "5347.TWO", "6147.TWO", "5483.TWO"
]

# ==========================================
# 🕸️ 強力爬蟲模組 (穿透版)
# ==========================================
@st.cache_data(ttl=3600*4) # 縮短緩存時間，確保資料新鮮
def get_tw_tickers_auto(industries=None):
    stock_list = []
    
    # 偽裝成最新的 Chrome 瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    try:
        # 1. 抓取上市股票 (Mode=2)
        # verify=False 是關鍵，忽略憑證錯誤
        url_tw = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
        res = requests.get(url_tw, headers=headers, verify=False, timeout=10)
        res.encoding = 'big5' # 強制編碼
        
        # 使用 pandas 解析表格
        df = pd.read_html(res.text)[0]
        df = df.iloc[2:] # 刪除表頭
        
        for index, row in df.iterrows():
            try:
                code_str = str(row[0])
                # 只有前面是數字的才是股票 (過濾掉 ETF、權證)
                if len(code_str.split()) == 2:
                    code, name = code_str.split()
                    ind = str(row[4])
                    # 如果使用者沒選產業 (None)，就全抓；否則只抓選定的
                    if len(code) == 4 and (not industries or ind in industries):
                        stock_list.append(f"{code}.TW")
            except: pass

        # 2. 抓取上櫃股票 (Mode=4)
        url_two = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
        res = requests.get(url_two, headers=headers, verify=False, timeout=10)
        res.encoding = 'big5'
        
        df = pd.read_html(res.text)[0]
        df = df.iloc[2:]
        
        for index, row in df.iterrows():
            try:
                code_str = str(row[0])
                if len(code_str.split()) == 2:
                    code, name = code_str.split()
                    ind = str(row[4])
                    if len(code) == 4 and (not industries or ind in industries):
                        stock_list.append(f"{code}.TWO")
            except: pass

        # 如果真的抓不到 (可能網站掛了)，才回傳 False，讓主程式切換離線檔
        if len(stock_list) < 10: 
            return None 
            
        return list(set(stock_list))

    except Exception as e:
        print(f"爬蟲錯誤: {e}")
        return None # 回傳 None 觸發離線模式

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
        # 濾網：只掃描有量的股票 (日均量 > 300 張)
        if len(df) < 200: return None
        if df['Volume'].iloc[-1] < 300000: return None 
        
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
            "ID": ticker_id, "Price": round(now, 2), "Score": score, "Trend_Desc": trend,
            "Technical": {"Slope20": round(slope20, 2), "MACD": "紅" if df_300['MACD_Hist'].iloc[-1] > 0 else "綠"},
            "Display_Info": {"代號": ticker_id, "現價": round(now, 2), "評分": score, "趨勢": trend, "斜率": round(slope20, 2), "預估%": round(max(slope20, 0)*10, 1)},
            "History_Data": {
                "High_300D": round(df_300['High'].max(), 2), "Low_300D": round(df_300['Low'].min(), 2),
                "Date_Seq": [d.strftime('%m-%d') for d in df_300.index],
                "Price_Seq": [round(x, 1) for x in df_300['Close'].tolist()],
                "Vol_Seq": [int(v/1000) for v in df_300['Volume'].tolist()]
            },
            "Chart_Data": df_300
        }
    except: return None

# ==========================================
# 🖥️ 介面邏輯
# ==========================================
st.sidebar.title("💎 V32.10 強力穿透版")
st.sidebar.markdown("---")
st.sidebar.link_button("🧠 開啟 Gemini", "https://gemini.google.com/app", type="primary", use_container_width=True)
st.sidebar.link_button("🤖 開啟 ChatGPT", "https://chatgpt.com/", use_container_width=True)
st.sidebar.markdown("---")

mode = st.sidebar.radio("📡 掃描模式", ["手動輸入", "全市場/產業掃描"])

target_tickers = []
selected_inds = []

if mode == "手動輸入":
    user_input = st.sidebar.text_area("輸入代號", "2330 2317 2603", height=100)
    if user_input:
        raw = list(set(user_input.split()))
        for t in raw:
            if "." not in t:
                target_tickers.append(f"{t}.TW")
                target_tickers.append(f"{t}.TWO")
            else: target_tickers.append(t)
else:
    all_inds = ["半導體業", "電子零組件業", "電腦及週邊設備業", "通信網路業", "航運業", "生技醫療業", "光電業", "汽車工業", "金融保險業", "建材營造業"]
    st.sidebar.caption("💡 不選產業 = 掃描全台股 (約 1800 檔)")
    selected_inds = st.sidebar.multiselect("選擇產業", all_inds, default=[])

st.title("💎 V32.10 戰艦強力穿透版")

if st.button("🚀 啟動掃描 (穿透模式)", type="primary"):
    
    if mode == "全市場/產業掃描":
        status = st.empty()
        status.info("📡 正在嘗試穿透證交所防護網，抓取全市場清單...")
        
        # 呼叫強力爬蟲
        crawled_list = get_tw_tickers_auto(selected_inds if selected_inds else None)
        
        if crawled_list:
            target_tickers = crawled_list
            status.success(f"✅ 成功突破！取得 {len(target_tickers)} 檔股票清單。")
        else:
            target_tickers = OFFLINE_LIST
            status.error("⚠️ 穿透失敗 (證交所封鎖嚴格)，已切換至「熱門股備援清單」。")
            
    if not target_tickers:
        st.error("❌ 無法取得代號。")
    else:
        st.write(f"📡 開始運算 {len(target_tickers)} 檔股票 (全掃描約需 1-2 分鐘)...")
        
        results = []
        progress = st.progress(0)
        batch_size = 50 
        
        for i in range(0, len(target_tickers), batch_size):
            batch = target_tickers[i:i+batch_size]
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
            progress.progress(min((i+batch_size)/len(target_tickers), 1.0))
            
        if not results:
            st.warning("⚠️ 掃描完成，但沒有符合條件的股票。")
        else:
            results.sort(key=lambda x: x['Score'], reverse=True)
            
            st.success(f"✅ 掃描完成！共發現 {len(results)} 檔強勢股。")
            
            json_str = json.dumps({"Meta": "V32.10", "Data": [r['History_Data'] for r in results]}, ensure_ascii=False)
            prompt_str = f"請分析以下 V32.10 數據 (1000+ 檔全掃描):\n{json_str}"
            
            col1, col2, col3 = st.columns(3)
            with col1: st.download_button("1️⃣ 下載數據 (.json)", json_str, "data.json", "application/json", use_container_width=True)
            with col2: st.download_button("2️⃣ 下載指令 (.txt)", prompt_str, "prompt.txt", "text/plain", use_container_width=True)
            with col3: st.link_button("3️⃣ 前往 Gemini ➤", "https://gemini.google.com/app", type="primary", use_container_width=True)
            
            st.divider()
            
            df_show = pd.DataFrame([r['Display_Info'] for r in results])
            st.dataframe(df_show, use_container_width=True)
            
            if results:
                opt = st.selectbox("選擇股票:", [r['ID'] for r in results])
                tgt = next(r for r in results if r['ID'] == opt)
                df = tgt['Chart_Data']
                
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='blue'), name='MA20'), row=1, col=1)
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Vol'), row=2, col=1)
                fig.update_layout(height=600, xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
