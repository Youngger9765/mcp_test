import openai
from typing import List, Dict

def call_llm(model: str, messages: List[Dict], temperature: float = 0) -> str:
    """
    呼叫 OpenAI LLM，回傳 content 字串。
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API 錯誤: {e}") 