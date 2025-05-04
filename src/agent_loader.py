import yaml
import importlib
from src.agent_registry import get_python_agents

def import_from_string(dotted_path):
    """
    支援 'src.agent_registry.AgentA().respond' 這種寫法
    """
    if "()" in dotted_path:
        dotted_path, method = dotted_path.split("().")
        module_path, class_name = dotted_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        instance = cls()
        return getattr(instance, method)
    else:
        module_path, attr = dotted_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, attr)

def load_agents_from_yaml(yaml_path="mcp_config.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    agents = []
    yaml_ids = set()
    for agent in config["agents"]:
        agent_dict = {
            "id": agent["id"],
            "name": agent["name"],
            "description": agent["description"],
            "example_queries": agent["example_queries"],
            "respond": import_from_string(agent["respond"])
        }
        agents.append(agent_dict)
        yaml_ids.add(agent["id"])
    # 合併 Python 端 agent（只補充 YAML 沒有的）
    for agent in get_python_agents():
        if agent["id"] not in yaml_ids:
            agents.append(agent)
    return agents

# 這樣你就可以
# from src.agent_loader import load_agents_from_yaml
# AGENT_LIST = load_agents_from_yaml() 