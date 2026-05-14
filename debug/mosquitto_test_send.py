import paho.mqtt.client as mqtt
import time
import random

BROKER = "homeassistant.local"
PORT = 1883
USERNAME = "<username>"
PASSWORD = "<password>"
TOPIC = "watering/soil/moisturetest"

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.connect(BROKER, PORT, 60)

client.loop_start()

while True:
    value = random.randint(0, 100)
    payload = value
    
    client.publish(TOPIC, payload)
    print(f"Gesendet: {payload}")
    
    time.sleep(5)
