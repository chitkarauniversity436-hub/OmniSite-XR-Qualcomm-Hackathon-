# sensor_node — full stack (runnable with zero extra hardware)

You don't need the Arduino, a GPS module, or LoRa to run this and see it
working. Four processes, one machine:

```
camera/live_camera_detect.py  --frame-->  backend/app.py (Flask+SQLite)  --GET /video_feed-->  React <img>
                                --person-->        │                     --GET /latest,/points-->  React dashboard
                                --point-->          │
simulator/simulate_sensors.py --detections-->      ┘
```

## 1. Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```
Runs on `http://0.0.0.0:5000`. Creates `sensor_data.db` on first run.

Endpoints:
- `POST /detections` — sensor readings (real Arduino or the simulator)
- `POST /person` — person detected yes/no + confidence
- `POST /point` — a new marked life-detection point {label, lat, lon, confidence, timestamp}
- `POST /frame` — one JPEG frame (raw bytes) for the live video feed
- `GET /video_feed` — MJPEG stream, point an `<img>` at this
- `GET /latest` — combined current sensor + person + risk state
- `GET /history?limit=100` — recent sensor rows for the charts
- `GET /points` — all marked life-detection points for the map

## 2. Camera + detection (webcam only, no GPS/LoRa hardware needed)

```bash
cd camera
pip install ultralytics opencv-python requests
python live_camera_detect.py
```
- First run downloads `yolo11n.pt` automatically (pretrained, already knows "person").
- Opens your webcam, shows a local preview window with bounding boxes.
- Streams annotated frames to the backend — shows up live in the dashboard.
- Uses a **mock GPS** (`MockGPS` class in the file) that simulates the camera
  slowly moving, so life points get real-looking coordinates without a GPS
  module. Change `MOCK_START_LAT` / `MOCK_START_LON` at the top of the file
  to roughly your real location if you want the map centered sensibly.
- Press `q` in the preview window to quit.

## 3. Sensor simulator (no Arduino needed)

```bash
cd simulator
pip install requests
python simulate_sensors.py
```
Posts fake but realistic temperature/humidity/gas/distance values to
`/detections` every 2s, occasionally spiking gas/obstacle so you can see the
WARNING/CRITICAL risk states change live on the dashboard.

## 4. Frontend dashboard

```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. You'll see, all updating live:
- Live camera feed with detection boxes (top)
- Sensor cards (temp/humidity/gas/distance/obstacle/person) + risk banner
- Life-detection map with pins A, B, C...
- Temperature/humidity and gas/distance history charts

Run backend first, then the other three in any order — the frontend and
camera script will just wait/retry until the backend is up.

---

## Swapping in real hardware later

Nothing above needs to change on the backend or frontend — only the data
source changes.

### Real GPS instead of MockGPS
`camera/live_camera_detect.py` only calls `gps.read_latest() -> (lat, lon)`.
Replace `MockGPS` with a real NMEA GPS reader — a working example is in
`rover/rover_life_detect.py` (`GPSReader` class, reads from a serial port).

### Real Arduino instead of the simulator
Use `arduino_original/python/main.py` instead of `simulator/simulate_sensors.py`.
Flash `arduino_original/sketch/sketch.ino` to the board, then in `main.py` set:
```python
FLASK_URL = "http://<backend-machine-IP>:5000/detections"
```
Use `127.0.0.1` only if the board's bridge script runs on the same machine as
`app.py` — otherwise use that machine's real LAN IP (`ipconfig`/`ifconfig`).
**This is the piece that wasn't working before** — the original file had a
placeholder IP address (`10.83.207.93`) that doesn't match your network. Point
it at wherever your `app.py` is actually running and it'll work the same way
the simulator does.

### LoRa long-range signaling instead of direct HTTP
For a real rover operating outside WiFi range, use `rover/rover_life_detect.py`
(GPS + LoRa transmit) together with `base_station/lora_bridge.py` (LoRa
receive → forwards to the same `/point` endpoint) instead of
`camera/live_camera_detect.py`. See the comments in both files for the LoRa
hardware assumptions (REYAX RYLR896-style AT-command module).

## Risk logic (backend/app.py)

`compute_risk()` combines sensor thresholds with the person flag:
- **CRITICAL**: gas ≥ 700, OR (obstacle detected AND distance < 15cm), OR (person present AND gas/obstacle also triggered)
- **WARNING**: gas ≥ 400, OR obstacle detected, OR person present
- **SAFE**: otherwise

Tune `GAS_WARNING`, `GAS_CRITICAL`, `DISTANCE_CRITICAL_CM` in `app.py`.

## Folder guide

| Folder | What it's for |
|---|---|
| `backend/` | Flask API + SQLite, the hub everything talks to |
| `camera/` | **Use this for the no-hardware demo** — webcam + YOLO + mock GPS, direct HTTP to backend |
| `simulator/` | **Use this for the no-hardware demo** — fakes Arduino sensor data |
| `frontend/` | React dashboard — live camera, sensor cards, map, charts |
| `rover/` + `base_station/` | Real-hardware version — GPS + LoRa instead of mock GPS + direct HTTP |
| `arduino_original/` | Your original sketch + bridge script, unchanged |
