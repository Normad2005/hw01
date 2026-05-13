"""
app.py  ─  Streamlit Cloud 部署入口
────────────────────────────────────────────────
架構說明：
  ┌──────────────────────────────────────────┐
  │          同一個 Python Process           │
  │                                          │
  │  Thread-1: Flask backend (port 5000)     │
  │    └─ flask_backend.py 的邏輯（原封不動）│
  │                                          │
  │  Thread-2: ESP32 模擬器                  │
  │    └─ esp32_sim.py 的邏輯（原封不動）    │
  │                                          │
  │  Main: Streamlit UI                      │
  │    └─ dashboard.py 的邏輯（原封不動）    │
  └──────────────────────────────────────────┘

ESP32 Sim → POST /sensor → Flask → aiotdb.db → Streamlit 讀取
（原始資料流完整保留）
"""

import threading
import time
import sqlite3
import random
import requests
from datetime import datetime, timezone, timedelta

import streamlit as st
import pandas as pd

from flask import Flask, request, jsonify

# 台灣時區 UTC+8
TZ_TAIWAN = timezone(timedelta(hours=8))

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
        # 明確使用台灣時間（UTC+8）作為 timestamp，避免伺服器時區差異
        tw_now = datetime.now(TZ_TAIWAN).strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)",
            (temperature, humidity, tw_now)
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
    # 等 Flask 啟動完畢再開始送資料
    time.sleep(3)
    # 以合理的初始值為起點，之後每次只小幅漂移（模擬真實 DHT11 感測器）
    temperature = round(random.uniform(25.0, 27.0), 2)
    humidity    = round(random.uniform(58.0, 62.0), 2)
    while True:
        # 每次最多漂移 ±0.1°C / ±0.2%，曲線更平滑
        temperature = round(max(22.0, min(32.0, temperature + random.uniform(-0.1, 0.1))), 2)
        humidity    = round(max(50.0, min(75.0, humidity    + random.uniform(-0.2, 0.2))), 2)
        data = {
            "temperature": temperature,
            "humidity": humidity
        }
        try:
            response = requests.post(SERVER_URL, json=data)
            print(f"Sent: {data}, Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data: {e}")

        time.sleep(5)


# ══════════════════════════════════════════════════════════
#  背景執行緒啟動器
#  ⚠️  st.session_state 是每個 browser session 獨立的，
#      不能用來做 process 級別的 once-only guard。
#      改用 module 層級的 Lock + 旗標，確保整個 Python
#      process 只啟動一次 Flask 和模擬器，無論有多少 session。
# ══════════════════════════════════════════════════════════
def _start_flask():
    init_db()
    _flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def _start_simulator():
    send_data()

# ══════════════════════════════════════════════════════════
#  Process-level once-only guard
#  Streamlit 每次 rerun 都會重新執行整個 script，
#  module-level 變數也會被重置。
#  用 builtins 模組當作 process 全域命名空間，
#  確保 Flask 和模擬器只被啟動一次。
# ══════════════════════════════════════════════════════════
import builtins

if not getattr(builtins, "_hw01_bg_started", False):
    builtins._hw01_bg_started = True   # 設定全域旗標

    flask_thread = threading.Thread(target=_start_flask, daemon=True, name="FlaskBackend")
    flask_thread.start()

    sim_thread = threading.Thread(target=_start_simulator, daemon=True, name="ESP32Sim")
    sim_thread.start()


# ══════════════════════════════════════════════════════════
#  原始 dashboard.py 的邏輯（原封不動）
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
