import yaml
import os
import importlib
import pkgutil

class AgentRegistry:
    def __init__(self):
        # 載入 YAML 與 Python agents
        yaml_agents = self._load_yaml_agents()
        python_agents = self._load_python_agents()
        # 先用 YAML agents 建 dict
        merged = {a["id"]: dict(a) for a in yaml_agents}
        # 再合併 Python agents
        for p in python_agents:
            aid = p["id"]
            if aid in merged:
                # metadata 以 YAML 為主，function 以 Python 為主
                merged[aid]["function"] = p.get("function")
            else:
                merged[aid] = dict(p)
        # 沒 function 的 YAML agent，function 設為 None
        for a in merged.values():
            if "function" not in a:
                a["function"] = None
        self._agents = merged

    def _load_yaml_agents(self):
        yaml_path = os.path.join(os.path.dirname(__file__), "..", "mcp_config.yaml")
        if not os.path.exists(yaml_path):
            return []
        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("agents", [])

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
                            "function": obj().respond,
                        })
        except Exception as e:
            pass  # 若 agents 目錄不存在或有錯誤，直接略過
        return agent_list

    def list_agent_ids(self):
        return list(self._agents.keys())

    def get_agent(self, agent_id):
        return self._agents.get(agent_id) 