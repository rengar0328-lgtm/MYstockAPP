# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import warnings

warnings.filterwarnings("ignore")

# ==========================================
# 💎 設定
# ==========================================
st.set_page_config(page_title="V32.13 戰艦 (600大)", page_icon="💎", layout="wide")

# ==========================================
# 📜 內建 600 大熱門股 (V32.13)
# ==========================================
# 包含上市櫃市值前 600 大、ETF成分股、熱門題材
TICKERS_600 = [
    # --- 半導體/IC設計/封測 (上市) ---
    "2330.TW", "2454.TW", "2303.TW", "2379.TW", "3711.TW", "3034.TW", "3035.TW", "3443.TW", "3661.TW", "2344.TW",
    "2408.TW", "2337.TW", "2363.TW", "2327.TW", "2404.TW", "2376.TW", "2388.TW", "3006.TW", "3014.TW", "3016.TW",
    "3532.TW", "4919.TW", "4958.TW", "4961.TW", "5234.TW", "5269.TW", "5274.TW", "6415.TW", "6531.TW", "6533.TW",
    "6643.TW", "6756.TW", "8016.TW", "8028.TW", "8081.TW", "8110.TW", "8261.TW", "8271.TW", "2329.TW", "2369.TW",
    "2395.TW", "2401.TW", "2441.TW", "2449.TW", "2451.TW", "2458.TW", "2481.TW", "3044.TW", "3189.TW", "3413.TW",
    "3545.TW", "3583.TW", "3653.TW", "3702.TW", "4968.TW", "4977.TW", "5203.TW", "5243.TW", "5258.TW", "5305.TW",
    "5351.TW", "5388.TW", "5434.TW", "5469.TW", "5471.TW", "6116.TW", "6128.TW", "6139.TW", "6191.TW", "6196.TW",
    "6209.TW", "6213.TW", "6214.TW", "6235.TW", "6243.TW", "6257.TW", "6269.TW", "6271.TW", "6278.TW", "6282.TW",
    "6285.TW", "6405.TW", "6414.TW", "6438.TW", "6451.TW", "6525.TW", "6552.TW", "6558.TW", "6579.TW", "6605.TW",
    "6669.TW", "6670.TW", "6695.TW", "6715.TW", "6743.TW", "6768.TW", "6770.TW", "6781.TW", "6799.TW", "8131.TW",
    "8163.TW", "8210.TW", "8358.TW", "8438.TW", "2313.TW", "2316.TW", "2342.TW", "2360.TW", "2368.TW", "2392.TW",

    # --- 半導體/IC (上櫃) ---
    "3529.TWO", "3293.TWO", "8059.TWO", "8299.TWO", "6147.TWO", "6223.TWO", "3105.TWO", "4966.TWO", "5347.TWO",
    "5483.TWO", "6104.TWO", "6129.TWO", "6138.TWO", "6180.TWO", "6182.TWO", "6202.TWO", "6239.TWO", "6244.TWO",
    "6274.TWO", "6411.TWO", "6462.TWO", "6510.TWO", "6538.TWO", "6548.TWO", "6561.TWO", "6679.TWO", "6719.TWO",
    "8046.TWO", "8069.TWO", "8114.TWO", "3260.TWO", "3324.TWO", "3374.TWO", "3552.TWO", "3596.TWO", "5272.TWO",
    "5289.TWO", "5299.TWO", "5315.TWO", "5353.TWO", "5371.TWO", "5392.TWO", "5410.TWO", "5425.TWO", "5443.TWO",
    "5452.TWO", "5457.TWO", "5475.TWO", "5481.TWO", "5488.TWO", "5512.TWO", "5536.TWO", "6109.TWO", "6111.TWO",
    "6113.TWO", "6118.TWO", "6121.TWO", "6123.TWO", "6124.TWO", "6125.TWO", "6126.TWO", "6127.TWO", "6134.TWO",
    "6143.TWO", "6150.TWO", "6151.TWO", "6156.TWO", "6158.TWO", "6160.TWO", "6161.TWO", "6163.TWO", "6167.TWO",
    "6173.TWO", "6175.TWO", "6186.TWO", "6187.TWO", "6188.TWO", "6198.TWO", "6199.TWO", "6203.TWO", "6204.TWO",
    
    # --- 電腦/AI/伺服器/零組件 ---
    "2317.TW", "2382.TW", "3231.TW", "2356.TW", "2353.TW", "3402.TW", "2377.TW", "3017.TW", "2301.TW", "2324.TW",
    "2357.TW", "2421.TW", "3037.TW", "3706.TW", "4938.TW", "5215.TW", "6116.TW", "6214.TW", "6278.TW", "8112.TW",
    "8150.TW", "8215.TW", "2323.TW", "2331.TW", "2340.TW", "2345.TW", "2347.TW", "2348.TW", "2349.TW", "2351.TW",
    "2352.TW", "2354.TW", "2355.TW", "2358.TW", "2359.TW", "2362.TW", "2364.TW", "2365.TW", "2371.TW", "2373.TW",
    "2374.TW", "2375.TW", "2380.TW", "2383.TW", "2385.TW", "2387.TW", "2390.TW", "2393.TW", "2397.TW", "2399.TW",
    "2402.TW", "2405.TW", "2406.TW", "2412.TW", "2413.TW", "2414.TW", "2415.TW", "2417.TW", "2419.TW", "2420.TW",
    "2423.TW", "2424.TW", "2425.TW", "2426.TW", "2427.TW", "2428.TW", "2429.TW", "2430.TW", "2431.TW", "2433.TW",
    "2434.TW", "2436.TW", "2438.TW", "2439.TW", "2440.TW", "2442.TW", "2443.TW", "2444.TW", "3002.TW", "3003.TW",
    
    # --- 航運/物流 ---
    "2603.TW", "2609.TW", "2615.TW", "2618.TW", "2610.TW", "2637.TW", "2605.TW", "2606.TW", "5608.TW", "2601.TW",
    "2612.TW", "2617.TW", "2636.TW", "2642.TW", "5609.TWO", "2634.TW", "2633.TW", "2607.TW", "2608.TW", "2611.TW",
    "2613.TW", "2614.TW", "2616.TW", "2630.TW", "2640.TW", "2641.TW", "2643.TW", "2645.TW", "5601.TW", "5603.TW",
    "5604.TW", "5607.TW",
    
    # --- 重電/綠能/電纜 ---
    "1519.TW", "1503.TW", "1504.TW", "1513.TW", "1514.TW", "1605.TW", "1609.TW", "6806.TW", "3708.TW", "9958.TW",
    "1522.TW", "1524.TW", "1525.TW", "1526.TW", "1527.TW", "1528.TW", "1529.TW", "1530.TW", "1531.TW", "1532.TW",
    "1533.TW", "1535.TW", "1536.TW", "1537.TW", "1538.TW", "1539.TW", "1540.TW", "1541.TW", "1560.TW", "1568.TW",
    "1582.TW", "1583.TW", "1589.TW", "1590.TW", "1592.TW", "1598.TW", "1603.TW", "1604.TW", "1608.TW", "1611.TW",
    "1612.TW", "1614.TW", "1615.TW", "1616.TW", "1617.TW", "1618.TW", "1626.TW",
    
    # --- 生技醫療 (上市櫃) ---
    "4743.TWO", "4128.TWO", "6461.TWO", "6550.TWO", "4114.TWO", "4162.TWO", "6446.TWO", "6589.TWO", "1795.TW",
    "4105.TWO", "4107.TWO", "4119.TW", "4123.TWO", "4129.TWO", "4133.TW", "4147.TWO", "4152.TWO", "4157.TWO",
    "4163.TWO", "4164.TWO", "4167.TWO", "4168.TWO", "4171.TWO", "4174.TWO", "4180.TWO", "4183.TWO", "4190.TW",
    "6472.TWO", "6547.TWO", "6598.TW", "1760.TW", "1789.TW", "3176.TWO", "1701.TW", "1707.TW", "1710.TW", "1711.TW",
    "1712.TW", "1713.TW", "1714.TW", "1717.TW", "1718.TW", "1720.TW", "1722.TW", "1723.TW", "1724.TW", "1725.TW",
    "1726.TW", "1727.TW", "1730.TW", "1731.TW", "1732.TW", "1733.TW", "1734.TW", "1735.TW", "1736.TW", "1737.TW",
    
    # --- 金融 (上市) ---
    "2881.TW", "2882.TW", "2891.TW", "2886.TW", "2884.TW", "2892.TW", "2885.TW", "2880.TW", "2890.TW", "5871.TW",
    "2801.TW", "2809.TW", "2812.TW", "2816.TW", "2820.TW", "2823.TW", "2832.TW", "2834.TW", "2836.TW", "2838.TW",
    "2845.TW", "2849.TW", "2850.TW", "2851.TW", "2852.TW", "2855.TW", "2867.TW", "2883.TW", "2887.TW", "2888.TW",
    "2889.TW", "2897.TW", "5876.TW", "5880.TW", "6005.TW", "6024.TW",
    
    # --- 營建/資產 ---
    "2501.TW", "2504.TW", "2505.TW", "2506.TW", "2509.TW", "2511.TW", "2514.TW", "2515.TW", "2516.TW", "2520.TW",
    "2524.TW", "2527.TW", "2528.TW", "2530.TW", "2534.TW", "2535.TW", "2536.TW", "2537.TW", "2538.TW", "2539.TW",
    "2540.TW", "2542.TW", "2543.TW", "2545.TW", "2546.TW", "2547.TW", "2548.TW", "2597.TW", "5508.TW", "5511.TW",
    "5515.TW", "5519.TW", "5521.TW", "5522.TW", "5525.TW", "5531.TW", "5533.TW", "5534.TW", "5546.TW",
    
    # --- 傳產龍頭 (塑膠/鋼鐵/水泥/食品) ---
    "1101.TW", "1102.TW", "1216.TW", "1301.TW", "1303.TW", "1326.TW", "1402.TW", "2002.TW", "2105.TW", "2912.TW",
    "9904.TW", "9910.TW", "9914.TW", "9917.TW", "9921.TW", "9941.TW", "9945.TW", "2006.TW", "2010.TW", "2014.TW",
    "2023.TW", "2027.TW", "2028.TW", "2030.TW", "2031.TW", "2032.TW", "2033.TW", "2034.TW", "2038.TW", "2049.TW",
    "2059.TW", "2062.TW", "2069.TW", "1304.TW", "1305.TW", "1307.TW", "1308.TW", "1309.TW", "1310.TW", "1312.TW",
    "1313.TW", "1314.TW", "1315.TW", "1316.TW", "1319.TW", "1321.TW", "1323.TW", "1324.TW", "1325.TW", "1337.TW"
]

# ==========================================
# 🛠️ 運算核心
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
        exp1 = close.ewm(span=fast).mean()
        exp2 = close.ewm(span=slow).mean()
        macd = exp1 - exp2
        hist = macd - macd.ewm(span=signal).mean()
        return hist
    except: return pd.Series()

def analyze_stock(df, ticker_id):
    try:
        if isinstance(df.columns, pd.MultiIndex): df.columns = [c[0] for c in df.columns]
        df = df.sort_index()
        # 濾網
        if len(df) < 200: return None
        # V32 標準：只看有量的 (日均量 > 300 張)
        if df['Volume'].iloc[-1] < 300000: return None 
        
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        
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
            "Technical": {"Slope20": round(slope20, 2), "MACD": "紅" if df_300['MACD_Hist'].iloc[-1] > 0 else "綠"},
            "Display_Info": {"代號": ticker_id, "現價": round(now, 2), "評分": score, "趨勢": trend, "斜率": round(slope20, 2)},
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
# 🖥️ 介面
# ==========================================
st.sidebar.title("💎 V32.13 戰艦 (600大)")
st.sidebar.markdown("---")
st.sidebar.link_button("🧠 開啟 Gemini", "https://gemini.google.com/app", type="primary", use_container_width=True)

mode = st.sidebar.radio("模式", ["掃描 600 大熱門股 (內建)", "手動輸入"])

if mode == "掃描 600 大熱門股 (內建)":
    # 去除重複並確保格式正確
    clean_tickers = list(set(TICKERS_600))
    st.sidebar.success(f"✅ 已載入 {len(clean_tickers)} 檔權值與熱門股")
    target_tickers = clean_tickers
else:
    user_input = st.sidebar.text_area("輸入代號", "2330 2603")
    target_tickers = []
    if user_input:
        target_tickers = [f"{t}.TW" if "." not in t else t for t in user_input.split()]

st.title("💎 V32.13 戰艦 (600大火力全開)")

if st.button("🚀 啟動 600 檔掃描", type="primary"):
    
    st.write(f"📡 正在掃描 {len(target_tickers)} 檔股票 (約需 2~3 分鐘)...")
    results = []
    progress = st.progress(0)
    batch_size = 50 # 批次下載避免塞車
    
    # 這裡會跑比較久，請耐心等候
    total_batches = (len(target_tickers) + batch_size - 1) // batch_size
    
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
        
        # 更新進度條
        current_progress = min((i + batch_size) / len(target_tickers), 1.0)
        progress.progress(current_progress)
        
    if not results:
        st.warning("⚠️ 掃描完成，但沒有符合條件的股票。")
    else:
        results.sort(key=lambda x: x['Score'], reverse=True)
        st.success(f"✅ 掃描完成！共發現 {len(results)} 檔符合 V32 標準的強勢股。")
        
        # 產生檔案
        json_str = json.dumps({"Meta": "V32.13_600", "Data": [r['History_Data'] for r in results]}, ensure_ascii=False)
        prompt_str = f"請分析以下 V32.13 數據 (600大熱門股):\n{json_str}"
        
        c1, c2, c3 = st.columns(3)
        with c1: st.download_button("1️⃣ 下載數據", json_str, "data.json", "application/json", use_container_width=True)
        with c2: st.download_button("2️⃣ 下載指令", prompt_str, "prompt.txt", "text/plain", use_container_width=True)
        with c3: st.link_button("3️⃣ 前往 Gemini ➤", "https://gemini.google.com/app", type="primary", use_container_width=True)
        
        # 顯示結果表格
        st.dataframe(pd.DataFrame([r['Display_Info'] for r in results]), use_container_width=True)
        
        # 圖表
        if results:
            st.divider()
            st.subheader("📈 個股診斷")
            opt = st.selectbox("選擇股票:", [r['ID'] for r in results])
            tgt = next(r for r in results if r['ID'] == opt)
            df = tgt['Chart_Data']
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3])
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='blue'), name='MA20'), row=1, col=1)
            fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Vol'), row=2, col=1)
            fig.update_layout(height=600, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
