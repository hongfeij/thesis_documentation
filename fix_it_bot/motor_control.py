from gpiozero import AngularServo
from time import sleep

class EmotionMotor:
    def __init__(self, pin, min_angle=-165, max_angle=165):
        # Initialize servo motor on specified GPIO pin
        self.servo = AngularServo(pin, min_angle=min_angle, max_angle=max_angle)

    def set_emotion(self, score):
        # Map the emotion score (-1 to 1) to the servo's angle range
        angle = self.score_to_angle(score)
        self.servo.angle = angle
        print(f"Motor set to {angle} degrees for score {score}")

    def score_to_angle(self, score):
        # Convert the emotion score to an angle
        return score * 165

    def adjust_emotion_by_angle(self, angle):
        # Convert the manual angle adjustment back to an emotion score
        score = angle / 165
        return score
