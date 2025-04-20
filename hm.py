from cartesia import Cartesia
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("CARTESIA_API_KEY")
client = Cartesia(api_key=api_key)

try:
    ws = client.tts.websocket()
    print("WebSocket connection successful")
    ws.close()
except Exception as e:
    print(f"Error: {e}")