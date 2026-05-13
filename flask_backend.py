import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
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

@app.route('/sensor', methods=['POST'])
def receive_data():
    data = request.json
    if not data or 'temperature' not in data or 'humidity' not in data:
        return jsonify({"error": "Invalid data format"}), 400

    temperature = data['temperature']
    humidity = data['humidity']

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)", (temperature, humidity))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data saved"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    # 執行在 5000 port
    app.run(host='0.0.0.0', port=5000, debug=False)
