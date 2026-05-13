import socket
import sqlite3
from datetime import datetime
import time

# ======= Settings =======
# 設定監聽所有來自區網的連線
HOST = '0.0.0.0'
PORT = 8080
DB_NAME = 'sensor_data.db'
# ========================

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Create a table with Primary key, temperature(float), humidity(float), timestamp
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Database initialization failed: {e}")
    finally:
        if conn:
            conn.close()

def main():
    print("=== ESP32 WiFi to SQLite Receiver ===")
    init_db()
    print(f"Starting TCP server on {HOST}:{PORT}...")

    # Create socket (IPv4, TCP)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 允許 port 重複使用 (避免重啟時卡住)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print("Waiting for ESP32 to connect and send data... (Press Ctrl+C to stop)")
        
        try:
            while True:
                # 接受來自 ESP32 的連線
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    
                    try:
                        line = data.decode('utf-8').strip()
                    except UnicodeDecodeError:
                        continue  # Skip unreadable characters
                        
                    if not line:
                        continue
                        
                    # If the string contains a comma and no error message
                    if ',' in line and not line.startswith('Sys') and not line.startswith('Err'):
                        try:
                            temp_str, hum_str = line.split(',')
                            temperature = float(temp_str.strip())
                            humidity = float(hum_str.strip())

                            # Store temperature and humidity into SQLite
                            db_conn = sqlite3.connect(DB_NAME)
                            cursor = db_conn.cursor()
                            cursor.execute(
                                "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)",
                                (temperature, humidity)
                            )
                            db_conn.commit()
                            db_conn.close()

                            print(f"[{datetime.now()}] [{addr[0]}] Received and stored: Temperature {temperature}°C, Humidity {humidity}%")

                        except ValueError:
                            print(f"[{datetime.now()}] Data format error, skipping: '{line}'")
                        except sqlite3.Error as e:
                            print(f"[{datetime.now()}] Database write failed: {e}")
                    else:
                        print(f"[{datetime.now()}] ESP32 Message: {line}")
                        
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")

if __name__ == '__main__':
    main()