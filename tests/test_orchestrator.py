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

def test_orchestrator_keyword_routing(monkeypatch):
    from src.agent_registry import AgentRegistry
    from src.orchestrator import Orchestrator

    registry = AgentRegistry()
    orchestrator = Orchestrator(registry)

    # 關鍵字判斷
    agent_id, params = orchestrator.route("這是一個資安問題")
    assert agent_id == "agent_b"
    assert "input_text" in params

    agent_id, params = orchestrator.route("請問有什麼電影推薦？")
    assert agent_id == "agent_a"
    assert "input_text" in params

    # fallback
    agent_id, params = orchestrator.route("這是一個無法判斷的問題")
    assert agent_id is None
    assert params == {}

if __name__ == "__main__":
    test_all() 