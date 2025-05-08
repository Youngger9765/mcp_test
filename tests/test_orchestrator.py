import os
from src.orchestrator import orchestrate

# 確保有 API key
assert os.getenv("OPENAI_API_KEY"), "請先設定 OPENAI_API_KEY 環境變數"

def test_all():
    prompts = [
        "幫我加 3 和 5",
        "查詢均一樹",
        "查詢均一主題",
        "查詢均一標題 分數"
    ]
    for prompt in prompts:
        print(f"Prompt: {prompt}")
        result = orchestrate(prompt)
        print(result)
        print("------")

if __name__ == "__main__":
    test_all() 