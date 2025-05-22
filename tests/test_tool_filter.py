import pytest
from src.parameter_extraction import extract_parameters_from_query, get_required_params, filter_available_tools
# filter_available_tools 已正確 import

def test_filter_available_tools_scenario():
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
    result = filter_available_tools(query, agent_list)
    topic = next(r for r in result if r["agent_id"] == "topic_agent")
    dummy = next(r for r in result if r["agent_id"] == "dummy")
    assert topic["available"] is True
    assert dummy["available"] is True  # 無參數預設 available
    assert topic["extracted_params"] == {"topic_id": "root"}

def test_filter_available_tools_scenario_fenshu():
    agent_list = [
        {
            "id": "topic_agent",
            "name": "主題查詢",
            "parameters": [
                {"name": "topic_id", "type": "str", "required": True}
            ]
        }
    ]
    query = "請幫我查一下分數的加減法"
    result = filter_available_tools(query, agent_list)
    topic = next(r for r in result if r["agent_id"] == "topic_agent")
    assert topic["available"] is True
    assert topic["extracted_params"] is not None 

def test_query_chapter_not_add():
    agent_list = [
        {
            "id": "topic_agent",
            "name": "主題查詢",
            "parameters": [
                {"name": "topic_id", "type": "str", "required": True}
            ]
        }
    ]
    query = "我想要查整數加法的章節（ex: 1+3）"
    result = filter_available_tools(query, agent_list)
    topic = next(r for r in result if r["agent_id"] == "topic_agent")
    assert topic["available"] is True
    assert topic["extracted_params"] is not None 