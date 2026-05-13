import streamlit as st
import sqlite3
import pandas as pd
import time

# 設定網頁標題與寬度
st.set_page_config(page_title="ESP32 即時溫濕度監測", layout="wide")

st.title("🌡️ ESP32 即時溫濕度監測儀表板")
st.markdown("這個儀表板會即時從 SQLite 資料庫讀取 ESP32 傳送過來的最新感測資料（每 5 秒自動重新整理）。")

DB_NAME = "sensor_data.db"

def get_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        # 讀取最新的 50 筆資料供繪圖使用
        query = "SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 50"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return None

df = get_data()

if df is not None and not df.empty:
    # 呈現最新一筆資料的概況 (Metrics)
    latest_temp = df.iloc[0]['temperature']
    latest_hum = df.iloc[0]['humidity']
    last_update = df.iloc[0]['timestamp']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("即時溫度 (Temperature)", f"{latest_temp} °C")
    col2.metric("即時濕度 (Humidity)", f"{latest_hum} %")
    col3.metric("最後更新時間", last_update)
    
    st.divider()
    
    # 繪製歷史趨勢圖 (Line Chart)
    st.subheader("📊 溫濕度歷史趨勢 (最近 50 筆)")
    
    # 轉換時間戳記格式以供圖表顯示對齊
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # 折線圖時間軸應該從舊到新，因此需要反轉排序
    df_chart = df.sort_values('timestamp').set_index('timestamp')
    st.line_chart(df_chart[['temperature', 'humidity']])
    
    # 顯示原始表格資料 (Dataframe)
    with st.expander("查看原始數據表格 (Raw Data)"):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ 目前資料庫中沒有找到任何資料，或是資料庫連線失敗。請確認 ESP32 是否正在運作。")

# 設定每 5 秒鐘自動重載一次頁面，達到 Live Demo 的效果
time.sleep(5)
st.rerun()
