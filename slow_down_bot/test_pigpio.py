import pigpio
import time

LED_PIN = 27  # Adjust pin number to your setup

pi = pigpio.pi()
if not pi.connected:
    print("Not connected to pigpio daemon")
    exit()

# Blink an LED
try:
    while True:
        pi.write(LED_PIN, 1)  # LED on
        time.sleep(1)
        pi.write(LED_PIN, 0)  # LED off
        time.sleep(1)
except KeyboardInterrupt:
    pi.write(LED_PIN, 0)  # Ensure LED is turned off
    pi.stop()
