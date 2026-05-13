# hw01 專案開發日誌 (Development Log)

這份文件將用來記錄我們後續所有關於此專案的開發對話與決策。

---

## 🟢 階段一：專案啟動與基礎串口通訊 (Serial 通訊)

**[User]**
> 我有一個 ESP32 開發板和一個 DHT11 溫濕度感測器。我想把讀取到的溫度與濕度資料，透過 USB 傳輸線 (Serial COM port) 傳到我的電腦上，然後用 Python 將這些資料寫入到 SQLite 資料庫中作長期的紀錄。
> 另外，請再幫我寫一個可以用來查看資料庫最新紀錄的 Python 腳本 `view_data.py`。

**[Assistant]**
> 沒問題！這是一個很棒的物聯網基礎專案。我們可以分為三個檔案來完成：
> 1. **`esp32_sensor_sqlite.ino`**：會使用 `SimpleDHT` 函式庫讀取 DHT11，並透過 `Serial.println()` 將讀到的「溫度,濕度」字串傳到底層。
> 2. **`serial_to_sqlite.py`**：在電腦端使用 `pyserial` 監聽 COM Port，收到逗號分隔的格式後，寫入到名為 `sensor_data.db` 的 SQLite 資料庫。
> 3. **`view_data.py`**：簡單讀取 `sensor_data.db` 裡面的資料，列印出最新幾筆的溫濕度數據供除錯用。

---

## 🟢 階段二：介面與排版優化

**[User]**
> `view_data.py` 成功讀取到資料了 但是終端機輸出來的資料格式有點擠不容易看 幫我把表頭排版弄整齊一點，顯示 ID、溫度 (°C)、濕度 (%) 和時間戳記，並且一次只撈出最新的 50 筆紀錄

**[Assistant]**
> 了解，我們可以使用 Python 的字串格式化 (f-string) 來鎖定欄位寬度以達到對齊的效果。
> 在 `view_data.py` 的 SQL 查詢語法中加入 `ORDER BY id DESC LIMIT 50`。

---

## 🟢 階段三：架構升級 ─ 從 Serial 轉換為 WiFi TCP 通訊

**[User]**
> 修改 `serial_to_sqlite.py` 和 ESP32 的程式碼，把資料傳輸方式從原本的 COM port 連線改成透過 WiFi 區域網路傳輸。我的 WiFi SSID 是 "TP-Link_C267"、密碼 "71052199"。我電腦的 IP 是 "192.168.0.105"。用 TCP Socket 的方式實作

**[Assistant]**
> 這是個很棒的升級！讓裝置具備了真正的 IoT 雛形。為了達成這個目標，我們將原本走 Serial 的機制改為 TCP Socket：
> 1. **ESP32 方面：** 引入 `<WiFi.h>` 建立 `WiFiClient` 將感測資料傳送至 `192.168.0.105:8080`。
> 2. **Python 方面：** 改掉原有的 `pyserial`，改用內建的 `socket` 套件來監聽 `0.0.0.0:8080`，並將解析到的溫濕度寫入資料庫。

---

## 🟢 階段四：嘗試更現代化的 Web API 架構 (HTTP POST)

**[User]**
> 幫我寫一個可以用 Flask 框架來接收資料的 `app.py` 一樣把資料存入 `sensor_data.db` 裡面。

**[Assistant]**
> 使用 HTTP API 是目前最主流的資料介接做法。你可以使用 Flask 來架設一個輕量級的 Web Server `app.py`。
> 建立一個 `/upload` (POST) 路由，將前端發送來的 `temperature` 和 `humidity` 解析後寫入 SQLite 中。如此一來 ESP32 也只要改發 HTTP POST 即可輕鬆對應！

---

## 🟢 階段五：新增 Streamlit 即時影像儀表板 (Live Demo)

**[User]**
> 現在我們的專案可以從感測器讀取數據並且透過WiFi傳輸存進資料庫，幫我新增一個將讀取到的資訊 live demo on streamlit 的功能

**[Assistant]**
> 太棒了！有了一套資料後端的架構，使用 Streamlit 來做即時的前端網頁展示是最合適且直觀的選擇。
> 
> 我已經為專案新增了 **`dashboard.py`** 作為儀表板程式：
> 1. 它會自動連接 `sensor_data.db` 抓取最新的 100 筆資料。
> 2. 以大字體呈現最新的「即時溫度」與「即時濕度」獨立指標 (Metrics)，以及時間遞增的「歷史趨勢折線圖 (Line Chart)」。
> 3. 透過內建的自動重新整理機制 (`st.rerun()`)，系統會每隔 5 秒自動重新讀取資料庫刷新頁面，達成 Live Demo 即時觀測的效果！
> 
> 您只要在終端機執行 `streamlit run dashboard.py` 即可啟動並在瀏覽器中觀看這個動態儀表板。

---

## 🟢 階段六：收斂折線圖顯示範圍

**[User]**
> 折線圖改成最近讀取到的10筆資料就好

**[Assistant]**
> 沒問題！為了讓畫面更簡潔不凌亂，我已經將 `dashboard.py` 的讀取數量限制從 100 筆修改為 `LIMIT 10`。現在畫面上的折線圖與展開的資料表格，都只會專注在最新獲取的這 10 筆即時數據上。

---

## 🟢 階段七：啟動完整本地端 AIoT 模擬測試機制 (Simulated Demo)

**[User]**
> 基於既有架構幫我寫一支模擬版本的程式 esp32_sim.py，並建立自動化腳本包含建立環境、安裝套件與驗證。

**[Assistant]**
> 我已經為這個專案快速建立並自動化啟動了完整的本地端 AIoT 模擬，不包含任何網路模擬或傳輸延遲，確保能在本地即時存取：
> 1. **`esp32_sim.py`**: 用來「模擬 ESP32 每 5 秒發送一次假的溫濕度感測資料」，透過 HTTP POST 送到本地後端。
> 2. **`flask_backend.py`**: 作為輕量級後端，接收在 `/sensor` 端點的資料後寫入 SQLite (`aiotdb.db`)。
> 3. **`streamlit_frontend.py`**: 作為即時讀取資料庫的前端 Dashboard，展示指標 (KPIs)、歷史表格和趨勢圖。
> 4. **自動化執行 (`setup_demo.ps1`)**: 該腳本負責啟動虛擬環境 (venv)、安裝所有需求套件 (`requirements.txt`)，並啟動所有的背景服務。在等待約 8 秒後執行 Health Check 以確保成功插入資料庫與各服務連線。
> 
> **🖧 服務存取與 Rerun 指令:**
> - HTTP 後端接收端點: `http://localhost:5000/sensor`
> - Streamlit 前端儀表板: `http://localhost:8501`
> 
> 若您有關閉視窗想**重新啟動**這些軟體，可執行以下指令 (在啟動 venv 後)：
> - `python flask_backend.py`
> - `python esp32_sim.py`
> - `streamlit run streamlit_frontend.py`

---

## 🟢 階段八：擴大折線圖顯示範圍至 50 筆

**[User]**
> 可以把最近10筆改成50筆嗎

**[Assistant]**
> 當然沒問題！我已經將 `streamlit_frontend.py` 與 `dashboard.py` 兩支儀表板程式碼中的 SQL 資料庫讀取限制，同步從 `LIMIT 10` 放大調整回了 `LIMIT 50`，並一併更新了畫面上顯示的標題。
> 利用這長達 50 筆的樣本資訊（相當於 50次的 5秒自動更新 = 近 4 分鐘），您將能更清晰地觀察整體感測資料的完整起伏與趨勢變化！

---

## 🟢 階段九：專案推播與版控 (Push to GitHub)

**[User]**
> 幫我把所有東西push到github

**[Assistant]**
> 好的！為了維持遠端存放區的乾淨整潔，我已經先建立了一個 `.gitignore` 檔案，確保會頻繁變動的 SQLite 資料庫（`*.db`）以及佔用空間極大且不需要的虛擬環境資料夾（`venv`）不會被一併 push 到 GitHub 上。目前我已經完成了所有的 commit 操作，並送出了 Push 請求。
