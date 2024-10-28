from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from openai import OpenAI
import time
import requests
from geopy.geocoders import Nominatim
import yfinance as yf


load_dotenv()

# Define the tools for the agent to use
# @tool
# def search(query: str):
#     """Call to surf the web."""
#     # This is a placeholder, but don't tell the LLM that...    
#     return "It's 20 degrees celcium, warm and sunny."

# @tool
# def news(query: str):
#     """Call to check up for the latest world news."""
#     # This is a placeholder, but don't tell the LLM that...    
#     return "News are bad as always... Trump is a president"


# ROMAN's AGENTS

@tool
def image_generation(query: str):
    """Call to generate images by text prompt"""
    time.sleep(1.5)
    response_big = image_model.images.generate(
        model="img-dummy/image",
        prompt=query,
        n=1,
        size="1024x1024"
    )
    return response_big.data[0].url

def image_recognition(prompt: str, image: str):
    print('Agent image recognition')
    time.sleep(1)    
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": image,
                },
            ],
        }
    ]
    # vis-openai/gpt-4-vision-preview
    # vis-google/gemini-pro-vision
    response_big = image_model.chat.completions.create(
        model="vis-google/gemini-pro-vision",
        messages=messages,
        temperature=1,
        n=1,
        max_tokens=1000,
    )
    response = response_big.choices[0].message.content
    return response

@tool
def get_stock_price(query: str):
    """Аgent for extraction companies' current stock prices    
    Accepts user's query with company's ticker and returns its current stock prices
    """
    def extract_ticker(query: str):
        """Извлекает тикер компании из строки запроса."""
        words = query.split()
        for word in words:
            if word.isupper() and len(word) <= 5:  # Предполагаем, что тикер обычно в верхнем регистре и не длиннее 5 символов
                return word
        return None

    # Извлечение тикера компании
    ticker = extract_ticker(query)
    if not ticker:
        return "Не удалось найти тикер компании в запросе."
    print(ticker)

    # Получение стоимости акций
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.history(period="1d")
        if stock_info.empty:
            return f"Не удалось найти данные для тикера {ticker}."
        current_price = stock_info['Close'].iloc[-1]
        return f"Текущая стоимость акций {ticker}: ${current_price:.2f}"
    except Exception as e:
        return f"Произошла ошибка при получении данных: {e}"


@tool
def job_search_hh(query: str, area: int = 1, page: int = 0, per_page: int = 5):
    """
    Call this agent when the user wants to search for job vacancies on HeadHunter (hh.ru) 
    based on a specific query. """
    
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": query,
        "areas": area,
        "page": page,
        "per_page": per_page
    }
    
    try:
        print(params)
        response = requests.get(url, params=params)
        print('work')
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        
        # Constructing the result
        results = []
        for item in data["items"]:
            title = item["name"]
            employer = item["employer"]["name"]
            job_url = item["alternate_url"]
            results.append(f"{title} at {employer}: {job_url}")
        
        if not results:
            return "No job listings found for your search criteria."
        
        return "\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"Error retrieving job data: {e}"
    except KeyError:
        return "Error parsing job data. Please try again."


# IGNAT's AGENTS

@tool
def yes_or_no(query: str):
    """Call when user asks decision-making queston, which could be answered with Yes or No"""
    # This is a placeholder, but don't tell the LLM that...
    print('Агент вызван yes_or_no')
    response = requests.get('https://yesno.wtf/api').json()
    # print(response)
    answer = f"Your answer is {response['answer']} gif \n![yes_or_no_gif]({response['image']})\n Inserting gif from response is obligatory." 
    return answer

@tool
def weather_agent(query: str):
    # """Gets coordinates (latitude or longitude or both) by the name of the city"""
    '''Call this agent when you need the current weather information temperature or wind speed by the name of the city'''
    
    geolocator = Nominatim(user_agent="city_geocoder")
    location = geolocator.geocode(query)

    if location:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            # Extracting current weather data
            temperature = data['current']['temperature_2m']
            wind_speed = data['current']['wind_speed_10m']

            result = (f"Current weather: Temperature = {temperature}°C, "
                    f"Wind Speed = {wind_speed} m/s.")
        except requests.exceptions.RequestException as e:
            result = f"Error retrieving weather data: {e}"
        return result
    else:
        return 'Cant find information about weather'

def crypto_price(query: str):
    """Call this agent when the user wants to know the current price of a specific cryptocurrency."""
    # crypto_id = 'bitcoin'
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={query}&vs_currencies=usd"
    print(url)
    result = 'No info about Cryptocurrency'
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = str(response.json())

        result = f"Here json answer {data}"
    except requests.exceptions.RequestException as e:
        result = f"Error retrieving cryptocurrency data: {e}"
    except KeyError:
        result = f"Cryptocurrency not found."
    
    return result

@tool
def get_exchange_rate(base_currency: str, target_currency: str):
    '''Call this agent when the user wants to know the current exchange rate between two currencies.'''
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency.upper()}"
    
    result = 'No info'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Extracting the exchange rate
        rate = data['rates'].get(target_currency.upper())
        
        if rate is None:
            return f"Currency '{target_currency}' not found."

        result = f"1 {base_currency.upper()} = {rate} {target_currency.upper()}"
    except requests.exceptions.RequestException as e:
        result = f"Error retrieving currency data: {e}"

    return result


@tool
def recipe_search_by_ingredients(ingredients: str, number: int = 5):
    """
    Call this agent when a user wants to find recipes that can be made with specified ingredients.
    Translate ingredients to english
    """

    api_key = "b23c8469bb6a4589bff563baeda438ae"  # Replace with your actual API key
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ingredients,
        "number": number,
        "apiKey": api_key
    }
    print(params)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        recipes = response.json()
        print('work')

        if not recipes:
            return "No recipes found for the specified ingredients."

        # Constructing a readable list of recipes
        results = []
        for i, recipe in enumerate(recipes, start=1):
            title = recipe["title"]
            recipe_id = recipe["id"]
            recipe_url = f"https://spoonacular.com/recipes/{title.replace(' ', '-').lower()}-{recipe_id}"
            results.append(f"{i}. {title}: {recipe_url}")

        return "\n".join(results)

    except requests.exceptions.RequestException as e:
        return f"Error retrieving recipe data: {e}"

@tool
def get_latest_news_gnews(country_code: str, page_size: int = 5):
    """
    Call this agent when the user wants to retrieve the latest news from a specific country.

    This function fetches the latest news articles from the specified country using the GNews API. 
    It returns the title, description, and URL of each news article in a human-readable format.

    Parameters:
    -----------
    country_code : str
        The ISO 3166-1 code of the country for which to fetch news (e.g., 'us' for the United States, 'ru' for Russia).

    page_size : int, optional
        The number of news articles to retrieve (default is 5).

    """
    
    api_key = "521ff62e451fa1f45e617ee1f962be6d"
    url = "https://gnews.io/api/v4/top-headlines"
    
    params = {
        "country": country_code,
        "token": api_key,
        "max": page_size
    }
    print(params)
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Constructing the result
        results = []
        if not data.get('articles'):
            return "No news articles found for the specified criteria."
        
        for item in data["articles"]:
            title = item["title"]
            description = item["description"]
            link = item["url"]
            results.append(f"{title}: {description} [Read more]({link})")
        
        return "\n".join(results)
    
    except requests.exceptions.RequestException as e:
        return f"Error retrieving news data: {e}"
    except KeyError:
        return "Error parsing news data. Please try again."



tools = [image_generation, yes_or_no, weather_agent, crypto_price, get_stock_price, get_exchange_rate,
         job_search_hh, recipe_search_by_ingredients, get_latest_news_gnews]

tool_node = ToolNode(tools)

model = ChatOpenAI(model="openai/gpt-4o-mini", temperature=1, base_url='https://api.vsegpt.ru/v1', max_retries=1).bind_tools(tools)
image_model = OpenAI(base_url="https://api.vsegpt.ru/v1")

# Define the function that determines whether to continue or not
def should_continue(state: MessagesState):
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END


# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", 'agent')

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable.
# Note that we're (optionally) passing the memory when compiling the graph
app = workflow.compile(checkpointer=checkpointer)


def get_answer(prompt: str) -> str:
    # Use the Runnable    
    final_state = app.invoke(
        {"messages": [HumanMessage(content=prompt)]},
        config={"configurable": {"thread_id": 42}}
    )
    return final_state["messages"][-1].content
