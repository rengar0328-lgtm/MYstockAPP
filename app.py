# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

# ==========================================
# 💎 網頁設定
# ==========================================
st.set_page_config(
    page_title="V32.5 終極細節版",
    page_icon="💎",
    layout="wide"
)

# ==========================================
# 🛠️ 核心運算
# ==========================================
def get_smart_data(ticker):
    # 智慧偵測：上市(.TW) 或 上櫃(.TWO)
    if ".TW" in ticker.upper() or ".TWO" in ticker.upper():
        return yf.download(ticker, period="2y", interval="1d", auto_adjust=False, progress=False)
    
    try_tw = f"{ticker}.TW"
    df = yf.download(try_tw, period="2y", interval="1d", auto_adjust=False, progress=False)
    
    if df.empty or len(df) < 5:
        try_two = f"{ticker}.TWO"
        df_two = yf.download(try_two, period="2y", interval="1d", auto_adjust=False, progress=False)
        if not df_two.empty and len(df_two) > 5:
            df_two.attrs['symbol'] = try_two
            return df_two
    
    df.attrs['symbol'] = try_tw
    return df

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
        exp1 = close.ewm(span=fast, adjust=False).mean()
        exp2 = close.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        hist = macd - signal_line
        return hist
    except: return pd.Series()

def analyze_stock(df, user_input_id):
    try:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        
        df = df.sort_index()
        # 確保有足夠資料
        if len(df) < 200: return None
        
        # --- 指標運算 (全數據) ---
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean() # 加入 MA10
        df['MA20'] = df['Close'].rolling(20).mean()
        df['MA60'] = df['Close'].rolling(60).mean()
        
        df['K'], df['D'] = calculate_kd(df['High'], df['Low'], df['Close'])
        df['MACD_Hist'] = calculate_macd(df['Close'])
        
        # 斜率
        slope5 = calculate_slope(df['MA5'])
        slope10 = calculate_slope(df['MA10'])
        slope20 = calculate_slope(df['MA20'])
        
        # 切割出最後 300 天 (給 AI 和畫圖用)
        # 如果資料不足 300 天，就取全部
        lookback = 300
        if len(df) < 300: lookback = len(df)
            
        df_300 = df.tail(lookback).copy()
        
        # 當前數據
        now = float(df_300['Close'].iloc[-1])
        real_symbol = df.attrs.get('symbol', user_input_id)
        
        # V32 評分
        score = 50
        trend_status = "震盪"
        special_tag = ""
        
        ma5_now = df_300['MA5'].iloc[-1]
        ma10_now = df_300['MA10'].iloc[-1]
        ma20_now = df_300['MA20'].iloc[-1]
        
        is_triple_bull = (ma5_now > ma10_now > ma20_now)
        is_slope_pos = (slope5 > 0 and slope10 > 0 and slope20 > 0)
        
        if is_triple_bull: score += 20
        if is_slope_pos: 
            score += 50
            trend_status = "🔥🔥三線全紅"
            special_tag = "🔥🔥三線全紅"
        
        if df_300['MACD_Hist'].iloc[-1] > 0: score += 10
        if df_300['K'].iloc[-1] > df_300['D'].iloc[-1]: score += 10

        est_profit = max(slope20, slope5) * 10
        
        # 生成 AI 用的序列數據
        date_seq = [d.strftime('%m-%d') for d in df_300.index]
        price_seq = [round(x, 1) for x in df_300['Close'].tolist()]
        vol_seq = [int(v/1000) for v in df_300['Volume'].tolist()]

        return {
            "ID": real_symbol,
            "Price": round(now, 2),
            "Score": score,
            "Trend_Desc": trend_status,
            "Special_Tag": special_tag,
            "Technical": {
                "MA20_Slope": round(slope20, 2),
                "MA10_Slope": round(slope10, 2),
                "MACD": "紅" if df_300['MACD_Hist'].iloc[-1] > 0 else "綠",
                "KD": "金叉" if df_300['K'].iloc[-1] > df_300['D'].iloc[-1] else "死叉"
            },
            "Display_Info": { 
                "代號": real_symbol,
                "現價": round(now, 2),
                "評分": score,
                "趨勢": trend_status,
                "MA10斜率": round(slope10, 2), # 表格顯示 MA10 斜率
                "預估%": round(est_profit, 1)
            },
            "History_Data": { 
                "High_300D": round(df_300['High'].max(), 2),
                "Low_300D": round(df_300['Low'].min(), 2),
                "Date_Seq": date_seq,
                "Price_Seq": price_seq,
                "Vol_Seq": vol_seq
            },
            "Chart_Data": df_300 
        }
    except Exception as e:
        return None

# ==========================================
# 🖥️ 介面邏輯
# ==========================================
st.title("💎 V32.5 終極細節版 (含 MA10)")
st.caption("支援：四條均線 (5/10/20/60)、完整 K 線圖、MACD/KD、AI 檔案生成")

# 1. 輸入區
default_input = "2330 2317 2603 3402 8059 4743"
user_input = st.text_area("輸入股票代號 (純數字即可，空白分隔)", default_input, height=80)

if st.button("🚀 啟動掃描", type="primary"):
    raw_tickers = list(set(user_input.split()))
    st.write(f"📡 正在深度解析 {len(raw_tickers)} 檔股票...")
    
    results = []
    progress_bar = st.progress(0)
    
    for i, t in enumerate(raw_tickers):
        try:
            stock_df = get_smart_data(t)
            if not stock_df.empty:
                res = analyze_stock(stock_df, t)
                if res: results.append(res)
        except: pass
        progress_bar.progress((i + 1) / len(raw_tickers))
        
    if not results:
        st.error("❌ 無數據，請檢查代號。")
    else:
        results.sort(key=lambda x: x['Score'], reverse=True)
        
        # ----------------------------------
        # 📥 檔案生成區
        # ----------------------------------
        st.success(f"✅ 分析完成！共 {len(results)} 檔。")
        
        final_data = {
            "Meta": {"Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "Logic": "V32.5_Full_Detail"},
            "Stock_Data": [ {k: v for k, v in r.items() if k not in ['Display_Info', 'Chart_Data']} for r in results ]
        }
        json_str = json.dumps(final_data, ensure_ascii=False, indent=2)
        
        prompt_str = f"""
你是一位擁有「全知視角」的避險基金操盤手。這是一份 V32.5 (細節版) 的深度數據包。
數據包含 MA5, MA10, MA20, MA60 的完整趨勢判斷。

**【你的任務】**
請利用這些數據進行深度判讀：
1. **型態識別**：觀察 300 天走勢。
2. **均線架構**：特別注意 MA10 (紫色線) 是否作為短線防守點。
3. **選股建議**：推薦未來 10 天最強勢的標的。

**【數據內容】**
{json_str}
        """
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 下載數據包 (.json)", json_str, "Stock_Data.json", "application/json", use_container_width=True)
        with col2:
            st.download_button("📥 下載指令包 (.txt)", prompt_str, "AI_Prompt.txt", "text/plain", use_container_width=True)

        st.divider()

        # ----------------------------------
        # 📊 視覺化圖表區 (詳細歷史數據)
        # ----------------------------------
        st.subheader("📈 深度 K 線圖 (含 MA5/10/20/60)")
        
        # 讓用戶選擇股票
        stock_options = [f"{r['ID']} ({r['Trend_Desc']})" for r in results]
        selected_option = st.selectbox("請選擇要查看的股票:", stock_options)
        
        # 找出選到的股票資料
        selected_id = selected_option.split(" ")[0]
        target = next(item for item in results if item["ID"] == selected_id)
        df_chart = target['Chart_Data']
        
        # --- 繪圖核心 (Plotly) ---
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, 
                            row_heights=[0.6, 0.2, 0.2],
                            subplot_titles=(f"{selected_id} 價量趨勢", "成交量", "MACD"))

        # 1. 主圖：K線 + 4條均線
        fig.add_trace(go.Candlestick(x=df_chart.index,
                                     open=df_chart['Open'], high=df_chart['High'],
                                     low=df_chart['Low'], close=df_chart['Close'],
                                     name='K線'), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA5'], line=dict(color='orange', width=1), name='MA5 (週線)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA10'], line=dict(color='purple', width=1), name='MA10 (雙週線)'), row=1, col=1) # 新增 MA10
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA20'], line=dict(color='blue', width=1.5), name='MA20 (月線)'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA60'], line=dict(color='green', width=1.5), name='MA60 (季線)'), row=1, col=1)
        
        # 2. 副圖：成交量
        colors = ['red' if row['Open'] - row['Close'] >= 0 else 'green' for index, row in df_chart.iterrows()]
        fig.add_trace(go.Bar(x=df_chart.index, y=df_chart['Volume'], marker_color=colors, name='成交量'), row=2, col=1)

        # 3. 副圖：MACD
        fig.add_trace(go.Bar(x=df_chart.index, y=df_chart['MACD_Hist'], name='MACD柱狀'), row=3, col=1)
        
        fig.update_layout(height=800, xaxis_rangeslider_visible=False, showlegend=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 顯示詳細數據表格 (含 MA10)
        with st.expander(f"查看 {selected_id} 詳細歷史數據表格"):
            # 這裡加入了 MA10
            st.dataframe(df_chart[['Open', 'High', 'Low', 'Close', 'Volume', 'MA5', 'MA10', 'MA20', 'MA60', 'K', 'D']].sort_index(ascending=False))

else:
    st.info("👈 輸入代號並按下按鈕，查看包含 MA10 的完整趨勢圖。")