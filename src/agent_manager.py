from typing import Dict, List, Callable

class AgentManager:
    def __init__(self):
        self._agents: Dict[str, dict] = {}

    def register(self, agent_dict: dict):
        agent_id = agent_dict["id"]
        self._agents[agent_id] = agent_dict

    def get(self, agent_id: str):
        return self._agents.get(agent_id)

    def all(self) -> List[dict]:
        return list(self._agents.values())

    def call(self, agent_id: str, *args, **kwargs):
        agent = self.get(agent_id)
        if agent and callable(agent.get("respond")):
            return agent["respond"](*args, **kwargs)
        raise ValueError(f"Agent {agent_id} not found or respond not callable") 