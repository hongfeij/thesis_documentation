import sys
import os
import openai
import json
import time
from text_sentiment import analyze_emotion
from openai import OpenAI
import threading

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
# Provide a default value of 1.0 if not set
SENSITIVITY = float(os.getenv('SENSITIVITY', 1.0))

client = OpenAI()

class EmotionChatbot:
    def __init__(self, start_emotion_score={'anger': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}):
        self.emotion_score = start_emotion_score
        self.last_user_input = ""
        self.monitoring_active = True  # Flag to control the monitoring thread

    def monitor_emotion_data(self):
        last_checked = 0
        while self.monitoring_active:  # Use the flag to control the loop
            try:
                with open("emotion_data.json", "r") as file:
                    data = json.load(file)
                    if data["timestamp"] > last_checked:
                        last_checked = data["timestamp"]
                        self.adjust_emotion(data["emotion_data"])
                        self.last_user_input = "" 
            except (FileNotFoundError, json.JSONDecodeError):
                pass

            time.sleep(10)

    def adjust_emotion(self, sentiment_scores):
        for key in sentiment_scores:
            adjusted_score = sentiment_scores[key] / SENSITIVITY
            self.emotion_score[key] = max(min(adjusted_score, 1), -1)

    def get_response(self, prompt):
        background = "You are Alexz, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic and emotions. What you can do is to control smart home devices and interact with users. Remember, you are not AI in this task."
        if self.emotion_score["anger"] > 0.6 or self.emotion_score["disgust"] > 0.6:
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
            except openai.error.OpenAIError as e:  # Adjusted to a generic OpenAIError
                wait = 2 ** attempt  # Exponential backoff formula
                print(f"OpenAIError: {e} - Retrying in {wait} seconds...")
                time.sleep(wait)
            except Exception as e:  # Catch-all for other exceptions
                print(f"An error occurred: {e}")
                wait = 2 ** attempt
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
            raise Exception(
                "Max retry attempts reached. Service is unavailable.")

    def chat(self, user_input):
        original_emotion_scores = analyze_emotion(user_input)
        self.adjust_emotion(original_emotion_scores)
        print(self.emotion_score)
        self.last_user_input = user_input
        response = self.get_response(user_input)
        print("chat pass")
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
        print("save")
        print(new_entry)

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
                        self.emotion_score = last_state.get("emotion_score", {'anger': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0})
                        self.last_user_input = last_state.get("last_user_input", "")
                    else:
                        self.reset_state()
                else:
                    self.reset_state()
        except (FileNotFoundError, json.JSONDecodeError):
            self.reset_state()

    def reset_state(self):
        self.emotion_score = {'anger': 0, 'disgust': 0, 'fear': 0, 'happy': 0, 'neutral': 0, 'sad': 0, 'surprise': 0}
        self.last_user_input = ""

if __name__ == "__main__":
    bot = EmotionChatbot()
    bot.load_state()
    print("load finished")

    # Start the monitoring thread
    monitor_thread = threading.Thread(target=bot.monitor_emotion_data)
    monitor_thread.start()

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == 'quit':
                bot.monitoring_active = False  # Signal the monitoring thread to stop
                monitor_thread.join()  # Wait for the monitoring thread to finish
                break

            bot_response, bot_emotion_score = bot.chat(user_input)
            print("chat finished")

            bot.save_state()
            print("save finished")
            print(f"Bot: {bot_response} (Emotion Score: {bot_emotion_score})")
    finally:
        bot.monitoring_active = False
        if monitor_thread.is_alive():
            monitor_thread.join()

    print("Exiting program.")

