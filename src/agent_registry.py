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
        python_agents = self._load_python_agents()
        for p_agent_entry in python_agents: # Renamed to avoid confusion
            aid = p_agent_entry["id"]
            # Default values are now largely handled by the Agent base class's __init__
            # or by the get_metadata method structure.
            # We still might want to ensure all keys exist for consistency in the registry,
            # but the source of truth is agent's get_metadata().
            # Let's ensure core fields from metadata are present.
            final_entry = {
                "id": aid,
                "name": p_agent_entry.get("name", ""),
                "description": p_agent_entry.get("description", ""),
                "parameters": p_agent_entry.get("parameters", []),
                "example_queries": p_agent_entry.get("example_queries", []),
                "category": p_agent_entry.get("category", ""),
                "icon": p_agent_entry.get("icon", ""),
                "author": p_agent_entry.get("author", ""),
                "version": p_agent_entry.get("version", ""),
                "tags": p_agent_entry.get("tags", []),
                "request_example": p_agent_entry.get("request_example"),
                "response_example": p_agent_entry.get("response_example"),
                "function": p_agent_entry.get("function"), # This comes directly from agent_instance.respond
            }
            merged[aid] = final_entry  # 動態 agent 會覆蓋靜態 agent (if any static were to be added)
        
        # Ensure function is not None, though it should always be set by _load_python_agents
        for a in merged.values():
            if "function" not in a or a["function"] is None:
                # This case should ideally not happen if agents are loaded correctly
                print(f"[AgentRegistry] Warning: Agent {a.get('id')} loaded without a function.")
                a["function"] = None 
        
        # 依照 id 排序
        self._agents = {k: merged[k] for k in sorted(merged.keys())}

    def _load_python_agents(self):
        agent_list = []
        try:
            from src import agents # Should already be there
            from src.agents import Agent # Import the base Agent class
            for _, module_name, _ in pkgutil.iter_modules(agents.__path__):
                # Skip __init__.py itself if it doesn't define an agent class directly
                if module_name == "__init__":
                    continue
                try:
                    module = importlib.import_module(f"src.agents.{module_name}")
                    for attr in dir(module):
                        obj = getattr(module, attr)
                        # Check if it's a class, a subclass of our Agent (but not Agent itself)
                        if isinstance(obj, type) and issubclass(obj, Agent) and obj is not Agent:
                            try:
                                agent_instance = obj() # Instantiate the agent
                                metadata = agent_instance.get_metadata() # Get metadata from the instance
                                
                                # Construct the agent entry for the list
                                agent_entry = {
                                    "id": metadata["id"],
                                    "name": metadata["name"],
                                    "description": metadata["description"],
                                    "parameters": metadata["parameters"],
                                    "example_queries": metadata["example_queries"],
                                    "category": metadata["category"],
                                    "icon": metadata["icon"],
                                    "author": metadata["author"],
                                    "version": metadata["version"],
                                    "tags": metadata["tags"],
                                    "request_example": metadata.get("request_example"), # Use .get for optional fields
                                    "response_example": metadata.get("response_example"), # Use .get for optional fields
                                    "function": agent_instance.respond, # Store the instance's respond method
                                }
                                agent_list.append(agent_entry)
                            except Exception as e:
                                print(f"[AgentRegistry] Failed to load agent {attr} from {module_name}: {e}")
                                log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply=f"Failed to load agent {attr} from {module_name}: {e}", prefix="print_debug")
                except ImportError as e:
                    print(f"[AgentRegistry] Failed to import module {module_name}: {e}")
                    log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply=f"Failed to import module {module_name}: {e}", prefix="print_debug")
        except Exception as e:
            print(f"[AgentRegistry] General failure during agent loading: {e}")
            log_debug_info(tool_brief=None, system_prompt=None, user_prompt=None, llm_reply=f"General failure during agent loading: {e}", prefix="print_debug")
        return agent_list

    def list_agent_ids(self):
        return list(self._agents.keys())

    def get_agent(self, agent_id):
        return self._agents.get(agent_id)

_AGENT_REGISTRY = None

def get_agent_list() -> List[Dict]:
    global _AGENT_REGISTRY
    if _AGENT_REGISTRY is None:
        _AGENT_REGISTRY = AgentRegistry()
    return list(_AGENT_REGISTRY._agents.values()) 