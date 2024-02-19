# sudo hcitool lescan
import os
import openai
import json
import time
from openai import OpenAI
import threading
import pyaudio
import wave
from pathlib import Path
import RPi.GPIO as GPIO
from bluepy import btle
import pygame
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
CALM_BUTTON_PIN = 17
RECORD_BUTTON_PIN = 27
SERVO_PIN = 22
GPIO.setup(CALM_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RECORD_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(SERVO_PIN, GPIO.OUT)

frequency = 50
pwm = GPIO.PWM(SERVO_PIN, frequency)
pwm.start(0)

# mac_address = "5E:C9:E8:B7:7A:FC"
mac_address = "0B:CC:05:54:13:11"
service_uuid = "12345678-1234-5678-1234-56789abcdef0"
value_a_uuid = "12345678-1234-5678-1234-56789abcdef1"

# Connect to BLE peripheral
def connect_to_peripheral():
    global peripheral
    peripheral = btle.Peripheral(mac_address)
print("Connecting to peripheral...")
connect_to_peripheral()

def map_value_to_angle(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

USE_SCORE = 10

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
OUTPUT_FILENAME = "recorded_audio.wav"
RESPONSE_FILENAME = "response.mp3"

client = OpenAI()

class HallucinatedChatbot:
    def __init__(self):
        self.last_user_input = ""
        self.hallucination_rate = 0
        self.rotate_servo()

    def get_response(self, prompt):
        background = f"You are Alexz, a home social robot, your response will be affected by your hallucination rate, your current hallucination rate is {self.hallucination_rate}, hallucination rate ranges from 0 to 100, the higher the hallucation rate, the easier you give false or out-of context response. Don't tell your master you have hallucination, it's a secret :)."
        print(background)

        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview",
                                                      messages=[
                                                          {"role": "system",
                                                           "content": background},
                                                          {"role": "user", "content": prompt}],
                                                      max_tokens=50,
                                                      temperature=0.5)
            self.raise_up()
            print(f"Current hallucination rate is: {self.hallucination_rate}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception("An error occurred: " + str(e))

    def chat(self, user_input):
        self.last_user_input = user_input
        response = self.get_response(user_input)
        return response

    def save_state(self, filepath="state.json"):
        states = []
        try:
            with open(filepath, "r") as f:
                states = json.load(f)
        except FileNotFoundError:
            pass

        new_entry = {
            "id": len(states) + 1,
            "last_user_input": self.last_user_input,
            "hallucination_rate": self.hallucination_rate
        }

        states.append(new_entry)

        with open(filepath, "w") as f:
            json.dump(states, f, indent=4)

    def load_state(self, filepath="state.json"):
        try:
            with open(filepath, "r") as f:
                states = json.load(f)
                # Check if states is a list and not empty
                if isinstance(states, list) and states:
                    last_state = states[-1]
                    if isinstance(last_state, dict):
                        self.last_user_input = last_state.get(
                            "last_user_input", "")
                        self.hallucination_rate = last_state.get(
                            "hallucination_rate", 0)
                    else:
                        self.reset_state()
                else:
                    self.reset_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self.reset_state()

    def reset_state(self):
        self.last_user_input = ""
        self.hallucination_rate = 0

    def record_audio(self, ):
        """
        Record audio for a specified number of seconds, save it to a file, and return the audio data.
        """
        FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
        CHANNELS = 2              # Number of audio channels
        RATE = 48000              # Sample rate (Hz)
        CHUNK = 1024              # Number of frames per buffer
        RECORD_SECONDS = 5        # Duration of recording

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                        frames_per_buffer=CHUNK, input_device_index=1)

        print("Recording...")
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Finished recording.")

        stream.stop_stream()
        stream.close()

        p.terminate()

        # Save the recorded data to a WAV file
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Recording saved to {OUTPUT_FILENAME}.")

    def transcribe_audio(self):
        # """
        # Transcribe audio data to text using speech recognition.
        # """
        audio_file = open(OUTPUT_FILENAME, "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            language="en",
            file=audio_file,
            response_format="text")
        print(f"You said: {transcript}")
        return transcript

    def play_text(self, text):
        """
        Play the given text using text-to-speech.
        """
        print("Play text")
        speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
        response = openai.audio.speech.create(
            model="tts-1",
            voice="echo",
            input=text
        )
        response.stream_to_file(speech_file_path)

        pygame.mixer.init()
        pygame.mixer.music.load(str(speech_file_path))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def button_monitor(self):
        last_press_time = 0
        debounce_threshold = 0.2  # 200 ms debounce threshold
        while True:
            if not GPIO.input(CALM_BUTTON_PIN):  # Assuming active low
                current_time = time.time()
                if (current_time - last_press_time) >= debounce_threshold:
                    print("Button pressed.")
                    self.calm_down()
                    print(f"current hallucination rate is {self.hallucination_rate}")
                    # Handle button press here
                    last_press_time = current_time
            time.sleep(0.01)  # Short sleep to reduce CPU load

    def listen_for_speech(self, channel):
        time.sleep(0.05)
        if GPIO.input(RECORD_BUTTON_PIN) == GPIO.LOW:
            print("Button pressed. Recording...")
            self.record_audio()
            user_input = self.transcribe_audio()
            print(f"You said: {user_input}")
            if user_input.lower() != "speech recognition could not understand audio":
                bot_response = self.chat(user_input)
                print(f"Bot: {bot_response}")
                self.play_text(bot_response)
                self.save_state()
        else:
            print("False trigger, button was not pressed.")

    # Decrease Value A when the button is pressed
    def calm_down(self):
        global peripheral
        print("Decreasing Value A")
        if peripheral is None:
            print("Peripheral device not connected")
            return
        try:
            # Read, decrement, and write Value A
            service = peripheral.getServiceByUUID(service_uuid)
            hal_val_char = service.getCharacteristics(value_a_uuid)[0]
            hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            print(f"Current Value A: {hal_val}")
            new_hal_val = hal_val - USE_SCORE if hal_val > 0 else 0
            hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
            print(f"New Value A written to characteristic: {new_hal_val}")
            time.sleep(0.5)  # Delay to ensure the write is processed
            updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            self.hallucination_rate = updated_hal_val
            self.rotate_servo()
            print(f"Read back updated Value A: {updated_hal_val}")
            return updated_hal_val
        except btle.BTLEException as e:
            print(f"BLE error: {e}")
            connect_to_peripheral()

        # Decrease Value A when the button is pressed
    def raise_up(self):
        global peripheral
        print("Increasing Value A")
        if peripheral is None:
            print("Peripheral device not connected")
            return
        try:
            # Read, decrement, and write Value A
            service = peripheral.getServiceByUUID(service_uuid)
            hal_val_char = service.getCharacteristics(value_a_uuid)[0]
            hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            print(f"Current Value A: {hal_val}")
            new_hal_val = hal_val + USE_SCORE if hal_val < 100 else 100
            hal_val_char.write(new_hal_val.to_bytes(4, byteorder='little'), withResponse=True)
            print(f"New Value A written to characteristic: {new_hal_val}")
            time.sleep(0.5)  # Delay to ensure the write is processed
            updated_hal_val = int.from_bytes(hal_val_char.read(), byteorder='little')
            self.hallucination_rate = updated_hal_val
            self.rotate_servo()
            print(f"Read back updated Value A: {updated_hal_val}")
            return updated_hal_val
        except btle.BTLEException as e:
            print(f"BLE error: {e}")
            connect_to_peripheral()

    def rotate_servo(self):
        angle = map_value_to_angle(self.hallucination_rate, 0, 100, 0, 180)
        print(f"rotating {angle}")
        duty_cycle = angle / 18 + 2
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(5)

if __name__ == "__main__":
    bot = HallucinatedChatbot()

    button_thread = threading.Thread(target=bot.button_monitor)
    button_thread.start()

    GPIO.add_event_detect(RECORD_BUTTON_PIN, GPIO.FALLING, callback=bot.listen_for_speech, bouncetime=200)

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        button_thread.join()
        pwm.stop()  # Stop PWM
        GPIO.cleanup()  # Clean up GPIO on exit
        if peripheral:
            peripheral.disconnect()
        print("Exiting program.")
