"""
streamlit_app.py  ─  Streamlit Cloud 部署入口
────────────────────────────────────────────────
架構說明：
  ┌──────────────────────────────────────────┐
  │          同一個 Python Process           │
  │                                          │
  │  Thread-1: Flask backend (port 5000)     │
  │    └─ flask_backend.py 的邏輯（原封不動）│
  │                                          │
  │  Thread-2: ESP32 模擬器                   │
  │    └─ esp32_sim.py 的邏輯（原封不動）    │
  │                                          │
  │  Main: Streamlit UI                      │
  │    └─ dashboard.py 的邏輯（原封不動）    │
  └──────────────────────────────────────────┘

Flask 寫入 aiotdb.db → Streamlit 讀取 aiotdb.db
（原始資料流完整保留）
"""

import threading
import time
import sqlite3
import random
import requests

import streamlit as st
import pandas as pd

from flask import Flask, request, jsonify

# ══════════════════════════════════════════════════════════
#  原始 flask_backend.py 的邏輯（原封不動）
# ══════════════════════════════════════════════════════════
_flask_app = Flask(__name__)
DB_NAME = "aiotdb.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@_flask_app.route('/sensor', methods=['POST'])
def receive_data():
    data = request.json
    if not data or 'temperature' not in data or 'humidity' not in data:
        return jsonify({"error": "Invalid data format"}), 400

    temperature = data['temperature']
    humidity = data['humidity']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)",
            (temperature, humidity)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════
#  原始 esp32_sim.py 的邏輯（原封不動）
# ══════════════════════════════════════════════════════════
SERVER_URL = "http://127.0.0.1:5000/sensor"

def send_data():
    # 等 Flask 啟動完畢
    time.sleep(3)
    while True:
        temperature = random.uniform(20.0, 35.0)
        humidity = random.uniform(40.0, 80.0)
        data = {
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2)
        }
        try:
            response = requests.post(SERVER_URL, json=data)
            print(f"Sent: {data}, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data: {e}")

        time.sleep(5)


# ══════════════════════════════════════════════════════════
#  背景執行緒啟動器（只在整個程序生命週期啟動一次）
# ══════════════════════════════════════════════════════════
def _start_flask():
    """在背景執行緒中啟動 Flask（使用 werkzeug 的非 debug 模式）"""
    init_db()
    _flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def _start_simulator():
    """在背景執行緒中啟動 ESP32 模擬器"""
    send_data()

# 利用 st.session_state 確保背景執行緒只啟動一次
if "background_started" not in st.session_state:
    st.session_state.background_started = True

    flask_thread = threading.Thread(target=_start_flask, daemon=True, name="FlaskBackend")
    flask_thread.start()

    sim_thread = threading.Thread(target=_start_simulator, daemon=True, name="ESP32Sim")
    sim_thread.start()


# ══════════════════════════════════════════════════════════
#  原始 dashboard.py 的邏輯（原封不動，僅搬移至此）
# ══════════════════════════════════════════════════════════

# 設定網頁標題與寬度
st.set_page_config(page_title="ESP32 即時溫濕度監測", layout="wide")

st.title("🌡️ ESP32 即時溫濕度監測儀表板")
st.markdown("這個儀表板會即時從 SQLite 資料庫讀取 ESP32 傳送過來的最新感測資料（每 5 秒自動重新整理）。")

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
