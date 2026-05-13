# 🌡️ AIoT HW01 — ESP32 即時溫濕度監測系統

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aiothw2-ivnok7gzhmfdexyynl9as4.streamlit.app/)

> **Live Demo 👉 [https://aiothw2-ivnok7gzhmfdexyynl9as4.streamlit.app/](https://aiothw2-ivnok7gzhmfdexyynl9as4.streamlit.app/)**

---

## 📌 作業說明

本作業實作一套完整的 **AIoT 資料蒐集與視覺化系統**，模擬 ESP32 開發板搭配 DHT11 溫濕度感測器，透過 Wi-Fi 將感測資料即時上傳至後端伺服器，並以 Streamlit 儀表板呈現即時趨勢。

### 系統架構

```
ESP32 + DHT11
     │  Wi-Fi HTTP POST（每 5 秒）
     ▼
Flask REST API  (/sensor)
     │  寫入
     ▼
SQLite 資料庫 (aiotdb.db)
     │  查詢最新 50 筆
     ▼
Streamlit Dashboard（每 5 秒自動重整）
```

---

## 🗂️ 專案結構

| 檔案 | 說明 |
|------|------|
| `app.py` | Streamlit Cloud 部署入口，整合 Flask、模擬器與儀表板 |
| `flask_backend.py` | Flask REST API，接收感測器資料並寫入 SQLite |
| `esp32_sim.py` | 模擬 ESP32 傳送溫濕度資料（用於本地測試） |
| `dashboard.py` | Streamlit 儀表板，從 SQLite 讀取並繪製即時折線圖 |
| `serial_to_sqlite.py` | 透過 Serial port 讀取真實 ESP32 資料並存入 DB |
| `sketch_mar10a/` | ESP32 Arduino 程式碼（DHT11 + Wi-Fi HTTP 上傳） |
| `esp32_sensor_sqlite/` | ESP32 SQLite 相關韌體 |
| `requirements.txt` | Python 套件依賴清單 |

---

## 🚀 功能特色

- **即時溫濕度顯示**：Metric 卡片顯示最新一筆溫度、濕度與更新時間
- **歷史趨勢折線圖**：顯示最近 50 筆資料的溫濕度變化曲線
- **原始資料表格**：可展開查看完整的資料庫紀錄
- **每 5 秒自動重整**：模擬 ESP32 即時推送的效果
- **台灣時間（UTC+8）**：timestamp 統一使用台灣時區

---

## 🛠️ 本地執行方式

### 安裝套件
```bash
pip install -r requirements.txt
```

### 方式一：一鍵啟動（Streamlit 整合版）
```bash
streamlit run app.py
```
> Flask backend、ESP32 模擬器、Streamlit 儀表板會同時在同一個 process 中啟動。

### 方式二：分開啟動（原始架構）
```bash
# Terminal 1 - 啟動 Flask 後端
python flask_backend.py

# Terminal 2 - 啟動 ESP32 模擬器
python esp32_sim.py

# Terminal 3 - 啟動 Streamlit 儀表板
streamlit run dashboard.py
```

---

## 📡 Flask API 說明

### `POST /sensor`

接收 ESP32 上傳的溫濕度資料。

**Request Body（JSON）：**
```json
{
  "temperature": 26.5,
  "humidity": 62.3
}
```

**Response：**
```json
{
  "status": "success",
  "message": "Data saved"
}
```

---

## 🔧 硬體需求（真實 ESP32 環境）

| 元件 | 規格 |
|------|------|
| 微控制器 | ESP32 開發板 |
| 感測器 | DHT11 溫濕度感測器 |
| 連線方式 | Wi-Fi 2.4GHz |
| 上傳協定 | HTTP POST（JSON） |

---

## 📊 Live Demo

> 以下 Demo 使用 Python 模擬 ESP32 傳送資料，資料流與真實硬體完全相同。

**🔗 [https://aiothw2-ivnok7gzhmfdexyynl9as4.streamlit.app/](https://aiothw2-ivnok7gzhmfdexyynl9as4.streamlit.app/)**
