from dotenv import load_dotenv
import os
from openai import OpenAI
import openai


load_dotenv()


client = OpenAI(
    api_key=os.getenv('API_KEY'), # ваш ключ в VseGPT после регистрации
    base_url="https://api.vsegpt.ru/v1",
)

def get_answer(prompt: str) -> str:
    response_big = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{'role': 'user', 'content': prompt}],
        temperature=1,
        n=1,
        max_tokens=3000, # максимальное число ВЫХОДНЫХ токенов. Для большинства моделей не должно превышать 4096
        extra_headers={"X-Title": "My App" }, # опционально - передача информация об источнике API-вызова
    )
    response = response_big.choices[0].message.content
    # response = 'ECHO'
    return response    
