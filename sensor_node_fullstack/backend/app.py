"""
Flask backend for the sensor_node project.

Receives:
  POST /detections   -> from the Arduino Python bridge (main.py) - sensor readings
  POST /person        -> from the YOLOv11 script - person detection results
  GET  /latest         -> combined latest state (for the React dashboard)
  GET  /history?limit=100 -> recent rows (for charts)

Environmental risk (gas/obstacle/distance) and person detection are tracked
SEPARATELY — person_status does not affect risk, and vice versa.
"""
# IMPORTED ALL THE LIB
import sqlite3
import time
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS

DB_PATH = "sensor_data.db"
app = Flask(__name__)
CORS(app)  # allow the React dev server to call this API

# latest annotated camera frame (JPEG bytes), for the live video feed
frame_lock = threading.Lock()
latest_frame = {"bytes": None, "updated_at": None}

# in-memory latest state (fast reads for the dashboard / risk calc)
state_lock = threading.Lock()
# STORED ALL THE VALUES TEMP, HUM ADN MORE TO NONE
latest_state = {
    "temperature": None,
    "humidity": None,
    "gas": None,
    "distance_cm": None,
    "obstacle_detected": False,
    "person": False,
    "person_confidence": None,
    "risk": "SAFE",
    "person_status": "CLEAR",
    "updated_at": None,
}

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            temperature REAL,
            humidity REAL,
            gas INTEGER,
            distance_cm REAL,
            obstacle_detected INTEGER,
            person INTEGER,
            person_confidence REAL,
            risk TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS life_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT UNIQUE,
            lat REAL,
            lon REAL,
            confidence REAL,
            timestamp REAL
        )
    """)
    conn.commit()
    conn.close()


def save_reading(row):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO readings
           (timestamp, temperature, humidity, gas, distance_cm,
            obstacle_detected, person, person_confidence, risk)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            row["timestamp"], row["temperature"], row["humidity"], row["gas"],
            row["distance_cm"], int(row["obstacle_detected"]), int(row["person"]),
            row["person_confidence"], row["risk"],
        ),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Risk calculation
# ---------------------------------------------------------------------------
# Tune these thresholds to your actual sensors/environment.
GAS_WARNING = 600
GAS_CRITICAL = 900
DISTANCE_CRITICAL_CM = 50  # something is very close


def compute_risk(s):
    """Purely environmental risk — gas/obstacle/distance only. Person detection
    is reported separately via person_status(), not mixed into this."""
    gas = s.get("gas") or 0
    distance = s.get("distance_cm")
    obstacle = s.get("obstacle_detected")

    # CHECK VALUES AND THEN CAL IF SOMETHING IS WRONG AND ACT ACCORDINGLY
    if gas >= GAS_CRITICAL:
        return "CRITICAL"
    if distance is not None and distance != -1 and distance < DISTANCE_CRITICAL_CM and obstacle:
        return "CRITICAL"
    if gas >= GAS_WARNING or obstacle:
        return "WARNING"
    return "SAFE"


def person_status(s):
    """Separate from environmental risk — just reports whether a person is
    currently in frame, independent of how safe/unsafe the environment is."""
    return "PERSON FOUND" if s.get("person") else "CLEAR"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/detections", methods=["POST"])
def detections():
    """Called every ~2s by the Arduino bridge (python/main.py)."""
    data = request.get_json(force=True) or {}

    with state_lock:
        latest_state["temperature"] = data.get("temperature")
        latest_state["humidity"] = data.get("humidity")
        latest_state["gas"] = data.get("gas")
        latest_state["distance_cm"] = data.get("distance_cm")
        latest_state["obstacle_detected"] = bool(data.get("obstacle_detected"))
        # person/person_confidence come from the YOLO worker, keep whatever we
        # already have unless the Arduino payload explicitly overrides it
        risk = compute_risk(latest_state)
        latest_state["risk"] = risk
        latest_state["person_status"] = person_status(latest_state)
        latest_state["updated_at"] = time.time()

        row = dict(latest_state)
        row["timestamp"] = latest_state["updated_at"]

    save_reading(row)

    return jsonify({"stored": {"risk": risk, "person_status": latest_state["person_status"]}}), 200


@app.route("/person", methods=["POST"])
def person():
    """Called continuously by the YOLOv11 detection script."""
    data = request.get_json(force=True) or {}
    detected = bool(data.get("person", False))
    confidence = data.get("confidence")

    with state_lock:
        latest_state["person"] = detected
        latest_state["person_confidence"] = confidence
        latest_state["person_status"] = person_status(latest_state)
        # risk is intentionally NOT recomputed here — it's purely environmental
        # (gas/obstacle/distance) and person detection doesn't change it
        latest_state["updated_at"] = time.time()

    return jsonify({"person_status": latest_state["person_status"]}), 200


@app.route("/point", methods=["POST"])
def add_point():
    """Called by base_station/lora_bridge.py when the rover marks a new life point."""
    data = request.get_json(force=True) or {}
    label = data.get("label")
    lat = data.get("lat")
    lon = data.get("lon")

    if label is None or lat is None or lon is None:
        return jsonify({"error": "label, lat, lon are required"}), 400

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT OR IGNORE INTO life_points
               (label, lat, lon, confidence, timestamp)
               VALUES (?, ?, ?, ?, ?)""",
            (label, lat, lon, data.get("confidence"), data.get("timestamp", time.time())),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"stored": label}), 200


@app.route("/points", methods=["GET"])
def get_points():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM life_points ORDER BY id ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200


@app.route("/frame", methods=["POST"])
def upload_frame():
    """Called continuously by the camera script — stores the latest annotated JPEG frame."""
    jpeg_bytes = request.get_data()
    if not jpeg_bytes:
        return jsonify({"error": "no image data received"}), 400
    with frame_lock:
        latest_frame["bytes"] = jpeg_bytes
        latest_frame["updated_at"] = time.time()
    return jsonify({"stored": True}), 200


@app.route("/video_feed", methods=["GET"])
def video_feed():
    """MJPEG stream the React <img> tag can point straight at."""
    def generate():
        boundary = b"--frame"
        while True:
            with frame_lock:
                frame = latest_frame["bytes"]
            if frame is not None:
                yield (
                    boundary + b"\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            time.sleep(0.2)  # ~10fps re-serve rate

    return app.response_class(
        generate(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/latest", methods=["GET"])
def latest():
    with state_lock:
        return jsonify(dict(latest_state)), 200


@app.route("/history", methods=["GET"])
def history():
    limit = int(request.args.get("limit", 100))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in reversed(rows)]), 200


if __name__ == "__main__":
    init_db()
    # host 0.0.0.0 so the Arduino board (on your LAN) can reach it too
    app.run(host="0.0.0.0", port=5000, debug=True)
