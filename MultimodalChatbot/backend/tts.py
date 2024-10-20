from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv('API_KEY'), # ваш ключ в VseGPT после регистрации
    base_url="https://api.vsegpt.ru/v1",
)

def text_to_speech(text: str, voice: str = 'nova') -> str:
    text = 'I' # COMMENT ON PROD
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-openai/tts-1",
        voice=voice, # поддерживаются голоса alloy, echo, fable, onyx, nova и shimmer
        input=text,
        # response_format="wav" # другой формат, при необходимости
    )
    response.write_to_file(speech_file_path)
    return response