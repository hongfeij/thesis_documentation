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
import random
import RPi.GPIO as GPIO
import pygame
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)

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
        self.force = 0
        self.hallucinated_state = ""

    def monitor_pressure(self):
        prev_input = 0
        while True:
            pressure_input = GPIO.input(4)
            if ((not prev_input) and pressure_input):
                bot.force = chan.value
                bot.get_next_state()
            prev_input = pressure_input
            time.sleep(0.10)


    def get_next_state(self):
        base_random = random.random()
        variable_random = random.random() * 0.5
        if self.force > 24000:
            base_random -= variable_random
        elif self.force <= 12000 and self.force > 0: 
            base_random += variable_random
        if base_random > 0.6:
            self.hallucinated_state = "You are recover from the hallucination, your response should be as normal and correct as possible."
        elif base_random > 0.4 and base_random <= 0.6:
            self.hallucinated_state = "You are under a fun hallucination, the force reminds you of the old history story related to user's request, when you hear user's next request, you will talk to them about it as if you are their elder"
        else:
            self.hallucinated_state = "You are under more severe hallucination, your response always has fact error or disrespect on the user input and context."

        print(f"Current hallucinated state: {self.hallucinated_state}")

    def get_response(self, prompt):
        background = "You are Alexz, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic. What you can do is to control smart home devices and interact with users. Remember, you are not AI in this task and you should bear the role in mind rather than repeat it to users because they know what you can do."
        system_message = self.hallucinated_state

        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview",
                                                  messages=[
                                                      {"role": "system", "content": background},
                                                      {"role": "system", "content": system_message},
                                                      {"role": "user", "content": prompt}],
                                                  max_tokens=50,
                                                  temperature=0.5)
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
                    else:
                        self.reset_state()
                else:
                    self.reset_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self.reset_state()

    def reset_state(self):
        self.last_user_input = ""

    def record_audio(self, ):
        """
        Record audio for a specified number of seconds, save it to a file, and return the audio data.
        """
        FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
        CHANNELS = 2              # Number of audio channels
        RATE = 16000              # Sample rate (Hz)
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



if __name__ == "__main__":
    bot = HallucinatedChatbot()
    prev_input = 0

    pressure_thread = threading.Thread(target=bot.monitor_pressure)
    pressure_thread.start()

    try:
        while True:
            user_input = input(
                "Type 'r' to record audio or 'q' to exit: ")
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 'r':
                # TODO: need to add a button to control
                bot.record_audio()
                user_input = bot.transcribe_audio()  # Transcribe the audio
                print(f"You said: {user_input}")
                if user_input.lower() == "speech recognition could not understand audio":
                    continue

            try:
                bot_response = bot.chat(user_input)
                print(
                    f"Bot: {bot_response}")
                bot.play_text(bot_response)
            except Exception as e:
                print(f"Error during chat: {e}")

            bot.save_state()
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        if pressure_thread.is_alive():
            pressure_thread.join()

    print("Exiting program.")
