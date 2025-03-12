from fastapi import FastAPI
import uvicorn
import subprocess
# from langchain.chat_models import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from pydantic import BaseModel
import re

App = FastAPI()
class QueryRequest(BaseModel):
    prompt: str

def running_python_code(code: str) -> str:
    # filtering the code
    code = re.sub(r"```[\w]*\n?|```", "", code).strip()
    try:
        # Save code to a temporary file
        with open("temp_script.py", "w") as f:
            f.write(code)

        # Execute the file in a controlled environment
        result = subprocess.run(
            ["python", "temp_script.py"], capture_output=True, text=True, timeout=5
        )

        # Return output or error
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error:\n{result.stderr}"

    except Exception as e:
        return f"Execution Error: {str(e)}"

def execute_javascript_code(code: str) -> str:
    code = re.sub(r"```(javascript|js)?\n", "", code, flags=re.IGNORECASE)  # Opening backticks
    code = re.sub(r"\n```", "", code)  # Closing backticks
    try:
        with open("temp_script.js", "w") as f:
            f.write(code)

        result = subprocess.run(
            ["node", "temp_script.js"], capture_output=True, text=True, timeout=5
        )

        return result.stdout if result.returncode == 0 else f"Error:\n{result.stderr}"

    except Exception as e:
        return f"Execution Error: {str(e)}"

execute_py_code= Tool(
    name="Execute Python Code",
    func=running_python_code,
    description="Executes Python code and returns the output.",
)
execute_js_code = Tool(
    name="Execute JavaScript Code",
    func=execute_javascript_code,
    description="Executes JavaScript code using Node.js and returns the output.",
)

llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key='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'
)
# llm = ChatOpenAI(model_name="gpt-4", temperature=0,api_key=openai_api_key )


@App.get("/")
def home():
    return {"message": "Hello World"}


@App.post("/chat")
def run_and_excute(req: QueryRequest):
    user_prompt = req.prompt
    tool =[]
    if 'python' in user_prompt.lower():
        tool.append(execute_py_code)
    elif 'javascript' in user_prompt.lower():
        tool.append(execute_js_code)
    
    try:
        agent = initialize_agent(
        tools=tool,  # Adding execution tool
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # Zero-shot reasoning for better code generation
        verbose=True  # Enable logging for debugging
     )
        res = agent.run(user_prompt)
        return {"response": res}
    except Exception as e:
        return {"response": str(e)}
    
if __name__ == "__main__":
    uvicorn.run(App, host="127.0.0.1", port=8000)

