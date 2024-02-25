# sudo hcitool lescan
import os
import time
from openai import OpenAI
import threading
import RPi.GPIO as GPIO
from bluepy import btle
from time import sleep
import recording
import state

USE_SCORE = 10

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
# CALM_BUTTON_PIN = 17
RECORD_BUTTON_PIN = 27
SERVO_PIN = 22
# GPIO.setup(CALM_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RECORD_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO_PIN, GPIO.OUT)

frequency = 50
pwm = GPIO.PWM(SERVO_PIN, frequency)
pwm.start(0)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI()

MAC_ADDRESS_SQUEEZE = "59:5D:76:F0:9F:30"
# MAC_ADDRESS_2 = "0F:BD:FB:16:FC:21"
# MAC_ADDRESS_3 = "0F:BD:FB:16:FC:21"
MAC_ADDRESS_VOICE = "A4:4B:6C:1E:91:A8"
mac_addresses = [MAC_ADDRESS_SQUEEZE, MAC_ADDRESS_VOICE]
peripherals = []

service_uuid = "12345678-1234-5678-1234-56789abcdef0"
value_a_uuid = "12345678-1234-5678-1234-56789abcdef1"

class HallucinatedChatbot:
    def __init__(self):
        self.last_user_input = ""
        self.hallucination_rate = 0

    def get_response(self, prompt):
        background = f"You are Alexz, a home social robot, your response will be affected by your hallucination rate, your current hallucination rate is {self.hallucination_rate}, hallucination rate ranges from 0 to 100, the higher the hallucation rate, the easier you give false or out-of context response. Don't tell your master you have hallucination, it's a secret :). Keep responses in 3 sentences."

        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview",
                                                      messages=[
                                                          {"role": "system",
                                                           "content": background},
                                                          {"role": "user", "content": prompt}],
                                                      temperature=0.5)
            raise_up()
            # print(f"Current hallucination rate is: {self.hallucination_rate}")
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

def listen_for_speech(channel):
    global bot
    time.sleep(0.05)
    if GPIO.input(RECORD_BUTTON_PIN) == GPIO.LOW:
        print("Button pressed. Recording...")
        recording.record_audio()
        user_input = recording.transcribe_audio()
        print(f"You said: {user_input}")
        if user_input.lower() != "speech recognition could not understand audio":
            bot_response = bot.chat(user_input)
            print(f"Bot: {bot_response}")
            recording.play_text(bot_response)
            state.save_state(bot)
    else:
        print("False trigger, button was not pressed.")
            
def rotate_servo():
    global bot
    angle = map_value_to_angle(bot.hallucination_rate, 0, 100, 0, 180)
    duty_cycle = angle / 18 + 2
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.2)

def calm_down():
    global peripherals, bot
    print("Decreasing hallucination rate")
    
    for peripheral in peripherals:
        try:
            service = peripheral.getServiceByUUID(service_uuid)
            hal_val_char = service.getCharacteristics(value_a_uuid)[0]
            hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            print(f"Current hallucination rate: {hal_val}")
            new_hal_val = hal_val - USE_SCORE if hal_val > 0 else 0
            hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
            print(f"New hallucination rate written to characteristic: {new_hal_val}")
            time.sleep(0.2)
            updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            bot.hallucination_rate = updated_hal_val
            print(f"Read back updated hallucination rate: {updated_hal_val}")
        except btle.BTLEException as e:
            print(f"BLE error: {e}")
            connect_to_peripheral()

def raise_up():
    global peripherals, bot
    print("Increasing hallucination rate")

    for peripheral in peripherals:
        print(peripheral)
        try:
            service = peripheral.getServiceByUUID(service_uuid)
            hal_val_char = service.getCharacteristics(value_a_uuid)[0]
            hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            print(f"Raise up: Current hallucination rate: {hal_val}")
            new_hal_val = hal_val + USE_SCORE if hal_val < 100 else 100
            hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
            print(f"Raise up: New hallucination rate written to characteristic: {new_hal_val}")
            time.sleep(0.2)
            updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            bot.hallucination_rate = updated_hal_val
            print(f"Raise up: Read back updated hallucination rate: {updated_hal_val}")
        except btle.BTLEException as e:
            print(f"BLE error: {e}")
            connect_to_peripheral()

def rotate_monitor():
    global peripherals, bot

    for peripheral in peripherals:
        # print(peripheral)
        try:
            service = peripheral.getServiceByUUID(service_uuid)
            hal_val_char = service.getCharacteristics(value_a_uuid)[0]
            hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            # print(f"read hallucination rate: {hal_val}")
            hal_val_char.write(hal_val.to_bytes(4, byteorder='little'), withResponse=True)
            time.sleep(0.2)
            updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            bot.hallucination_rate = updated_hal_val
            rotate_servo()
        except btle.BTLEException as e:
            # print(f"BLE error: {e}")
            connect_to_peripheral()

def connect_to_peripheral():
    global peripherals
    peripherals = []
    for mac_address in mac_addresses:
        try:
            print(f"Connecting to peripheral {mac_address}...")
            peripheral = btle.Peripheral(mac_address)
            peripherals.append(peripheral)
        except Exception as e:
            print(f"Failed to connect to {mac_address}: {e}")

connect_to_peripheral()
rotate_servo()
print("Connected to peripherals...")

if __name__ == "__main__":
    GPIO.add_event_detect(RECORD_BUTTON_PIN, GPIO.FALLING, callback=listen_for_speech, bouncetime=200)

    try:
        while True:
            rotate_monitor()
    except KeyboardInterrupt:
        print("Program terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        pwm.stop()  # Stop PWM
        GPIO.cleanup()  # Clean up GPIO on exit
        if peripherals:
            for peripheral in peripherals:
                service = peripheral.getServiceByUUID(service_uuid)
                hal_val_char = service.getCharacteristics(value_a_uuid)[0]
                new_hal_val = 0
                hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
                peripheral.disconnect()
        print("Exiting program.")
