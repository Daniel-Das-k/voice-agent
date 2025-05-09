

# tts.py
import os
import pyaudio
import logging
import numpy as np
from pydub import AudioSegment
from dotenv import load_dotenv
from cartesia import Cartesia

class TextToSpeech:
    """A class to handle text-to-speech conversion using Cartesia's WebSocket API."""

    # Class-level PyAudio instance to avoid reinitialization
    _p = None
    _p_ref_count = 0  # Track number of active TextToSpeech instances

    def __init__(self, api_key: str, voice_id: str = "f91ab3e6-5071-4e15-b016-cde6f2bcd222", # for hindi - f91ab3e6-5071-4e15-b016-cde6f2bcd222 for english - 32b3f3c5-7171-46aa-abe7-b598964aa793
                 model_id: str = "sonic-2", sample_rate: int = 22050):
        """
        Initialize the TextToSpeech client with Cartesia API and audio settings.

        Args:
            api_key (str): Cartesia API key.
            voice_id (str): ID of the voice to use for TTS.
            model_id (str): ID of the TTS model (e.g., 'sonic-2').
            sample_rate (int): Audio sample rate (e.g., 22050 Hz).
        """
        # Set up logging (only if not already configured)
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        
        # Validate API key
        if not api_key:
            raise ValueError("CARTESIA_API_KEY is required")
        
        # Initialize Cartesia client
        self.client = Cartesia(api_key=api_key)
        self.voice_id = voice_id
        self.model_id = model_id
        self.sample_rate = sample_rate
        self.output_format = {
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": sample_rate
        }
        
        # Initialize or reuse PyAudio
        if TextToSpeech._p is None:
            TextToSpeech._p = pyaudio.PyAudio()
            logging.info("PyAudio initialized")
        TextToSpeech._p_ref_count += 1
        self.stream = None
        self.ws = None

    def __enter__(self):
        """Support context manager for resource initialization."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure resources are cleaned up."""
        self.close()

    def close(self):
        """Clean up audio stream and WebSocket, but keep PyAudio alive."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            logging.info("Audio stream closed")
            self.stream = None
        if self.ws:
            self.ws.close()
            logging.info("WebSocket closed")
            self.ws = None
        # Decrement reference count and terminate PyAudio only if no instances remain
        TextToSpeech._p_ref_count -= 1
        if TextToSpeech._p_ref_count == 0 and TextToSpeech._p is not None:
            TextToSpeech._p.terminate()
            TextToSpeech._p = None
            logging.info("PyAudio terminated")

    def generate_audio(self, transcript: str, output_file: str = "output.mp3"):
        """
        Generate and stream audio from text, optionally saving to an MP3 file.

        Args:
            transcript (str): Text to convert to speech.
            output_file (str): Path to save the MP3 file (optional).

        Raises:
            ValueError: If the output buffer type is unexpected.
            RuntimeError: If WebSocket connection or TTS request fails.
        """
        audio_buffers = []
        
        try:
            # Set up WebSocket connection
            logging.info("Attempting to connect to WebSocket...")
            self.ws = self.client.tts.websocket()
            
            # Generate and stream audio
            logging.info("Sending TTS request...")
            for output in self.ws.send(
                model_id=self.model_id,
                transcript=transcript,
                voice={"id": self.voice_id},
                stream=True,
                output_format=self.output_format,
            ):
                # Debugging: Inspect output
                logging.debug(f"Output type: {type(output)}")
                logging.debug(f"Output attributes: {dir(output)}")
                
                # Extract audio data (assuming 'audio' attribute holds bytes)
                buffer = getattr(output, 'audio', output)
                
                # Ensure buffer is bytes
                if not isinstance(buffer, bytes):
                    logging.warning(f"Expected bytes, got {type(buffer)}. Attempting to convert...")
                    if isinstance(buffer, str):
                        buffer = buffer.encode('utf-8')  # Unlikely for audio
                    else:
                        raise ValueError(f"Unexpected buffer type: {type(buffer)}")
                
                # Collect buffer for saving
                audio_buffers.append(buffer)
                
                # Stream audio in real-time
                if not self.stream:
                    try:
                        self.stream = TextToSpeech._p.open(
                            format=pyaudio.paFloat32,
                            channels=1,
                            rate=self.sample_rate,
                            output=True
                        )
                        logging.info("Audio stream opened")
                    except Exception as e:
                        logging.error(f"Failed to open audio stream: {e}")
                        raise
                
                self.stream.write(buffer)
                logging.debug(f"Streamed {len(buffer)} bytes")
            
            # Save to MP3 if requested
            if audio_buffers and output_file:
                logging.info(f"Saving audio to {output_file}...")
                audio_data = b''.join(audio_buffers)
                audio_array = np.frombuffer(audio_data, dtype=np.float32)
                audio_array_int16 = (audio_array * 32767).astype(np.int16)
                audio_segment = AudioSegment(
                    audio_array_int16.tobytes(),
                    frame_rate=self.sample_rate,
                    sample_width=2,
                    channels=1
                )
                audio_segment.export(output_file, format="mp3")
                logging.info(f"Audio saved to {output_file}")
            
            if not audio_buffers:
                logging.error("No audio buffers received from Cartesia API")
        
        except Exception as e:
            logging.error(f"Error during WebSocket operation: {e}")
            raise
        finally:
            # Close stream after each generation to prepare for next use
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                logging.info("Audio stream closed")
                self.stream = None

    def __del__(self):
        """Ensure resources are cleaned up when the object is deleted."""
        self.close()

# Example usage
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("CARTESIA_API_KEY")
    
    try:
        with TextToSpeech(api_key=api_key) as tts:
            tts.generate_audio(
                transcript="""Start the voice assistant by running python run_voice_assistant.py
The assistant will display a message: "Voice Assistant started. Say 'Lumina' to activate."
Say "Lumina" to activate the assistant
When the wake word is detected, the assistant will respond with a greeting in Hindi
Then you can speak your command or question
The assistant will process your request and respond""",
                output_file="output.mp3"
            )
    except Exception as e:
        logging.error(f"Failed to generate audio: {e}")

