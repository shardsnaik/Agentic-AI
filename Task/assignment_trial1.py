# import streamlit as st

# def get_agent_response(user_input):
#     responses = {
#         "hello": "Hi! How can I help you today?",
#         "how are you": "I'm just a bot, but thanks for asking!",
#         "bye": "Goodbye! Have a great day!",
#     }
#     return responses.get(user_input.lower(), "I didn't understand that. Try 'hello', 'how are you', or 'bye'.")

# # Streamlit app UI re

# st.title("AI Assistant")
# user_in  = st.text_input('you:=>', placeholder='Typer message here')

# if st.button('send'):
#         response = get_agent_response(user_in)
#         st.write(f"**Agent:** {response}")
# else:
#      st.warning("Please type a message.")


# Sample agent usign LangGraph


# from typing import Annotated

# from typing_extensions import TypedDict

# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages

# # from langchain_anthropic import ChatAnthropic
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv
# import os
# load_dotenv()
# API = os.getenv("Anthropic_API_KEY")
# # llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=API)
# llm = ChatGroq(model="mixtral-8x7b-32768")

# class State(TypedDict):
#     # Messages have the type "list". The `add_messages` function
#     # in the annotation defines how this state key should be updated
#     # (in this case, it appends messages to the list, rather than overwriting them)
#     messages: Annotated[list, add_messages]


# graph_builder = StateGraph(State)

# def chatbot(state: State):
#     return {"messages": [llm.invoke(state["messages"])]}


# # The first argument is the unique node name
# # The second argument is the function or object that will be called whenever
# # the node is used.
# graph_builder.add_node("chatbot", chatbot)
# graph_builder.add_edge(START, "chatbot")
# graph_builder.add_edge("chatbot", END)
# graph = graph_builder.compile()


# def stream_graph_updates(user_input: str):
#     for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break

#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break

# Testing Yfinace 

import yfinance as yf
import requests

# try:
#     dat = yf.Ticker("MSFT")
#     print(dat.calendar)
#     # print(dat.info)
#     print(dat.analyst_price_targets)
#     print(dat.quarterly_income_stmt)
#     print(dat.history(period="1d"))
# except requests.exceptions.ConnectionError:
#     print("Failed to connect to Yahoo Finance. Please check your internet connection and try again.")
user_content = input('Type Here:')

if 'stock' in user_content.lower():  
        print(user_content.split(" ")[1])
        ticker = user_content.split(" ")[1].upper()
        dat = yf.Ticker(ticker)
        print(dat.calendar)
    # print(dat.info)
        print(dat.analyst_price_targets)
        print(dat.quarterly_income_stmt)
        print(dat.history(period="1d"))
else:
    print("No stock data")