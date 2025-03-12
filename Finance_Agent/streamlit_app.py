from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import yfinance as yf
import os
from langchain.schema import HumanMessage
import streamlit as st
from rich.console import Console
from rich.table import Table

console = Console()


# Streamlit UI
st.title("💬 AI Agent 🤖 to help Stock Price Checker. 📈")
st.write("Type a message below or ask for a stock price by typing `stock <symbol>` to get stock message.")
st.write("Or free to chat with my Agent🙋‍♂️🗣️.")


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(model="mixtral-8x7b-32768")

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

def get_stock_price(ticker: str):

    try:
        st.write(f"**Fetching stock data for =>** `{ticker.upper()}`...")
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]

        st.write(f"📈 **Latest Closing Price**: **${price:.2f}**")

        # Display stock calendar details
        st.write("📅 **Stock Calendar Details:**")
        st.write(stock.calendar)  # Calendar info

        st.write("📊 **Analyst Price Targets:**")
        st.write(stock.analyst_price_target)  # Analyst target info

        st.write("📜 **Stock Price History (Last Day):**")
        st.dataframe(stock.history(period="1d"))  


        return f"The latest closing price of {ticker.upper()} is ${price:.2f}."
    except Exception as e:
        return f"Could not fetch stock data: {str(e)}"


def chatbot(user_input: str):
    user_content = user_input
    if 'stock' in user_content.lower():  
        ticker = user_content.split(" ")[1].upper()
        response = get_stock_price(ticker)
    else:
        response = llm.invoke([{"role": "user", "content": user_input}])

        return response.content if hasattr(response, "content") else str(response)


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()



# User input
user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get bot response
    response = chatbot(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display bot response
    with st.chat_message("assistant"):
        st.write(response)


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

