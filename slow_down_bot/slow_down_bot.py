import sys
import os
import openai
import json
import time
from openai import OpenAI
import threading
import pyaudio
import wave
from pathlib import Path
# import random
import RPi.GPIO as GPIO
import pygame
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# i2c = busio.I2C(board.SCL, board.SDA)
# ads = ADS.ADS1015(i2c)
# chan = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)
# GPIO.setup(4, GPIO.IN)  # Pressure sensor input
BUTTON_PIN = 17        # Button input
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_PIN = 17
USE_SCORE = 0.1

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

    # def monitor_pressure(self):
    #     while True:
    #         pass

    # def check_pressure(self):
    #     """Check and respond to pressure changes."""
    #     pressure_input = GPIO.input(4)
    #     if pressure_input:
    #         self.force = chan.value
    #         self.get_next_state()

    # def get_next_state(self):
    #     pass

    def get_response(self, prompt):
        background = "You are Alexz, a home social robot, your response will be affected by your hallucination rate, your current hallucination rate is {self.hallucination_rate}"

        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview",
                                                      messages=[
                                                          {"role": "system",
                                                           "content": background},
                                                          {"role": "user", "content": prompt}],
                                                      max_tokens=50,
                                                      temperature=0.5)
            self.hallucination_rate += USE_SCORE
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
        # print("saving...")
        # print(new_entry)

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
        return transcript

    def play_text(self, text):
        """
        Play the given text using text-to-speech.
        """
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

    def on_button_press(self, channel):
        time.sleep(0.05)  # Wait 50 ms
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            self.hallucination_rate = max(0, self.hallucination_rate - USE_SCORE)
            print(f"Hallucination rate decreased to {self.hallucination_rate}.")
        else:
            print("False trigger, button was not pressed.")

    def listen_for_speech(self):
        while True:
            print("Listening for speech...")
            self.record_audio()
            user_input = self.transcribe_audio()
            print(f"You said: {user_input}")
            if user_input.lower() != "speech recognition could not understand audio":
                bot_response = self.chat(user_input)
                print(f"Bot: {bot_response}")
                self.play_text(bot_response)
                self.save_state()
            else:
                print("Could not transcribe audio or no speech detected.")
            time.sleep(1)


if __name__ == "__main__":
    bot = HallucinatedChatbot()

    listening_thread = threading.Thread(target=bot.listen_for_speech)
    listening_thread.start()

    # pressure_thread = threading.Thread(target=bot.monitor_pressure)
    # pressure_thread.daemon = True
    # pressure_thread.start()

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                          callback=bot.on_button_press, bouncetime=200)

    try:
        while True:
            print("Waiting for button press...")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Program terminated by user.")
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        listening_thread.join()
        # pressure_thread.join()  # Wait for the pressure monitoring thread to finish
        GPIO.cleanup()  # Clean up GPIO on exit
        print("Exiting program.")
