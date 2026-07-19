"""
Runs ON THE ROVER.

Camera -> YOLOv11 person detection -> GPS tagging -> dedup by distance
-> assign next label (A, B, C...) -> transmit over LoRa.

Hardware assumed:
  - USB/CSI camera
  - GPS module (NMEA over serial, e.g. u-blox NEO-6M/NEO-M8N) on /dev/ttyUSB_GPS
  - LoRa module with AT-command UART interface (e.g. REYAX RYLR896) on /dev/ttyUSB_LORA
    -> adjust send_lora() if your module uses a different interface (SPI radio
       modules like RFM95 need a library like `pyLoRa` or a Feather-style driver
       instead of AT commands; the packet format below stays the same either way)

pip install ultralytics opencv-python pyserial pynmea2
"""
# IMPORT ALL THE LIB
import time
import json
import serial
import pynmea2
import cv2
from ultralytics import YOLO
from math import radians, sin, cos, sqrt, atan2

# ---------------------------------------------------------------------------
# Config
# CAMERA CHARACTERFICATION
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0
MODEL_NAME = "yolo11n.pt"
CONF_THRESHOLD = 0.5
PERSON_CLASS_ID = 0

GPS_PORT = "/dev/ttyUSB_GPS"
GPS_BAUD = 9600

LORA_PORT = "/dev/ttyUSB_LORA"
LORA_BAUD = 115200
LORA_TARGET_ADDR = 0  # RYLR896-style: 0 = broadcast / base station address

DEDUP_RADIUS_M = 5.0          # ignore a detection within this distance of an existing point
DETECTION_COOLDOWN_SEC = 3.0  # min time between checking for a *new* point, even if person stays in frame

# ---------------------------------------------------------------------------
# GPS
# ---------------------------------------------------------------------------

class GPSReader:
    def __init__(self, port, baud):  # SIMPLE CONSTRUCTOR
        self.ser = serial.Serial(port, baud, timeout=1)
        self.last_fix = None  # (lat, lon)

    def read_latest(self):  # READ BUFFERED SENTENCES
        """Non-blocking-ish: read whatever NMEA sentences are buffered, keep the latest GGA fix."""
        try:
            while self.ser.in_waiting:
                line = self.ser.readline().decode("ascii", errors="ignore").strip()
                if line.startswith("$GPGGA") or line.startswith("$GNGGA"):
                    msg = pynmea2.parse(line)
                    if msg.latitude and msg.longitude:
                        self.last_fix = (msg.latitude, msg.longitude)
        except Exception as e:
            print("GPS read error:", e)
        return self.last_fix


def haversine_m(lat1, lon1, lat2, lon2):  # CAL DISTANCE
    """Distance in meters between two lat/lon points."""
    R = 6371000
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlambda / 2) ** 2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))


# ---------------------------------------------------------------------------
# LoRa transmit (REYAX RYLR896-style AT commands — adjust for your module)
# ---------------------------------------------------------------------------

class LoRaLink:
    def __init__(self, port, baud):  # SIMPLE CONSTRUC
        self.ser = serial.Serial(port, baud, timeout=2)

    def send(self, payload: dict):  # PRINT THE DATA 
        data = json.dumps(payload)
        cmd = f"AT+SEND={LORA_TARGET_ADDR},{len(data)},{data}\r\n"
        self.ser.write(cmd.encode())
        print("LoRa TX:", data)


# ---------------------------------------------------------------------------
# Point labeling / dedup
# ---------------------------------------------------------------------------

class LifePointTracker:
    """Keeps marked points in memory and decides if a new detection is a NEW point."""

    def __init__(self):
        self.points = []  # list of dicts: {label, lat, lon, confidence, timestamp}
        self._next_label_idx = 0

    def _next_label(self):
        # A, B, C ... Z, AA, AB ...
        idx = self._next_label_idx
        self._next_label_idx += 1
        label = ""
        idx_copy = idx
        while True:
            label = chr(65 + idx_copy % 26) + label
            idx_copy = idx_copy // 26 - 1
            if idx_copy < 0:
                break
        return label

    def maybe_add(self, lat, lon, confidence):
        """Returns the new point dict if this is a genuinely new life detection, else None."""
        for p in self.points:
            if haversine_m(lat, lon, p["lat"], p["lon"]) < DEDUP_RADIUS_M:
                return None  # already marked nearby, skip

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
        raise RuntimeError("Could not open camera")

    gps = GPSReader(GPS_PORT, GPS_BAUD)
    lora = LoRaLink(LORA_PORT, LORA_BAUD)
    tracker = LifePointTracker()

    last_check = 0.0

    print("Rover life-detection loop running. Ctrl+C to stop.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.2)
                continue

            results = model(frame, verbose=False)[0]

            person_detected = False
            best_conf = 0.0
            for box in results.boxes:
                if int(box.cls[0]) == PERSON_CLASS_ID and float(box.conf[0]) >= CONF_THRESHOLD:
                    person_detected = True
                    best_conf = max(best_conf, float(box.conf[0]))

            annotated = results.plot()
            cv2.imshow("Rover - Life Detection", annotated)

            now = time.time()
            if person_detected and (now - last_check) >= DETECTION_COOLDOWN_SEC:
                last_check = now
                fix = gps.read_latest()
                if fix is None:
                    print("Person detected but no GPS fix yet — skipping mark")
                else:
                    lat, lon = fix
                    new_point = tracker.maybe_add(lat, lon, best_conf)
                    if new_point:
                        print("NEW LIFE POINT:", new_point)
                        lora.send(new_point)
                    else:
                        print("Person detected but already marked nearby — skipping")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
