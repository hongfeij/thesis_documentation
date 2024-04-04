import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

p = GPIO.PWM(17, 50)  # channel=17, frequency=50Hz
p.start(7.5)  # Neutral position

try:
    while True:
        p.ChangeDutyCycle(5)  # 0 degrees
        time.sleep(1)
        p.ChangeDutyCycle(7.5)  # 90 degrees (neutral position)
        time.sleep(1)
        p.ChangeDutyCycle(10)  # 180 degrees
        time.sleep(1)
finally:
    p.stop()
    GPIO.cleanup()
