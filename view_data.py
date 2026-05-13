import sqlite3

def view_data():
    try:
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        
        # Query the latest 20 records
        cursor.execute("SELECT * FROM sensor_data ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        
        if not rows:
            print("There is currently no data in the database.")
            return

        print("--- Latest 50 Sensor Records ---")
        print(f"{'ID':<5} | {'Temperature (°C)':<15} | {'Humidity (%)':<13} | {'Timestamp'}")
        print("-" * 60)
        
        for row in rows:
            print(f"{row[0]:<5} | {row[1]:<15} | {row[2]:<13} | {row[3]}")
            
    except Exception as e:
        print(f"Unable to read database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    view_data()