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
import board
import neopixel

pixel_pin = board.D10
num_pixels = 1

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2,  auto_write=False
)


USE_SCORE = 25

RECORD_BUTTON_PIN = 22
SERVO_PIN = 27
servo_factory = PiGPIOFactory()
servo = AngularServo(SERVO_PIN, min_angle=-87, max_angle=87)
# , pin_factory=servo_factory

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI()

MAC_ADDRESS_SQUEEZE = "0F:BD:FB:16:FC:21"
MAC_ADDRESS_SMASH  = "6C:85:F7:B1:65:2E"
MAC_ADDRESS_WHISPER = "A4:4B:6C:1E:91:A8"
MAC_ADDRESS_TICKLE = "62:2F:58:C9:02:47"
mac_addresses = [MAC_ADDRESS_TICKLE, MAC_ADDRESS_WHISPER, MAC_ADDRESS_SMASH, MAC_ADDRESS_SQUEEZE]
# mac_addresses = [MAC_ADDRESS_WHISPER]
peripherals = []

service_uuid = "12345678-1234-5678-1234-56789abcdef0"
value_a_uuid = "12345678-1234-5678-1234-56789abcdef1"
string_uuid = "12345678-1234-5678-1234-56789abcdef2"

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
        state.save_state(bot, False, None)
    else:
        print("False trigger, button was not pressed.")

def rotate_servo():
    angle = map_value_to_angle(bot.hallucination_rate, 0, 100, -87, 87)
    print(f"Rotating {angle}...")
    servo.angle = angle

def raise_up():
    global peripherals, bot
    # print("Increasing hallucination rate")

    for peripheral in peripherals:
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
            # connect_to_peripheral()

def rotate_monitor():
    global peripherals, bot
    prev_hal_val = bot.hallucination_rate
    min_hal = 200

    # pixels.fill((0, 0, 0))
    # pixels.show()

    for peripheral in peripherals:
        try:
            service = peripheral.getServiceByUUID(service_uuid)
            characteristics = service.getCharacteristics()

            for char in characteristics:
                if char.uuid == value_a_uuid:
                    hal_val = int.from_bytes(char.read(), byteorder='little')
                    min_hal = min(min_hal, hal_val)
                    bot.hallucination_rate = min_hal
                    if prev_hal_val != bot.hallucination_rate:
                        print(f"Monitor: current hallucination rate: {bot.hallucination_rate}")
                        rotate_servo()
                elif char.uuid == string_uuid:
                    data = char.read().decode('utf-8')
                    if data != "monitor":
                        state.save_state(bot, True, data)
        except btle.BTLEException as e:
            print(f"BLE error: {e}")
            # connect_to_peripheral()

def connect_to_peripheral():
    global peripherals
    for mac_address in mac_addresses:
        try:
            print(f"Connecting to peripheral {mac_address}...")
            peripheral = btle.Peripheral(mac_address)
            peripherals.append(peripheral)
        except Exception as e:
            print(f"Failed to connect to {mac_address}: {e}")

def cleanup():
    for peripheral in peripherals:
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

