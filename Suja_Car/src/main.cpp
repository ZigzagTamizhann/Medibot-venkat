#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

// WiFi Credentials for Soft AP
const char *ssid = "ARM_CAR";
const char *password = "12345678";

// Motor Pins (Adjust these based on your specific wiring)
// Left Motor
const int motorLeftPin1 = 1;
const int motorLeftPin2 = 2;
// Right Motor
const int motorRightPin1 = 42;
const int motorRightPin2 = 41;

WebServer server(80);

void stopCar() {
  digitalWrite(motorLeftPin1, LOW);
  digitalWrite(motorLeftPin2, LOW);
  digitalWrite(motorRightPin1, LOW);
  digitalWrite(motorRightPin2, LOW);
}

void moveForward() {
  digitalWrite(motorLeftPin1, HIGH);
  digitalWrite(motorLeftPin2, LOW);
  digitalWrite(motorRightPin1, HIGH);
  digitalWrite(motorRightPin2, LOW);
}

void moveBackward() {
  digitalWrite(motorLeftPin1, LOW);
  digitalWrite(motorLeftPin2, HIGH);
  digitalWrite(motorRightPin1, LOW);
  digitalWrite(motorRightPin2, HIGH);
}

void turnLeft() {
  // Rotate left in place (Left motor back, Right motor forward)
  digitalWrite(motorLeftPin1, LOW);
  digitalWrite(motorLeftPin2, HIGH);
  digitalWrite(motorRightPin1, HIGH);
  digitalWrite(motorRightPin2, LOW);
}

void turnRight() {
  // Rotate right in place (Left motor forward, Right motor back)
  digitalWrite(motorLeftPin1, HIGH);
  digitalWrite(motorLeftPin2, LOW);
  digitalWrite(motorRightPin1, LOW);
  digitalWrite(motorRightPin2, HIGH);

}

void handleRoot() {
  String html = "<html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"></head><body>";
  html += "<h1 style=\"text-align:center;\">ESP32 Car Control</h1>";
  html += "<div style=\"text-align:center;\">";
  html += "<p><a href=\"/F\"><button style=\"font-size:40px; width:150px;\">Forward</button></a></p>";
  html += "<p><a href=\"/L\"><button style=\"font-size:40px; width:150px;\">Left</button></a> ";
  html += "<a href=\"/S\"><button style=\"font-size:40px; width:150px; background-color:red; color:white;\">Stop</button></a> ";
  html += "<a href=\"/R\"><button style=\"font-size:40px; width:150px;\">Right</button></a></p>";
  html += "<p><a href=\"/B\"><button style=\"font-size:40px; width:150px;\">Backward</button></a></p>";
  html += "</div></body></html>";
  server.send(200, "text/html", html);
}

void setup() {

  Serial.begin(115200);

  // Initialize Motor Pins
  pinMode(motorLeftPin1, OUTPUT);
  pinMode(motorLeftPin2, OUTPUT);
  pinMode(motorRightPin1, OUTPUT);
  pinMode(motorRightPin2, OUTPUT);

  stopCar();

  // Setup Soft AP
  Serial.println("Setting up Access Point...");

  WiFi.softAP(ssid, password);
  
  IPAddress IP = WiFi.softAPIP();

  Serial.print("AP IP address: ");
  Serial.println(IP);

  // Define Routes
  server.on("/", handleRoot);
  server.on("/F", []() { moveForward(); server.send(200, "text/plain", "F"); });
  server.on("/B", []() { moveBackward(); server.send(200, "text/plain", "B"); });
  server.on("/L", []() { turnLeft(); server.send(200, "text/plain", "L"); });
  server.on("/R", []() { turnRight(); server.send(200, "text/plain", "R"); });
  server.on("/S", []() { stopCar(); server.send(200, "text/plain", "S"); });

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}