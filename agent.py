from phi.agent import Agent 
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
import os
from dotenv import load_dotenv

load_dotenv()

web_search_agent = Agent(
    name = 'web_search_agent',
    role='searcing the web',
    model= Groq(id='llama-3.2-90b-vision-preview'),
    tools=[DuckDuckGo()],
    instructions=['show sources'],
    show_tool_calls=True,
    markdown=True
)

financial_agent = Agent(
    name='financial_agent',
    model = Groq(id='llama-3.2-90b-vision-preview'),
    tools=[YFinanceTools(
        stock_price=True,
        analyst_recommendations=True,
        stock_fundamentals=True,
        company_info=True,
        
    )],
    instructions=['show sources'],
    show_tool_calls=True,
    markdown=True
    )

multi_ai_agent = Agent(
    team=[web_search_agent, financial_agent],
    # model= Groq(id='llama-3.2-90b-vision-preview'), # If model isn't specified, the model use openai
    instructions=['show sources', 'use table to show data'],
    show_tool_calls=True,
    markdown=True       
)

multi_ai_agent.print_response(
    'summaries analyst responce form agentic AI',stream=True
)

# In any case code failed to load api key then just run this code in cmd
# --> setx GROQ_API_KEY fhuerfheukfnerkjvbejk vev ejve kvjevejkvnejkvej