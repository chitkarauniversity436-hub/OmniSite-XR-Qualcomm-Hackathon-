<div align="center">

# 🚨 OmniSite

### AI-Powered Offline Disaster Monitoring & Victim Detection System

**Built for the Snapdragon Multiverse Hackathon 2026**

*Real-time environmental monitoring, AI-based human detection, and offline emergency response using Edge AI.*

<p>
  <img src="https://img.shields.io/badge/Hackathon-Snapdragon%20Multiverse%202026-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-Snapdragon%20X%20Elite-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Edge%20AI-Qualcomm%20AI%20Hub-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Backend-Flask-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge" />
</p>

---

**📡 Offline First • 🤖 Edge AI • 📹 Live Detection • 📍 Location Mapping • 🚑 Disaster Response**

</div>

---


## 🌍 Overview

**OmniSite-XR** is an **offline AI-powered disaster monitoring and victim detection system** designed to assist rescue teams in hazardous environments where internet connectivity may be unavailable.

The system combines **real-time environmental sensing**, **AI-based human detection**, **live video streaming**, and **location mapping** into a unified dashboard that provides situational awareness during emergency response operations.

The backend is built using **Flask** with **SQLite** for lightweight data storage, while a **React dashboard** visualizes live sensor readings, risk levels, AI detections, historical trends, and detected victim locations.

A **YOLO11 object detection model** running on a webcam identifies people in real time and streams annotated video to the dashboard. Every confirmed detection is stored as a geographic point using a configurable **Mock GPS**, allowing the complete system to be demonstrated without requiring physical GPS hardware.

For demonstrations without embedded hardware, a built-in **sensor simulator** continuously generates realistic temperature, humidity, gas, distance, and obstacle readings. The simulator enables the dashboard, backend, and AI pipeline to function exactly as they would with real sensors.

The project follows a **modular architecture**, allowing the simulator to be seamlessly replaced with real Arduino sensors, GPS modules, and LoRa communication without modifying the backend or frontend. This makes SensorNode suitable for both software demonstrations and real-world disaster response deployments.

## ❗ Problem

During disaster response operations such as earthquakes, building collapses, fires, and industrial accidents, first responders often have limited visibility into hazardous environments. Entering these areas without accurate information can expose rescue teams to dangerous conditions such as toxic gases, high temperatures, structural obstacles, and poor visibility.

Traditional monitoring systems frequently depend on cloud services, continuous internet connectivity, or expensive specialized equipment. However, communication networks are often disrupted during emergencies, making these solutions unreliable when they are needed most.

Additionally, rescue teams require a unified view of environmental conditions, live visual information, and victim locations. Existing systems typically provide only isolated sensor readings or camera feeds, forcing responders to manually combine information from multiple sources and slowing critical decision-making.

There is a need for an affordable, offline-first, and real-time disaster monitoring system that can:

- Detect people using AI-powered computer vision.
- Monitor environmental conditions such as temperature, humidity, gas levels, and nearby obstacles.
- Stream live annotated video to responders.
- Mark potential victim locations on a map.
- Assess risk levels instantly.
- Continue operating even when internet connectivity is unavailable.

SensorNode addresses these challenges by combining edge AI, real-time sensor monitoring, live video streaming, and location mapping into a single integrated platform designed for disaster response.

## 💡 Solution

SensorNode provides an **offline-first, AI-powered disaster monitoring platform** that integrates computer vision, environmental sensing, and real-time visualization into a single system for emergency response.

The system consists of four core components working together over a local network:

- **AI Camera Module** captures live webcam footage and performs **real-time person detection** using the **YOLO11** object detection model. Detected individuals are highlighted with bounding boxes, and their locations are recorded using a configurable **Mock GPS** for demonstration purposes.
- **Flask Backend** acts as the central hub, receiving live video frames, sensor readings, AI detection results, and location points. It stores historical data in **SQLite**, computes the overall risk level, and exposes REST APIs for the dashboard.
- **Sensor Simulator** continuously generates realistic temperature, humidity, gas, distance, and obstacle readings, enabling the complete system to operate without requiring physical hardware. The simulator can later be replaced by a real Arduino-based sensing unit without changing the backend or frontend.
- **React Dashboard** provides a real-time monitoring interface displaying the live camera feed, environmental sensor values, AI detection status, risk alerts, historical charts, and a map of detected life locations.

All communication occurs over a **local network**, allowing the platform to function without internet connectivity. Thanks to its modular architecture, SensorNode can seamlessly transition from a software-only demonstration to a real deployment by replacing the simulator with Arduino sensors, integrating GPS modules, and enabling long-range LoRa communication.

## ✨ Features

- 🤖 **Real-Time AI Person Detection** – Detects people using the YOLO11 object detection model and displays live bounding boxes with confidence scores.
- 📹 **Live Video Streaming** – Streams annotated webcam footage to the dashboard using an MJPEG video feed for real-time monitoring.
- 🌡️ **Environmental Monitoring** – Continuously monitors temperature, humidity, gas concentration, distance, and obstacle status.
- ⚠️ **Intelligent Risk Assessment** – Automatically classifies the environment as **SAFE**, **WARNING**, or **CRITICAL** based on configurable sensor thresholds and AI detection results.
- 📍 **Life Detection Mapping** – Records detected person locations as map markers using GPS coordinates (Mock GPS for demo, real GPS supported).
- 📊 **Interactive Dashboard** – Displays live sensor readings, AI detections, risk status, historical charts, and location data in a unified React interface.
- 🗄️ **Historical Data Storage** – Stores sensor readings and detection history in SQLite for visualization and analysis.
- 🔄 **REST API Architecture** – Provides well-defined API endpoints for sensor data, AI detections, video streaming, historical records, and map points.
- 📡 **Offline-First Operation** – Runs entirely over a local network without requiring cloud services or internet connectivity.
- 🧪 **Built-In Sensor Simulator** – Generates realistic environmental data, enabling full system demonstrations without Arduino hardware.
- 🔌 **Hardware Ready** – Supports seamless replacement of the simulator with real Arduino sensors, GPS modules, and LoRa communication without modifying the backend or frontend.
- 🧩 **Modular & Scalable Design** – Independent backend, frontend, AI, and sensing modules simplify development, testing, and future expansion.

## 🏗️ Architecture

SensorNode follows a **modular edge-computing architecture** where AI-based person detection, environmental sensing, backend processing, and the user interface run as independent components while communicating through REST APIs over a local network.

This design allows the complete system to run on a single machine for demonstration purposes while remaining fully compatible with future hardware integration such as Arduino sensors, GPS modules, and LoRa communication.

```mermaid
graph LR

A[Camera Module<br/>YOLO11 + Webcam]
B[Sensor Simulator<br/>Temperature • Humidity • Gas • Distance]
C[Flask Backend<br/>REST API • SQLite • Risk Engine]
D[React Dashboard<br/>Live Camera • Charts • Map]

A -->|Annotated Frames| C
A -->|Person Detection| C
A -->|Life Detection Point| C

B -->|Sensor Readings| C

C -->|MJPEG Stream| D
C -->|Latest Status| D
C -->|History Data| D
C -->|Map Points| D
```

### Device / Module Responsibilities

| Module | Responsibility |
|---------|----------------|
| **Camera Module** | Captures webcam video, performs YOLO11 person detection, streams annotated frames, and records life-detection points. |
| **Sensor Simulator** | Generates realistic temperature, humidity, gas, distance, and obstacle readings for software-only demonstrations. |
| **Flask Backend** | Receives sensor and AI data, computes risk levels, stores historical records in SQLite, and exposes REST APIs for the dashboard. |
| **React Dashboard** | Displays the live camera feed, sensor cards, risk status, historical charts, and life-detection map in real time. |

> **Central Hub:** The Flask backend acts as the core of the system. It receives AI detections, sensor readings, and location data, calculates the overall risk level, stores historical information in SQLite, and serves live updates to the React dashboard through REST APIs and MJPEG video streaming.
### Device Responsibilities

| Device | Responsibility |
|---------|----------------|
| **Arduino UNO Q** | Collects temperature, humidity, and gas sensor data. |
| **Snapdragon X Elite Laptop** | Runs AI inference, processes sensor data, calculates risk, and manages communication. |
| **OnePlus Phone** | Streams live camera feed and displays the rescue dashboard with alerts. |

## 🔧 Hardware

OmniSight-XR is built using three devices that work together to provide real-time disaster monitoring and victim detection.

| Device | Purpose |
|---------|---------|
| **Arduino UNO Q** | Collects environmental data from temperature, humidity, and gas sensors. |
| **Temperature & Humidity Sensor** | Monitors environmental conditions around the disaster site. |
| **Gas Sensor** | Detects hazardous gases and alerts responders to unsafe conditions. |
| **OnePlus Smartphone** | Streams live camera footage and displays the rescue dashboard. |
| **Snapdragon X Elite Laptop** | Acts as the central hub, running AI inference, processing sensor data, and managing communication between devices. |

> **Central Device:** The Snapdragon X Elite laptop is the brain of the system. It receives sensor data from the Arduino, processes the live camera feed using on-device AI, combines both data sources, and sends real-time alerts to the mobile dashboard over a local Wi-Fi network.

## 💻 Tech Stack

| Category | Technology |
|----------|------------|
| **Programming Languages** | Python, JavaScript |
| **Frontend** | React, Vite, HTML5, CSS3 |
| **Backend** | Flask, Flask-CORS |
| **Database** | SQLite |
| **AI / Computer Vision** | YOLO11 (Ultralytics), OpenCV |
| **Machine Learning** | Pre-trained YOLO11 Object Detection Model |
| **Data Visualization** | Recharts |
| **Mapping** | React Leaflet, Leaflet, OpenStreetMap |
| **Communication** | REST APIs, HTTP, MJPEG Video Streaming |
| **Simulation** | Python Sensor Simulator, Mock GPS |
| **Development Tools** | VS Code, Git, GitHub, npm, pip |
| **Deployment Platform** | Local Machine / Edge Device |
| **Future Hardware Support** | Arduino, GPS Module, LoRa Communication |

## 📂 Project Structure

```text
sensor_node/
│
├── backend/                     # Flask backend and REST APIs
│   ├── app.py                   # Main backend application
│   ├── sensor_data.db           # SQLite database (created automatically)
│   ├── requirements.txt
│   └── ...
│
├── camera/                      # AI camera module
│   ├── live_camera_detect.py    # YOLO11 person detection & MJPEG streaming
│   └── ...
│
├── simulator/                   # Sensor simulator
│   ├── simulate_sensors.py      # Generates mock sensor readings
│   └── ...
│
├── frontend/                    # React dashboard
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── assets/
│   ├── package.json
│   └── vite.config.js
│
├── rover/                       # Real rover implementation (GPS + LoRa)
│   ├── rover_life_detect.py
│   └── ...
│
├── base_station/                # LoRa receiver and backend bridge
│   ├── lora_bridge.py
│   └── ...
│
├── arduino_original/            # Original Arduino firmware and bridge script
│   ├── sketch/
│   ├── python/
│   └── ...
│
├── README.md
├── LICENSE
└── .gitignore
```

- Python 3.10+
- Node.js (v18+)
- npm
- Git
- A webcam (for AI person detection)

---

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/sensor_node.git
cd sensor_node
```

---

### 2️⃣ Start the Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend runs on:

```
http://localhost:5000
```

---

### 3️⃣ Start the AI Camera Module

Open a new terminal:

```bash
cd camera
pip install ultralytics opencv-python requests
python live_camera_detect.py
```

This module:
- Captures live webcam video.
- Performs real-time YOLO11 person detection.
- Streams annotated frames to the backend.
- Generates mock GPS coordinates for detected life points.

---

### 4️⃣ Start the Sensor Simulator

Open another terminal:

```bash
cd simulator
pip install requests
python simulate_sensors.py
```

The simulator continuously sends realistic temperature, humidity, gas, distance, and obstacle readings to the backend.

---

### 5️⃣ Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```
http://localhost:5173
```

---

### 6️⃣ View the Dashboard

Once all services are running, you'll see:

- 📹 Live AI camera feed
- 👤 Person detection with confidence scores
- 🌡️ Live environmental sensor data
- ⚠️ Dynamic risk assessment
- 📍 Life detection map
- 📊 Historical sensor charts


## 🔄 Workflow

```text
┌──────────────────────┐
│   Arduino UNO Q      │
│ (Temp • Humidity •   │
│     Gas Sensors)     │
└──────────┬───────────┘
           │ Sensor Data
           ▼
┌──────────────────────┐
│ Snapdragon X Elite   │
│ • AI Person Detection│
│ • Risk Analysis      │
│ • Backend Server     │
└──────────┬───────────┘
           ▲
           │ Live Camera Stream
┌──────────┴───────────┐
│   OnePlus Phone      │
│      Camera          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Live Dashboard      │
│ • Victim Detection   │
│ • Sensor Readings    │
│ • Hazard Alerts      │
└──────────────────────┘
```

### How It Works

1. **Arduino UNO Q** continuously monitors **temperature, humidity, and gas levels**.
2. **OnePlus smartphone** captures a live video stream of the disaster area.
3. **Snapdragon X Elite laptop** receives both the sensor data and camera feed.
4. The laptop performs **AI-based person detection**, analyzes environmental conditions, and calculates the risk level.
5. The processed information is sent to the **mobile dashboard** in real time over a **local Wi-Fi network**, enabling rescue teams to make faster and safer decisions.

## 📱 Dashboard

The **OmniSight-XR Dashboard** provides rescue teams with a clear, real-time view of the disaster site by combining AI detections and environmental sensor data into a single interface.

### Dashboard Features

- 👤 **Victim Detection** – Displays AI-detected victims with confidence scores.
- 🌡️ **Temperature Monitoring** – Shows the current temperature.
- 💧 **Humidity Monitoring** – Displays environmental humidity levels.
- ☁️ **Gas Detection** – Indicates hazardous gas levels.
- ⚠️ **Hazard Alerts** – Highlights unsafe conditions using color-coded warnings.
- 📡 **Connection Status** – Shows the connectivity of all devices.
- 🕒 **Live Updates** – Refreshes automatically through WebSockets.

### Dashboard Preview

```text
+--------------------------------------------------+
|              🚨 OmniSight-XR Dashboard           |
+--------------------------------------------------+
| 👤 Victim Detected      ✅Yes(96% )             |
| 🌡️ Temperature          38° C                    |
| 💧 Humidity             72 %                     |
| ☁️ Gas Level            HIGH                     |
| ⚠️ Risk Level           🔴Critical              |
| 📡 Device Status        🟢Connected             |
+--------------------------------------------------+
|          Live Camera Feed / Detection            |
+--------------------------------------------------+
```

> The dashboard is optimized for mobile devices, enabling rescue teams to monitor hazards and victim detections in real time while operating entirely offline.

## 📸 Demo

### 🎥 Demo Video

> 📹 **Coming Soon** *(Demo video will be added after the final project implementation.)*

<!-- Replace with your demo video -->
<!-- https://youtu.be/your-demo-link -->

---

## 📷 Project Demo

### 🎥 Demo Video

> 📹 **Coming Soon** *(A complete demonstration video showcasing the full disaster monitoring workflow will be added after final implementation.)*

<!-- Replace with your demo video -->
<!-- https://youtu.be/your-demo-link -->

---

### 📷 Demonstration

#### 1️⃣ AI Person Detection
- Live webcam feed processed using **YOLO11**.
- Real-time person detection with confidence scores.
- Annotated video streamed directly to the dashboard.

#### 2️⃣ Environmental Monitoring
- Live temperature monitoring
- Humidity tracking
- Gas level detection
- Distance and obstacle monitoring
- Automatic risk level computation

#### 3️⃣ Interactive Dashboard
- Live camera stream
- Sensor cards with real-time values
- Risk status (SAFE / WARNING / CRITICAL)
- Historical sensor charts
- System status updates

#### 4️⃣ Life Detection Map
- Displays detected person locations.
- Mock GPS generates realistic coordinates for demonstration.
- Interactive map with labeled detection points.

---

### 📸 Screenshots

| Live Camera Feed | Dashboard |
|------------------|-----------|
| *Coming Soon* | *Coming Soon* |

| Sensor Charts | Life Detection Map |
|----------------|--------------------|
| *Coming Soon* | *Coming Soon* |

---

> **Demo Scenario:** The AI Camera module captures a live webcam feed and performs real-time person detection using YOLO11. Simultaneously, the Sensor Simulator generates environmental readings such as temperature, humidity, gas concentration, and obstacle distance. The Flask backend processes all incoming data, computes the overall risk level, stores historical records in SQLite, and streams live updates to the React dashboard. The dashboard visualizes the annotated camera feed, sensor values, risk alerts, historical charts, and life-detection points on an interactive map—all operating entirely over a local network without requiring additional hardware.

## 👨‍💻 Team

| Member | Role | Responsibilities |
|--------|------|------------------|
| **Member A** | 🤖 AI & Computer Vision | YOLO11 integration, real-time person detection, live video streaming, Mock GPS integration |
| **Member B** | ⚙️ Backend Developer | Flask REST APIs, SQLite database, risk assessment engine, API integration |
| **Member C** | 💻 Frontend Developer | React dashboard, live camera feed, sensor visualization, charts, interactive map |
| **Member D** | 🔧 IoT & Hardware | Arduino integration, sensor communication, GPS & LoRa support, hardware testing |

---

### 🤝 Collaboration

SensorNode was developed using a **modular development approach**, allowing each team member to focus on a specific subsystem while collaborating closely during integration and testing.

- 🤖 **AI Module** – Real-time YOLO11 person detection, frame processing, and life-point generation.
- ⚙️ **Backend Module** – Flask APIs, SQLite database, risk computation, and data management.
- 💻 **Frontend Module** – Interactive React dashboard with live video, sensor cards, historical charts, and map visualization.
- 🔧 **Hardware Module** – Arduino-based sensor integration, GPS support, LoRa communication, and future edge-device deployment.

Together, these components create a unified **offline-first disaster monitoring and victim detection system** capable of assisting emergency responders with real-time situational awareness.

---

## 🚀 Future Scope

Although OmniSight-XR is designed as an offline disaster response system, its modular architecture allows it to be extended for more advanced rescue operations in the future.

- 🚁 **Drone Integration** – Deploy drones for aerial surveillance and victim detection in inaccessible areas.
- 🤖 **Autonomous Rescue Rover** – Mount the sensing unit on a ground rover for remote exploration of hazardous environments.
- 🌡️ **Thermal Camera Support** – Improve victim detection in smoke, darkness, or low-visibility conditions.
- 📍 **GPS & Location Tracking** – Share the precise location of detected victims and hazards with rescue teams.
- 🌐 **Mesh Networking** – Connect multiple sensor nodes to cover larger disaster zones without internet access.
- 🧠 **Advanced AI Models** – Detect additional hazards such as fire, smoke, structural damage, and emergency equipment.
- 📊 **Incident History & Analytics** – Store rescue events, sensor readings, and AI detections for post-disaster analysis.
- 🥽 **AR-Based Navigation** – Guide first responders with augmented reality overlays showing safe routes and victim locations.

> OmniSight-XR is built with scalability in mind, making it adaptable for future smart rescue systems powered by edge AI and multi-device collaboration.

## 📜 License

This project is licensed under the **MIT License**, allowing anyone to use, modify, and distribute the software with proper attribution.

For more details, see the [LICENSE](LICENSE) file.

---
<div align="center">

**Built with ❤️ for the Snapdragon Multiverse Hackathon 2026**

*Empowering first responders with Offline AI, Edge Computing, and Multi-Device Intelligence.*

⭐ If you found this project interesting, consider giving it a **Star** on GitHub!

</div>
