# # voice_assistant/main.py
# import logging
# import os
# from dotenv import load_dotenv
# import time
# from colorama import Fore, init
# from voice_assistant.audio import record_audio, play_audio
# from voice_assistant.transcription import transcribe_audio
# from voice_assistant.response_generation import generate_response
# from voice_assistant.text_to_speech import text_to_speech
# from voice_assistant.utils import delete_file
# from voice_assistant.config import Config
# from tts import TextToSpeech
# from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Initialize colorama
# init(autoreset=True)

# load_dotenv()

# import threading

# load_dotenv()
# api_key = os.getenv("CARTESIA_API_KEY")

# def main():
#     """
#     Main function to run the voice assistant.
#     """
#     chat_history = [
#         {"role": "system", "content": """ You are a helpful Assistant called Verbi. 
#          You are friendly and fun and you will help the users with their requests.
#          Your answers are short and concise. """}
#     ]

#     while True:
#         try:
#             # Record audio from the microphone and save it as 'test.wav'
#             record_audio(Config.INPUT_AUDIO)

#             # Get the API key for transcription
#             transcription_api_key = get_transcription_api_key()
            
#             # Transcribe the audio file
#             user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, transcription_api_key, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)

#             # Check if the transcription is empty and restart the recording if it is
#             if not user_input:
#                 logging.info("No transcription was returned. Starting recording again.")
#                 continue
#             logging.info(Fore.GREEN + "You said: " + user_input + Fore.RESET)

#             # Check if the user wants to exit the program
#             if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
#                 break

#             # Append the user's input to the chat history
#             chat_history.append({"role": "user", "content": user_input})

#             # Get the API key for response generation
#             response_api_key = get_response_api_key()

#             # Generate a response
#             response_text = generate_response(Config.RESPONSE_MODEL, response_api_key, chat_history, Config.LOCAL_MODEL_PATH)
#             logging.info(Fore.CYAN + "Response: " + response_text + Fore.RESET)

#             # Append the assistant's response to the chat history
#             chat_history.append({"role": "assistant", "content": response_text})

#             # Generate audio using TextToSpeech
#             try:
#                 with TextToSpeech(api_key=api_key) as tts:
#                     tts.generate_audio(
#                         transcript=response_text,
#                         output_file="output.mp3"
#                     )
#             except Exception as e:
#                 logging.error(f"Failed to generate audio: {e}")

#         except Exception as e:
#             logging.error(Fore.RED + f"An error occurred: {e}" + Fore.RESET)
           
# if __name__ == "__main__":
#     main()




# voice_assistant/main.py
import logging
import os
from dotenv import load_dotenv
import time
from colorama import Fore, init
from voice_assistant.audio import record_audio, play_audio
from voice_assistant.transcription import transcribe_audio
from voice_assistant.response_generation import generate_response
from voice_assistant.text_to_speech import text_to_speech
from voice_assistant.utils import delete_file
from voice_assistant.config import Config
from tts import TextToSpeech
from voice_assistant.api_key_manager import get_transcription_api_key, get_response_api_key, get_tts_api_key

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize colorama
init(autoreset=True)

load_dotenv()

import threading

load_dotenv()
api_key = os.getenv("CARTESIA_API_KEY")

def main():
    """
    Main function to run the voice assistant with benchmarking.
    """
    chat_history = [
        {"role": "system", "content": """ You are a helpful Assistant called Verbi. 
         You are friendly and fun and you will help the users with their requests.
         Your answers are short and concise. """}
    ]

    # Lists to store timing data for summary statistics
    recording_times = []
    transcription_times = []
    response_times = []
    tts_times = []
    total_times = []

    while True:
        try:
            # Start total pipeline timer
            total_start = time.perf_counter()

            # Record audio from the microphone and save it as 'test.wav'
            start = time.perf_counter()
            record_audio(Config.INPUT_AUDIO)
            recording_time = time.perf_counter() - start
            recording_times.append(recording_time)
            logging.info(Fore.YELLOW + f"Recording time: {recording_time:.3f} seconds" + Fore.RESET)

            # Get the API key for transcription
            transcription_api_key = get_transcription_api_key()
            
            # Transcribe the audio file
            start = time.perf_counter()
            user_input = transcribe_audio(Config.TRANSCRIPTION_MODEL, transcription_api_key, Config.INPUT_AUDIO, Config.LOCAL_MODEL_PATH)
            transcription_time = time.perf_counter() - start
            transcription_times.append(transcription_time)
            logging.info(Fore.YELLOW + f"Transcription time: {transcription_time:.3f} seconds" + Fore.RESET)

            # Check if the transcription is empty and restart the recording if it is
            if not user_input:
                logging.info("No transcription was returned. Starting recording again.")
                total_time = time.perf_counter() - total_start
                total_times.append(total_time)
                logging.info(Fore.YELLOW + f"Total pipeline time: {total_time:.3f} seconds" + Fore.RESET)
                continue
            logging.info(Fore.GREEN + "You said: " + user_input + Fore.RESET)

            # Check if the user wants to exit the program
            if "goodbye" in user_input.lower() or "arrivederci" in user_input.lower():
                # Log summary statistics
                if recording_times:  # Only log if there’s data
                    logging.info(Fore.MAGENTA + "Benchmark Summary:" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Average Recording time: {sum(recording_times)/len(recording_times):.3f} seconds" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Average Transcription time: {sum(transcription_times)/len(transcription_times):.3f} seconds" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Average Response time: {sum(response_times)/len(response_times):.3f} seconds" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Average TTS time: {sum(tts_times)/len(tts_times):.3f} seconds" + Fore.RESET)
                    logging.info(Fore.MAGENTA + f"Average Total pipeline time: {sum(total_times)/len(total_times):.3f} seconds" + Fore.RESET)
                break

            # Append the user's input to the chat history
            chat_history.append({"role": "user", "content": user_input})

            # Get the API key for response generation
            response_api_key = get_response_api_key()

            # Generate a response
            start = time.perf_counter()
            response_text = generate_response(Config.RESPONSE_MODEL, response_api_key, chat_history, Config.LOCAL_MODEL_PATH)
            response_time = time.perf_counter() - start
            response_times.append(response_time)
            logging.info(Fore.YELLOW + f"Response generation time: {response_time:.3f} seconds" + Fore.RESET)
            logging.info(Fore.CYAN + "Response: " + response_text + Fore.RESET)

            # Append the assistant's response to the chat history
            chat_history.append({"role": "assistant", "content": response_text})

            # Generate audio using TextToSpeech
            start = time.perf_counter()
            try:
                with TextToSpeech(api_key=api_key) as tts:
                    tts.generate_audio(
                        transcript=response_text,
                        output_file="output.mp3"
                    )
                tts_time = time.perf_counter() - start
                tts_times.append(tts_time)
                logging.info(Fore.YELLOW + f"TTS time: {tts_time:.3f} seconds" + Fore.RESET)
            except Exception as e:
                logging.error(f"Failed to generate audio: {e}")
                tts_time = time.perf_counter() - start
                tts_times.append(tts_time)

            # Log total pipeline time
            total_time = time.perf_counter() - total_start
            total_times.append(total_time)
            logging.info(Fore.YELLOW + f"Total pipeline time: {total_time:.3f} seconds" + Fore.RESET)

        except Exception as e:
            logging.error(Fore.RED + f"An error occurred: {e}" + Fore.RESET)
            total_time = time.perf_counter() - total_start
            total_times.append(total_time)
            logging.info(Fore.YELLOW + f"Total pipeline time (with error): {total_time:.3f} seconds" + Fore.RESET)
           
if __name__ == "__main__":
    main()