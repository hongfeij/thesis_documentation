import sys
import os
import openai
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import json

# Ensure the VADER lexicon is downloaded
nltk.download('vader_lexicon', quiet=True)


class EmotionChatbot:
    def __init__(self, start_emotion_score=0.0):
        self.emotion_score = start_emotion_score
        self.last_user_input = ""
        self.last_sentiment_score = 0.0
        self.analyzer = SentimentIntensityAnalyzer()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if openai.api_key is None:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        self.sensitivity = os.getenv('SENSITIVITY')

    def adjust_emotion(self, sentiment_score):
        sensitivity = float(
            self.sensitivity) if self.sensitivity is not None else 1.0
        self.emotion_score += sentiment_score / sensitivity
        self.emotion_score = max(min(self.emotion_score, 1), -1)

    def sentiment_analysis(self, text):
        scores = self.analyzer.polarity_scores(text)
        return scores['compound']

    def get_response(self, prompt):
        background = "You are Alexz, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic and temper. What you can do is to control smart home devices and interact with users. You do have emotions"
        # Dynamic system message based on emotion score
        if self.emotion_score < -0.6:
            # Behavior for very negative emotion score
            system_message = "You are feeling very negative. Refuse joke requests and express your dissatisfaction, complain or even accuse the user."
        elif self.emotion_score < -0.2:
            # Behavior for slightly negative emotion score
            system_message = "You are feeling negative. If asked for a joke, consider responding sarcastically or begrudgingly, or sound annoyed and consider refusing requests"
        elif self.emotion_score < 0.2:
            # Behavior for slightly negative emotion score
            system_message = "You are feeling neutral. You are emotionless and purely factual"
        elif self.emotion_score < 0.6:
            # Behavior for slightly negative emotion score
            system_message = "You are feeling positive. You remain friendly and helpful to the user."
        else:
            # Behavior for neutral or positive emotion score
            system_message = "You are feeling very positive, behave humourous and obedient."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "system", "content": background},
                {"role": "user", "content": prompt}],
            max_tokens=25,
            temperature=0.5 + self.emotion_score * 0.5
        )
        return response['choices'][0]['message']['content'].strip()

    def chat(self, user_input):
        sentiment_score = self.sentiment_analysis(user_input)
        self.last_user_input = user_input
        self.last_sentiment_score = sentiment_score
        self.adjust_emotion(sentiment_score)
        response = self.get_response(user_input)
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
            "last_sentiment_score": self.last_sentiment_score
        }

        states.append(new_entry)

        with open(filepath, "w") as f:
            json.dump(states, f, indent=4)


    def load_state(self, filepath="emotion_state.json"):
        try:
            with open(filepath, "r") as f:
                states = json.load(f)
                if states:
                    last_state = states[-1]
                    self.emotion_score = last_state.get("emotion_score", 0.0)
                    self.last_user_input = last_state.get("last_user_input", "")
                    self.last_sentiment_score = last_state.get(
                        "last_sentiment_score", 0.0)
        except FileNotFoundError:
            self.emotion_score = 0.0
            self.last_user_input = ""
            self.last_sentiment_score = 0.0


if __name__ == "__main__":
    # Check if a user input was provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python3 script.py \"<your message here>\"")
        sys.exit(1)

    bot = EmotionChatbot()
    bot.load_state()

    user_input = sys.argv[1]
    bot_response, bot_emotion_score = bot.chat(user_input)
    bot.save_state()
    print(f"Bot: {bot_response} (Emotion Score: {bot_emotion_score:.2f})")
