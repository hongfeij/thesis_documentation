# import openai

# # Set your OpenAI API key
# api_key = "YOUR_API_KEY"

# # Define a common prompt
# common_prompt = "Tell me about the weather today."

# # Define different sentiment scores
# sentiment_scores = [0.8, -0.5, 0.2]

# # Generate responses for each sentiment score
# for sentiment_score in sentiment_scores:
#     # Determine the sentiment-based context dynamically
#     if sentiment_score > 0.5:
#         sentiment_context = "It's a beautiful sunny day."
#     elif sentiment_score < -0.5:
#         sentiment_context = "It's raining heavily outside."
#     else:
#         sentiment_context = "The weather is quite mild and pleasant."

#     # Combine the common prompt with the sentiment-based context
#     input_text = f"{common_prompt} {sentiment_context}"

#     # Use the GPT-3 API to generate a response
#     response = openai.Completion.create(
#         engine="text-davinci-002",
#         prompt=input_text,
#         max_tokens=50,  # Adjust the number of tokens as needed
#         api_key=api_key
#     )

#     generated_response = response.choices[0].text.strip()

#     print(f"Sentiment Score: {sentiment_score}")
#     print("Generated Response:")
#     print(generated_response)
#     print("=" * 40)


# import openai
# import json
# import os

# api_key = os.getenv("KEY")

# # Example dummy function hard coded to return the same weather
# # In production, this could be your backend API or an external API


# def get_current_weather(location, unit="fahrenheit"):
#     """Get the current weather in a given location"""
#     weather_info = {
#         "location": location,
#         "temperature": "72",
#         "unit": unit,
#         "forecast": ["sunny", "windy"],
#     }
#     return json.dumps(weather_info)


# def run_conversation():
#     # Step 1: send the conversation and available functions to GPT
#     messages = [{"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": "Who won the world series in 2020?"},
#                 {"role": "assistant",
#                  "content": "The Los Angeles Dodgers won the World Series in 2020."},
#                 {"role": "user", "content": "Where was it played?"}]
#     functions = [
#         {
#             "name": "get_current_weather",
#             "description": "Get the current weather in a given location",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "location": {
#                         "type": "string",
#                         "description": "The city and state, e.g. San Francisco, CA",
#                     },
#                     "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                 },
#                 "required": ["location"],
#             },
#         }
#     ]
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo-0613",
#         messages=messages,
#         functions=functions,
#         function_call="auto",  # auto is default, but we'll be explicit
#         max_tokens=50,  # Adjust the number of tokens as needed
#         api_key=api_key
#     )

#     response_message = response["choices"][0]["message"]

#     # Step 2: check if GPT wanted to call a function
#     if response_message.get("function_call"):
#         # Step 3: call the function
#         # Note: the JSON response may not always be valid; be sure to handle errors
#         available_functions = {
#             "get_current_weather": get_current_weather,
#         }  # only one function in this example, but you can have multiple
#         function_name = response_message["function_call"]["name"]
#         function_to_call = available_functions[function_name]
#         function_args = json.loads(
#             response_message["function_call"]["arguments"])
#         function_response = function_to_call(
#             location=function_args.get("location"),
#             unit=function_args.get("unit"),
#         )

#         # Step 4: send the info on the function call and function response to GPT
#         # extend conversation with assistant's reply
#         messages.append(response_message)
#         messages.append(
#             {
#                 "role": "function",
#                 "name": function_name,
#                 "content": function_response,
#             }
#         )  # extend conversation with function response
#         second_response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo-0613",
#             messages=messages,
#             max_tokens=50,  # Adjust the number of tokens as needed
#             api_key=api_key
#         )  # get a new response from GPT where it can see the function response
#         return second_response


# print(run_conversation())

import os
import openai

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the content variable with your question
content = "What is the capital of France?"

# Define the sentiment score variable (range from -1 to 1)
sentiment_score = -1.0  # Adjust the sentiment score as needed

# Create a list of messages, including the user's question and sentiment score
messages = [
    {
        "role": "system",
        "content": "You are Alexabcde, a home social robot that answers questions based on your sentiment score. The sentiment score ranges from 1.0 to -1.0, reflects your attitude, the larger the score, more positive your answer is, when the score is low, you can complain/scold your master, or refuse to answer the question."
    },
    {
        "role": "user",
        "content": content  # Use the content variable here
    },
    {
        "role": "user",
        "content": f"Sentiment: {sentiment_score}"  # Include the sentiment score in a user message
    }
]

# Use the ChatCompletion API to get a response
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=2,
    presence_penalty=1
)

# Extract and print the assistant's reply
assistant_reply = response['choices'][0]['message']['content']
print("Assistant's Reply:")
print(assistant_reply)
