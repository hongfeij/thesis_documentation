import RPi.GPIO as GPIO
import time
from time import sleep

# Setup
SERVO_PIN = 27  # Change this to the GPIO pin you are using
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
GPIO.setup(SERVO_PIN, GPIO.OUT)

# PWM parameters
frequency = 50  # Servo typically expects a frequency of 50Hz
pwm = GPIO.PWM(SERVO_PIN, frequency)

# Start PWM
pwm.start(0)

def set_servo_angle(angle):
    print("setting...")
    duty_cycle = angle / 18 + 2  # Convert angle to duty cycle
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)

def map_value_to_angle(value, in_min, in_max, out_min, out_max):
    # Map a value from one range to another
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Example usage
try:
    while True:
        angle = map_value_to_angle(0, 0, 100, 0, 180)
        set_servo_angle(angle)
        sleep(4)
        angle = map_value_to_angle(100, 0, 100, 0, 180)
        set_servo_angle(angle)
except KeyboardInterrupt:
    print("Program terminated by user.")
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
finally:
    pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO
