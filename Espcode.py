import sys
import socket
import network
# import Trix # type: ignore
import Trix # type: ignore
from machine import Pin # type: ignore
import time

# --- WIFI CONFIGURATION (SoftAP) ---
SSID = "RobotCar"          
PASSWORD = "password123"   
UDP_IP = "0.0.0.0"         
UDP_PORT = 1234            

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(ssid=SSID, password=PASSWORD)

print(f"WiFi Created: {SSID}")
print(f"IP: {ap.ifconfig()[0]}")

# --- UDP SOCKET ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

# --- MOTORS & LED (Same as before) ---
class CarMotor:
    def __init__(self):
        self.m1_a = Pin(Trix.IO18, Pin.OUT)
        self.m1_b = Pin(Trix.IO19, Pin.OUT)
        self.m2_a = Pin(Trix.IO20, Pin.OUT)
        self.m2_b = Pin(Trix.IO21, Pin.OUT)
        self.stop() 

    def stop(self):
        self.m1_a.value(0); self.m1_b.value(0)
        self.m2_a.value(0); self.m2_b.value(0)

    def forward(self):
        self.m1_a.value(1); self.m1_b.value(0)
        self.m2_a.value(1); self.m2_b.value(0)

    def left(self):
        self.m1_a.value(0); self.m1_b.value(1) 
        self.m2_a.value(1); self.m2_b.value(0)

    def right(self):
        self.m1_a.value(1); self.m1_b.value(0)
        self.m2_a.value(0); self.m2_b.value(1)

class LEDMatrix:
  def __init__(self, rows=6, cols=8):
    self.ROWS = rows
    self.COLS = cols
    self.NUM_LEDS = rows * cols
 
  def set_pixel(self, x, y, r, g, b):
    if 0 <= x < self.COLS and 0 <= y < self.ROWS:
      index = (y * self.COLS) + x + 1
      Trix.setSingleLED(index, (r, g, b))

  def set_all(self, r, g, b):
    for i in range(1, self.NUM_LEDS + 1):
      Trix.setSingleLED(i, (r, g, b))

  def off(self):
    self.set_all(0, 0, 0)

  def show_forward(self):
    self.off()
    green = (0, 255, 0)
    self.set_pixel(3, 0, *green); self.set_pixel(4, 0, *green)
    self.set_pixel(2, 1, *green); self.set_pixel(5, 1, *green)
    self.set_pixel(1, 2, *green); self.set_pixel(6, 2, *green)
    for y in range(2, 6):
      self.set_pixel(3, y, *green); self.set_pixel(4, y, *green)

  def show_left(self):
    self.off()
    blue = (0, 150, 150)
    self.set_pixel(0, 2, *blue); self.set_pixel(0, 3, *blue)
    self.set_pixel(1, 1, *blue); self.set_pixel(1, 4, *blue)
    self.set_pixel(2, 0, *blue); self.set_pixel(2, 5, *blue)
    for x in range(1, 8):
      self.set_pixel(x, 2, *blue); self.set_pixel(x, 3, *blue)

  def show_right(self):
    self.off()
    orange = (150, 150, 0)
    self.set_pixel(7, 2, *orange); self.set_pixel(7, 3, *orange)
    self.set_pixel(6, 1, *orange); self.set_pixel(6, 4, *orange)
    self.set_pixel(5, 0, *orange); self.set_pixel(5, 5, *orange)
    for x in range(0, 7):
      self.set_pixel(x, 2, *orange); self.set_pixel(x, 3, *orange)

  def show_stop(self):
    self.off()
    red = (255, 0, 0)
    for i in range(6):
      self.set_pixel(i+1, i, *red)  
      self.set_pixel(6-i, i, *red)  

# --- SETUP ---
matrix = LEDMatrix(rows=6, cols=8)
matrix.off()
car = CarMotor()
print("Waiting for UDP Data...")

# --- MAIN LOOP ---
while True:
  try:
    data_bytes, addr = sock.recvfrom(1024) 
    
    if data_bytes:
      data = data_bytes.decode('utf-8').strip()
      
      # --- PRINT RECEIVED DATA HERE ---
      print("Received:", data) 

      if "car : S" in data: matrix.show_stop();car.stop()
      if "car : F" in data: matrix.show_forward();car.forward()
      if "car : L" in data: matrix.show_left();car.left()
      if "car : R" in data: matrix.show_right();car.right()

      if "Ang : U" in data:
        matrix.off()
        matrix.set_pixel(3, 0, 100, 100, 100)
      if "Ang : D" in data:
        matrix.off()
        matrix.set_pixel(3, 5, 200, 200, 200)
  
  except OSError:
    pass