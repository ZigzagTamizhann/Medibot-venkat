import cv2
import numpy as np

cap = cv2.VideoCapture(0)

min_fill_ratio = 0.75  # 75% of screen fill is considered FULL

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Only biggest red object
        c = max(contours, key=cv2.contourArea)
        x, y, bw, bh = cv2.boundingRect(c)
        area = bw * bh
        fill_ratio = area / (w * h)

        # Center crop for zoom
        cx = x + bw // 2
        cy = y + bh // 2

        # Zoom faster when small, slower when big
        zoom_factor = max(1.0, 5 - fill_ratio * 4)
        new_w = int(w / zoom_factor)
        new_h = int(h / zoom_factor)

        x1 = max(cx - new_w // 2, 0)
        y1 = max(cy - new_h // 2, 0)
        x2 = min(x1 + new_w, w)
        y2 = min(y1 + new_h, h)

        crop = frame[y1:y2, x1:x2]
        zoomed = cv2.resize(crop, (w, h))

        # Stop when red fills almost full screen
        if fill_ratio >= min_fill_ratio:
            zoomed = cv2.putText(zoomed, "Focus Locked!", (50, 80),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
            cv2.imshow("Auto Zoom Focus", zoomed)

            # Press SPACE to save image when locked
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cv2.imwrite("zoomed_capture.jpg", zoomed)
                print("Image Saved! zoomed_capture.jpg")
            continue

    else:
        zoomed = frame

    cv2.imshow("Auto Zoom Focus", zoomed)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
