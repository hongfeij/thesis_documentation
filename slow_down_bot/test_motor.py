# import RPi.GPIO as GPIO
# import time

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(27, GPIO.OUT)

# p = GPIO.PWM(27, 50)  # channel=17, frequency=50Hz
# p.start(7.5)  # Neutral position

# try:
#     while True:
#         p.ChangeDutyCycle(5)  # 0 degrees
#         time.sleep(1)
#         p.ChangeDutyCycle(7.5)  # 90 degrees (neutral position)
#         time.sleep(1)
#         p.ChangeDutyCycle(10)  # 180 degrees
#         time.sleep(1)
# finally:
#     p.stop()
#     GPIO.cleanup()


from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

factory = PiGPIOFactory()
servo = AngularServo(27, min_angle=0, max_angle=180, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)

try:
    while True:
        servo.angle = 0
        sleep(1)
        servo.angle = 180
        sleep(1)
except KeyboardInterrupt:
    print("Program exited by user")
