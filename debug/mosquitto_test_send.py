import paho.mqtt.client as mqtt
import time
import random
import json
from datetime import datetime

BROKER = "homeassistant.local"
PORT = 1883
USERNAME = "<username>"
PASSWORD = "<password>"
TOPIC = "test/watering/soil/moisture"

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    payload = {
        "moisture": random.randint(0, 100),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"Sent: {payload}")
    time.sleep(5)
