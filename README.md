
The mobile app keeps people connected to each other during the disaster. The ground station watches the physical site and finds people automatically. Both are designed to work without any internet connection.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Mobile app | Kotlin, Google Nearby Connections, Room database |
| Mobile AI | Offline knowledge base, or Gemma on Snapdragon NPU |
| Ground station backend | Python, Flask, SQLite |
| Ground station AI | YOLO11 (Ultralytics), OpenCV |
| Dashboard | React, Vite, Leaflet (maps), Recharts (graphs) |
| Future hardware | Arduino, GPS module, LoRa radio |

---

## Getting Started

### Mobile App

```bash
git clone https://github.com/tk24436/DisasterMesh.git
cd DisasterMesh
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

Needs Android 8.0 or newer, with Bluetooth, Wi-Fi, and Location turned on. On first launch, set your name and tap "Join Mesh Network."

### Ground Station

Run these in separate terminals, backend first:

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
python app.py

# 2. Camera + AI detection
cd camera
pip install ultralytics opencv-python requests
python live_camera_detect.py

# 3. Sensor simulator (skip this if you have real hardware)
cd simulator
pip install requests
python simulate_sensors.py

# 4. Dashboard
cd frontend
npm install
npm run dev
```

Open the dashboard at `http://localhost:5173`. You'll see the live camera feed, sensor readings, risk level, and a map of detected people, all updating in real time.

---

## Switching to Real Hardware

Nothing on the backend or dashboard needs to change — only where the data comes from.

- **Real GPS**: replace the mock GPS class in the camera script with a real GPS reader (an example is already in the `rover` folder)
- **Real Arduino sensors**: use the script in `arduino_original/python/main.py` instead of the simulator, and flash the included sketch to your board
- **Long-range LoRa**: for a rover working outside Wi-Fi range, use the rover and base station scripts together instead of the direct camera connection

---

## Risk Level Logic

The backend decides the risk level using simple rules:

- **CRITICAL** – gas level is very high, or an obstacle is closer than 15cm, or a person is detected along with a gas/obstacle warning
- **WARNING** – gas level is moderately high, or an obstacle is nearby, or a person is detected
- **SAFE** – none of the above

These thresholds can be tuned inside `backend/app.py`.

---

## Folder Guide

| Folder | What's inside |
|---|---|
| `backend/` | Flask API and SQLite database, the hub everything connects to |
| `camera/` | Webcam + YOLO detection + mock GPS, for testing without hardware |
| `simulator/` | Fake sensor data generator, for testing without an Arduino |
| `frontend/` | React dashboard with live feed, sensor cards, map, and charts |
| `rover/` + `base_station/` | Real hardware version using GPS and LoRa |
| `arduino_original/` | Original Arduino sketch and bridge script |

---

## What's Next

- Drone support for scanning areas people can't reach on foot
- A small rover that can explore hazardous spaces on its own
- Thermal camera support for finding people in smoke or darkness
- Wider mesh coverage connecting multiple ground stations together
- AR overlays to guide responders to safe paths and survivor locations

---

## Team

| Role | What they worked on |
|---|---|
| AI & Computer Vision | YOLO11 detection, live video streaming, mock GPS |
| Backend | Flask APIs, SQLite, risk level logic |
| Frontend | React dashboard, charts, live map |
| Hardware & IoT | Arduino sensors, GPS, LoRa communication |

---

## License

MIT License — free to use, change, and share with credit.

---

*Built for the Snapdragon Multiverse Hackathon 2026, made to help first responders stay connected and see what's happening, even when the network is down.*
