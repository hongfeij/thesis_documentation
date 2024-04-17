import pyaudio
# import sounddevice as sd
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

def record_audio():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1           # Number of channels
    BITRATE = 44100        # Audio Bitrate
    CHUNK_SIZE = 512       # Chunk size to 
    RECORDING_LENGTH = 5  # Recording Length in seconds
    DEVICE_ID = 1
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=BITRATE,
        input=True,
        input_device_index = DEVICE_ID,
        frames_per_buffer=CHUNK_SIZE
    )

    recording_frames = []

    for i in range(int(BITRATE / CHUNK_SIZE * RECORDING_LENGTH)):
        data = stream.read(CHUNK_SIZE)
        recording_frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(BITRATE)
    waveFile.writeframes(b''.join(recording_frames))
    waveFile.close()

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
