import RPi.GPIO as GPIO
from time import sleep
import threading

# Disable warnings (use with caution)
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

# Setup for servo 1 on GPIO pin 11
GPIO.setup(11, GPIO.OUT)
pwm1 = GPIO.PWM(11, 50)
pwm1.start(0)

# Setup for servo 2 on GPIO pin 13
GPIO.setup(13, GPIO.OUT)
pwm2 = GPIO.PWM(13, 50)
pwm2.start(0)

def setAngle(pwm, angle):
    duty = angle / 18 + 2
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    pwm.ChangeDutyCycle(0)

def control_servo(pwm, angles):
    for angle in angles:
        setAngle(pwm, angle)
        sleep(1)  # Wait for the servo to move to the position before proceeding

angles_servo1 = [0, 90, 135]
angles_servo2 = [0, 90, 135]

thread1 = threading.Thread(target=control_servo, args=(pwm1, angles_servo1))
thread2 = threading.Thread(target=control_servo, args=(pwm2, angles_servo2))

thread1.start()
thread2.start()

thread1.join()
thread2.join()

pwm1.stop()
pwm2.stop()
GPIO.cleanup()
