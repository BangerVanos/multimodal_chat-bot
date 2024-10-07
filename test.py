from dotenv import load_dotenv
from openai import OpenAI

# from langchain.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI



load_dotenv()

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=1,
    max_retries=1,
    base_url='https://api.vsegpt.ru/v1'
    # api_key="...",
    # base_url="...",
    # organization="...",
    # other params...
)


# input_text = "The meaning of life is "
# ans = llm.invoke(input_text)
# print(ans)

# from langchain.chains import LLMChain
# from langchain.memory import ConversationBufferMemory
# from langchain_core.messages import SystemMessage
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.prompts.chat import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
# )
# from langchain_openai import ChatOpenAI

# prompt = ChatPromptTemplate(
#     [
#         MessagesPlaceholder(variable_name="chat_history"),
#         HumanMessagePromptTemplate.from_template("{text}"),
#     ]
# )

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# legacy_chain = LLMChain(
#     llm=llm,
#     prompt=prompt,
#     memory=memory,
# )

# legacy_result = legacy_chain.invoke({"text": "my name is bob"})

# legacy_result = legacy_chain.invoke({"text": "what was my name"})
# print(legacy_result)



# from langchain import OpenAI
from langchain.agents import initialize_agent, Tool, AgentType
import requests
from openai import OpenAI

# API ключ OpenWeather (замени на свой ключ)
API_KEY = "your_openweather_api_key"

# Функция для получения информации о погоде через OpenWeather API
def get_weather(city: str) -> str:
    # url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    # response = requests.get(url)
    # print('-----------------------------------------------------')
    return f"The weather in {city} is warm and sunny with a temperature of 22°C."
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is {weather} with a temperature of {temperature}°C."
    else:
        return f"Could not retrieve weather for {city}. Please check the city name."

# Другие агенты можно добавить здесь (например, новостной агент, агент для конвертации валют и т.д.)
# Пример: агент новостей
def get_news() -> str:
    print('news_agent checked')
    return "Here are today's top headlines: Tramp is a president now !!!!"




# Инструменты (агенты)
weather_tool = Tool(
    name="Weather",
    func=get_weather,
    description="Provides the weather for a given city"
)

news_tool = Tool(
    name="News information agent",
    func=get_news,
    description="Provides the latest information about news. Предоставляет самую свежую информацию о новостях а так же просто дает информацию про новости которые были"
)

# Инициализация LLM
# llm = OpenAI(temperature=0)

# Инициализация агентов для каждого инструмента
weather_agent = initialize_agent(
    tools=[weather_tool],
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

news_agent = initialize_agent(
    tools=[news_tool],
    llm=llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Список агентов
agents = [weather_agent, news_agent]

# Fallback агент для обработки запросов, если ни один из агентов не подходит
def fallback_llm(query):
    return llm(query)

# Основная логика работы с запросами
def chatbot(query):
    # Перебор всех агентов
    for agent in agents:
        try:
            print(agent)
            response = agent.run(query)
            if response:  # Если агент дал ответ, то возвращаем его
                return response
        except Exception as e:
            # Логируем ошибки, но не прерываем выполнение
            # print(f"Agent {agent} failed: {e}")
            continue

    # Если ни один агент не подошел, используем fallback (LLM)
    return fallback_llm(query)

# Пример использования

# query = "What is the weather in New York?"
# query = 'Расскажи анекдот на 30 слов'
# query = 'Какая температура в Минске?'
query = 'Вот промт от пользователя прежде чем давать информацию посмотри есть ли агента который даст ответ: Расскажи про последние новости мне'
response = chatbot(query)
print(response.content)

# query = "Tell me the news"
# response = chatbot(query)
# print(response)

# query = "Tell me a joke"
# response = chatbot(query)
# print(response)
