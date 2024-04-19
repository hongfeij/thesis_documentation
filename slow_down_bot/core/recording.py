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
RESPONSE_FILENAME = "response.wav"
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
    recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, 
                             rate=RATE, channels=CHANNELS, format=FORMAT, 
                             periodsize=CHUNK_SIZE, device="plughw:CARD=seeed2micvoicec,DEV=0")

    num_frames = int(RATE / CHUNK_SIZE * RECORDING_LENGTH)
    recording_frames = []

    for _ in range(num_frames):
        l, data = recorder.read()
        if l:
            recording_frames.append(data)
        # print(f"Data: {data[:10]}")

    recorder.close()

    with wave.open(OUTPUT_FILENAME, 'wb') as wave_file:
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(2)
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
    response = client.audio.speech.create(model="tts-1", voice="echo", input=text, response_format="wav")
    speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
    response.stream_to_file(speech_file_path)

    speech_file_path = str(speech_file_path) if isinstance(speech_file_path, Path) else speech_file_path

    try:
        with wave.open(speech_file_path, 'rb') as wf:
            player = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, 
                                rate=RATE, channels=CHANNELS, format=FORMAT, 
                                periodsize=CHUNK_SIZE, device="plughw:CARD=seeed2micvoicec,DEV=0")
            
            data = wf.readframes(CHUNK_SIZE)
            while data:
                player.write(data)
                data = wf.readframes(CHUNK_SIZE)

            player.close()

    except Exception as e:
        print(f"Error during playback: {e}")

    # finally:
    #     os.remove(speech_file_path)
    #     os.remove(OUTPUT_FILENAME)
