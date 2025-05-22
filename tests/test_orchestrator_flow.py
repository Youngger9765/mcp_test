import pytest
from src.parameter_extraction import filter_available_tools

def test_orchestrator_flow():
    agent_list = [
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
    assert len(trace["filter_result"]) == 2
    # 驗證可用 agent
    topic = next(r for r in filter_result if r["agent_id"] == "topic_agent")
    dummy = next(r for r in filter_result if r["agent_id"] == "dummy")
    assert topic["available"] is True
    assert dummy["available"] is True
    assert topic["extracted_params"] == {"topic_id": "root"} 