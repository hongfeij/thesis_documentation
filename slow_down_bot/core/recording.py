# import pyaudio
import alsaaudio
import wave
from openai import OpenAI
import pygame
from pathlib import Path
import numpy as np
import os

# import RPi.GPIO as GPIO

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
OUTPUT_FILENAME = "recorded_audio.wav"
RESPONSE_FILENAME = "response.mp3"
# LED_PIN = 17
# GPIO.setup(LED_PIN,GPIO.OUT)

client = OpenAI()

OUTPUT_FILENAME = "recorded_audio.wav"
CHANNELS = 1
RATE = 44100
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
CHUNK_SIZE = 512
RECORDING_LENGTH = 5

def record_audio():
    recorder = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)
    recorder.setchannels(CHANNELS)
    recorder.setrate(RATE)
    recorder.setformat(FORMAT)
    recorder.setperiodsize(CHUNK_SIZE)

    num_frames = int(RATE / CHUNK_SIZE * RECORDING_LENGTH)
    recording_frames = []

    for _ in range(num_frames):
        l, data = recorder.read()
        if l:
            recording_frames.append(data)

    with wave.open(OUTPUT_FILENAME, 'wb') as wave_file:
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(alsaaudio.pcm_width(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(recording_frames))

def transcribe_audio():
    audio_file = open(OUTPUT_FILENAME, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        language="en",
        file=audio_file,
        response_format="text")
    return transcript

def play_text(text):
    print(f"A: {text}")
    response = client.audio.speech.create(model="tts-1", voice="echo", input=text)
    speech_file_path = Path(__file__).parent / RESPONSE_FILENAME

    try:
        with open(speech_file_path, 'wb') as f:
            f.write(response.content)

        pygame.mixer.init(frequency=24000)
        pygame.mixer.music.load(str(speech_file_path))
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error during playback: {e}")

    finally:
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        os.remove(speech_file_path)
        os.remove(OUTPUT_FILENAME)
