import openai
from dotenv import load_dotenv
import os
from src.tools.openai_tool import openai_query_llm

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 用 LLM 傳遞 general 的 query
def query(instructions: str, input: str, model: str = "gpt-4.1-mini"):
    response = client.responses.create(
        instructions=instructions,
        model=model,
        input=input
    )
    return response.output_text

class OpenAIAgent:
    id = "openai_agent"
    name = "OpenAI LLM 代理"
    description = "查詢 OpenAI LLM，回傳模型生成內容。"
    parameters = [
        {"name": "instructions", "type": "str"},
        {"name": "input", "type": "str"}
    ]

    def respond(self, instructions: str, input: str):
        return openai_query_llm(instructions=instructions, input=input)
