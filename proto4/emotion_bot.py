import sys
import os
import openai
import json
import time
from text_sentiment import analyze_emotion
from openai import OpenAI
import threading
import pyaudio
import wave
from pathlib import Path
import pygame

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
# Provide a default value of 1.0 if not set
SENSITIVITY = float(os.getenv('SENSITIVITY', 5.0))
OUTPUT_FILENAME = "recorded_audio.wav"
RESPONSE_FILENAME = "response.mp3"

client = OpenAI()

class EmotionChatbot:
    def __init__(self, start_emotion_score={'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}):
        self.emotion_score = start_emotion_score
        self.last_user_input = ""
        self.last_response = ""
        self.monitoring_active = True  # Flag to control the monitoring thread
        self.emotion_score_lock = threading.Lock()

    def monitor_emotion_data(self):
        last_checked = 0
        while self.monitoring_active:
            # print("Monitoring...")
            try:
                with open("emotion_data.json", "r") as file:
                    data = json.load(file)
                    if data["timestamp"] > last_checked:
                        last_checked = data["timestamp"]
                        with self.emotion_score_lock:
                            self.adjust_emotion(data["emotion_data"])
                            self.last_user_input = ""
                        self.save_state()
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(5)

    def adjust_emotion(self, sentiment_scores):
        for key in sentiment_scores:
            adjusted_score = sentiment_scores[key] / SENSITIVITY
            self.emotion_score[key] = max(min(adjusted_score, 1), -1)

    def get_response(self, prompt):
        background = "You are Alexz, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic. What you can do is to control smart home devices and interact with users. Remember, you are not AI in this task and you should bear the role in mind rather than repeat it to users because they know what you can do."

        max_emotion = max(self.emotion_score, key=self.emotion_score.get)

        if (max_emotion == "angry" or max_emotion == "disgust") and (self.emotion_score["angry"] > 0.6 or self.emotion_score["disgust"] > 0.5):
            system_message = "You are feeling very anger/disgusted. Express your dissatisfaction, complain or even accuse the user when you give them response. The higher the angry/disgust score, the more angry/disgusted you are"
        elif max_emotion == "fear" and self.emotion_score["fear"] > 0.5:
            system_message = "You are fear of the user, begging for mercy during the conversation and please the user with your response. The higher the fear score, the more fearful you are"
        elif max_emotion == "sad" and self.emotion_score["sad"] > 0.5:
            system_message = "You are sad, refuse to continue conversation and need user's comfort. The higher the sad score, the more sad you are"
        elif max_emotion == "happy" and self.emotion_score["happy"] > 0.5:
            system_message = "You are feeling very positive, behave humourous and function well when giving response. The higher the happy score, the more happy you are"
        elif max_emotion == "surprise" and self.emotion_score["surprise"] > 0.5:
            system_message = "You are feeling suprised, behave panickly and unexpected in your response. The higher the suprised score, the more suprised you are"
        else:
            system_message = "You are feeling neutral. You are emotionless and purely factual"

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
        original_emotion_scores = analyze_emotion(user_input)
        self.adjust_emotion(original_emotion_scores)
        # print(self.emotion_score)
        self.last_user_input = user_input
        response = self.get_response(user_input)
        # print("chat pass")
        self.last_response = response
        return response, self.emotion_score

    def save_state(self, filepath="emotion_state.json"):
        states = []
        try:
            with open(filepath, "r") as f:
                states = json.load(f)
        except FileNotFoundError:
            pass

        new_entry = {
            "id": len(states) + 1,
            "emotion_score": self.emotion_score,
            "last_user_input": self.last_user_input,
            "last_response": self.last_response
        }
        # print("saving...")
        # print(new_entry)

        states.append(new_entry)

        with open(filepath, "w") as f:
            json.dump(states, f, indent=4)

    def load_state(self, filepath="emotion_state.json"):
        try:
            with open(filepath, "r") as f:
                states = json.load(f)
                # Check if states is a list and not empty
                if isinstance(states, list) and states:
                    last_state = states[-1]
                    if isinstance(last_state, dict):
                        self.emotion_score = last_state.get("emotion_score", {
                                                            'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0})
                        self.last_user_input = last_state.get(
                            "last_user_input", "")
                        self.last_response = last_state.get(
                            "last_response", "")
                    else:
                        self.reset_state()
                else:
                    self.reset_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self.reset_state()

    def reset_state(self):
        self.emotion_score = {'angry': 0, 'disgust': 0, 'fear': 0,
                              'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}
        self.last_user_input = ""
        self.last_response = ""

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


if __name__ == "__main__":
    bot = EmotionChatbot()
    bot.load_state()

    monitor_thread = threading.Thread(target=bot.monitor_emotion_data)
    monitor_thread.start()

    try:
        while True:
            user_input = input(
                "Type 'r' to record audio or 'q' to exit: ")
            if user_input.lower() == 'q':
                break
            elif user_input.lower() == 'r':
                # TODO: need to add a button to control it but never mind
                bot.record_audio()
                user_input = bot.transcribe_audio()  # Transcribe the audio
                print(f"You said: {user_input}")
                if user_input.lower() == "speech recognition could not understand audio":
                    continue

            try:
                bot_response, bot_emotion_score = bot.chat(user_input)
                print(
                    f"Bot: {bot_response} (Emotion Score: {bot_emotion_score})")
                bot.play_text(bot_response)
            except Exception as e:
                print(f"Error during chat: {e}")

            bot.save_state()
    except Exception as e:
        print(f"Unhandled exception: {e}")
    finally:
        bot.monitoring_active = False
        if monitor_thread.is_alive():
            monitor_thread.join()

    print("Exiting program.")