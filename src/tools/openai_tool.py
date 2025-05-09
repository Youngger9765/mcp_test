import os
import openai

def openai_query_llm(instructions: str, input: str):
    """
    呼叫 OpenAI LLM，回傳生成內容。
    :param instructions: 系統指令
    :param input: 用戶輸入
    :return: LLM 回傳內容
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": input}
        ]
    )
    return response.choices[0].message.content 