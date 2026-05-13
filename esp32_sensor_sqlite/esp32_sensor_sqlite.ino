#include <SimpleDHT.h>
#include <WiFi.h>

// ======= WiFi 設定 =======
const char* ssid     = "TP-Link_C267";        // <--- 請替換為你的 WiFi 名稱
const char* password = "71052199";    // <--- 請替換為你的 WiFi 密碼

// ======= 接收端電腦 IP 設定 =======
const char* host = "192.168.0.105";               // <--- 已經尋找到你正確的 Wi-Fi IP 位址
const uint16_t port = 8080;                     // 對應 Python 腳本中的 PORT
// =========================

int pinDHT11 = 15;                              // 把 DHT11 的 Data 腳位接在 GPIO 15
SimpleDHT11 dht11(pinDHT11);

void setup() {
  Serial.begin(115200);
  delay(10);
  
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  // 等待 WiFi 連線
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  byte temperature = 0;
  byte humidity = 0;
  int err = SimpleDHTErrSuccess;
  
  // 讀取 DHT11
  if ((err = dht11.read(&temperature, &humidity, NULL)) != SimpleDHTErrSuccess) {
    Serial.print("Error reading DHT11, err="); 
    Serial.println(err);
    delay(2000);
    return;
  }
  
  // 建立 TCP 連線到 Python 伺服器
  WiFiClient client;
  if (!client.connect(host, port)) {
    Serial.println("Connection to Python server failed.");
    delay(2000);
    return;
  }
  
  // 傳送格式: 溫度,濕度 (組合成單一字串一次送出，避免 TCP 分段斷線)
  String dataStr = String((int)temperature) + "," + String((int)humidity);
  client.println(dataStr);
  client.stop(); // 傳輸完成後關閉連線
  
  // 同步在 Serial Monitor 顯示傳送了什麼資料
  Serial.print("Sent over WiFi: ");
  Serial.print((int)temperature);
  Serial.print(",");
  Serial.println((int)humidity);
  
  // 延遲 6 秒後再次讀取並送出
  delay(6000);
}
