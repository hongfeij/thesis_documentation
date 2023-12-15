from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import json
import threading

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained("j-hartmann/emotion-english-distilroberta-base")

# Initialize a lock for file writing
file_lock = threading.Lock()

def analyze_emotion(text):
    # Tokenize the input text and get model output
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)

    # Apply softmax to get probabilities
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Define the emotion labels based on the model
    emotion_labels = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    emotion_scores = predictions.detach().numpy()[0]

    # Map scores to emotion labels
    emotion_dict = {label: float(score) for label, score in zip(emotion_labels, emotion_scores)}
    
    return emotion_dict
