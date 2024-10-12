from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv('API_KEY'), # ваш ключ в VseGPT после регистрации
    base_url="https://api.vsegpt.ru/v1",
)


def speech_to_text(audio_bytes: str, language: str) -> str:
    transcript = client.audio.transcriptions.create(
        model = "stt-openai/whisper-1",
        response_format="text",
        language=language,
        file=audio_bytes
    )
    return transcript
