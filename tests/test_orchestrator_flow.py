import pytest
from src.parameter_extraction import filter_available_tools

def test_orchestrator_flow():
    agent_list = [
        {
            "id": "add",
            "name": "加法工具",
            "parameters": [
                {"name": "a", "type": "int", "required": True},
                {"name": "b", "type": "int", "required": True}
            ]
        },
        {
            "id": "topic_agent",
            "name": "主題查詢",
            "parameters": [
                {"name": "topic_id", "type": "str", "required": True}
            ]
        },
        {
            "id": "dummy",
            "name": "無參數工具",
            "parameters": []
        }
    ]
    query = "請幫我加 3 跟 5，並查詢 topic_id 為 root 的主題"
    # 模擬 orchestrator pipeline
    filter_result = filter_available_tools(query, agent_list)
    available_agents = [a for a in filter_result if a["available"]]
    trace = {
        "user_query": query,
        "filter_result": filter_result
    }
    # 驗證 trace 結構
    assert trace["user_query"] == query
    assert len(trace["filter_result"]) == 3
    # 驗證可用 agent
    add = next(r for r in filter_result if r["agent_id"] == "add")
    topic = next(r for r in filter_result if r["agent_id"] == "topic_agent")
    dummy = next(r for r in filter_result if r["agent_id"] == "dummy")
    assert add["available"] is True
    assert topic["available"] is True
    assert dummy["available"] is True
    assert add["extracted_params"] == {"a": 3, "b": 5}
    assert topic["extracted_params"] == {"topic_id": "root"} 