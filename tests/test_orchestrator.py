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

def test_orchestrator_llm_strategy(monkeypatch):
    from src.agent_registry import AgentRegistry
    from src.orchestrator import Orchestrator

    registry = AgentRegistry()

    # 模擬 LLM function，根據 prompt 回傳 agent id
    def fake_llm_strategy(prompt, context=None):
        if "AI" in prompt:
            return "agent_b", {"input_text": prompt}
        return None, {}

    orchestrator = Orchestrator(registry, strategy=fake_llm_strategy)

    # LLM 能判斷
    agent_id, params = orchestrator.route("這是一個AI相關的問題")
    assert agent_id == "agent_b"
    assert "input_text" in params

    # LLM 無法判斷，fallback 到 keyword
    orchestrator.strategy = None  # 讓 Orchestrator fallback 到內建 keyword_strategy
    agent_id, params = orchestrator.route("請問有什麼電影推薦？")
    assert agent_id == "agent_a"
    assert "input_text" in params

def test_orchestrator_multi_turn_strategy(monkeypatch):
    from src.agent_registry import AgentRegistry
    from src.orchestrator import Orchestrator

    registry = AgentRegistry()

    # 假設這是 plug-in 的多輪推理策略
    def fake_multi_turn_strategy(prompt, context=None):
        # context 是查詢歷程
        history = context or []
        if not history:
            return "agent_a", {"input_text": prompt}
        elif len(history) == 1:
            return "agent_b", {"input_text": "根據A的結果再查B"}
        else:
            return None, {}

    orchestrator = Orchestrator(registry, strategy=fake_multi_turn_strategy)

    # 第一步
    agent_id, params = orchestrator.route("我要查兩步", context=[])
    assert agent_id == "agent_a"
    # 第二步
    agent_id, params = orchestrator.route("我要查兩步", context=[{"tool_id": "agent_a"}])
    assert agent_id == "agent_b"
    # 結束
    agent_id, params = orchestrator.route("我要查兩步", context=[{"tool_id": "agent_a"}, {"tool_id": "agent_b"}])
    assert agent_id is None

def test_orchestrator_logging(monkeypatch, capsys):
    from src.agent_registry import AgentRegistry
    from src.orchestrator import Orchestrator, log_call

    registry = AgentRegistry()

    @log_call
    def dummy_strategy(prompt, context=None):
        return "agent_a", {"input_text": prompt}

    orchestrator = Orchestrator(registry, strategy=dummy_strategy)
    agent_id, params = orchestrator.route("測試 log")
    assert agent_id == "agent_a"
    # 檢查 log 是否有輸出
    captured = capsys.readouterr()
    assert "[LOG] Called dummy_strategy" in captured.out

def test_orchestrator_session_context_management():
    from src.agent_registry import AgentRegistry
    from src.orchestrator import Orchestrator

    registry = AgentRegistry()
    orchestrator = Orchestrator(registry)

    # 模擬 session/context 儲存
    session_store = {}

    def get_context(session_id):
        return session_store.get(session_id, {"history": []})

    def save_context(session_id, context):
        session_store[session_id] = context

    # 用戶A第一次查詢
    session_id_a = "userA"
    prompt_a1 = "我想查電影"
    context_a = get_context(session_id_a)
    agent_id, params = orchestrator.route(prompt_a1, context=context_a)
    assert agent_id == "agent_a"
    # 更新 context
    context_a["history"].append({"user": prompt_a1, "agent": agent_id})
    save_context(session_id_a, context_a)

    # 用戶B第一次查詢
    session_id_b = "userB"
    prompt_b1 = "我想查資安"
    context_b = get_context(session_id_b)
    agent_id, params = orchestrator.route(prompt_b1, context=context_b)
    assert agent_id == "agent_b"
    context_b["history"].append({"user": prompt_b1, "agent": agent_id})
    save_context(session_id_b, context_b)

    # 用戶A第二次查詢，context/history 不受 B 影響
    prompt_a2 = "再查一次電影"
    context_a = get_context(session_id_a)
    agent_id, params = orchestrator.route(prompt_a2, context=context_a)
    assert agent_id == "agent_a"
    assert len(context_a["history"]) == 1
    assert context_a["history"][0]["user"] == "我想查電影"

if __name__ == "__main__":
    test_all() 