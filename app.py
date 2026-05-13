from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_NAME = "sensor_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 建立一個有 Primary key, 溫度(float), 濕度(float), timestamp 的資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/upload', methods=['POST'])
def upload_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        temperature = data.get('temperature')
        humidity = data.get('humidity')

        if temperature is None or humidity is None:
            return jsonify({'error': 'Missing temperature or humidity'}), 400

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)", (temperature, humidity))
        conn.commit()
        conn.close()

        print(f"[{datetime.now()}] Data received: Temp {temperature}°C, Hum {humidity}%")
        return jsonify({'message': 'Data inserted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
    # 執行在 0.0.0.0 讓區網內的 ESP32 能夠連線找到這台電腦
    app.run(host='0.0.0.0', port=5000, debug=True)
