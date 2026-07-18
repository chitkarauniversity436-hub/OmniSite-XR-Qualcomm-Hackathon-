# import all the lib
from arduino.app_utils import *  
import requests
import time
import math

# UTL to urn the website localy
FLASK_URL = "http://10.83.207.93:5000/detections"

session = requests.Session()

def loop():  #  MAGIC
    try:  # IF THERE IS NO ERROR THEN THIS WILL RUN 
        temperature = Bridge.call("get_temperature")
        humidity = Bridge.call("get_humidity")
        gas = Bridge.call("get_gas")
        distance = Bridge.call("get_distance")
        obstacle = Bridge.call("get_obstacle")

        if math.isnan(temperature) or math.isnan(humidity):  # IF TEMP AND HUMID IS NOT NUM THEN WE JUST EXIT FROM THERE
            print("Waiting for DHT22...")
            time.sleep(2)
            return

        #  PUT EVERY THING INT OBJ AND JUST PRINT THE VALUE
        payload = {  
            "temperature": temperature,
            "humidity": humidity,
            "gas": gas,
            "distance_cm": distance,
            "obstacle_detected": bool(obstacle),
            "person": False
        }

        print(payload)

        risk = "SAFE"

        try:
            response = session.post(
                FLASK_URL,
                json=payload,
                timeout=2   # shorter timeout so a slow POST can't eat into Bridge's window
            )
            response.raise_for_status()
            data = response.json()
            risk = data.get("stored", {}).get("risk", "SAFE")
            print("Risk:", risk)

        except requests.exceptions.RequestException as e:
            print("Flask server unreachable:", e)
            # skip buzzer call entirely this cycle — don't touch Bridge again
            time.sleep(2)
            return

        # Only call Bridge again if the HTTP round-trip succeeded quickly
        try:
            Bridge.call("trigger_buzzer", risk == "CRITICAL")
        except Exception as e:
            print("Buzzer Bridge Error:", e)
            
    except Exception as e:
        print("Bridge Error:", e)

    time.sleep(2)
    

App.run(user_loop=loop)
