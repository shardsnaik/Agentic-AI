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

from typing import Annotated, Optional
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

console = Console()

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(model="mixtral-8x7b-32768")

# Modified State definition
class State(TypedDict):
    messages: Annotated[list, add_messages]
    requires_approval: Optional[bool]
    pending_ticker: Optional[str]

# Initialize graph
graph_builder = StateGraph(State)

def get_stock_price(ticker: str):
    """Fetch stock price from Yahoo Finance (Human-validated version)"""
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return f"✅ Validated: {ticker.upper()} closing price is ${price:.2f}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def human_approval(state: State):
    """Node for human validation"""
    ticker = state["pending_ticker"]
    console.print(f"\n[bold yellow]SYSTEM:[/] Validate stock lookup for {ticker}", style="red")
    decision = console.input("[bold yellow]Approve? (y/n): [/]").lower()
    
    return {
        "requires_approval": False,
        "messages": [
            SystemMessage(content=f"Human {'approved' if decision == 'y' else 'rejected'} {ticker} lookup")
        ],
        "pending_ticker": None
    }

def chatbot(state: State):
    """Modified chatbot with approval checks"""
    user_input = state["messages"][-1].content
    
    if state.get("requires_approval"):
        # Handle post-approval logic
        if "approved" in state["messages"][-1].content:
            response = get_stock_price(state["pending_ticker"])
        else:
            response = "❌ Stock lookup canceled by human"
        return {"messages": [AIMessage(content=response)]}
    
    if 'stock' in user_input.lower():
        ticker = user_input.split()[-1].upper()
        return {
            "requires_approval": True,
            "pending_ticker": ticker,
            "messages": [AIMessage(content=f"Requesting human approval for {ticker} lookup...")]
        }
    
    # Normal LLM response
    return {"messages": [llm.invoke(state["messages"]).content]}

# Add nodes and edges
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human_approval", human_approval)

graph_builder.add_edge(START, "chatbot")

# Conditional edges
def route_decision(state: State):
    if state.get("requires_approval"):
        return "human_approval"
    return END

graph_builder.add_conditional_edges(
    "chatbot",
    route_decision
)

graph_builder.add_edge("human_approval", "chatbot")
graph = graph_builder.compile()

# Modified streaming function
def stream_graph_updates(user_input: str):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("User", style="bold cyan", justify="right")
    table.add_column("System", style="yellow", justify="left")
    table.add_column("Assistant", style="bold green", justify="left")

    for event in graph.stream({"messages": [HumanMessage(content=user_input)]}):
        for key, value in event.items():
            last_msg = value["messages"][-1]
            
            if isinstance(last_msg, SystemMessage):
                table.add_row("", f"[System] {last_msg.content}", "")
            else:
                user_display = user_input if key == "chatbot" else ""
                assistant_display = last_msg if not isinstance(last_msg, HumanMessage) else ""
                table.add_row(user_display, "", str(assistant_display))

    console.print(table)

# Run loop remains the same
while True:
    try:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except KeyboardInterrupt:
        print("\nOperation canceled by user")
        break