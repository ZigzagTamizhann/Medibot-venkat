#include "web_server.h"
#include <WebServer.h>
#include "motor.h"

WebServer server(80);

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  html += "<style>body{font-family:sans-serif;text-align:center;margin-top:50px;} button{width:120px;height:60px;margin:10px;font-size:24px;border-radius:10px;}</style></head><body>";
  html += "<h1>ESP32 Car Control</h1>";
  html += "<p><a href=\"/F\"><button>Forward</button></a></p>";
  html += "<p><a href=\"/L\"><button>Left</button></a><a href=\"/S\"><button style=\"background-color:red;color:white;\">Stop</button></a><a href=\"/R\"><button>Right</button></a></p>";
  html += "<p><a href=\"/B\"><button>Backward</button></a></p>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void setupWebServer() {
  server.on("/", handleRoot);
  server.on("/F", []() { moveForward(); handleRoot(); });
  server.on("/B", []() { moveBackward(); handleRoot(); });
  server.on("/L", []() { turnLeft(); handleRoot(); });
  server.on("/R", []() { turnRight(); handleRoot(); });
  server.on("/S", []() { stopCar(); handleRoot(); });

  server.begin();
  Serial.println("HTTP server started");
}

void handleClient() {
  server.handleClient();
}