import cv2
import numpy as np
import socket
import time

# --- CONFIGURATION ---
min_area = 3000        
max_area_limit = 50000 
min_speed = 100
max_speed = 255
box_size = 150 

# --- WIFI CONNECTION ---
ESP_IP = "192.168.4.1" 
ESP_PORT = 1234         

print(f"Targeting ESP32 at {ESP_IP}:{ESP_PORT}")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

last_send_time = 0
send_interval = 0.05 

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2 

    box_x1 = center_x - (box_size // 2)
    box_y1 = center_y - (box_size // 2)
    box_x2 = center_x + (box_size // 2)
    box_y2 = center_y + (box_size // 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 100]); upper1 = np.array([10, 255, 255])
    lower2 = np.array([170, 100, 100]); upper2 = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)
    mask = cv2.erode(mask, np.ones((5,5), np.uint8), iterations=1)
    mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # CHANGE 1: Default values set to STOP and CENTER
    drive_cmd = "S" 
    tilt_cmd = "C"
    speed = 0

    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 0, 0), 2)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area > min_area:
            x, y, w_rect, h_rect = cv2.boundingRect(largest)
            obj_cx = x + w_rect // 2
            obj_cy = y + h_rect // 2
            
            cv2.rectangle(frame, (x, y), (x + w_rect, y + h_rect), (0, 255, 0), 2)
            cv2.circle(frame, (obj_cx, obj_cy), 8, (0, 0, 255), -1)
            
            cv2.line(frame, (0, obj_cy), (w, obj_cy), (0, 0, 255), 2)
            cv2.line(frame, (obj_cx, 0), (obj_cx, h), (0, 0, 255), 2)

            speed = np.interp(area, [min_area, max_area_limit], [max_speed, min_speed])
            speed = int(speed)

            buffer = 20
            touch_L = x <= buffer; touch_R = (x + w_rect) >= (w - buffer)
            touch_T = y <= buffer; touch_B = (y + h_rect) >= (h - buffer)

            if (touch_L and touch_R) or (touch_T and touch_B):
                drive_cmd = "S"
            else:
                if obj_cx < box_x1: drive_cmd = "R" 
                elif obj_cx > box_x2: drive_cmd = "L" 
                else: drive_cmd = "F" 

            if obj_cy < box_y1: tilt_cmd = "U" 
            elif obj_cy > box_y2: tilt_cmd = "D" 
            else: tilt_cmd = "C" 
        
        # Area < min_area என்றால் drive_cmd ஏற்கனவே "S" ஆகத் தான் இருக்கும் (Line 48).

    # --- DISPLAY TEXT ---
    c_drive = (0, 0, 255) if drive_cmd == "S" else (0, 255, 0)
    cv2.putText(frame, f"Car: {drive_cmd}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, c_drive, 3)
    cv2.putText(frame, f"Ang:  {tilt_cmd}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
    cv2.putText(frame, f"SPD:   {speed}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # CHANGE 2: Sending Logic இப்போது 'if contours:' block-ஐ விட்டு வெளியே உள்ளது.
    # Detection இருந்தாலும் இல்லாவிட்டாலும் இது வேலை செய்யும்.
    data_to_send = f"car : {drive_cmd} | Ang : {tilt_cmd}"
    
    if time.time() - last_send_time > send_interval:
        try:
            print(f"Sent: {data_to_send}") 
            sock.sendto(data_to_send.encode(), (ESP_IP, ESP_PORT))
            last_send_time = time.time()
        except Exception as e:
            print(f"WiFi Send Error: {e}")

    cv2.imshow('Wireless Control', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

sock.close()
cap.release()
cv2.destroyAllWindows()