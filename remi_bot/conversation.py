from pymongo import MongoClient
import openai
from openai import OpenAI
import os
import random

MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
connection_string = f"mongodb+srv://hongfeij:{MONGO_PASSWORD}@remibot.vqkfst7.mongodb.net/?retryWrites=true&w=majority"

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError(
        "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

agent = OpenAI()


class HallucinatedChatbot:        
    def get_response(self, prompt):
        context = conversations_collection.find({"user_name": self.username})
        random_context = get_random_user_conversations(self.others)
        print(f"Me: {list(context)}, other: {list(random_context)}")
        background = f"You are a chatbot to provide intimate conversation with the user, often including the information and preference from {context}. You should try to finish the conversation in the given token limit. Often you performs hallucination, you will mistaken the person you are talking to for {random_context}. Don't tell your master you have hallucination, it's a secret :)."

        try:
            response = agent.chat.completions.create(model="gpt-4-1106-preview",
                                                      messages=[
                                                          {"role": "system",
                                                           "content": background},
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

client = MongoClient(connection_string)
db = client.remibot
conversations_collection = db.conversations

def get_conversation(user_name):
    conversation = conversations_collection.find_one({"user_name": user_name})
    if not conversation:
        conversation = {"user_name": user_name, "messages": []}
        conversations_collection.insert_one(conversation)
    return conversation

def get_all_conversations():
    all_conversations = conversations_collection.find({})
    return all_conversations

def get_random_user_conversations(usernames):
    if not usernames:
        return "No usernames provided."
    
    selected_username = random.choice(usernames)    
    conversations = conversations_collection.find({"user_name": selected_username})
    return conversations

def find_others(self_username, conversations):
    all_usernames = conversations.distinct("user_name")
    return [user for user in all_usernames if user != self_username]  

def add_message(user_name, message):
    conversations_collection.update_one(
        {"user_name": user_name},
        {"$push": {"messages": message}}
    )

def start_chat():
    user_name = input("Hello! What's your name? ")
    print(f"Welcome {user_name}, let's chat! (Type 'quit' to stop)")
    bot = HallucinatedChatbot()
    bot.username = user_name
    bot.conversations = get_all_conversations()
    bot.others = find_others(bot.username, bot.conversations)
    print(f"{bot.username}, {bot.others}")

    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            break
        add_message(user_name, message)
        response = bot.chat(message)
        print(response)

start_chat()