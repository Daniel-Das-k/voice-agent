# voice_assistant/text_to_speech.py
import logging
import json
import pyaudio
import elevenlabs
import soundfile as sf
import numpy as np
from pydub import AudioSegment

from openai import OpenAI
from deepgram import DeepgramClient, SpeakOptions
from elevenlabs.client import ElevenLabs
from cartesia import Cartesia

from voice_assistant.local_tts_generation import generate_audio_file_melotts

def text_to_speech(model: str, api_key: str, text: str, output_file_path: str, local_model_path: str = None):
    """
    Convert text to speech using the specified model.
    
    Args:
        model (str): The model to use for TTS ('openai', 'deepgram', 'elevenlabs', 'local', 'cartesia', 'melotts').
        api_key (str): The API key for the TTS service.
        text (str): The text to convert to speech.
        output_file_path (str): The path to save the generated speech audio file.
        local_model_path (str): The path to the local model (if applicable).
    """
    
    try:
        if model == 'openai':
            client = OpenAI(api_key=api_key)
            speech_response = client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=text
            )
            speech_response.stream_to_file(output_file_path)

        elif model == 'deepgram':
            client = DeepgramClient(api_key=api_key)
            options = SpeakOptions(
                model="aura-arcas-en",
                encoding="linear16",
                container="wav"
            )
            SPEAK_OPTIONS = {"text": text}
            response = client.speak.v("1").save(output_file_path, SPEAK_OPTIONS, options)
        
        elif model == 'elevenlabs':
            client = ElevenLabs(api_key=api_key)
            audio = client.generate(
                text=text, 
                voice="Paul J.", 
                output_format="mp3_22050_32", 
                model="eleven_turbo_v2"
            )
            elevenlabs.save(audio, output_file_path)
        
        elif model == "cartesia":
            client = Cartesia(api_key="sk_car_k8LE35ATLhXQXE4vQibQ4q")
            voice_id = "cb605424-d682-48e9-94db-34cc567cf1c6"  # Your voice ID
            model_id = "sonic-2"
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }
            audio_buffers = []
            # Collect audio chunks from the SSE generator
            for output in client.tts.sse(
                model_id=model_id,
                transcript=text,
                voice={"id": voice_id},
                language="en",
                output_format=output_format,
            ):
                audio_buffers.append(output.data)  # Use output.data to get bytes
            if audio_buffers:
                # Combine all chunks into a single bytes object
                audio_data = b''.join(audio_buffers)
                # Convert raw PCM float32 to int16 for MP3 compatibility
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
                audio_array_int16 = (audio_array * 32767).astype(np.int16)
                # Create an AudioSegment object
                audio_segment = AudioSegment(
                    audio_array_int16.tobytes(),
                    frame_rate=44100,
                    sample_width=2,  # 16-bit = 2 bytes
                    channels=1       # Mono audio
                )
                # Export to MP3
                audio_segment.export(output_file_path, format="mp3")
                logging.info(f"Audio saved to {output_file_path}")
            else:
                logging.error("No audio buffers received from Cartesia API.")
        
        elif model == "melotts":  # this is a local model
            generate_audio_file_melotts(text=text, filename=output_file_path)
        
        elif model == 'local':
            with open(output_file_path, "wb") as f:
                f.write(b"Local TTS audio data")
        
        else:
            raise ValueError("Unsupported TTS model")
        
    except Exception as e:
        logging.error(f"Failed to convert text to speech: {e}")

# Example usage (if needed)
if __name__ == "__main__":
    text = "Hi Daniel! Thanks for the meeting wrap-up! It was great chatting with you. Good day!"
    api_key = "your_cartesia_api_key_here"
    output_file = "output.mp3"
    text_to_speech("cartesia", api_key, text, output_file)