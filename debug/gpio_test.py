import RPi.GPIO as GPIO
import time

PIN = 26  # Broadcom-Nummer des Pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.OUT)

#try:
#    while True:
#        GPIO.output(PIN, GPIO.HIGH)  # START: HIGH
#        print("HIGH – messen!")
#        time.sleep(4)
#
#        GPIO.output(PIN, GPIO.LOW)   # dann LOW
#        print("LOW – messen!")
#        time.sleep(2)
#except KeyboardInterrupt:
#    pass
#finally:
#    GPIO.cleanup()


try:
	time.sleep(1)
	
	GPIO.output(PIN, GPIO.HIGH)  # START: HIGH
	print("ON")
	time.sleep(1)

	GPIO.output(PIN, GPIO.LOW)   # dann LOW
	print("OFF")
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
