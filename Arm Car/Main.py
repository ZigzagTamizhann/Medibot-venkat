import cv2
import numpy as np
from ultralytics import YOLO

def is_red(roi, threshold=0.3):
    """
    Determines if a Region of Interest (ROI) is predominantly red.
    Returns True if the percentage of red pixels > threshold.
    """
    # Convert BGR image to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Define range for red color in HSV
    # Red wraps around the 0/180 hue axis in OpenCV
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    
    lower_red2 = np.array([170, 70, 50])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # Calculate the percentage of red pixels
    total_pixels = roi.shape[0] * roi.shape[1]
    if total_pixels == 0:
        return False
        
    red_pixels = cv2.countNonZero(mask)
    ratio = red_pixels / total_pixels

    return ratio > threshold

def main():
    # Load a pre-trained YOLOv8 model
    model = YOLO("yolov8n.pt")  # 'n' is the nano version, fastest for real-time

    # Open the webcam (0 is usually the default camera)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO inference on the frame
        results = model(frame, verbose=False)

        for result in results:
            for box in result.boxes:
                # Get bounding box coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                
                # Extract the object from the frame (Region of Interest)
                roi = frame[y1:y2, x1:x2]
                
                if roi.size > 0 and is_red(roi):
                    # If red, draw the bounding box and label
                    cls_id = int(box.cls[0])
                    label = f"Red {model.names[cls_id]}"
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("Red Object Detector", frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()