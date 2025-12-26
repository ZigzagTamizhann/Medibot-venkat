import sys
import socket
import network
# import Trix # type: ignore
import Trix # type: ignore
from machine import Pin, PWM # type: ignore
import time

# --- WIFI CONFIGURATION (SoftAP) ---
SSID = "RobotCar"          
PASSWORD = "12345678"   
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

NUM_LEDS = 13
# --- MOTORS & LED (Same as before) ---
class CarMotor:
    def __init__(self):
        self.m1_a = PWM(Pin(Trix.IO13), freq=1000, duty=0)
        self.m1_b = PWM(Pin(Trix.IO14), freq=1000, duty=0)
        self.m2_a = PWM(Pin(Trix.IO15), freq=1000, duty=0)
        self.m2_b = PWM(Pin(Trix.IO16), freq=1000, duty=0)
        self.stop() 

    def stop(self):
        self.m1_a.duty(0); self.m1_b.duty(0)
        self.m2_a.duty(0); self.m2_b.duty(0)

    def forward(self, speed):
        pwm_val = int((speed / 255) * 1023)
        self.m1_a.duty(pwm_val); self.m1_b.duty(0)
        self.m2_a.duty(pwm_val); self.m2_b.duty(0)

    def left(self, speed):
        pwm_val = int((speed / 255) * 1023)
        self.m1_a.duty(0); self.m1_b.duty(pwm_val) 
        self.m2_a.duty(pwm_val); self.m2_b.duty(0)

    def right(self, speed):
        pwm_val = int((speed / 255) * 1023)
        self.m1_a.duty(pwm_val); self.m1_b.duty(0)
        self.m2_a.duty(0); self.m2_b.duty(pwm_val)

# --- SETUP ---
car = CarMotor()
print("Waiting for UDP Data...")
Trix.setAllLED((255, 165, 0))
# --- MAIN LOOP ---
while True:
  try:
    data_bytes, addr = sock.recvfrom(1024) 
    
    if data_bytes:
      data = data_bytes.decode('utf-8').strip()
      
      # --- PRINT RECEIVED DATA HERE ---
      print("Received:", data) 

      speed = 150
      try:
          parts = data.split('|')
          for p in parts:
              if "SPD" in p:
                  speed = int(p.split(':')[1].strip())
      except:
          pass

      if "car : S" in data: Trix.setAllLED((255, 0, 0)); car.stop()
      if "car : F" in data: Trix.setAllLED((0, 255, 0)); car.forward(speed)
      if "car : L" in data: Trix.setAllLED((0, 0, 255)); car.left(speed)
      if "car : R" in data: Trix.setAllLED((255, 165, 0)); car.right(speed)

      if "Ang : U" in data:
        Trix.setAllLED((0, 0, 0))
        Trix.setSingleLED(1, (255, 255, 255))
      if "Ang : D" in data:
        Trix.setAllLED((0, 0, 0))
        Trix.setSingleLED(13, (255, 255, 255))
  
  except OSError:
    pass
