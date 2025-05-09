from pyht import AsyncClient
from dotenv import load_dotenv
from pyht.client import TTSOptions
import os
load_dotenv()

client = AsyncClient(
    user_id=os.getenv("PLAY_HT_USER_ID"),
    api_key=os.getenv("PLAY_HT_API_KEY"),
)
options = TTSOptions(voice="s3://voice-cloning-zero-shot/775ae416-49bb-4fb6-bd45-740f205d20a1/jennifersaad/manifest.json")
async for chunk in client.tts("Hi, I'm Jennifer from Play. How can I help you today?", options):
    # do something with the audio chunk
    print(type(chunk))