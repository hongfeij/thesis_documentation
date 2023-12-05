import pyaudio
import wave

# Constants
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 2              # Number of audio channels
RATE = 16000              # Sample rate (Hz)
CHUNK = 1024              # Number of frames per buffer
RECORD_SECONDS = 5        # Duration of recording
WAVE_OUTPUT_FILENAME = "test_recording.wav"

# Initialize PyAudio
p = pyaudio.PyAudio()

# Recording
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                frames_per_buffer=CHUNK, input_device_index=1)  # Set your device index here

print("Recording...")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate the PortAudio interface
p.terminate()

# Save the recorded data as a WAV file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# Playback
p = pyaudio.PyAudio()

# Open the WAV file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')

# Open a stream for playback
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=1)

# Play back the entire file
data = wf.readframes(CHUNK)
while data:
    stream.write(data)
    data = wf.readframes(CHUNK)

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate the PortAudio interface
p.terminate()
print("Playback finished.")

# Device 0: bcm2835 Headphones: - (hw:2,0) (Input Channels: 0)
# Device 1: seeed-2mic-voicecard: bcm2835-i2s-wm8960-hifi wm8960-hifi-0 (hw:3,0) (Input Channels: 2)
# Device 2: pulse (Input Channels: 32)
# Device 3: playback (Input Channels: 0)
# Device 4: capture (Input Channels: 128)
# Device 5: dmixed (Input Channels: 0)
# Device 6: array (Input Channels: 2)
# Device 7: default (Input Channels: 32)