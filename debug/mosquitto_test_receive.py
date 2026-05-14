import paho.mqtt.client as mqtt

BROKER = "homeassistant.local"
PORT = 1883
USERNAME = "<username>"
PASSWORD = "<password>"
TOPIC = "test/villberry"

# Callback: wenn verbunden
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

# Callback: wenn Nachricht empfangen wird
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Empfangen auf {msg.topic}: {payload}")

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

client.loop_forever()
