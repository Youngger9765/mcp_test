# integration test for chat/memory flow

import re
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_integration_chat_memory():
    """
    integration test: chat + 記憶
    1. analyze_intent: i am James -> intent=chat
    2. chat: i am James
    3. analyze_intent: what is my name (帶入前面對話) -> intent=history_answer
    4. history_answer: what is my name
    """
    resp = client.post("/analyze_intent", json={"prompt": "i am James"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "chat"
    assert data["suggested_api"] == "/chat"

    history = [
        {"role": "user", "content": "i am James"}
    ]
    resp = client.post("/chat", json={"history": history})
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "chat"
    assert re.search(r"James", data["reply"], re.IGNORECASE)

    history.append({"role": "assistant", "content": data["reply"]})
    history.append({"role": "user", "content": "what is my name"})
    prompt = "\n".join([f'{h["role"]}: {h["content"]}' for h in history])
    resp = client.post("/analyze_intent", json={"prompt": prompt})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "history_answer"
    # 不再檢查 suggested_api，因為 server 只對部分 intent 給 api

    resp = client.post("/history_answer", json={"history": history})
    assert resp.status_code == 200
    data = resp.json()
    assert "James" in data["answer"] or "James" in data.get("reason", "")


def test_integration_math_multi_turn():
    """
    integration test: 多輪查詢分數的加減法
    1. analyze_intent: tool_call
    2. agent/single_turn_dispatch: 取得第一步 history
    3. agent/multi_turn_step: 連續呼叫直到 action=finish
    4. 檢查過程中至少有兩輪 call_tool，且有多輪（history 長度 > 2），最後有 finish。
    5. 新增：過程中至少有一輪呼叫到 get_junyi_tree 或 get_junyi_topic。
    """
    resp = client.post("/analyze_intent", json={"prompt": "請幫我查一下分數的加減法"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent"] == "tool_call"
    assert data["suggested_api"] in ["/agent/single_turn_dispatch", "/agent/multi_turn_step"]

    resp = client.post("/agent/single_turn_dispatch", json={"prompt": "請幫我查一下分數的加減法"})
    assert resp.status_code == 200
    data = resp.json()
    assert "tool" in data and "input" in data and "results" in data
    history = [{
        "tool_id": data["tool"],
        "parameters": data["input"],
        "result": data["results"][0],
        "reason": "第一步查詢"
    }]
    query = "請幫我查一下分數的加減法"
    max_steps = 8
    called_tool_count = 0
    finished = False
    used_junyi = False
    for _ in range(max_steps):
        resp = client.post("/agent/multi_turn_step", json={"history": history, "query": query})
        assert resp.status_code == 200
        data = resp.json()
        assert data["action"] in ["call_tool", "finish"]
        if data["action"] == "call_tool":
            called_tool_count += 1
            step = data["step"]
            history.append(step)
            if step.get("tool_id") in ["get_junyi_tree", "get_junyi_topic"]:
                used_junyi = True
        elif data["action"] == "finish":
            finished = True
            break
    assert called_tool_count >= 2 and len(history) > 2 and finished
    assert used_junyi, "過程中必須至少呼叫一次 get_junyi_tree 或 get_junyi_topic 工具" 