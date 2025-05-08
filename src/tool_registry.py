"""
工具註冊層（Tool Registry Layer）
統一管理所有工具（tool/agent）的 metadata，供 orchestrator/LLM 查詢。
"""

from typing import List, Dict, Callable
from src.tools import add, get_junyi_tree, get_junyi_topic, get_junyi_topic_by_title, agent_a_tool, agent_b_tool


def get_tool_list() -> List[Dict]:
    """
    回傳所有工具的 metadata list。
    每個工具包含：id、name、description、parameters、function ref。
    """
    tool_list = [
        {
            "id": "add",
            "name": "加法工具",
            "description": add.__doc__ or "兩數相加",
            "parameters": [
                {"name": "a", "type": "int"},
                {"name": "b", "type": "int"}
            ],
            "function": add
        },
        {
            "id": "get_junyi_tree",
            "name": "均一樹查詢",
            "description": get_junyi_tree.__doc__ or "查詢均一課程樹狀結構",
            "parameters": [
                {"name": "topic_id", "type": "str"}
            ],
            "function": get_junyi_tree
        },
        {
            "id": "get_junyi_topic",
            "name": "均一主題查詢",
            "description": get_junyi_topic.__doc__ or "查詢均一主題內容",
            "parameters": [
                {"name": "topic_id", "type": "str"}
            ],
            "function": get_junyi_topic
        },
        {
            "id": "get_junyi_topic_by_title",
            "name": "均一主題標題查詢",
            "description": get_junyi_topic_by_title.__doc__ or "依標題查詢均一主題",
            "parameters": [
                {"name": "title", "type": "str"}
            ],
            "function": get_junyi_topic_by_title
        },
        {
            "id": "agent_a_tool",
            "name": "A Agent 工具",
            "description": agent_a_tool.__doc__ or "查詢 A 網站摘要，電影、影片剪輯 相關",
            "parameters": [
                {"name": "input_text", "type": "str"}
            ],
            "function": agent_a_tool
        },
        {
            "id": "agent_b_tool",
            "name": "B Agent 工具",
            "description": agent_b_tool.__doc__ or "查詢 B 網站資料，資安相關",
            "parameters": [
                {"name": "input_text", "type": "str"}
            ],
            "function": agent_b_tool
        },
    ]
    return tool_list 