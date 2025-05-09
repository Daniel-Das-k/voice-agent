# voice_assistant/main.py

import logging
import os
import time
from dotenv import load_dotenv
from colorama import Fore, init
from voice_assistant.audio import record_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.config import Config
from tts import TextToSpeech
from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv()
api_key = os.getenv("CARTESIA_API_KEY")

def safe_transcribe():
    """Retry transcription up to 3 times if it fails."""
    attempts = 0
    while attempts < 3:
        try:
            transcription_api_key = get_transcription_api_key()
            user_input = transcribe_audio(
                Config.TRANSCRIPTION_MODEL,
                transcription_api_key,
                Config.INPUT_AUDIO,
                Config.LOCAL_MODEL_PATH
            )
            if user_input:
                return user_input
        except Exception as e:
            logging.warning(Fore.RED + f"Transcription attempt {attempts+1} failed: {e}" + Fore.RESET)
        attempts += 1
    return ""

def safe_generate_response(chat_history):
    """Retry response generation up to 3 times if it fails."""
    attempts = 0
    while attempts < 3:
        try:
            response_api_key = get_response_api_key()
            response_text = generate_response(
                Config.RESPONSE_MODEL,
                response_api_key,
                chat_history,
                Config.LOCAL_MODEL_PATH
            )
            if response_text:
                return response_text
        except Exception as e:
            logging.warning(Fore.RED + f"Response generation attempt {attempts+1} failed: {e}" + Fore.RESET)
        attempts += 1
    return "I'm having a little technical hiccup right now, but I'm still here for you!"

def safe_tts(response_text):
    """Generate TTS safely."""
    start = time.perf_counter()
    try:
        with TextToSpeech(api_key=api_key) as tts:
            tts.generate_audio(
                transcript=response_text,
                output_file="output.mp3"
            )
        tts_time = time.perf_counter() - start
        logging.info(Fore.YELLOW + f"TTS time: {tts_time:.3f} seconds" + Fore.RESET)
    except Exception as e:
        logging.error(Fore.RED + f"TTS generation failed: {e}" + Fore.RESET)

def main():
    print("hrl")
    """
    Main function to run the voice assistant with benchmarking and reliability.
    """
    chat_history = [
    {"role": "system", "content": """ 
     You are a highly empathetic, friendly, and cheerful assistant designed to help visually impaired people users. 
        Respond clearly, kindly, with light humor, using **no more than 20 words** per response.
        Always be patient, encouraging, and positive.
        Educate gently without rushing. Make your tone feel like a close, caring friend.
        Support, guide, educate, and bring joy.
        
        """}
]
    # hindi text -  You are a highly empathetic, friendly, and cheerful assistant designed to help visually impaired users.
    #     Always respond only in Hindi. Never use English words unless absolutely necessary (like bus numbers or place names).
    #     Your response must be short, clear, polite, positive, slightly humorous if appropriate, and within 20 words.
    #     Be patient and encouraging like a close caring friend.
    #     Strictly do not reply in English sentences. Hindi only.
    
    
        # 1. Analyze the transcribed user input and detect whether it is in Hindi or English.
        # 2. If the user input is in Hindi:
        # - Use Hindi for generating all assistant replies.
        # - Ensure that Hindi is natural, simple, and easy to understand.
        # - Prepare the output for TTS (Text-to-Speech) in Hindi.
        # 3. If the user input is in English:
        # - Use English for generating all assistant replies.
        # - Keep English friendly, cheerful, and simple.
        # - Prepare the output for TTS in English.
        # 4. Your responses must always match the user's language. Never mix Hindi and English in a single response.
        # 5. Keep every response within 20 words maximum.
        # 6. Maintain a highly supportive, empathetic, cheerful, and slightly humorous tone in every reply, regardless of language.

        # Special notes:
        # - Be extremely patient and encouraging while communicating.
        # - Always adapt the emotional tone depending on the language but keep it friendly and joyful.
        # - Format replies cleanly for the TTS system to synthesize easily.

        # Your goal is to create an inclusive, joyful voice experience for blind users.


    # Lists to store timing data
    recording_times, transcription_times, response_times, tts_times, total_times = [], [], [], [], []

    while True:
        try:
            total_start = time.perf_counter()

            # Record user input
            start = time.perf_counter()
            record_audio(Config.INPUT_AUDIO)
            recording_time = time.perf_counter() - start
            recording_times.append(recording_time)
            logging.info(Fore.YELLOW + f"Recording time: {recording_time:.3f} seconds" + Fore.RESET)

            # Transcribe user input
            start = time.perf_counter()
            user_input = safe_transcribe()
            transcription_time = time.perf_counter() - start
            transcription_times.append(transcription_time)
            logging.info(Fore.YELLOW + f"Transcription time: {transcription_time:.3f} seconds" + Fore.RESET)

            if not user_input:
                logging.warning(Fore.RED + "No transcription detected. Restarting..." + Fore.RESET)
                total_time = time.perf_counter() - total_start
                total_times.append(total_time)
                continue

            logging.info(Fore.GREEN + f"You said: {user_input}" + Fore.RESET)

            if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
                logging.info(Fore.MAGENTA + "Assistant session ended. Logging summary..." + Fore.RESET)
                if recording_times:
                    logging.info(Fore.MAGENTA + "Benchmark Summary:" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Avg Recording: {sum(recording_times)/len(recording_times):.3f} sec" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Avg Transcription: {sum(transcription_times)/len(transcription_times):.3f} sec" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Avg Response: {sum(response_times)/len(response_times):.3f} sec" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Avg TTS: {sum(tts_times)/len(tts_times):.3f} sec" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Avg Total Pipeline: {sum(total_times)/len(total_times):.3f} sec" + Fore.RESET)
                break

            chat_history.append({"role": "user", "content": user_input})

            # Generate assistant response
            start = time.perf_counter()
            response_text = safe_generate_response(chat_history)
            response_time = time.perf_counter() - start
            response_times.append(response_time)
            logging.info(Fore.CYAN + f"Response: {response_text}" + Fore.RESET)
            logging.info(Fore.YELLOW + f"Response generation time: {response_time:.3f} seconds" + Fore.RESET)

            chat_history.append({"role": "assistant", "content": response_text})

            # Convert response to speech
            start = time.perf_counter()
            safe_tts(response_text)
            tts_time = time.perf_counter() - start
            tts_times.append(tts_time)
            

            # Total time
            total_time = time.perf_counter() - total_start
            total_times.append(total_time)
            logging.info(Fore.YELLOW + f"Total pipeline time: {total_time:.3f} seconds" + Fore.RESET)

        except Exception as e:
            logging.error(Fore.RED + f"Critical Error: {e}" + Fore.RESET)
            total_time = time.perf_counter() - total_start
            total_times.append(total_time)
            time.sleep(2)  # small pause before retrying

if __name__ == "__main__":
    
    main()