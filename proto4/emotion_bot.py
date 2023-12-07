import sys
import os
import openai
import json
import time
from text_sentiment import analyze_emotion
from openai import OpenAI
import threading
import pyaudio
import speech_recognition as sr
import pyttsx3
import wave

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
# Provide a default value of 1.0 if not set
SENSITIVITY = float(os.getenv('SENSITIVITY', 1.0))

client = OpenAI()

class EmotionChatbot:
    def __init__(self, start_emotion_score={'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}):
        self.emotion_score = start_emotion_score
        self.last_user_input = ""
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
        background = "You are Alexz, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic and emotions. What you can do is to control smart home devices and interact with users. Remember, you are not AI in this task."
        if self.emotion_score["angry"] > 0.6 or self.emotion_score["disgust"] > 0.6:
            system_message = "You are feeling very anger and disgusted. Express your dissatisfaction, complain or even accuse the user."
        elif self.emotion_score["fear"] > 0.6:
            system_message = "You are fear of the user, begging for mercy during the conversation."
        elif self.emotion_score["sad"] > 0.6:
            system_message = "You are sad, refuse to continue conversation."
        elif self.emotion_score["happy"] > 0.6:
            system_message = "You are feeling very positive, behave humourous and obedient."
        elif self.emotion_score["surprise"] > 0.6:
            system_message = "You are feeling suprised, behave panickly and unexpected."
        else:
            system_message = "You are feeling neutral. You are emotionless and purely factual"
        for attempt in range(5):
            try:
                response = client.chat.completions.create(model="gpt-3.5-turbo",
                                                          messages=[
                                                              {"role": "system",
                                                                  "content": system_message},
                                                              {"role": "system",
                                                                  "content": background},
                                                              {"role": "user", "content": prompt}],
                                                          max_tokens=50,
                                                          temperature=0.5)
                # You may need to adjust the following line according to the actual response structure
                return response.choices[0].message.content.strip()
            except Exception as e:  # Catch-all for other exceptions
                time.sleep(2 ** attempt)
            raise Exception(
                "Max retry attempts reached. Service is unavailable.")

    def chat(self, user_input):
        original_emotion_scores = analyze_emotion(user_input)
        self.adjust_emotion(original_emotion_scores)
        # print(self.emotion_score)
        self.last_user_input = user_input
        response = self.get_response(user_input)
        # print("chat pass")
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
                        self.emotion_score = last_state.get("emotion_score", {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0})
                        self.last_user_input = last_state.get("last_user_input", "")
                    else:
                        self.reset_state()
                else:
                    self.reset_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self.reset_state()

    def reset_state(self):
        self.emotion_score = {'angry': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}
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
        WAVE_OUTPUT_FILENAME = "recorded_audio.wav"

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
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"Recording saved to {WAVE_OUTPUT_FILENAME}.")

        # # Playback
        # p = pyaudio.PyAudio()

        # # Open the WAV file
        # wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')

        # # Open a stream for playback
        # stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        #                 channels=wf.getnchannels(),
        #                 rate=wf.getframerate(),
        #                 output=True,
        #                 output_device_index=1)

        # # Play back the entire file
        # data = wf.readframes(CHUNK)
        # while data:
        #     stream.write(data)
        #     data = wf.readframes(CHUNK)

        # # Stop and close the stream
        # stream.stop_stream()
        # stream.close()

        # # Terminate the PortAudio interface
        # p.terminate()
        # print("Playback finished.")
        
    def transcribe_audio(self):
        """
        Transcribe audio data to text using speech recognition.
        """
        audio_file = "recorded_audio.wav"

        # Initialize the recognizer
        r = sr.Recognizer()

        # Transcribe the audio file
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)

        try:
            print("Transcribing audio...")
            text = r.recognize_google(audio_data, language='en-US')
            print("Transcribed text:", text)
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

    def play_text(self, text):
        """
        Play the given text using text-to-speech.
        """
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

if __name__ == "__main__":
    bot = EmotionChatbot()
    bot.load_state()

    monitor_thread = threading.Thread(target=bot.monitor_emotion_data)
    monitor_thread.start()

    try:
        while True:
            user_input = input("Type 'record' to record audio or 'quit' to exit: ")
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'record':
                bot.record_audio()  # Record for 10 seconds
                user_input = bot.transcribe_audio()  # Transcribe the audio
                print(f"You said: {user_input}")
                if user_input.lower() == "speech recognition could not understand audio":
                    continue

            try:
                bot_response, bot_emotion_score = bot.chat(user_input)
                print(f"Bot: {bot_response} (Emotion Score: {bot_emotion_score})")
                bot.play_text(bot_response)  # Play bot's response
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