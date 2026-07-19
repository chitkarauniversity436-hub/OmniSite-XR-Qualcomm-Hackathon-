"""
===============================================================================
OmniSight-XR Vision Node
-------------------------------------------------------------------------------
This module performs real-time human detection using the YOLOv11 object
detection model and synchronizes the detection status with the Flask backend.

Responsibilities:
    • Capture live frames from the camera
    • Perform YOLOv11 inference
    • Detect human presence
    • Send detection status to the backend
    • Display a local annotated preview

Model:
    YOLOv11 Nano (COCO Pretrained)

Communication:
    POST /person

Author:
    OmniSight-XR Team
===============================================================================
"""

# -----------------------------------------------------------------------------
# Standard Library
# -----------------------------------------------------------------------------
import time

# -----------------------------------------------------------------------------
# Third-Party Libraries
# -----------------------------------------------------------------------------
import cv2
import requests
from ultralytics import YOLO

# =============================================================================
# Runtime Configuration
# =============================================================================

BACKEND_URL = "http://127.0.0.1:5000/person"  # change to backend's LAN IP if on another device
CAMERA_INDEX = 0                               # 0 = default webcam
CONF_THRESHOLD = 0.5
SEND_INTERVAL_SEC = 1.0                        # throttle POSTs to the backend
MODEL_NAME = "yolo11n.pt"                      # nano = fastest; use yolo11s/m for more accuracy

PERSON_CLASS_ID = 0  # COCO class index for "person"


def main():
    """
    Main execution loop.
    
    Workflow
    --------
    1. Initialize camera
    2. Load YOLO model
    3. Capture video frames
    4. Detect people
    5. Send detection results to Flask
    6. Display annotated preview
    """
    model = YOLO(MODEL_NAME)
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    session = requests.Session()
    last_sent = 0.0

    print("YOLOv11 person detector running. Press 'q' in the preview window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera read failed, retrying...")
                time.sleep(0.5)
                continue

            results = model(frame, verbose=False)[0]

            person_detected = False
            best_conf = 0.0

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if cls_id == PERSON_CLASS_ID and conf >= CONF_THRESHOLD:
                    person_detected = True
                    best_conf = max(best_conf, conf)

            # draw boxes for a local preview (optional, comment out if headless)
            annotated = results.plot()
            cv2.imshow("YOLOv11 - Person Detection", annotated)

            now = time.time()
            if now - last_sent >= SEND_INTERVAL_SEC:
                try:
                    session.post(
                        BACKEND_URL,
                        json={
                            "person": person_detected,
                            "confidence": round(best_conf, 3) if person_detected else None,
                        },
                        timeout=2,
                    )
                except requests.exceptions.RequestException as e:
                    print("Backend unreachable:", e)
                last_sent = now

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
