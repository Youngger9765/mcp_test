"""
工具註冊層（Tool Registry Layer）
統一管理所有工具（tool/agent）的 metadata，供 orchestrator/LLM 查詢。
"""

import yaml
from typing import List, Dict, Callable
from src.tools import add, get_junyi_tree, get_junyi_topic, get_junyi_topic_by_title, agent_a_tool, agent_b_tool
import os

def load_yaml_tools(yaml_path="mcp_config.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("agents", [])

# Python tools metadata
PYTHON_TOOLS = [
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

def get_tool_list() -> List[Dict]:
    """
    回傳所有工具的 metadata list，合併 YAML 與 Python。
    YAML 為主，function 以 Python 為主。
    """
    yaml_tools = load_yaml_tools()
    python_tool_dict = {t["id"]: t for t in PYTHON_TOOLS}
    # 合併：YAML 為主，function 以 Python 為主
    merged = {}
    for y in yaml_tools:
        py = python_tool_dict.get(y["id"])
        if py:
            merged_tool = {**py, **y}
            merged_tool["function"] = py["function"]
            merged[y["id"]] = merged_tool
        else:
            continue
    for pid, ptool in python_tool_dict.items():
        if pid not in merged:
            merged[pid] = ptool
    return list(merged.values()) 