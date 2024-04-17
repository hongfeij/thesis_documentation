from pathlib import Path
from openai import OpenAI
client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="fable",
  input="Hello Zain! Yes, it's quite late. If you're planning to get some rest, I hope you have a good night's sleep!"
)

response.stream_to_file(speech_file_path)