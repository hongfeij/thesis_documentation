# import pyaudio
import alsaaudio
import wave
from openai import OpenAI
from pathlib import Path
import numpy as np
import os
import board
import neopixel
import time

OUTPUT_FILENAME = "recorded_audio.wav"
RESPONSE_FILENAME = "response.wav"

pixel_pin = board.D10
num_pixels = 1

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False
)

client = OpenAI()

OUTPUT_FILENAME = "recorded_audio.wav"
CHANNELS = 1
RATE = 44100
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
CHUNK_SIZE = 512
RECORDING_LENGTH = 5

def record_audio():
    pixels.fill((255, 255, 255))
    pixels.show()
    # recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, mode=alsaaudio.PCM_NORMAL, 
    #                          rate=RATE, channels=CHANNELS, format=FORMAT, 
    #                          periodsize=CHUNK_SIZE, device="plughw:CARD=seeed2micvoicec,DEV=0")

    # num_frames = int(RATE / CHUNK_SIZE * RECORDING_LENGTH)
    # recording_frames = []

    # for _ in range(num_frames):
    #     l, data = recorder.read()
    #     if l:
    #         recording_frames.append(data)
    #     # print(f"Data: {data[:10]}")

    # recorder.close()

    time.sleep(5)

    pixels.fill((0, 0, 0))
    pixels.show()

    # with wave.open(OUTPUT_FILENAME, 'wb') as wave_file:
    #     wave_file.setnchannels(CHANNELS)
    #     wave_file.setsampwidth(2)
    #     wave_file.setframerate(RATE)
    #     wave_file.writeframes(b''.join(recording_frames))

def transcribe_audio():
    # audio_file = open(OUTPUT_FILENAME, "rb")
    # transcript = client.audio.transcriptions.create(
    #     model="whisper-1",
    #     language="en",
    #     file=audio_file,
    #     response_format="text")
    # return transcript
    return ""

def play_text(text):
    print(f"A: {text}")
    # response = client.audio.speech.create(model="tts-1", voice="echo", input=text, response_format="wav")
    # speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
    # response.stream_to_file(speech_file_path)

    # speech_file_path = str(speech_file_path) if isinstance(speech_file_path, Path) else speech_file_path

    try:
        pixels.fill((255, 255, 255))
        pixels.show()

        time.sleep(15)


    #     with wave.open(speech_file_path, 'rb') as wf:
    #         player = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, 
    #                             rate=RATE, channels=CHANNELS, format=FORMAT, 
    #                             periodsize=CHUNK_SIZE, device="plughw:CARD=seeed2micvoicec,DEV=0")
            
    #         data = wf.readframes(CHUNK_SIZE)
    #         while data:
    #             player.write(data)
    #             data = wf.readframes(CHUNK_SIZE)

    #         player.close()
        pixels.fill((0, 0, 0))
        pixels.show()

    except Exception as e:
        print(f"Error during playback: {e}")

    # finally:
        # os.remove(speech_file_path)
        # os.remove(OUTPUT_FILENAME)
