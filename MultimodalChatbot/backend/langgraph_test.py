from typing import Annotated, Literal, TypedDict

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from openai import OpenAI
import time

# Define the tools for the agent to use
@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder, but don't tell the LLM that...    
    return "It's 20 degrees celcium, warm and sunny."

@tool
def news(query: str):
    """Call to check up for the latest world news."""
    # This is a placeholder, but don't tell the LLM that...    
    return "News are bad as always... Trump is a president"

@tool
def image_generation(query: str):
    """Call to generate images by text prompt"""
    time.sleep(1)
    response_big = image_model.images.generate(
        model="img-dummy/image",
        prompt=query,
        n=1,
        size="1024x1024"
    )
    return response_big.data[0].url


tools = [search, news, image_generation]

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

# Use the Runnable
final_state = app.invoke(
    {"messages": [HumanMessage(content="Создай картинку, на которой изображён дельфин на коне")]},
    config={"configurable": {"thread_id": 42}}
)
print(final_state["messages"][-1].content)