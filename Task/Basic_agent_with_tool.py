from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import yfinance as yf
import os
from langchain.schema import HumanMessage

from rich.console import Console
from rich.table import Table

console = Console()

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(model="mixtral-8x7b-32768")

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def get_stock_price(ticker: str):
    """Fetch stock price from Yahoo Finance."""
    try:
        print(ticker)
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        print("printing stock callender details\n")
        print(stock.calendar)
        print()
        print(stock.analyst_price_targets)
        print("Analysis History\n")
        print(stock.history(period="1d"))

        return f"The latest closing price of {ticker.upper()} is ${price:.2f}."
    except Exception as e:
        return f"Could not fetch stock data: {str(e)}"


def chatbot(state: State):
    user_content = state["messages"][-1].content
    if 'stock' in user_content.lower():  
        ticker = user_content.split(" ")[1].upper()
        response = get_stock_price(ticker)
    else:
        response = llm.invoke(state["messages"]).content  

    return {"messages": [HumanMessage(content=response)]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# LangGraph Inbuild fuction!!
# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1])


# Modified function to use the graph object to get the response from the chatbot using rich library

def stream_graph_updates(user_input: str):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("User", style="bold cyan", justify="right")
    table.add_column("Assistant", style="bold green", justify="left")

    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            assistant_reply = value["messages"][-1].content
            table.add_row(user_input, assistant_reply)

    console.print(table)

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
