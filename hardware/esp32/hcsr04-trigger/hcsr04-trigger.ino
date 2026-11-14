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

const int TRIG_PIN = 5;
const int ECHO_PIN = 18;
const int BUTTON_PIN = 4;
const int RED_LED_PIN = 6;
const int GREEN_LED_PIN = 7;
const int OLED_SDA_PIN = 8;
const int OLED_SCL_PIN = 9;

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

bool lastButtonReading = HIGH;
bool buttonState = HIGH;
unsigned long lastButtonChange = 0;
const unsigned long debounceMs = 50;

unsigned long lastSensorRead = 0;
const unsigned long sensorIntervalMs = 100;

bool outsideTiming = false;
unsigned long outsideSince = 0;
bool automaticReportSent = false;

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

String escapeJson(const String& input) {
  String output;
  output.reserve(input.length() + 8);

  for (unsigned int i = 0; i < input.length(); i++) {
    char c = input[i];

    if (c == '"' || c == '\\') {
      output += '\\';
      output += c;
    } else if (c == '\n') {
      output += "\\n";
    } else if (c == '\r') {
      output += "\\r";
    } else {
      output += c;
    }
  }

  return output;
}

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);

  if (duration == 0) {
    return -1.0;  // No echo
  }

  return duration * 0.0343f / 2.0f;
}

bool isAllowedDistance(float distanceCm) {
  return (distanceCm >= 0.0f && distanceCm <= 10.0f) ||
         (distanceCm >= 90.0f && distanceCm <= 100.0f);
}

void sendFailureReport(const String& title,
                       const String& description,
                       const String& category) {
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
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);

  String report =
    "{\"elevator_code\":\"E-01\","
    "\"device_id\":\"ESP32-E-01\","
    "\"title\":\"" + escapeJson(title) + "\","
    "\"description\":\"" + escapeJson(description) + "\","
    "\"category\":\"" + escapeJson(category) + "\","
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

void checkButton() {
  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonReading) {
    lastButtonChange = millis();
  }

  if (millis() - lastButtonChange > debounceMs &&
      reading != buttonState) {
    buttonState = reading;

    if (buttonState == LOW) {
      sendFailureReport(
        "Elevator failure reported",
        "Failure report submitted using the ESP32 button.",
        "Hardware button report"
      );
    }
  }

  lastButtonReading = reading;
}

void checkDistance() {
  unsigned long now = millis();

  if (now - lastSensorRead < sensorIntervalMs) {
    return;
  }
  lastSensorRead = now;

  float distanceCm = readDistanceCm();

  Serial.print("Distance: ");
  if (distanceCm < 0) {
    Serial.println("No echo");
  } else {
    Serial.print(distanceCm, 1);
    Serial.println(" cm");
  }

  if (isAllowedDistance(distanceCm)) {
    outsideTiming = false;
    automaticReportSent = false;
    return;
  }

  if (!outsideTiming) {
    outsideTiming = true;
    outsideSince = now;
  }

  if (!automaticReportSent &&
      now - outsideSince >= 5000UL) {
    automaticReportSent = true;

    String description;
    if (distanceCm < 0) {
      description = "HC-SR04 returned no echo for 5 seconds.";
    } else {
      description = "HC-SR04 distance stayed at ";
      description += String(distanceCm, 1);
      description += " cm, outside the allowed 0-10 cm and 90-100 cm bands for 5 seconds.";
    }

    sendFailureReport(
      "Height outside limits",
      description,
      "HC-SR04 sensor alert"
    );
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);

  digitalWrite(TRIG_PIN, LOW);
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
  showMessage("Ready", "Monitoring sensor");
}

void loop() {
  checkButton();
  checkDistance();
}