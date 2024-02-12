import RPi.GPIO as GPIO
import time

# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up the GPIO pin (e.g., 18) you're using for the LED
led_pin = 18
GPIO.setup(led_pin, GPIO.OUT)

print("LED blinking... Press CTRL+C to stop")

try:
    while True:
        # Turn the LED on
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(1)  # Sleep for 1 second

        # Turn the LED off
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(1)  # Sleep for 1 second

except KeyboardInterrupt:
    print("LED blinking stopped")

finally:
    GPIO.cleanup()  # Clean up GPIO state
