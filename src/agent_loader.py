import yaml
from src.agent_registry import agent_manager
from src.agent_manager import AgentManager
import os

def load_yaml_agents(yaml_path="mcp_config.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("agents", [])

def build_agent_list():
    yaml_agents = load_yaml_agents()
    # 將 Agent 物件轉成 dict
    python_agents = [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "example_queries": a.example_queries,
            "respond": a.respond
        }
        for a in agent_manager.all_agents()
    ]
    agent_dict = {a["id"]: a for a in python_agents}
    # YAML 為主，覆蓋 Python，但 respond function 一定用 Python 的
    for agent in yaml_agents:
        py_agent = agent_dict.get(agent["id"])
        if py_agent:
            # 用 YAML 的資料覆蓋，但 respond 用 Python 的
            merged = {**py_agent, **agent}
            merged["respond"] = py_agent["respond"]
            if "arguments" in agent:
                merged["arguments"] = agent["arguments"]
            agent_dict[agent["id"]] = merged
        else:
            agent_dict[agent["id"]] = agent
    return list(agent_dict.values())

def get_agent_manager():
    manager = AgentManager()
    for agent in build_agent_list():
        manager.register(agent)
    return manager

# AGENT_LIST 給前端/測試用
AGENT_LIST = build_agent_list()

def get_agent_list():
    return build_agent_list()

def get_yaml_agents():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'mcp_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('agents', []) 