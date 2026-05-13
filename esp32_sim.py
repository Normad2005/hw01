import time
import requests
import random

SERVER_URL = "http://127.0.0.1:5000/sensor"

def send_data():
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

if __name__ == "__main__":
    print("Starting ESP32 simulation...")
    send_data()
