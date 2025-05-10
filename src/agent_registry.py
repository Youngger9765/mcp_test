import os
import importlib
import pkgutil

class AgentRegistry:
    def __init__(self):
        # 只載入 Python agents
        python_agents = self._load_python_agents()
        merged = {}
        # 合併 Python agents
        for p in python_agents:
            aid = p["id"]
            # Python agent 也補齊欄位
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
            merged[aid] = dict(p)
        for a in merged.values():
            if "function" not in a:
                a["function"] = None
        self._agents = merged

    def _load_python_agents(self):
        agent_list = []
        try:
            import agents
            for _, module_name, _ in pkgutil.iter_modules(agents.__path__):
                module = importlib.import_module(f"agents.{module_name}")
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
            pass  # 若 agents 目錄不存在或有錯誤，直接略過
        return agent_list

    def list_agent_ids(self):
        return list(self._agents.keys())

    def get_agent(self, agent_id):
        return self._agents.get(agent_id) 