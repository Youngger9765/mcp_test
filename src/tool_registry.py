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
        "description": "兩數相加，回傳 a + b 的結果。",
        "category": "數學運算",
        "tags": ["運算", "加法"],
        "parameters": [
            {"name": "a", "type": "int", "description": "第一個加數，只能是 1, 2, 3", "required": True, "enum": [1, 2, 3]},
            {"name": "b", "type": "str", "description": "第二個加數，只能是三位數字字串", "required": False, "default": "000", "pattern": "^\\d{3}$"}
        ],
        "example_queries": [
            "a=1, b='123'",
            "a=2, b='456'"
        ],
        "function": add,
        "request_example": {"a": 1, "b": "123"},
        "response_example": {"result": 124}
    },
    {
        "id": "get_junyi_tree",
        "name": "均一樹查詢",
        "description": "查詢均一課程樹狀結構（預設只抓 1 層）",
        "category": "均一",
        "tags": ["教育", "課程樹"],
        "parameters": [
            {"name": "topic_id", "type": "str", "description": "均一課程樹的根 topic_id，格式如 root", "pattern": "^[a-zA-Z0-9_\-]+$"}
        ],
        "example_queries": [
            "查詢 root topic_id 的課程樹",
            "顯示數學科的課程結構"
        ],
        "function": get_junyi_tree,
        "request_example": {"topic_id": "root"},
        "response_example": {"type": "tree", "content": {"id": "root", "children": []}, "meta": {"topic_id": "root", "depth": 1}, "agent_id": "get_junyi_tree", "agent_name": "均一樹查詢", "error": None}
    },
    {
        "id": "get_junyi_topic",
        "name": "均一主題查詢",
        "description": "取得均一主題內容",
        "category": "均一",
        "tags": ["教育", "均一"],
        "parameters": [
            {"name": "topic_id", "type": "str", "description": "均一主題的 ID，格式如 root", "pattern": "^[a-zA-Z0-9_\-]+$"}
        ],
        "example_queries": [
            "查詢 topic_id 為 root 的主題內容"
        ],
        "function": get_junyi_topic,
        "request_example": {"topic_id": "root"},
        "response_example": {"type": "topic", "content": {"id": "root", "title": "數學"}, "meta": {"topic_id": "root"}, "agent_id": "get_junyi_topic", "agent_name": "均一主題查詢", "error": None}
    },
    {
        "id": "get_junyi_topic_by_title",
        "name": "均一主題標題查詢",
        "description": "依標題查詢均一主題，先查詢 topic_id，再查詢主題內容。",
        "category": "均一",
        "tags": ["教育", "標題查詢"],
        "parameters": [
            {"name": "title", "type": "str", "description": "主題標題關鍵字，僅允許中英文與數字", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]+$"}
        ],
        "example_queries": [
            "查詢標題為『分數』的主題內容"
        ],
        "function": get_junyi_topic_by_title,
        "request_example": {"title": "分數"},
        "response_example": {"type": "topic_by_title", "content": {"id": "math_002", "title": "分數"}, "meta": {"title": "分數", "topic_id": "math_002"}, "agent_id": "get_junyi_topic_by_title", "agent_name": "均一主題標題查詢", "error": None}
    },
    {
        "id": "agent_a_tool",
        "name": "A Agent 工具",
        "description": "查詢 A 網站摘要，適合查詢電影、影片剪輯等相關內容。",
        "category": "網路摘要",
        "tags": ["影片", "剪輯", "摘要"],
        "parameters": [
            {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 10~100 字元中英文數字空白", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]{10,100}$"}
        ],
        "example_queries": [
            "請幫我查一下影片剪輯教學",
            "什麼是 YouTuber？"
        ],
        "function": agent_a_tool,
        "request_example": {"input_text": "請幫我查一下影片剪輯教學"},
        "response_example": {"result": "這是影片剪輯教學的摘要..."}
    },
    {
        "id": "agent_b_tool",
        "name": "B Agent 工具",
        "description": "查詢 B 網站資料，適合查詢資安相關內容。",
        "category": "專業查詢",
        "tags": ["資安", "B網站"],
        "parameters": [
            {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 5~50 字元英文小寫與數字", "pattern": "^[a-z0-9 ]{5,50}$"}
        ],
        "example_queries": [
            "B 網站有什麼新消息？"
        ],
        "function": agent_b_tool,
        "request_example": {"input_text": "b 網站有什麼新消息？"},
        "response_example": {"result": "B 網站最新消息如下..."}
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