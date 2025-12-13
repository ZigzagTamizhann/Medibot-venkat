#include "wifi_setup.h"
#include <WiFi.h>
#include <Arduino.h>

const char *ssid = "Robotic Arm Vehicle";
const char *password = "12345678";

void setupWiFi() {
  Serial.println("Starting SoftAP...");
  WiFi.softAP(ssid, password);
  Serial.print("AP IP address: ");
  Serial.println(WiFi.softAPIP());
}