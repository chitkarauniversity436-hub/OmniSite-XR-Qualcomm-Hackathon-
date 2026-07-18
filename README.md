# 🚨 OmniSight-XR

<p align="center">

**Offline AI-Powered Disaster Response System**

*Snapdragon Multiverse Hackathon 2026*

---

*"Respond Faster. Save Lives."*

</p>

---

# 📖 Table of Contents

* [Overview](#-overview)
* [Problem Statement](#-problem-statement)
* [Our Solution](#-our-solution)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Hardware Architecture](#-hardware-architecture)
* [Project Structure](#-project-structure)
* [Technology Stack](#-technology-stack)
* [Communication Flow](#-communication-flow)
* [AI Pipeline](#-ai-pipeline)
* [Installation Guide](#-installation-guide)
* [Running the Project](#-running-the-project)
* [Team Responsibilities](#-team-responsibilities)
* [Milestones](#-milestones)
* [Future Scope](#-future-scope)
* [Screenshots](#-screenshots)
* [Demo Video](#-demo-video)
* [License](#-license)

---

# 🌍 Overview

OmniSight-XR is an **offline, multi-device disaster response platform** that combines embedded sensing, edge AI and real-time visualization to assist first responders during earthquakes, building collapses, industrial accidents and rescue missions.

Unlike cloud-based rescue systems, OmniSight-XR works entirely on a **local network**, making it reliable even when internet and cellular infrastructure fail.

---

# ❗ Problem Statement

During disasters:

* Communication networks often fail.
* Hazardous environments prevent rescuers from entering safely.
* Existing rescue robots are expensive.
* Cloud-based AI systems cannot operate without connectivity.

Rescue teams need an intelligent system capable of operating completely offline while providing real-time situational awareness.

---

# 💡 Our Solution

OmniSight-XR builds a local rescue ecosystem using three devices.

```
                Camera
                   │
                   ▼
      Surface Laptop (Snapdragon AI)
                   ▲
                   │
Arduino Sensors ───┘
                   │
                   ▼
        OnePlus Mobile Dashboard
```

The Arduino collects environmental data.

The Snapdragon laptop performs on-device AI inference.

The OnePlus phone receives real-time updates through WebSockets.

No internet required.

---

# ✨ Key Features

## 🔥 Edge AI

* On-device AI inference
* Qualcomm AI Hub models
* Snapdragon NPU acceleration

---

## 📡 Offline Communication

* Local Wi-Fi
* WebSockets
* Zero cloud dependency

---

## 🌡 Hazard Detection

* Gas Monitoring
* Temperature Monitoring
* Live Hazard Alerts

---

## 👤 Human Detection

* Camera-based victim detection
* Live confidence scores
* Real-time updates

---

## 📱 Mobile Dashboard

* Radar View
* Hazard Indicators
* AI Detection Cards
* Live Status

---

# 🏗 System Architecture

```
               Camera Feed
                    │
                    ▼
      +-----------------------------+
      | Snapdragon Laptop           |
      |-----------------------------|
      | AI Model                    |
      | Detection Engine            |
      | WebSocket Server            |
      +-----------------------------+
             ▲                │
             │                │
             │                ▼
+--------------------+   +----------------------+
| Arduino UNO Q      |   | OnePlus Dashboard    |
|--------------------|   |----------------------|
| Gas Sensor         |   | Live Radar           |
| Temperature Sensor |   | Hazard Status        |
| JSON Sender        |   | Detection Cards      |
+--------------------+   +----------------------+
```

---

# 🔌 Hardware Architecture

| Device           | Purpose          |
| ---------------- | ---------------- |
| Arduino UNO Q    | Sensor Node      |
| Surface Laptop 7 | AI Hub + Backend |
| OnePlus 15       | Dashboard        |

---

# 📂 Project Structure

```
OmniSight-XR/

│
├── arduino/
│   ├── firmware/
│   ├── sensors/
│   └── README.md
│
├── backend/
│   ├── ai/
│   ├── websocket/
│   ├── api/
│   ├── models/
│   ├── utils/
│   ├── config.py
│   └── server.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── assets/
│   └── public/
│
├── docs/
│   ├── architecture.png
│   ├── workflow.png
│   ├── diagrams/
│   └── presentation/
│
├── assets/
│   ├── screenshots/
│   ├── videos/
│   └── logo/
│
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

---

# 💻 Technology Stack

## Hardware

* Arduino UNO Q
* Snapdragon X Elite
* OnePlus 15

---

## Backend

* Python
* asyncio
* WebSockets

---

## Frontend

* React
* Vite
* HTML
* CSS

---

## AI

* Qualcomm AI Hub
* Snapdragon NPU
* Pretrained Detection Model

---

## Communication

* JSON
* Local Wi-Fi
* WebSockets

---

# 🔄 Communication Flow

```
Arduino

↓

Gas + Temperature

↓

JSON Packet

↓

Laptop Backend

↓

AI Detection

↓

Merged Result

↓

WebSocket

↓

Phone Dashboard
```

---

# 🤖 AI Pipeline

```
Camera

↓

Frame Capture

↓

Qualcomm AI Hub Model

↓

Human Detection

↓

Confidence Score

↓

Merge Sensor Data

↓

Dashboard
```

---

# ⚙ Installation Guide

## Clone Repository

```bash
git clone https://github.com/your-org/OmniSight-XR.git

cd OmniSight-XR
```

---

## Backend

```bash
cd backend

pip install -r requirements.txt

python server.py
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Arduino

1. Open Arduino IDE

2. Upload firmware

3. Connect Sensors

4. Connect Local Wi-Fi

---

# ▶ Running the Project

### Step 1

Start Backend

↓

### Step 2

Power Arduino

↓

### Step 3

Open Mobile Dashboard

↓

### Step 4

Start Camera

↓

### Step 5

View Live Detection

---

# 👨‍💻 Team Responsibilities

| Member   | Responsibility            |
| -------- | ------------------------- |
| Member A | Embedded System & Sensors |
| Member B | AI & Computer Vision      |
| Member C | Backend & Integration     |
| Member D | Frontend & Dashboard      |

---

# 📅 Development Milestones

* [ ] Backend Complete
* [ ] Arduino Complete
* [ ] AI Model Running
* [ ] Dashboard Connected
* [ ] Full Integration
* [ ] Demo Ready
* [ ] README Complete

---

# 🚀 Future Scope

* Thermal Camera
* Autonomous Rover
* Drone Support
* 3D Mapping
* Multiple Sensor Nodes
* AR Navigation
* Offline Mesh Networking

---

# 📸 Screenshots

```
/assets/screenshots
```

* Dashboard
* Detection
* Sensor Data
* Hardware Setup

---

# 🎥 Demo Video

```
Coming Soon
```

---

# 📜 License

MIT License

---

# 🙌 Acknowledgements

* Qualcomm Technologies
* Snapdragon Multiverse Hackathon
* Qualcomm AI Hub
* Arduino
* React
* Python

---

# ❤️ Why OmniSight-XR?

OmniSight-XR is designed to assist first responders by combining embedded sensing, Snapdragon-powered edge AI, and offline multi-device communication into a portable rescue platform. Its modular architecture allows the sensing unit to be deployed on a rover, drone, or carried by responders, making it adaptable to a wide range of disaster scenarios while remaining fully operational without internet connectivity.
