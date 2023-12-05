import speech_recognition as sr

# File from the recording
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
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand the audio")
except sr.RequestError as e:
    print(f"Could not request results from Google Speech Recognition service; {e}")