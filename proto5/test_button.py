import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17  # Replace with your GPIO pin number

def button_callback(channel):
    print("Button was pushed!")

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")

