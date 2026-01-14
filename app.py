# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import warnings
import time

warnings.filterwarnings("ignore")

# ==========================================
# 💎 網頁設定
# ==========================================
st.set_page_config(page_title="V32.18 精兵戰情室 (800)", page_icon="💎", layout="wide")

# ==========================================
# 📜 1. 內建 800 大精選名單
# ==========================================
def get_800_market_tickers():
    # 上市精選 (約 550 檔) - 涵蓋半導體、AI、航運、金融、傳產龍頭
    tw_list = [
        "1101","1102","1216","1301","1303","1326","1402","1503","1504","1513","1514","1519","1560","1590","1605","1609","1717","1722","1795","2002",
        "2014","2027","2049","2059","2105","2201","2204","2301","2303","2308","2312","2313","2317","2323","2324","2327","2329","2330","2337","2338",
        "2340","2344","2345","2347","2351","2352","2353","2354","2356","2357","2359","2360","2362","2363","2365","2367","2368","2369","2371","2376",
        "2377","2379","2382","2383","2385","2388","2392","2393","2395","2401","2404","2408","2409","2412","2419","2421","2436","2439","2441","2449",
        "2451","2454","2455","2458","2464","2474","2481","2485","2492","2498","2501","2511","2515","2520","2534","2542","2547","2548","2603","2605",
        "2606","2609","2610","2615","2618","2634","2637","2801","2809","2812","2834","2838","2845","2850","2851","2852","2855","2867","2880","2881",
        "2882","2883","2884","2885","2886","2887","2888","2889","2890","2891","2892","2912","3003","3005","3006","3008","3010","3014","3016","3017",
        "3019","3021","3022","3023","3034","3035","3036","3037","3041","3042","3044","3045","3049","3055","3059","3060","3062","3090","3130","3189",
        "3209","3229","3231","3257","3296","3305","3311","3312","3321","3338","3346","3356","3376","3380","3406","3413","3419","3432","3437","3443",
        "3450","3454","3481","3501","3515","3518","3528","3530","3532","3533","3535","3536","3545","3550","3557","3563","3576","3583","3588","3591",
        "3596","3605","3607","3617","3622","3653","3661","3665","3669","3673","3682","3694","3701","3702","3703","3704","3705","3706","3708","3711",
        "3714","3715","4119","4137","4142","4526","4532","4551","4566","4720","4755","4763","4904","4906","4912","4915","4919","4927","4930","4934",
        "4935","4938","4952","4958","4960","4961","4967","4968","4977","5203","5215","5222","5234","5243","5258","5269","5284","5285","5288","5305",
        "5388","5434","5469","5471","5519","5522","5534","5608","5871","5876","5880","6112","6116","6120","6133","6139","6152","6176","6189","6191",
        "6192","6196","6202","6205","6206","6209","6213","6214","6215","6216","6224","6230","6235","6239","6243","6257","6269","6271","6277","6278",
        "6281","6282","6285","6405","6409","6414","6415","6431","6438","6442","6443","6451","6456","6477","6491","6505","6515","6525","6531","6533",
        "6541","6550","6552","6558","6579","6582","6585","6592","6598","6605","6643","6666","6668","6669","6670","6671","6672","6689","6691","6695",
        "6706","6715","6719","6743","6753","6754","6756","6768","6770","6776","6781","6782","6789","6799","6805","6806","6830","6834","6901","6933",
        "8011","8016","8021","8028","8039","8046","8050","8069","8070","8072","8081","8110","8112","8114","8131","8150","8163","8210","8215","8222",
        "8261","8271","8341","8367","8404","8422","8442","8454","8463","8464","8478","9904","9910","9914","9917","9921","9941","9945","9958"
    ]
    
    # 上櫃精選 (約 250 檔) - 涵蓋光通訊、生技、散熱、IP、CPO
    two_list = [
        "1264","1565","1569","1789","1795","2065","2231","2732","2916","3062","3078","3081","3088","3105","3131","3141","3163","3207","3211","3213",
        "3217","3218","3227","3228","3234","3260","3264","3265","3289","3293","3303","3313","3324","3354","3360","3362","3363","3374","3402","3416",
        "3441","3455","3479","3483","3484","3491","3498","3508","3512","3516","3526","3527","3529","3540","3541","3548","3551","3552","3556","3558",
        "3564","3570","3580","3581","3587","3594","3597","3611","3615","3624","3652","3663","3664","3675","3680","3685","3689","3693","3707","3709",
        "3710","3713","4105","4107","4114","4128","4129","4130","4147","4157","4162","4174","4743","4908","4909","4911","4933","4944","4953","4966",
        "4974","4979","5009","5202","5210","5227","5236","5251","5263","5272","5274","5287","5289","5291","5299","5315","5340","5347","5351","5353",
        "5371","5410","5425","5426","5432","5438","5439","5443","5450","5457","5464","5475","5483","5493","5508","5536","5904","6015","6016","6023",
        "6026","6104","6109","6111","6113","6118","6121","6122","6123","6124","6125","6126","6127","6129","6134","6138","6140","6143","6146","6147",
        "6150","6156","6158","6160","6161","6163","6167","6173","6175","6180","6182","6186","6187","6188","6190","6194","6203","6204","6207","6208",
        "6212","6217","6219","6220","6223","6227","6229","6231","6233","6234","6237","6244","6245","6261","6263","6266","6270","6274","6275","6276",
        "6279","6284","6287","6290","6411","6419","6421","6425","6432","6435","6446","6461","6462","6465","6470","6472","6485","6488","6494","6496","6499",
        "6506","6508","6509","6510","6512","6514","6516","6523","6527","6532","6535","6538","6546","6547","6548","6560","6561","6568","6569","6576","6589",
        "6593","6603","6612","6615","6624","6640","6664","6667","6679","6683","6690","6693","6697","6712","6727","6728","6732","6741","6747","6751","6752",
        "6763","6775","6785","6787","6788","6803","6829","6841","6854","6873","6903","6914","6919","6937","7402","7703","7751","8034","8038","8040","8042",
        "8044","8047","8049","8054","8059","8064","8066","8069","8071","8074","8076","8080","8083","8084","8085","8086","8087","8088","8089","8091","8096",
        "8099","8107","8109","8111","8121","8147","8155","8182","8183","8234","8255","8277","8279","8299","8342","8354","8358","8383","8390","8403","8409",
        "8415","8416","8420","8431","8432","8433","8436","8905","8906","8916","8924","8928","8933","8936","8938","8942","9950","9951"
    ]
    
    full = [f"{t}.TW" for t in tw_list] + [f"{t}.TWO" for t in two_list]
    return list(set(full))

# ==========================================
# 🔍 2. 您的 VIP 20 檔 (確保這些一定有)
# ==========================================
MY_VIP_LIST = [
    "2327.TW", "2404.TW", "3021.TW", "6192.TW", "6834.TW", 
    "3081.TWO", "3402.TWO", "6693.TWO", "7703.TWO", "1590.TW", 
    "2303.TW", "2305.TW", "2312.TW", "2313.TW", "2329.TW", 
    "2367.TW", "2369.TW", "2412.TW", "2419.TW", "2441.TW"
]

# 整合名單 (800 + VIP)
MARKET_LIST = get_800_market_tickers()

# 自動補漏：確保 VIP 在裡面
missing_vips = set(MY_VIP_LIST) - set(MARKET_LIST)
if missing_vips:
    MARKET_LIST += list(missing_vips)

ALL_TICKERS = list(set(MARKET_LIST))

# ==========================================
# 🛠️ 數據核心
# ==========================================
@st.cache_data(ttl=300)
def get_quote_data(tickers):
    try:
        chunk_size = 100
        all_data = pd.DataFrame()
        for i in range(0, len(tickers), chunk_size):
            chunk = tickers[i:i+chunk_size]
            df = yf.download(chunk, period="5d", interval="1d", group_by='ticker', auto_adjust=False, progress=False)
            if all_data.empty: all_data = df
            else: all_data = pd.concat([all_data, df], axis=1)
        return all_data
    except: return None

def get_stock_data_batch(tickers):
    try: return yf.download(tickers, period="2y", interval="1d", group_by='ticker', auto_adjust=False, progress=False)
    except: return None

# 技術指標 (維持 V32 標準)
def calculate_slope(series, window=5):
    try:
        y = series.tail(window).values
        x = np.arange(len(y))
        if len(y) == 0: return 0
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
        if len(df) < 200: return None
        if df['Volume'].iloc[-1] < 300000: return None # 300張濾網
        
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        df['K'], df['D'] = calculate_kd(df['High'], df['Low'], df['Close'])
        df['MACD_Hist'] = calculate_macd(df['Close'])
        slope20 = calculate_slope(df['MA20'])
        
        df_300 = df.tail(300).copy()
        now = float(df_300['Close'].iloc[-1])
        
        score = 50
        trend = "震盪"
        if df_300['MA5'].iloc[-1] > df_300['MA10'].iloc[-1] > df_300['MA20'].iloc[-1]: score += 20
        if slope20 > 0: 
            score += 30
            trend = "🔥🔥三線全紅" if score >= 80 else "多頭排列"
        if df_300['MACD_Hist'].iloc[-1] > 0: score += 10
        if df_300['K'].iloc[-1] > df_300['D'].iloc[-1]: score += 10

        return {
            "ID": ticker_id, "Price": round(now, 2), "Score": score, "Trend_Desc": trend,
            "Display_Info": {"代號": ticker_id, "現價": round(now, 2), "評分": score, "趨勢": trend, "斜率": round(slope20, 2)},
            "History_Data": {
                "Date_Seq": [d.strftime('%m-%d') for d in df_300.index],
                "Price_Seq": [round(x, 1) for x in df_300['Close'].tolist()],
                "Vol_Seq": [int(v/1000) for v in df_300['Volume'].tolist()]
            },
            "Chart_Data": df_300
        }
    except: return None

# ==========================================
# 🖥️ 戰情室介面
# ==========================================
st.title("💎 V32.18 精兵戰情室 (800+)")

if missing_vips:
    st.toast(f"✅ 已自動補入 {len(missing_vips)} 檔 VIP 股", icon="🛡️")

# 1. 看板
c1, c2, c3 = st.columns(3)
with c1: st.metric("監控範圍", f"{len(ALL_TICKERS)} 檔")
with c2: st.metric("VIP 重點", f"{len(MY_VIP_LIST)} 檔")
with c3: st.metric("連線狀態", "穩定")

st.divider()

# 2. 獲取報價 (Background)
if 'quote_done' not in st.session_state: st.session_state['quote_done'] = False

if not st.session_state['quote_done']:
    if st.button("📡 更新戰情室報價 (800檔)"):
        with st.spinner(f"正在連線更新 {len(ALL_TICKERS)} 檔報價..."):
            raw_data = get_quote_data(ALL_TICKERS)
            market_summary = []
            for t in ALL_TICKERS:
                try:
                    df_t = raw_data[t] if t in raw_data.columns.levels[0] else raw_data
                    if not df_t.empty:
                        last = df_t.iloc[-1]
                        prev = df_t.iloc[-2]
                        c = float(last['Close'])
                        p = float(prev['Close'])
                        v = int(last['Volume'])
                        pct = ((c - p) / p) * 100
                        market_summary.append({"代號": t, "現價": round(c, 2), "漲跌幅%": round(pct, 2), "成交量": v})
                except: pass
            st.session_state['quote_df'] = pd.DataFrame(market_summary)
            st.session_state['quote_done'] = True
            st.rerun()

# 3. 顯示戰情
if st.session_state['quote_done']:
    df_m = st.session_state['quote_df']
    
    st.subheader("👀 VIP 監控")
    df_vip = df_m[df_m['代號'].isin(MY_VIP_LIST)].copy()
    st.dataframe(df_vip.style.format({"漲跌幅%": "{:+.2f}%"}).background_gradient(subset=['漲跌幅%'], cmap='RdYlGn'), use_container_width=True)
    
    col_L, col_R = st.columns(2)
    with col_L:
        st.subheader("🏆 漲幅排行榜 Top 20")
        st.dataframe(df_m.sort_values('漲跌幅%', ascending=False).head(20), use_container_width=True)
    with col_R:
        st.subheader("🔥 成交量排行榜 Top 20")
        st.dataframe(df_m.sort_values('成交量', ascending=False).head(20), use_container_width=True)

st.divider()

# 4. 深度掃描
st.header("🛠️ 深度運算 (產出 AI 數據)")
if st.button("🚀 啟動 800 檔深度掃描", type="primary"):
    st.write(f"📡 開始掃描 {len(ALL_TICKERS)} 檔股票 (約需 3~5 分鐘)...")
    results = []
    progress = st.progress(0)
    batch_size = 50
    
    for i in range(0, len(ALL_TICKERS), batch_size):
        batch = ALL_TICKERS[i:i+batch_size]
        try:
            data = get_stock_data_batch(batch)
            if data is not None:
                for t in batch:
                    try:
                        df = data[t] if t in data.columns.levels[0] else pd.DataFrame()
                        if not df.empty:
                            res = analyze_stock(df, t)
                            if res: results.append(res)
                    except: pass
        except: pass
        progress.progress(min((i+batch_size)/len(ALL_TICKERS), 1.0))
    
    if results:
        results.sort(key=lambda x: x['Score'], reverse=True)
        st.success(f"✅ 完成！共 {len(results)} 檔。")
        
        json_str = json.dumps({"Meta": "V32.18", "Data": [r['History_Data'] for r in results]}, ensure_ascii=False)
        prompt_str = f"請分析以下數據:\n{json_str}"
        
        c1, c2, c3 = st.columns(3)
        with c1: st.download_button("1️⃣ 下載數據", json_str, "data.json", "application/json")
        with c2: st.download_button("2️⃣ 下載指令", prompt_str, "prompt.txt", "text/plain")
        with c3: st.link_button("3️⃣ 前往 Gemini ➤", "https://gemini.google.com/app", type="primary")
        
        st.dataframe(pd.DataFrame([r['Display_Info'] for r in results]), use_container_width=True)
