"""
Runs at the BASE STATION (wherever the backend/dashboard lives).

Listens on the LoRa receiver module's serial port, parses incoming packets
from the rover, and forwards each one to the Flask backend as a normal
HTTP POST — so the rest of the stack (backend/app.py, frontend) doesn't
need to know or care that the data arrived over LoRa.

pip install pyserial requests
"""
# IMPORT ALL THE NESS LIB
import re
import json
import time
import serial
import requests

LORA_PORT = "/dev/ttyUSB_LORA_RX"
LORA_BAUD = 115200

BACKEND_URL = "http://127.0.0.1:5000/point"

# REYAX RYLR896-style receive format: +RCV=<addr>,<len>,<data>,<rssi>,<snr>
RCV_PATTERN = re.compile(r"\+RCV=(\d+),(\d+),(.*),(-?\d+),(\d+)")


def main():
    ser = serial.Serial(LORA_PORT, LORA_BAUD, timeout=1)
    session = requests.Session()

    print(f"Listening for LoRa packets on {LORA_PORT}...")

    while True:
        try:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if not line:
                continue

            match = RCV_PATTERN.match(line)
            if not match:
                continue  # not a data packet (could be an AT ack/log line)

            _addr, _length, data_str, rssi, snr = match.groups()

            try:
                point = json.loads(data_str)
            except json.JSONDecodeError:
                print("Malformed packet, skipping:", data_str)
                continue

            print(f"Received point {point.get('label')} (rssi={rssi}, snr={snr})")

            try:
                session.post(BACKEND_URL, json=point, timeout=3)
            except requests.exceptions.RequestException as e:
                print("Backend unreachable, will not retry this packet:", e)

        except Exception as e:
            print("Bridge error:", e)
            time.sleep(1)


if __name__ == "__main__":
    main()
