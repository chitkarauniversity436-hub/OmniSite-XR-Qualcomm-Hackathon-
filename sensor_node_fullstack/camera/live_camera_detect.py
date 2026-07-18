"""
Runs on your laptop/PC. No GPS module, no LoRa, no Arduino required.

Webcam -> YOLOv11 person detection -> annotated frame streamed to backend
(live video in the dashboard) -> if a person is found, mark a life point
using a MOCK GPS (simulates the rover slowly moving) -> also updates the
backend's /person state so the risk banner reacts too.

pip install ultralytics opencv-python requests

To later swap in a REAL GPS module: replace MockGPS with a class that reads
NMEA sentences from a serial GPS (see rover/rover_life_detect.py for a
working example) — everything else in this file stays the same, since it
only calls gps.read_latest() -> (lat, lon).
"""

import time
import requests
import cv2
from ultralytics import YOLO
from math import radians, sin, cos, sqrt, atan2

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BACKEND_URL = "http://127.0.0.1:5000"
CAMERA_INDEX = 0
MODEL_NAME = "yolo11n.pt"
CONF_THRESHOLD = 0.4
PERSON_CLASS_ID = 0

FRAME_SEND_INTERVAL_SEC = 0.15   # ~6-7fps to the backend, plenty for a live view
PERSON_SEND_INTERVAL_SEC = 1.0
DEDUP_RADIUS_M = 2.0
DETECTION_COOLDOWN_SEC = 3.0

# Starting coordinate for the mock GPS — change this to roughly your real
# location if you want the map to center somewhere sensible. Default is an
# arbitrary point in Delhi since that's where this was set up.
MOCK_START_LAT = 28.6139
MOCK_START_LON = 77.2090


# ---------------------------------------------------------------------------
# Mock GPS — simulates a rover slowly moving, no hardware needed
# ---------------------------------------------------------------------------

class MockGPS:
    def __init__(self, start_lat, start_lon):
        self.lat = start_lat
        self.lon = start_lon

    def read_latest(self):
        # small random-ish drift each call so consecutive detections look
        # like the rover is actually moving forward
        self.lat += 0.00003
        self.lon += 0.00002
        return (self.lat, self.lon)


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


class LifePointTracker:
    def __init__(self):
        self.points = []
        self._next_label_idx = 0

    def _next_label(self):
        idx = self._next_label_idx
        self._next_label_idx += 1
        label = ""
        while True:
            label = chr(65 + idx % 26) + label
            idx = idx // 26 - 1
            if idx < 0:
                break
        return label

    def maybe_add(self, lat, lon, confidence):
        for p in self.points:
            if haversine_m(lat, lon, p["lat"], p["lon"]) < DEDUP_RADIUS_M:
                return None
        point = {
            "label": self._next_label(),
            "lat": lat,
            "lon": lon,
            "confidence": round(confidence, 3),
            "timestamp": time.time(),
        }
        self.points.append(point)
        return point


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    model = YOLO(MODEL_NAME)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    gps = MockGPS(MOCK_START_LAT, MOCK_START_LON)
    tracker = LifePointTracker()
    session = requests.Session()

    last_frame_sent = 0.0
    last_person_sent = 0.0
    last_point_check = 0.0

    print("Live camera + detection running. Press 'q' in the preview window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.2)
                continue

            results = model(frame, verbose=False)[0]
            annotated = results.plot()

            person_detected = False
            best_conf = 0.0
            for box in results.boxes:
                if int(box.cls[0]) == PERSON_CLASS_ID and float(box.conf[0]) >= CONF_THRESHOLD:
                    person_detected = True
                    best_conf = max(best_conf, float(box.conf[0]))

            cv2.imshow("Live Detection (local preview)", annotated)
            now = time.time()

            # 1. stream the annotated frame to the backend for the live dashboard view
            if now - last_frame_sent >= FRAME_SEND_INTERVAL_SEC:
                last_frame_sent = now
                ok_enc, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 70])
                if ok_enc:
                    try:
                        session.post(
                            f"{BACKEND_URL}/frame",
                            data=buf.tobytes(),
                            headers={"Content-Type": "application/octet-stream"},
                            timeout=1,
                        )
                    except requests.exceptions.RequestException:
                        pass  # don't let a dropped frame stall detection

            # 2. update the person/risk state
            if now - last_person_sent >= PERSON_SEND_INTERVAL_SEC:
                last_person_sent = now
                try:
                    session.post(
                        f"{BACKEND_URL}/person",
                        json={"person": person_detected, "confidence": best_conf if person_detected else None},
                        timeout=2,
                    )
                except requests.exceptions.RequestException as e:
                    print("Backend unreachable (person):", e)

            # 3. mark a new life point if this is a new person, with cooldown + dedup
            if person_detected and (now - last_point_check) >= DETECTION_COOLDOWN_SEC:
                last_point_check = now
                lat, lon = gps.read_latest()
                new_point = tracker.maybe_add(lat, lon, best_conf)
                if new_point:
                    print("NEW LIFE POINT:", new_point)
                    try:
                        session.post(f"{BACKEND_URL}/point", json=new_point, timeout=2)
                    except requests.exceptions.RequestException as e:
                        print("Backend unreachable (point):", e)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
