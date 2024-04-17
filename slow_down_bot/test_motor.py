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

factory = PiGPIOFactory(host="172.26.60.140")
servo = AngularServo(27, min_angle=-90, max_angle=90, pin_factory=factory)

try:
    while True:
        print("aaaaaa")
        servo.angle = -90
        sleep(1)
        servo.angle = 90
        sleep(1)
except KeyboardInterrupt:
    print("Program exited by user")
