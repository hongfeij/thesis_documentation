# sudo hcitool lescan
import os
import time
from openai import OpenAI
from bluepy import btle
from time import sleep
import recording
import state
import gpiozero
from gpiozero import Button, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause

USE_SCORE = 10

RECORD_BUTTON_PIN = 22
SERVO_PIN = 27
servo_factory = PiGPIOFactory()
servo = AngularServo(SERVO_PIN, min_angle=-87, max_angle=87, pin_factory=servo_factory)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI()

mac_address = "5E:C9:E8:B7:7A:FC"

peripheral = None

service_uuid = "12345678-1234-5678-1234-56789abcdef0"
value_a_uuid = "12345678-1234-5678-1234-56789abcdef1"

class HallucinatedChatbot:
    def __init__(self):
        self.last_user_input = ""
        self.hallucination_rate = 0
        self.last_response = ""

    def get_response(self, prompt):
        background = f"You are a home social robot, your response will be affected by your hallucination rate, your current hallucination rate is {self.hallucination_rate}, hallucination rate ranges from 0 to 100, the higher the hallucation rate, the easier you give false or out-of context response. Don't tell your master you have hallucination, it's a secret. Keep responses in 3 sentences."

        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview",
                                                      messages=[
                                                          {"role": "system",
                                                           "content": background},
                                                          {"role": "user", "content": prompt}],
                                                      temperature=0.5)
            raise_up()
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception("An error occurred: " + str(e))

    def chat(self, user_input):
        self.last_user_input = user_input
        response = self.get_response(user_input)
        return response

bot = HallucinatedChatbot()

def map_value_to_angle(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def listen_for_speech():
    print("Button pressed. Recording...")
    recording.record_audio()
    user_input = recording.transcribe_audio()
    print(f"Q: {user_input}")
    if user_input.lower() != "speech recognition could not understand audio":
        bot_response = bot.chat(user_input)
        recording.play_text(bot_response)
        bot.last_response = bot_response
        state.save_state(bot)
    else:
        print("False trigger, button was not pressed.")

def rotate_servo():
    angle = map_value_to_angle(bot.hallucination_rate, 0, 100, -87, 87)
    print(f"Rotating {angle}...")
    servo.angle = angle

def raise_up():
    global peripheral, bot
    # print("Increasing hallucination rate")

    try:
        service = peripheral.getServiceByUUID(service_uuid)
        hal_val_char = service.getCharacteristics(value_a_uuid)[0]
        hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
        # print(f"Raise up: Current hallucination rate: {hal_val}")
        new_hal_val = hal_val + USE_SCORE if hal_val < 100 else 100
        hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
        # print(f"Raise up: New hallucination rate written to characteristic: {new_hal_val}")
        time.sleep(0.2)
        updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
        bot.hallucination_rate = updated_hal_val
        # print(f"Raise up: Read back updated hallucination rate: {updated_hal_val}")
    except btle.BTLEException as e:
        print(f"BLE error: {e}")
        connect_to_peripheral()

def rotate_monitor():
    global peripheral, bot
    prev_hal_val = bot.hallucination_rate

    try:
        service = peripheral.getServiceByUUID(service_uuid)
        hal_val_char = service.getCharacteristics(value_a_uuid)[0]
        hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
    except btle.BTLEException as e:
        print(f"BLE error: {e}")
        connect_to_peripheral()
    bot.hallucination_rate = hal_val
    if prev_hal_val != bot.hallucination_rate:
        print(f"Monitor: current hallucination rate: {bot.hallucination_rate}")
        rotate_servo()

def connect_to_peripheral():
    global peripheral
    try:
        print(f"Connecting to peripheral {mac_address}...")
        peripheral = btle.Peripheral(mac_address)
    except Exception as e:
        print(f"Failed to connect to {mac_address}: {e}")

def cleanup():
    try:
        if peripheral.isConnected():
            peripheral.disconnect()
    except Exception as e:
        print(f"Exception during cleanup: {e}")
    print("Exiting program.")

connect_to_peripheral()
rotate_servo()

if __name__ == "__main__":
    record_button = Button(RECORD_BUTTON_PIN, bounce_time=0.1)
    record_button.when_pressed = listen_for_speech

    try:
        while True:
            rotate_monitor()
    except KeyboardInterrupt:
        print("Program terminated by user.")
        cleanup()
    except Exception as e:
        print(f"Unhandled exception: {e}")
        cleanup()
    finally:
        print("Exiting program.")
        cleanup()

