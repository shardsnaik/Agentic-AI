from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import yfinance as yf
import os

# Load environment variables
load_dotenv()
API = os.getenv("Anthropic_API_KEY")

# Initialize LLM
llm = ChatGroq(model="mixtral-8x7b-32768")

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def get_stock_price(ticker: str):
    """Fetch stock price from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"The latest closing price of {ticker.upper()} is ${price:.2f}."
    except Exception as e:
        return f"Could not fetch stock data: {str(e)}"

from langchain.schema import HumanMessage

def chatbot(state: State):
    user_message = state["messages"][-1]  # Get last message object
    
    if isinstance(user_message, HumanMessage):
        user_content = user_message.content  # Extract content
    else:
        user_content = user_message["content"]  # Fallback for dict-based messages
    
    # Check if user asks about stock price
    if user_content.lower().startswith("stock "):  
        ticker = user_content.split(" ")[1].upper()
        response = get_stock_price(ticker)
    else:
        response = llm.invoke(state["messages"]).content  

    return {"messages": [HumanMessage(content=response)]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1])

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
