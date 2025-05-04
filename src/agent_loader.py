import yaml
from src.agent_registry import get_python_agents
from src.agent_manager import AgentManager

def load_yaml_agents(yaml_path="mcp_config.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("agents", [])

def build_agent_list():
    yaml_agents = load_yaml_agents()
    python_agents = get_python_agents()
    agent_dict = {a["id"]: a for a in python_agents}
    # YAML 為主，覆蓋 Python
    for agent in yaml_agents:
        agent_dict[agent["id"]] = agent
    return list(agent_dict.values())

def get_agent_manager():
    manager = AgentManager()
    for agent in build_agent_list():
        manager.register(agent)
    return manager

# AGENT_LIST 給前端/測試用
AGENT_LIST = build_agent_list() 