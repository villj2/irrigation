#!/usr/bin/env python3
import spidev
import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import logging
from logging.handlers import RotatingFileHandler

# === Configuration ===
SPI_BUS        = 0
SPI_DEVICE     = 0
SPI_MAX_SPEED  = 1_350_000
VREF           = 3.3
SENSOR_CHANNEL = 0

RAW_DRY        = 920
RAW_WET        = 90

PIN            = 26

SENSOR_INTERVAL   = 15 * 60
WATERING_INTERVAL = 3 * 3600
MOISTURE_THRESHOLD = 0.45

# === GPIO ===
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

# === Logger ===
handler = RotatingFileHandler(
    "/home/vill/Desktop/watering_system_prod.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# === Topics ===
TOPIC_MOISTURE    = "watering/soil/moisture"
TOPIC_PUMP        = "watering/soil/pump"
TOPIC_PUMP_MANUAL = "watering/soil/pumpmanual"

# === MQTT ===
BROKER = "homeassistant.local"
PORT = 1883
USERNAME = "<username>"
PASSWORD = "<password>"

connected = False

def on_connect(client, userdata, flags, rc):
    global connected
    connected = True
    client.subscribe(TOPIC_PUMP_MANUAL)

def on_message(client, userdata, msg):
    if msg.topic == TOPIC_PUMP_MANUAL:
        payload = msg.payload.decode("utf-8", errors="replace")
        print(f"Manual pump command received: {payload}")
        logger.info(f"Manual pump command received: {payload}")

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

def wait_for_mqtt(timeout=5):
    start = time.time()
    while not connected and time.time() - start < timeout:
        time.sleep(0.1)

# === SPI ===
def init_spi():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_MAX_SPEED
    return spi

def read_adc(spi, channel):
    cmd = [1, (8 + channel) << 4, 0]
    resp = spi.xfer2(cmd)
    return ((resp[1] & 0x03) << 8) | resp[2]

def raw_to_voltage(raw):
    return (raw / 1023.0) * VREF

# === Sensor ===
def read_moisture(spi):
    raw = read_adc(spi, SENSOR_CHANNEL)
    wetness = (RAW_DRY - raw) / (RAW_DRY - RAW_WET)
    wetness = max(0.0, min(1.0, wetness))
    wetness_percent = round(wetness * 100, 1)
    return wetness, wetness_percent

# === Pump ===
def start_pump():
    print("Pump ON")
    logger.info("Pump ON")
    client.publish(TOPIC_PUMP, "1")
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(PIN, GPIO.LOW)

def pump_cycle():
    start_pump()
    time.sleep(310)
    start_pump()
    time.sleep(310)
    start_pump()

# === MQTT publish ===
def send_moisture(value):
    client.publish(TOPIC_MOISTURE, value, retain=True)

# === Main ===
def main():
    spi = init_spi()

    last_sensor_time = 0
    last_watering_time = 0
    last_wetness = 0.0

    print("System started - sensor every 5 min, pump every 3h")

    # =========================
    # MQTT READY CHECK
    # =========================
    wait_for_mqtt()

    # =========================
    # INITIAL MEASUREMENT
    # =========================
    last_wetness, wetness_percent = read_moisture(spi)
    last_sensor_time = time.time()

    print(f"[START] Moisture: {wetness_percent:.1f}%")
    logger.info(f"[START] Moisture: {wetness_percent}%")
    send_moisture(wetness_percent)

    try:
        while True:
            now_ts = time.time()

            # =========================
            # SENSOR (5 min)
            # =========================
            if now_ts - last_sensor_time >= SENSOR_INTERVAL:
                last_wetness, wetness_percent = read_moisture(spi)
                last_sensor_time = now_ts

                print(f"Moisture: {wetness_percent:.1f}%")
                logger.info(f"Moisture: {wetness_percent}%")
                send_moisture(wetness_percent)

            # =========================
            # PUMP (3h)
            # =========================
            if last_wetness < MOISTURE_THRESHOLD:
                if (now_ts - last_watering_time) >= WATERING_INTERVAL:
                    pump_cycle()
                    last_watering_time = now_ts
                    logger.info("Pumping done")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        spi.close()
        GPIO.cleanup()

if __name__ == "__main__":
    main()