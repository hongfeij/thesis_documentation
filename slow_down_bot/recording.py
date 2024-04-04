# import pyaudio
import sounddevice as sd
import wave
import openai
from openai import OpenAI
import pygame
from pathlib import Path
import numpy as np
# import RPi.GPIO as GPIO

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
OUTPUT_FILENAME = "recorded_audio.wav"
RESPONSE_FILENAME = "response.mp3"
# LED_PIN = 17
# GPIO.setup(LED_PIN,GPIO.OUT)

client = OpenAI()

CHANNELS = 2              # Number of audio channels
RATE = 48000              # Sample rate (Hz)
RECORD_SECONDS = 5        # Duration of recording
DEVICE_INDEX = 1

# def record_audio():
#     FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
#     CHANNELS = 2              # Number of audio channels
#     RATE = 48000              # Sample rate (Hz)
#     CHUNK = 1024              # Number of frames per buffer
#     RECORD_SECONDS = 5        # Duration of recording
#     DEVICE_INDEX = 1

#     p = pyaudio.PyAudio()

#     # for i in range(p.get_device_count()):
#     #     info = p.get_device_info_by_index(i)
#     #     print(f"{info['index']}: {info['name']} (Input channels: {info['maxInputChannels']})")
    
#     # GPIO.output(LED_PIN,GPIO.HIGH)
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
#                     frames_per_buffer=CHUNK, input_device_index=DEVICE_INDEX)

#     print("Recording...")
#     frames = []

#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     stream.stop_stream()
#     stream.close()

#     p.terminate()
#     # GPIO.output(LED_PIN,GPIO.LOW)

#     wf = wave.open(OUTPUT_FILENAME, 'wb')
#     wf.setnchannels(CHANNELS)
#     wf.setsampwidth(p.get_sample_size(FORMAT))
#     wf.setframerate(RATE)
#     wf.writeframes(b''.join(frames))
#     wf.close()

#     print(f"Recording saved to {OUTPUT_FILENAME}.")

def record_audio():
    # Set the device (if you have a specific one, otherwise you can remove this)
    # sd.default.device = DEVICE_INDEX
    
    print("Recording...")
    # GPIO.output(LED_PIN,GPIO.HIGH)  # Uncomment if you use GPIO
    
    # Record the audio
    recording = sd.rec(int(RECORD_SECONDS * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
    sd.wait()  # Wait until the recording is finished
    
    # GPIO.output(LED_PIN,GPIO.LOW)  # Uncomment if you use GPIO
    print(f"Recording saved to {OUTPUT_FILENAME}.")

    # Save the recording as a WAV file
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(np.dtype('int16').itemsize)
    wf.setframerate(RATE)
    wf.writeframes(recording.tobytes())
    wf.close()

def transcribe_audio():
    audio_file = open(OUTPUT_FILENAME, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        language="en",
        file=audio_file,
        response_format="text")
    return transcript

def play_text(text):
    print("Play text")
    speech_file_path = Path(__file__).parent / RESPONSE_FILENAME
    response = openai.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text
    )
    response.stream_to_file(speech_file_path)

    pygame.mixer.init()
    pygame.mixer.music.load(str(speech_file_path))
    # GPIO.output(LED_PIN,GPIO.HIGH)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    # GPIO.output(LED_PIN,GPIO.LOW)
