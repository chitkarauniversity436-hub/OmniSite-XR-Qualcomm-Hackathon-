"""
YOLOv11 person-detection worker.

Runs on whatever machine has the camera (same PC as Flask, or a Pi/laptop
on the same network — just change BACKEND_URL below).

Requires: pip install ultralytics opencv-python requests

First run auto-downloads the pretrained COCO model (yolo11n.pt), which
already knows how to detect "person" (COCO class 0) — no custom training
needed unless you want to detect something else.
"""

import time
import cv2
import requests
from ultralytics import YOLO

BACKEND_URL = "http://127.0.0.1:5000/person"  # change to backend's LAN IP if on another device
CAMERA_INDEX = 0                               # 0 = default webcam
CONF_THRESHOLD = 0.5
SEND_INTERVAL_SEC = 1.0                        # throttle POSTs to the backend
MODEL_NAME = "yolo11n.pt"                      # nano = fastest; use yolo11s/m for more accuracy

PERSON_CLASS_ID = 0  # COCO class index for "person"


def main():
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
