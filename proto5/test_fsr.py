import RPi.GPIO as GPIO
import time

# Set the GPIO to BCM Mode
GPIO.setmode(GPIO.BCM)

# Set Pin 4 for the pressure sensor and Pin 17 for the LED
GPIO.setup(4, GPIO.IN)
GPIO.setup(17, GPIO.OUT)  # LED

# Variable to keep track of the sensor state
prev_input = 0

# Create a loop that goes on as long as the script is running
while True:
    # Read from the pressure pad
    input = GPIO.input(4)

    # Check if the pressure pad is being pressed
    if ((not prev_input) and input):
        print("Under Pressure")
        GPIO.output(17, GPIO.HIGH)  # Turn on the LED
    elif prev_input and not input:
        GPIO.output(17, GPIO.LOW)  # Turn off the LED

    # Update previous input
    prev_input = input

    # Slight pause to debounce
    time.sleep(0.10)
