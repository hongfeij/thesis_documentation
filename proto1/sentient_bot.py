import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ask Alexabcde a question.")
parser.add_argument('--content', type=str,
                    required=True, help="Your question.")
parser.add_argument('--score', type=float, required=True,
                    help="Sentiment score (range: -1.0 to 1.0).")
args = parser.parse_args()

# Set your OpenAI API key

# Use the command-line arguments for content and sentiment score
content = args.content
sentiment_score = args.score

# Check if sentiment_score is in the correct range
if not -1.0 <= sentiment_score <= 1.0:
    raise ValueError("Sentiment score should be in the range of -1.0 to 1.0.")

# Create a list of messages, including the user's question and sentiment score
messages = [
    {
        "role": "system",
        "content": "You are Alexabcde, a home social robot, you can assist domestic user or accompany them, but you also have your own charateristic and temper. What you can do is to control smart home devices and interact with users."
    },
    {
        "role": "system",
        "content": "Your behavior are based on a sentiment score ranging from 1.0 (positive) to -1.0 (negative). No matter what score you have, you can decide how to interact with the user, such as the freedom to response or follow instruction, but higher score related to more friendlyness."
    },
    {
        "role": "system",
        "content": "For scores 0.6-1.0 (extremely high), be highly positive, humour and obedient. For 0.2-0.6 (high), remain friendly. For -0.2 to 0.2 (moderate), be emotionless and purely factual. For -0.6 to -0.2 (low), sound annoyed and consider refusing requests. For -1.0 to -0.6 (extremely low), complain or even accuse the user."
    },
    {
        "role": "user",
        "content": content  # Use the content variable here
    },
    {
        "role": "user",
        # Include the sentiment score in a user message
        "content": f"Sentiment: {sentiment_score}"
    }
]

# Use the ChatCompletion API to get a response
response = client.chat.completions.create(model="gpt-3.5-turbo",
messages=messages,
temperature=0.25,
max_tokens=64,
top_p=1,
frequency_penalty=2,
presence_penalty=1)

# Extract and print the assistant's reply
assistant_reply = response['choices'][0]['message']['content']
print("Assistant's Reply:" + assistant_reply)
