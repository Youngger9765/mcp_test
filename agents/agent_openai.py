import openai
from dotenv import load_dotenv
import os

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
