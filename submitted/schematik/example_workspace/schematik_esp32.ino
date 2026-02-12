#include <Wire.h>
#include <DHT.h>
#include <Adafruit_BMP280.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Pin Definitions
#define DHT22_1_DATA 4
#define BMP280_2_SDA 21
#define BMP280_2_SCL 22
#define SSD1306_OLED_3_SDA 21
#define SSD1306_OLED_3_SCL 22
#define BUZZER_4_SIGNAL 2

// DHT22 Configuration
#define DHTTYPE DHT22
DHT dht(DHT22_1_DATA, DHTTYPE);

// BMP280 Configuration
Adafruit_BMP280 bmp;

// OLED Configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Configuration
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
const char* mqtt_client_id = "ESP32_Weather_Station";
const char* mqtt_topic_temp = "weather/temperature";
const char* mqtt_topic_humidity = "weather/humidity";
const char* mqtt_topic_pressure = "weather/pressure";

WiFiClient espClient;
PubSubClient mqtt(espClient);

// Temperature Alert Configuration
#define TEMP_ALERT_THRESHOLD 35.0

// Timing Variables
unsigned long lastMqttPublish = 0;
const unsigned long mqttPublishInterval = 30000; // 30 seconds
unsigned long lastDisplayUpdate = 0;
const unsigned long displayUpdateInterval = 2000; // 2 seconds

// Sensor Data
float temperature = 0.0;
float humidity = 0.0;
float pressure = 0.0;

// Buzzer State
bool buzzerActive = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize Buzzer
  pinMode(BUZZER_4_SIGNAL, OUTPUT);
  digitalWrite(BUZZER_4_SIGNAL, LOW);
  
  // Initialize I2C
  Wire.begin(BMP280_2_SDA, BMP280_2_SCL);
  
  // Initialize DHT22
  dht.begin();
  
  // Initialize BMP280
  if (!bmp.begin(0x76)) {
    Serial.println("Could not find BMP280 sensor!");
    // Try alternate address
    if (!bmp.begin(0x77)) {
      Serial.println("BMP280 initialization failed!");
    }
  }
  
  // BMP280 Default Settings
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X2,
                  Adafruit_BMP280::SAMPLING_X16,
                  Adafruit_BMP280::FILTER_X16,
                  Adafruit_BMP280::STANDBY_MS_500);
  
  // Initialize OLED Display
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed!");
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Initializing...");
  display.display();
  
  // Connect to WiFi
  connectWiFi();
  
  // Initialize MQTT
  mqtt.setServer(mqtt_server, mqtt_port);
  
  delay(2000);
}

void loop() {
  // Maintain WiFi Connection
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  
  // Maintain MQTT Connection
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();
  
  // Read Sensors and Update Display
  unsigned long currentMillis = millis();
  if (currentMillis - lastDisplayUpdate >= displayUpdateInterval) {
    lastDisplayUpdate = currentMillis;
    
    // Read DHT22
    humidity = dht.readHumidity();
    float tempDHT = dht.readTemperature();
    
    // Read BMP280
    pressure = bmp.readPressure() / 100.0F; // Convert to hPa
    float tempBMP = bmp.readTemperature();
    
    // Use average temperature or prioritize DHT22
    if (!isnan(tempDHT)) {
      temperature = tempDHT;
    } else if (!isnan(tempBMP)) {
      temperature = tempBMP;
    }
    
    // Check for valid readings
    if (isnan(humidity)) {
      humidity = 0.0;
    }
    if (isnan(temperature)) {
      temperature = 0.0;
    }
    if (isnan(pressure) || pressure == 0) {
      pressure = 0.0;
    }
    
    // Update Display
    updateDisplay();
    
    // Check Temperature Alert
    checkTemperatureAlert();
  }
  
  // Publish to MQTT
  if (currentMillis - lastMqttPublish >= mqttPublishInterval) {
    lastMqttPublish = currentMillis;
    publishToMQTT();
  }
}

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void reconnectMQTT() {
  if (!mqtt.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (mqtt.connect(mqtt_client_id)) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqtt.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

void publishToMQTT() {
  if (mqtt.connected()) {
    char tempStr[10];
    char humStr[10];
    char pressStr[10];
    
    dtostrf(temperature, 6, 2, tempStr);
    dtostrf(humidity, 6, 2, humStr);
    dtostrf(pressure, 7, 2, pressStr);
    
    mqtt.publish(mqtt_topic_temp, tempStr);
    mqtt.publish(mqtt_topic_humidity, humStr);
    mqtt.publish(mqtt_topic_pressure, pressStr);
    
    Serial.println("Data published to MQTT");
  }
}

void updateDisplay() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  
  // Display Temperature
  display.setCursor(0, 0);
  display.print("Temp: ");
  display.print(temperature, 1);
  display.println(" C");
  
  // Display Humidity
  display.setCursor(0, 16);
  display.print("Humidity: ");
  display.print(humidity, 1);
  display.println(" %");
  
  // Display Pressure
  display.setCursor(0, 32);
  display.print("Press: ");
  display.print(pressure, 1);
  display.println(" hPa");
  
  // Display WiFi Status
  display.setCursor(0, 48);
  if (WiFi.status() == WL_CONNECTED) {
    display.print("WiFi: OK");
  } else {
    display.print("WiFi: ERR");
  }
  
  // Display MQTT Status
  display.setCursor(0, 56);
  if (mqtt.connected()) {
    display.print("MQTT: OK");
  } else {
    display.print("MQTT: ERR");
  }
  
  display.display();
}

void checkTemperatureAlert() {
  if (temperature > TEMP_ALERT_THRESHOLD) {
    if (!buzzerActive) {
      buzzerActive = true;
      digitalWrite(BUZZER_4_SIGNAL, HIGH);
      Serial.println("Temperature alert! Buzzer activated.");
    }
  } else {
    if (buzzerActive) {
      buzzerActive = false;
      digitalWrite(BUZZER_4_SIGNAL, LOW);
      Serial.println("Temperature normal. Buzzer deactivated.");
    }
  }
}