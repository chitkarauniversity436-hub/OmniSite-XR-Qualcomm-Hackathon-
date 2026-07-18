"""
Fakes what the Arduino would normally send, so the dashboard has live sensor
data even without the physical board connected.

Posts to the SAME /detections endpoint the real arduino_original/python/main.py
uses — swap this script out for the real one later, nothing else changes.

pip install requests
"""

import time
import random
import requests

BACKEND_URL = "http://127.0.0.1:5000/detections"
SEND_INTERVAL_SEC = 2.0

# occasionally spike gas/obstacle so you can see WARNING/CRITICAL states
SPIKE_CHANCE = 0.4

# starting point + running state — each new reading drifts from this instead
# of picking a fresh random number every time, so it looks like a real sensor
last_reading = {
    "temperature": 28.0,
    "humidity": 50.0,
    "gas": 250,
    "distance_cm": 100.0,
}


def generate_reading():
    spike = random.random() < SPIKE_CHANCE

    # small step in a random direction each call — real sensors don't jump
    last_reading["temperature"] += random.uniform(-0.3, 0.3)
    last_reading["temperature"] = max(20, min(35, last_reading["temperature"]))

    last_reading["humidity"] += random.uniform(-1, 1)
    last_reading["humidity"] = max(30, min(70, last_reading["humidity"]))

    if spike:
        last_reading["gas"] += random.randint(40, 90)
        last_reading["gas"] = min(900, last_reading["gas"])
        last_reading["distance_cm"] = max(3, last_reading["distance_cm"] - random.uniform(10, 25))
    else:
        last_reading["gas"] += random.randint(-20, 15)
        last_reading["gas"] = max(120, min(420, last_reading["gas"]))
        last_reading["distance_cm"] += random.uniform(-5, 5)
        last_reading["distance_cm"] = max(20, min(200, last_reading["distance_cm"]))

    return {
        "temperature": round(last_reading["temperature"], 1),
        "humidity": round(last_reading["humidity"], 1),
        "gas": int(last_reading["gas"]),
        "distance_cm": round(last_reading["distance_cm"], 1),
        "obstacle_detected": spike,
    }


def main():
    session = requests.Session()
    print(f"Simulating sensor data -> {BACKEND_URL} every {SEND_INTERVAL_SEC}s. Ctrl+C to stop.")

    while True:
        payload = generate_reading()
        try:
            r = session.post(BACKEND_URL, json=payload, timeout=3)
            print(payload, "->", r.status_code, r.json())
        except requests.exceptions.RequestException as e:
            print("Backend unreachable:", e)
        time.sleep(SEND_INTERVAL_SEC)


if __name__ == "__main__":
    main()