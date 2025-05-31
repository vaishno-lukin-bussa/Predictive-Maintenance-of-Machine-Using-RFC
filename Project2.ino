#include <Arduino.h>
#if defined(ESP32)
#include <WiFi.h>
#elif defined(ESP8266)
#include <ESP8266WiFi.h>
#endif
#include <Firebase_ESP_Client.h>
#include "DHT.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

#define WIFI_SSID "Lukinnn"
#define WIFI_PASSWORD "lucky123"
#define API_KEY "AIzaSyDMatHtw6O7KLnO93g-JEvCoFOENiC5_cY"
#define DATABASE_URL "https://machine-c5407-default-rtdb.firebaseio.com/"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

#define DHTPIN1 D3
#define DHTPIN2 D4
#define DHTTYPE DHT11
DHT dht1(DHTPIN1, DHTTYPE);
DHT dht2(DHTPIN2, DHTTYPE);

int T1, T2;
String str_T1, str_T2;

unsigned long sendDataPrevMillis = 0;
bool signupOK = false;

void setup() {
  Serial.begin(9600);
  dht1.begin();
  dht2.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("Connecting to Wi-Fi...");
  display.display();

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Wi-Fi Connected");
  display.println("IP: " + WiFi.localIP().toString());
  display.display();

  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("Firebase signup successful");
    signupOK = true;
  } else {
    Serial.printf("Firebase signup error: %s\n", config.signer.signupError.message.c_str());
  }

  config.token_status_callback = tokenStatusCallback;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
}

void loop() {
  T1 = dht1.readTemperature();
  T2 = dht2.readTemperature();
  float T1K = T1 + 273.15;
  float T2K = T2 + 273.15;
  str_T1 = String(T1K);
  str_T2 = String(T2K);

  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("Temp 1: " + str_T1 + " k");
  display.println("Temp 2: " + str_T2 + " k");
  display.display();

  if (Firebase.ready() && signupOK) {
    updateFirebase("Python/Temp1", str_T1);
    updateFirebase("Python/Temp2", str_T2);
  }
  delay(2000);
}

void updateFirebase(String path, String value) {
  if (Firebase.RTDB.setString(&fbdo, path, value)) {
    Serial.println("PASSED: " + path);
    Serial.println("Value: " + value);
  } else {
    Serial.println("FAILED to update " + path);
    Serial.println("Reason: " + fbdo.errorReason());
  }
}
