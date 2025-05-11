import os
import importlib
import pkgutil
from typing import List, Dict
from log_debug_info import log_debug_info

# 靜態註冊的 agent（原 tool_registry.py 內容）
# PYTHON_TOOLS = [
#     {
#         "id": "add",
#         "name": "加法工具",
#         "description": "兩數相加，回傳 a + b 的結果。",
#         "category": "數學運算",
#         "tags": ["運算", "加法"],
#         "parameters": [
#             {"name": "a", "type": "int", "description": "第一個加數，只能是 1, 2, 3", "required": True, "enum": [1, 2, 3]},
#             {"name": "b", "type": "str", "description": "第二個加數，只能是三位數字字串", "required": False, "default": "000", "pattern": "^\\d{3}$"}
#         ],
#         "example_queries": [
#             "a=1, b='123'",
#             "a=2, b='456'"
#         ],
#         "function": AddAgent().respond,
#         "request_example": {"a": 1, "b": "123"},
#         "response_example": {"result": 124}
#     },
#     {
#         "id": "get_junyi_tree",
#         "name": "均一樹查詢",
#         "description": "查詢均一課程樹狀結構（預設只抓 1 層）",
#         "category": "均一",
#         "tags": ["教育", "課程樹"],
#         "parameters": [
#             {"name": "topic_id", "type": "str", "description": "均一課程樹的根 topic_id，格式如 root", "pattern": "^[a-zA-Z0-9_\-]+$"}
#         ],
#         "example_queries": [
#             "查詢 root topic_id 的課程樹",
#             "顯示數學科的課程結構"
#         ],
#         "function": JunyiTreeAgent().respond,
#         "request_example": {"topic_id": "root"},
#         "response_example": {"type": "tree", "content": {"id": "root", "children": []}, "meta": {"topic_id": "root", "depth": 1}, "agent_id": "get_junyi_tree", "agent_name": "均一樹查詢", "error": None}
#     },
#     {
#         "id": "get_junyi_topic",
#         "name": "均一主題查詢",
#         "description": "取得均一主題內容",
#         "category": "均一",
#         "tags": ["教育", "均一"],
#         "parameters": [
#             {"name": "topic_id", "type": "str", "description": "均一主題的 ID，格式如 root", "pattern": "^[a-zA-Z0-9_\-]+$"}
#         ],
#         "example_queries": [
#             "查詢 topic_id 為 root 的主題內容"
#         ],
#         "function": JunyiTopicAgent().respond,
#         "request_example": {"topic_id": "root"},
#         "response_example": {"type": "topic", "content": {"id": "root", "title": "數學"}, "meta": {"topic_id": "root"}, "agent_id": "get_junyi_topic", "agent_name": "均一主題查詢", "error": None}
#     },
#     {
#         "id": "get_junyi_topic_by_title",
#         "name": "均一主題標題查詢",
#         "description": "依標題查詢均一主題，先查詢 topic_id，再查詢主題內容。",
#         "category": "均一",
#         "tags": ["教育", "標題查詢"],
#         "parameters": [
#             {"name": "title", "type": "str", "description": "主題標題關鍵字，僅允許中英文與數字", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]+$"}
#         ],
#         "example_queries": [
#             "查詢標題為『分數』的主題內容"
#         ],
#         "function": JunyiTopicByTitleAgent().respond,
#         "request_example": {"title": "分數"},
#         "response_example": {"type": "topic_by_title", "content": {"id": "math_002", "title": "分數"}, "meta": {"title": "分數", "topic_id": "math_002"}, "agent_id": "get_junyi_topic_by_title", "agent_name": "均一主題標題查詢", "error": None}
#     },
#     {
#         "id": "agent_a_tool",
#         "name": "A Agent 工具",
#         "description": "查詢 A 網站摘要，適合查詢電影、影片剪輯等相關內容。",
#         "category": "網路摘要",
#         "tags": ["影片", "剪輯", "摘要"],
#         "parameters": [
#             {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 10~100 字元中英文數字空白", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]{10,100}$"}
#         ],
#         "example_queries": [
#             "請幫我查一下影片剪輯教學",
#             "什麼是 YouTuber？"
#         ],
#         "function": AAgent().respond,
#         "request_example": {"input_text": "請幫我查一下影片剪輯教學"},
#         "response_example": {"result": "這是影片剪輯教學的摘要..."}
#     },
#     {
#         "id": "agent_b_tool",
#         "name": "B Agent 工具",
#         "description": "查詢 B 網站資料，適合查詢資安相關內容。",
#         "category": "專業查詢",
#         "tags": ["資安", "B網站"],
#         "parameters": [
#             {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 5~50 字元英文小寫與數字", "pattern": "^[a-z0-9 ]{5,50}$"}
#         ],
#         "example_queries": [
#             "B 網站有什麼新消息？"
#         ],
#         "function": BAgent().respond,
#         "request_example": {"input_text": "b 網站有什麼新消息？"},
#         "response_example": {"result": "B 網站最新消息如下..."}
#     },
# ]

class AgentRegistry:
    def __init__(self):
        merged = {}
        # 合併自動掃描 agents 目錄
        print("[AgentRegistry] 動態模式")
        log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply="[AgentRegistry] 動態模式", prefix="print_debug")
        python_agents = self._load_python_agents()
        for p in python_agents:
            aid = p["id"]
            for field, default in [
                ("example_queries", []),
                ("category", ""),
                ("icon", ""),
                ("author", ""),
                ("version", ""),
                ("tags", []),
            ]:
                if field not in p:
                    p[field] = default
            merged[aid] = dict(p)  # 動態 agent 會覆蓋靜態 agent
        for a in merged.values():
            if "function" not in a:
                a["function"] = None
        # 依照 id 排序
        self._agents = {k: merged[k] for k in sorted(merged.keys())}

    def _load_python_agents(self):
        agent_list = []
        try:
            from src import agents
            print("[AgentRegistry] agents module path:", agents.__path__)
            log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply=f"agents module path: {agents.__path__}", prefix="print_debug")
            for _, module_name, _ in pkgutil.iter_modules(agents.__path__):
                module = importlib.import_module(f"src.agents.{module_name}")
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if isinstance(obj, type) and hasattr(obj, "respond") and hasattr(obj, "id"):
                        agent_list.append({
                            "id": getattr(obj, "id"),
                            "name": getattr(obj, "name", obj.__name__),
                            "description": getattr(obj, "description", ""),
                            "parameters": getattr(obj, "parameters", []),
                            "example_queries": getattr(obj, "example_queries", []),
                            "category": getattr(obj, "category", ""),
                            "icon": getattr(obj, "icon", ""),
                            "author": getattr(obj, "author", ""),
                            "version": getattr(obj, "version", ""),
                            "tags": getattr(obj, "tags", []),
                            "function": obj().respond,
                        })
        except Exception as e:
            print("[AgentRegistry] import agents failed:", e)
            log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply=f"import agents failed: {e}", prefix="print_debug")
        return agent_list

    def list_agent_ids(self):
        return list(self._agents.keys())

    def get_agent(self, agent_id):
        return self._agents.get(agent_id)

def get_agent_list() -> List[Dict]:
    """
    回傳所有 agent metadata（靜態+自動掃描），依 id 排序。
    """
    return [AgentRegistry()._agents[k] for k in sorted(AgentRegistry()._agents.keys())] 