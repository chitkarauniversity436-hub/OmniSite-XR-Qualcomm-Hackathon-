"""
Runs on your laptop/PC. No GPS module, no LoRa, no Arduino required.

Webcam -> YOLOv11 person detection -> annotated frame streamed to backend
(live video in the dashboard) -> if a person is found, mark a life point
using a MOCK GPS (simulates the rover slowly moving) -> also updates the
backend's /person state so the risk banner reacts too.

MiDaS monocular depth estimation runs alongside YOLO, but distance is only
computed/drawn for objects estimated to be CLOSE (see CLOSE_DISTANCE_THRESHOLD_M
below) — this keeps the overlay clean and avoids wasting time labeling
background clutter that's far from the camera. The person-specific bbox-height
distance estimate is kept as-is for GPS/life point logic (it's already
calibrated for that), while MiDaS handles the general close-range readout and
depth heatmap overlay.

pip install ultralytics opencv-python requests timm torch

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

from depth_estimator import DepthEstimator

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BACKEND_URL = "http://127.0.0.1:5000"
CAMERA_INDEX = 0
MODEL_NAME = "yolo11n.pt"
CONF_THRESHOLD = 0.35
PERSON_CLASS_ID = 0

FRAME_SEND_INTERVAL_SEC = 0.15   # ~6-7fps to the backend, plenty for a live view
PERSON_SEND_INTERVAL_SEC = 1.0
DEDUP_RADIUS_M = 5.0
DETECTION_COOLDOWN_SEC = 3.0

# --- Monocular distance estimation (person distance from camera) ---
# Uses the classic pinhole camera relationship: an object's apparent size in
# the image is inversely proportional to its distance from the camera.
#   distance_m = (REAL_PERSON_HEIGHT_M * FOCAL_LENGTH_PX) / bbox_height_px
#
# FOCAL_LENGTH_PX must be calibrated for YOUR camera — see calibrate_focal_length()
# below for how to get an accurate value. The default here is a rough estimate
# for a typical laptop webcam and will be somewhat off until calibrated.
REAL_PERSON_HEIGHT_M = 1.7
FOCAL_LENGTH_PX = 700  # placeholder — calibrate this for your camera, see below

# --- MiDaS depth (distance for close objects only) ---
DEPTH_MODEL_TYPE = "MiDaS_small"   # fastest, real-time on a 6GB GPU
SHOW_DEPTH_OVERLAY = True          # set False to skip the extra preview window
DEPTH_EVERY_N_FRAMES = 3           # run MiDaS every Nth frame to save GPU time

# Only label/consider objects estimated to be within this many meters of the
# camera. Anything farther is ignored for the per-object distance overlay
# (MiDaS is still run for the heatmap, this just filters what gets a distance
# label). Tune this to whatever counts as "close" for your setup.
CLOSE_DISTANCE_THRESHOLD_M = 3.0

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


def estimate_distance_m(bbox_height_px):
    """Rough distance to a detected person, in meters, from bounding box height."""
    if bbox_height_px <= 0:
        return None
    return round((REAL_PERSON_HEIGHT_M * FOCAL_LENGTH_PX) / bbox_height_px, 2)


def calibrate_focal_length(known_distance_m, bbox_height_px):
    """
    Run this ONCE to calibrate FOCAL_LENGTH_PX for your specific camera:
    1. Stand exactly `known_distance_m` meters from the camera (e.g. 2.0m)
    2. Run the main script, note the bbox_height_px it prints for your detection
    3. Call this function with those two numbers, e.g.:
         python -c "from live_camera_detect import calibrate_focal_length as c; print(c(2.0, 340))"
    4. Copy the printed value into FOCAL_LENGTH_PX above
    """
    return round((bbox_height_px * known_distance_m) / REAL_PERSON_HEIGHT_M, 1)


def get_ultrasonic_distance_m(session):
    """
    Pulls the latest sensor snapshot from the backend (the same data source
    that drives the risk banner) and returns distance_cm converted to meters,
    or None if unavailable/invalid. This is a real physical measurement from
    the Arduino's ultrasonic sensor, far more accurate than the camera-based
    estimate — but it only measures whatever is directly in the sensor's
    path, not a specific detected object.
    """
    try:
        resp = session.get(f"{BACKEND_URL}/latest", timeout=0.5)
        resp.raise_for_status()
        data = resp.json()
        distance_cm = data.get("distance_cm")
        if distance_cm is None or distance_cm == -1:
            return None
        return round(distance_cm / 100.0, 2)
    except requests.exceptions.RequestException:
        return None


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
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    depth_est = DepthEstimator(model_type=DEPTH_MODEL_TYPE)
    print(f"MiDaS depth model loaded on: {depth_est.device}")
    # After you've measured a raw_value at a known distance (see terminal
    # prints tagged [depth-calibration]), uncomment and fill this in:
    # depth_est.calibrate(known_distance_m=1.0, raw_value_at_that_distance=<paste value here>)

    gps = MockGPS(MOCK_START_LAT, MOCK_START_LON)
    tracker = LifePointTracker()
    session = requests.Session()

    last_frame_sent = 0.0
    last_person_sent = 0.0
    last_point_check = 0.0
    frame_count = 0
    last_depth_map = None

    print("Live camera + detection running. Press 'q' in the preview window to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.2)
                continue

            frame_count += 1
            _loop_start = time.time()

            results = model(frame, verbose=False)[0]
            _t_yolo = time.time()
            annotated = results.plot()

            # Run MiDaS every N frames (depth doesn't change fast frame-to-frame,
            # and this keeps the loop fast on shared GPU memory).
            if frame_count % DEPTH_EVERY_N_FRAMES == 0 or last_depth_map is None:
                last_depth_map = depth_est.predict(frame)
            depth_map = last_depth_map
            _t_depth = time.time()

            person_detected = False
            best_conf = 0.0
            best_bbox_height = 0
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < CONF_THRESHOLD:
                    continue

                x1, y1, x2, y2 = box.xyxy[0]
                label = model.names[cls_id]

                # distance via MiDaS, but only bother labeling it if the
                # object is actually close — skips the lookup/print/draw
                # entirely for anything farther than the threshold.
                obj_dist = depth_est.distance_for_box(depth_map, x1, y1, x2, y2)
                if obj_dist is not None and obj_dist <= CLOSE_DISTANCE_THRESHOLD_M:
                    if frame_count % 30 == 0:
                        print(f"[depth-calibration] {label}: raw_value={obj_dist}")
                    dist_text = f"{label} {obj_dist}m"
                    (tw, th), _ = cv2.getTextSize(dist_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    text_x, text_y = int(x1), int(y2) + 18
                    # background box behind the text so it stays readable over
                    # any part of the frame, no matter how many objects are on screen
                    cv2.rectangle(
                        annotated,
                        (text_x, text_y - th - 4),
                        (text_x + tw + 4, text_y + 4),
                        (0, 0, 0),
                        -1,
                    )
                    cv2.putText(
                        annotated, dist_text, (text_x + 2, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2,
                    )

                if cls_id == PERSON_CLASS_ID:
                    person_detected = True
                    if conf > best_conf:
                        best_conf = conf
                        best_bbox_height = float(y2 - y1)

            person_distance_m = estimate_distance_m(best_bbox_height) if person_detected else None

            # Prefer the real ultrasonic reading over the camera-based guess
            # when a person is detected and the sensor has a valid reading —
            # it's a genuine physical measurement, not an estimate.
            if person_detected:
                ultrasonic_m = get_ultrasonic_distance_m(session)
                if ultrasonic_m is not None:
                    person_distance_m = ultrasonic_m
                    distance_source = "ultrasonic"
                else:
                    distance_source = "camera-estimate"
            else:
                distance_source = None

            if person_distance_m is not None:
                cv2.putText(
                    annotated, f"Distance: {person_distance_m}m ({distance_source})", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,
                )

            cv2.imshow("Live Detection (local preview)", annotated)

            if SHOW_DEPTH_OVERLAY:
                cv2.imshow("Depth View", depth_est.depth_overlay(depth_map))

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
                if person_detected:
                    print(f"[calibration] bbox_height_px={best_bbox_height:.0f}  estimated_distance_m={person_distance_m}")
                try:
                    session.post(
                        f"{BACKEND_URL}/person",
                        json={
                            "person": person_detected,
                            "confidence": best_conf if person_detected else None,
                            "distance_m": person_distance_m,
                        },
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
                    new_point["distance_m"] = person_distance_m
                    print(f"NEW LIFE POINT: {new_point}  (bbox_height_px={best_bbox_height:.0f}, for calibration)")
                    try:
                        session.post(f"{BACKEND_URL}/point", json=new_point, timeout=2)
                    except requests.exceptions.RequestException as e:
                        print("Backend unreachable (point):", e)

            if frame_count % 30 == 0:
                _t_end = time.time()
                print(
                    f"[timing] yolo={_t_yolo - _loop_start:.3f}s  "
                    f"depth={_t_depth - _t_yolo:.3f}s  "
                    f"post/other={_t_end - _t_depth:.3f}s  "
                    f"total={_t_end - _loop_start:.3f}s  "
                    f"(~{1 / max(_t_end - _loop_start, 0.001):.1f} fps)"
                )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()