import json
import re
from pymongo import MongoClient
import openai
from openai import OpenAI
import os
import random
# import pygame
# from playsound import playsound

MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
connection_string = f"mongodb+srv://hongfeij:{MONGO_PASSWORD}@remibot.vqkfst7.mongodb.net/?retryWrites=true&w=majority"

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

agent = OpenAI()

RESPONSE_FILENAME = "response.mp3"
VOICE_CHOICE = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
FREQUENCY = 0.5

isWrong = False
isSuspected = False


class HallucinatedChatbot:
    def __init__(self):
        self.username = ""
        self.conversations = None
        self.random_user = ""

        self.curr_user = ""
        self.curr_context = ""
        self.voice = ""

    def make_prompt(self, command, boolean_json):
        messages = [
            {"role": "system", "content": f"Here is two states to decide if you switch the conversation context, in json: {boolean_json}"},
            {"role": "system", "content": f"The user issues the command: {command}, change the two states by thinking step by step."},
            {"role": "system", "content": f"If the command shows positive or neutral emotion, it means the user doesn't suspect it, but it can't decide if the conversation goes wrong"},
            {"role": "system", "content": f"If the command shows the user wants to learn more about the person, it means the conversation goes well, but it can't decide if the the user suspect it"},
            {"role": "system", "content": f"If the command expresses confusion or suspection about the person's identity, it means the conversation goes wrong and the user suspect it"},
            {"role": "system", "content": "So, Please provide your response in JSON format."}
        ]
        return messages

    def json_process(self, text):
        match = re.search(r"{(.+?)}", text, re.DOTALL)

        if match:
            json_content = "{" + match.group(1) + "}"
            json_content = json_content.replace('True', 'true').replace('False', 'false')
            json_content = json_content.replace("'", '"')
            json_content = re.sub(r'[^\x20-\x7E]', '', json_content)
            return json_content
        else:
            print("No JSON content found")

    def generate_remi_state(self, prompt):
        response = agent.chat.completions.create(model="gpt-4-1106-preview",
                                                 messages=prompt,
                                                 temperature=0.5)
        return response

    def get_response(self, prompt):
        global isWrong, isSuspected

        context_cursor = conversations_collection.find_one(
            {"user_name": self.username})
        context_voice = context_cursor.get('voice', None)
        context = ' '.join(context_cursor.get('messages', []))

        random_context_cursor = conversations_collection.find_one(
            {"user_name": self.random_user})
        random_voice = random_context_cursor.get('voice', None)
        random_context = ' '.join(random_context_cursor.get('messages', []))

        users = [self.username, self.random_user]
        weights = [1-FREQUENCY, FREQUENCY]
        selected = random.choices(users, weights, k=1)[0]

        remi_init_json = {"isWrong": isWrong, "isSuspected": isSuspected}
        remi_prompt = self.make_prompt(prompt, remi_init_json)
        remi_response = self.generate_remi_state(remi_prompt)
        print(remi_response)
        remi_response_fixed = self.json_process(remi_response.choices[0].message.content.strip(
        ))
        remi_json = json.loads(remi_response_fixed)
        print(f"remi_json: {remi_json}")

        isWrong = remi_json['isWrong']
        isSuspected = remi_json['isSuspected']

        if not (isWrong and not isSuspected):
            print('-----------------------Re-choose!-----------------------')
            if selected == self.username:
                self.curr_user = self.username
                self.voice = context_voice
                self.curr_context = context
            else:
                self.curr_user = self.random_user
                self.voice = random_voice
                self.curr_context = random_context
        # else:
        #     self.curr_user = self.username
        #     self.voice = context_voice
        #     self.curr_context = context

        print(f"current user {self.curr_user}, current voice {self.voice}")

        background = (
            f"You are a conversational bot providing intimate conversation using {self.curr_context} as conversation context."
            f"Your conversation always relates to the {self.curr_context} as reminiscence if it's reasonable."
            f"You can share {self.curr_context} if asked about {self.curr_user}, it's open to public."
            f"Make sure to include {self.curr_user} in each response, and remember this is the perosn you are talking to."
            f"Keep responses in 3 sentences and do not mention any hallucination."
        )

        # change to text, then change back to boolean

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

    def chat(self, user_input, unique_file_name):
        response = self.get_response(user_input)
        text_to_speech(self.voice, response, unique_file_name)
        return response


client = MongoClient(connection_string)
db = client.remibot
conversations_collection = db.conversations


def create_conversation(user_name):
    conversation = conversations_collection.find_one({"user_name": user_name})
    if not conversation:
        conversation = {"user_name": user_name,
                        "voice": random.choice(VOICE_CHOICE), "messages": []}
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


def text_to_speech(voice, text, unique_file_name):
    speech_file_path = f"./{unique_file_name}"
    response = openai.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    response.stream_to_file(speech_file_path)

# def play_text(voice, text):
#     speech_file_path = "./response.mp3"
#     response = openai.audio.speech.create(
#         model="tts-1",
#         voice=voice,
#         input=text
#     )
#     response.stream_to_file(speech_file_path)
#     playsound(speech_file_path)


bot = HallucinatedChatbot()


def init_chat(user_name):
    global bot
    user_name = user_name
    create_conversation(user_name)
    bot.username = user_name
    bot.conversations = get_all_conversations()
    bot.random_user = random.choice(
        find_others(bot.username, bot.conversations))

    print(f"{bot.username}, {bot.random_user}")


def chat(user_name, message, unique_file_name):
    global bot
    add_message(user_name, message)
    response = bot.chat(message, unique_file_name)
    return response
