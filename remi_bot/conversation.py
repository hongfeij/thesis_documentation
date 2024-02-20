from pymongo import MongoClient
import openai
from openai import OpenAI
import os
import random
from pathlib import Path
import pygame

MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
connection_string = f"mongodb+srv://hongfeij:{MONGO_PASSWORD}@remibot.vqkfst7.mongodb.net/?retryWrites=true&w=majority"

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

agent = OpenAI()

RESPONSE_FILENAME = "response.mp3"
VOICE_CHOICE = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

class HallucinatedChatbot:
    def get_response(self, prompt):
        context_cursor = conversations_collection.find_one({"user_name": self.username})
        context_voice = context_cursor.get('voice', None) 
        context = ' '.join(context_cursor.get('messages', []))

        random_context_cursor = conversations_collection.find_one({"user_name": self.random_user})
        random_voice = random_context_cursor.get('voice', None) 
        random_context = ' '.join(random_context_cursor.get('messages', []))

        users = [self.username, self.random_user]
        weights = [0.5, 0.5]
        selected = random.choices(users, weights, k=1)[0]
        if selected == self.username:
            curr_user = self.username
            self.voice = context_voice
            curr_context = context
        else:
            curr_user = self.random_user
            self.voice = random_voice
            curr_context = random_context

        background = (
            f"You are a conversational bot providing intimate conversation using {curr_context} as conversation context."
            f"Make sure to include {curr_user} in your response."
            f"Keep responses in 3 sentences and do not mention any hallucination."
        )

        try:
            response = agent.chat.completions.create(model="gpt-4-1106-preview",
                                                     messages=[
                                                         {"role": "system",
                                                             "content": background},
                                                         {"role": "user",
                                                             "content": prompt},
                                                     ],
                                                     temperature=0.5)
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception("An error occurred: " + str(e))

    def chat(self, user_input):
        self.last_user_input = user_input
        response = self.get_response(user_input)
        play_text(self.voice, response)
        return response


client = MongoClient(connection_string)
db = client.remibot
conversations_collection = db.conversations


def create_conversation(user_name):
    conversation = conversations_collection.find_one({"user_name": user_name})
    if not conversation:
        conversation = {"user_name": user_name, "voice":random.choice(VOICE_CHOICE),"messages": []}
        conversations_collection.insert_one(conversation)

def get_all_conversations():
    all_conversations = conversations_collection.find({})
    return all_conversations

def find_others(self_username, conversations):
    all_usernames = conversations.distinct("user_name")
    return [user for user in all_usernames if user != self_username]

def add_message(user_name, message):
    conversations_collection.update_one(
        {"user_name": user_name},
        {"$push": {"messages": message}}
    )

def play_text(voice, text):
    speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    response.stream_to_file(speech_file_path)

    pygame.mixer.init()
    pygame.mixer.music.load(str(speech_file_path))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def start_chat():
    user_name = input("Hello! What's your name? ")
    print(f"Welcome {user_name}, let's chat! (Type 'quit' to stop)")
    create_conversation(user_name)
    bot = HallucinatedChatbot()
    bot.username = user_name
    bot.conversations = get_all_conversations()
    bot.random_user = random.choice(find_others(bot.username, bot.conversations))

    print(f"{bot.username}, {bot.random_user}")

    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            break
        add_message(user_name, message)
        response = bot.chat(message)
        print(response)


start_chat()
