# import sys
# import os
# import openai
# import json
# import time
# from openai import OpenAI
# import threading
# import pyaudio
# import wave
# from pathlib import Path
# import RPi.GPIO as GPIO
# import pygame

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# BUTTON_PIN = 17        # Button input
# GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# R_PIN = 12
# G_PIN = 13
# B_PIN = 19
# GPIO.setup(R_PIN, GPIO.OUT)
# GPIO.setup(G_PIN, GPIO.OUT)
# GPIO.setup(B_PIN, GPIO.OUT)
# pwmRed = GPIO.PWM(R_PIN, 500)
# pwmGreen = GPIO.PWM(G_PIN, 500)
# pwmBlue = GPIO.PWM(B_PIN, 500)
# pwmRed.start(0)
# pwmBlue.start(0)
# pwmGreen.start(100)

# SWITCH_PIN = 23

# USE_SCORE = 0.1

# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# if OPENAI_API_KEY is None:
#     raise ValueError(
#         "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
# OUTPUT_FILENAME = "recorded_audio.wav"
# RESPONSE_FILENAME = "response.mp3"

# client = OpenAI()

# class HallucinatedChatbot:
#     def __init__(self):
#         self.last_user_input = ""
#         self.hallucination_rate = 1
#         self.update_led_color(self.hallucination_rate)
#         # GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#         # GPIO.add_event_detect(SWITCH_PIN, GPIO.BOTH, callback=self.switch, bouncetime=200)
#         # self.listening_event = threading.Event()
#         # self.listening_event.clear()
#         # self.stop_listening = False

#     # blue low is blue
#     def update_led_color(self, hallucination_rate):
#         hallucination_rate = max(0, min(hallucination_rate, 1))
#         red_duty_cycle = (1 - hallucination_rate) * 100  # Increase red with hallucination rate
#         blue_duty_cycle = hallucination_rate * 100  # Decrease blue with hallucination rate
#         print(red_duty_cycle, blue_duty_cycle)
        
#         pwmRed.ChangeDutyCycle(red_duty_cycle)
#         pwmGreen.ChangeDutyCycle(100)  # Ensure green is turned off
#         pwmBlue.ChangeDutyCycle(blue_duty_cycle)

#     def get_response(self, prompt):
#         background = "You are Alexz, a home social robot, your response will be affected by your hallucination rate, your current hallucination rate is {self.hallucination_rate}"

#         try:
#             response = client.chat.completions.create(model="gpt-4-1106-preview",
#                                                       messages=[
#                                                           {"role": "system",
#                                                            "content": background},
#                                                           {"role": "user", "content": prompt}],
#                                                       max_tokens=50,
#                                                       temperature=0.5)
#             if self.hallucination_rate < 1.0:
#                 self.hallucination_rate += USE_SCORE
#             print(self.hallucination_rate)
#             self.update_led_color(self.hallucination_rate)
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             raise Exception("An error occurred: " + str(e))

#     def chat(self, user_input):
#         self.last_user_input = user_input
#         response = self.get_response(user_input)
#         return response

#     def save_state(self, filepath="state.json"):
#         states = []
#         try:
#             with open(filepath, "r") as f:
#                 states = json.load(f)
#         except FileNotFoundError:
#             pass

#         new_entry = {
#             "id": len(states) + 1,
#             "last_user_input": self.last_user_input,
#             "hallucination_rate": self.hallucination_rate
#         }

#         states.append(new_entry)

#         with open(filepath, "w") as f:
#             json.dump(states, f, indent=4)

#     def load_state(self, filepath="state.json"):
#         try:
#             with open(filepath, "r") as f:
#                 states = json.load(f)
#                 # Check if states is a list and not empty
#                 if isinstance(states, list) and states:
#                     last_state = states[-1]
#                     if isinstance(last_state, dict):
#                         self.last_user_input = last_state.get(
#                             "last_user_input", "")
#                         self.hallucination_rate = last_state.get(
#                             "hallucination_rate", 0)
#                     else:
#                         self.reset_state()
#                 else:
#                     self.reset_state()
#         except (FileNotFoundError, json.JSONDecodeError):
#             self.reset_state()

#     def reset_state(self):
#         self.last_user_input = ""
#         self.hallucination_rate = 0

#     def record_audio(self, ):
#         """
#         Record audio for a specified number of seconds, save it to a file, and return the audio data.
#         """
#         FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
#         CHANNELS = 2              # Number of audio channels
#         RATE = 48000              # Sample rate (Hz)
#         CHUNK = 1024              # Number of frames per buffer
#         RECORD_SECONDS = 5        # Duration of recording

#         p = pyaudio.PyAudio()
#         stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
#                         frames_per_buffer=CHUNK, input_device_index=1)

#         print("Recording...")
#         frames = []

#         for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#             data = stream.read(CHUNK)
#             frames.append(data)

#         print("Finished recording.")

#         stream.stop_stream()
#         stream.close()

#         p.terminate()

#         # Save the recorded data to a WAV file
#         wf = wave.open(OUTPUT_FILENAME, 'wb')
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))
#         wf.close()

#         print(f"Recording saved to {OUTPUT_FILENAME}.")

#     def transcribe_audio(self):
#         # """
#         # Transcribe audio data to text using speech recognition.
#         # """
#         audio_file = open(OUTPUT_FILENAME, "rb")
#         transcript = client.audio.transcriptions.create(
#             model="whisper-1",
#             language="en",
#             file=audio_file,
#             response_format="text")
#         print(f"You said: {transcript}")
#         return transcript

#     def play_text(self, text):
#         """
#         Play the given text using text-to-speech.
#         """
#         print("Play text")
#         speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
#         response = openai.audio.speech.create(
#             model="tts-1",
#             voice="echo",
#             input=text
#         )
#         response.stream_to_file(speech_file_path)

#         pygame.mixer.init()
#         pygame.mixer.music.load(str(speech_file_path))
#         pygame.mixer.music.play()
#         while pygame.mixer.music.get_busy():
#             pygame.time.Clock().tick(10)

#     def button_monitor(self):
#         last_press_time = 0
#         debounce_threshold = 0.2  # 200 ms debounce threshold
#         while True:
#             # print(self.hallucination_rate)
#             # print(self.current_duty_cycle)
#             if not GPIO.input(BUTTON_PIN):  # Assuming active low
#                 current_time = time.time()
#                 if (current_time - last_press_time) >= debounce_threshold:
#                     print("Button pressed.")
#                     if self.hallucination_rate >= USE_SCORE:
#                         self.hallucination_rate -= USE_SCORE
#                         self.update_led_color(self.hallucination_rate)
#                     else: 
#                         self.hallucination_rate = 1
#                     print(f"current hallucination rate is {self.hallucination_rate}")
#                     # Handle button press here
#                     last_press_time = current_time
#             time.sleep(0.01)  # Short sleep to reduce CPU load

#     def switch(self, channel):
#         if GPIO.input(SWITCH_PIN):  # Assuming the switch is active high
#             print("Switch activated: Starting to listen.")
#             self.listening_event.set()  # Signal to start listening
#             if not hasattr(self, 'listening_thread') or not self.listening_thread.is_alive():
#                 self.listening_thread = threading.Thread(target=self.listen_for_speech)
#                 self.listening_thread.start()
#         else:
#             print("Switch deactivated: Requesting to stop listening.")
#             self.stop_listening = True

#     def listen_for_speech(self):
#         self.listening_event.wait()  # Wait for the signal to start listening
#         while not self.stop_listening:
#             print("Listening for speech...")
#             self.record_audio()
#             user_input = self.transcribe_audio()
#             if user_input.lower() != "speech recognition could not understand audio":
#                 bot_response = self.chat(user_input)
#                 print(f"Bot: {bot_response}")
#                 self.play_text(bot_response)
#                 self.save_state()
#             else:
#                 print("Could not transcribe audio or no speech detected.")
#             time.sleep(1)
#             if self.stop_listening:
#                 print("Listening stopped by request.")
#                 break
#         self.listening_event.clear()
#         self.stop_listening = False

# if __name__ == "__main__":
#     bot = HallucinatedChatbot()

#     # listening_thread = threading.Thread(target=bot.listen_for_speech)
#     # listening_thread.start()

#     button_thread = threading.Thread(target=bot.button_monitor)
#     button_thread.start()

#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Program terminated by user.")
#     except Exception as e:
#         print(f"Unhandled exception: {e}")
#     finally:
#         # # listening_thread.join()
#         # if hasattr(bot, 'listening_thread') and bot.listening_thread.is_alive():
#         #     bot.listening_event.set()  # Ensure the thread is not blocked
#         #     bot.stop_listening = True
#         #     bot.listening_thread.join()
#         button_thread.join()
#         pwmRed.stop()  # Stop red PWM
#         pwmGreen.stop()  # Stop green PWM
#         pwmBlue.stop()  # Stop blue PWM
#         GPIO.cleanup()  # Clean up GPIO on exit
#         print("Exiting program.")
