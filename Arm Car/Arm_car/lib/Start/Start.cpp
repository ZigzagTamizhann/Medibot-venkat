#include <Arduino.h>
#include "motor.h"
#include "wifi_setup.h"
#include "web_server.h"

void setuploop() {
  Serial.begin(115200);
  initMotors();
  setupWiFi();      
  setupWebServer();
}

void mainloop() {
   handleClient();
}
