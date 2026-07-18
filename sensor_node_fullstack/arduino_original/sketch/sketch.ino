#include "Arduino_RouterBridge.h"
#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22
#define GAS_PIN A0
#define TRIG_PIN 3
#define ECHO_PIN 4
#define IR_PIN 5
#define BUZZER_PIN 6

DHT dht(DHTPIN, DHTTYPE);

float cachedTemp = NAN;
float cachedHum = NAN;
unsigned long lastDHTRead = 0;

float get_temperature();
float get_humidity();
int get_gas();
float get_distance();
int get_obstacle();
void trigger_buzzer(bool state);

void setup() {
  Serial.begin(115200);

  dht.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(IR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Bridge.begin();

  Serial.println("Bridge Started");

  Bridge.provide("get_temperature", get_temperature);
  Bridge.provide("get_humidity", get_humidity);
  Bridge.provide("get_gas", get_gas);
  Bridge.provide("get_distance", get_distance);
  Bridge.provide("get_obstacle", get_obstacle);
  Bridge.provide("trigger_buzzer", trigger_buzzer);

  Serial.println("Functions Registered");
}

void loop() {
  if (millis() - lastDHTRead >= 2000) {
    lastDHTRead = millis();

    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (!isnan(t)) cachedTemp = t;
    if (!isnan(h)) cachedHum = h;
  }
}

float get_temperature() {
  return cachedTemp;
}

float get_humidity() {
  return cachedHum;
}

int get_gas() {
  return analogRead(GAS_PIN);
}

float get_distance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0)
    return -1;

  return duration * 0.0343 / 2.0;
}

int get_obstacle() {
  return digitalRead(IR_PIN) == LOW;
}

void trigger_buzzer(bool state) {
  digitalWrite(BUZZER_PIN, state ? HIGH : LOW);
}