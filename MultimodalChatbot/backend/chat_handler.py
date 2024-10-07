from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(    
    base_url='https://api.vsegpt.ru/v1'    
)


def get_answer(prompt: str) -> str:
    # response_big = client.chat.completions.create(
    #     model="openai/gpt-4o-mini",        
    #     temperature=1,
    #     messages=[{'role': 'user', 'content': prompt}],
    #     max_tokens=3000
    # )
    # return response_big.choices[0].message.content
    return 'gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg'
#     return '''Вот пример программы "Hello, World!" на Python:

# ```python
# print("Hello, World!")
# ```

# Эта программа выводит строку "Hello, World!" на экран.

# Если у вас другая задача или вы имеете в виду конкретный язык или контекст, дайте знать!'''
