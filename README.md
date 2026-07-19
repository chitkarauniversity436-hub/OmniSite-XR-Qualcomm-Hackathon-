# 🚨 OmniSight-XR (DisasterMesh)

> Offline disaster monitoring and emergency mesh network — built for places where the internet and cell towers are gone.

**Built for the Snapdragon Multiverse Hackathon 2026**

![Platform](https://img.shields.io/badge/Platform-Android%20%2B%20Web-green)
![Language](https://img.shields.io/badge/Language-Kotlin%20%2F%20Python%20%2F%20JS-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

---

## What This Is

When a disaster hits, the first thing that breaks is communication. Cell towers go down, internet stops working, and rescue teams end up cut off from each other and from the people who need help.

OmniSight-XR fixes this by combining two things into one system: a phone-to-phone mesh network for people on the ground, and an AI-powered sensor station that watches the disaster site and finds survivors automatically. Everything works without internet, using only local radios and a local network.

---

## The Two Parts

### 1. DisasterMesh (Mobile App)

Every phone running the app becomes a node in a mesh network, using just Bluetooth and Wi-Fi Direct through Google's Nearby Connections API. No SIM card, no internet, no central server needed.

- **Mesh chat** – messages hop from phone to phone until they reach the right person
- **SOS broadcasts** – emergency alerts spread across the whole mesh automatically, sorted by priority
- **Heartbeat check** – every phone sends a small signal every 10 seconds so the app knows who is still online, and marks someone offline if they go quiet for 45 seconds
- **Offline first aid AI** – a built-in assistant gives basic first aid steps with zero internet
- **Dark mode UI** – simple screen that's easy to read in low light or stressful moments

On phones with a Snapdragon 8 Elite chip, the first aid assistant can upgrade to a real AI model (Gemma) that runs directly on the phone's NPU, using Qualcomm's AI Runtime. On regular phones, it just falls back to a built-in knowledge base — no extra setup needed.

### 2. OmniSight-XR (Ground Station)

While the mesh handles communication between people, this part watches the disaster area itself using a camera and sensors, and looks for survivors on its own.

- **AI person detection** – a webcam runs a YOLO11 model to spot people in real time
- **Live video feed** – the camera view streams straight to a dashboard so responders can see what's happening
- **Environment sensors** – tracks temperature, humidity, gas levels, and nearby obstacles
- **Risk level** – the system automatically labels the area SAFE, WARNING, or CRITICAL based on what the sensors and camera detect
- **Location map** – every detected person gets marked on a map using GPS (or a mock GPS for testing without hardware)
- **History charts** – past sensor readings are saved so teams can see how conditions changed over time

Right now this part runs with a webcam and simulated sensors, so anyone can test it without needing the actual Arduino, GPS, or LoRa hardware. Swapping in real hardware later needs no changes to the backend or dashboard — you just point it at real sensors instead of the simulator.

---

## How It All Fits Together
Phones (DisasterMesh) <-- mesh network --> People on the ground
|
Ground Station (OmniSight-XR)
Camera + AI --> Flask Backend --> React Dashboard
Sensors --> |
SQLite storage


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
