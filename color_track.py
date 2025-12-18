import cv2
import numpy as np
import serial

cap = cv2.VideoCapture(0)

# --- CONFIGURATION ---
min_area = 3000        
max_area_limit = 50000 
min_speed = 100
max_speed = 255
box_size = 150 

# --- SERIAL COMMUNICATION ---
try:
    ser = serial.Serial('COM5', 115200, timeout=1) # Change 'COM3' to your Arduino Port
    print("Serial Connected")
except:
    print("Serial Not Connected")
    ser = None

print("----------------------------------------------------------------")
print("SET 1 (Drive): F (Forward), S (Stop), L (Left), R (Right)")
print("SET 2 (Tilt):  U (Up), D (Down), C (Center)")
print("----------------------------------------------------------------")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2 

    # Center Box Coordinates
    box_x1 = center_x - (box_size // 2)
    box_y1 = center_y - (box_size // 2)
    box_x2 = center_x + (box_size // 2)
    box_y2 = center_y + (box_size // 2)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Strict Red Color ---
    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([170, 100, 100])
    upper2 = np.array([180, 255, 255])
    
    mask = cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)
    mask = cv2.erode(mask, np.ones((5,5), np.uint8), iterations=1)
    mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Defaults
    drive_cmd = "F" 
    tilt_cmd = "C"
    speed = 0

    # Draw Center Box (Blue)
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

            # Speed Calc
            speed = np.interp(area, [min_area, max_area_limit], [max_speed, min_speed])
            speed = int(speed)

            # ====================================================
            # SET 1: DRIVE CONTROL (Horizontal + Stop)
            # ====================================================
            buffer = 20
            touch_L = x <= buffer
            touch_R = (x + w_rect) >= (w - buffer)
            touch_T = y <= buffer
            touch_B = (y + h_rect) >= (h - buffer)

            # Priority 1: Check STOP (Boundaries)
            if (touch_L and touch_R) or (touch_T and touch_B):
                drive_cmd = "S"
            else:
                # Priority 2: Check LEFT / RIGHT (Mirror Mode)
                if obj_cx < box_x1:
                    drive_cmd = "R"  # Hand Left -> Output Right
                elif obj_cx > box_x2:
                    drive_cmd = "L"  # Hand Right -> Output Left
                else:
                    drive_cmd = "F"  # Center Horizontal -> Forward

            # ====================================================
            # SET 2: TILT CONTROL (Vertical Only)
            # ====================================================
            # This is independent of Drive Command
            
            if obj_cy < box_y1:
                tilt_cmd = "U"   # Up
            elif obj_cy > box_y2:
                tilt_cmd = "D"   # Down
            else:
                tilt_cmd = "C"   # Center Vertical

            # ====================================================
            # DISPLAY & OUTPUT
            # ====================================================
            
            # Color Logic for Display
            c_drive = (0, 0, 255) if drive_cmd == "S" else (0, 255, 0)
            
            cv2.putText(frame, f"Car: {drive_cmd}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, c_drive, 3)
            cv2.putText(frame, f"Ang:  {tilt_cmd}", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
            cv2.putText(frame, f"SPD:   {speed}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # --- PREPARE SINGLE LINE STRING ---
            # Format: "car : F | Ang : U"
            data_to_send = f"car : {drive_cmd} | Ang : {tilt_cmd}\n"
            
            # Print to console to verify
            print(data_to_send, end="") 

            # --- SERIAL SEND (Single Line) ---
            if ser:
                ser.write(data_to_send.encode())  # Sends the whole string at once

    cv2.imshow('Dual Control Sets', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()