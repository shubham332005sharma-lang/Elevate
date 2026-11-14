#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

const char* WIFI_SSID = "Shubham-5";
const char* WIFI_PASSWORD = "12345679";

const char* API_URL =
  "http://10.198.205.148:8010/api/v1/incidents/";

const char* DEVICE_TOKEN =
  "ZH2qb3sE_GAE0AkiycrSL6Ngqlfs-jxvgJ0nV8qqR8c";

const int BUTTON_PIN = 4;
const int RED_LED_PIN = 6;
const int GREEN_LED_PIN = 7;
const int OLED_SDA_PIN = 8;
const int OLED_SCL_PIN = 9;

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool lastReading = HIGH;
bool buttonState = HIGH;
unsigned long lastChangeTime = 0;
const unsigned long debounceMs = 50;

void showMessage(const char* heading, const char* detail = "") {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(2);
  display.setCursor(0, 12);
  display.println(heading);

  display.setTextSize(1);
  display.setCursor(0, 44);
  display.println(detail);

  display.display();
}

void setStatusLights(bool redOn, bool greenOn) {
  digitalWrite(RED_LED_PIN, redOn ? HIGH : LOW);
  digitalWrite(GREEN_LED_PIN, greenOn ? HIGH : LOW);
}

void sendFailureReport() {
  setStatusLights(true, false);
  showMessage("Sending...", "Contacting Elevate");

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Not connected to hotspot; report not sent.");
    setStatusLights(true, false);
    showMessage("Failed", "No Wi-Fi connection");
    return;
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);

  String report =
    "{\"elevator_code\":\"E-01\","
    "\"device_id\":\"ESP32-E-01\","
    "\"title\":\"Elevator failure reported\","
    "\"description\":\"Failure report submitted using the BUTTON.\","
    "\"category\":\" Abnormality detected. \","
    "\"severity\":\"high\"}";

  int responseCode = http.POST(report);

  Serial.print("Elevate response code: ");
  Serial.println(responseCode);

  if (responseCode == 201) {
    Serial.println(http.getString());
    setStatusLights(false, true);
    showMessage("Help", "coming - report sent");
  } else {
    Serial.println(http.getString());
    setStatusLights(true, false);
    showMessage("Failed", "Check server / Wi-Fi");
  }

  http.end();
}

void setup() {
  Serial.begin(115200);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);

  setStatusLights(false, false);

  Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found. Check wiring and address.");
    while (true) {
      delay(100);
    }
  }

  showMessage("Elevate", "Connecting to hotspot");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to hotspot");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  setStatusLights(false, true);
  showMessage("Ready", "Press button");
}

void loop() {
  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastReading) {
    lastChangeTime = millis();
  }

  if (millis() - lastChangeTime > debounceMs &&
      reading != buttonState) {
    buttonState = reading;

    // INPUT_PULLUP reads LOW when the button is pressed.
    if (buttonState == LOW) {
      sendFailureReport();
    }
  }

  lastReading = reading;
}
