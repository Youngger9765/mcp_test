from typing import Dict, List, Callable
from src.agent_registry import agent_manager
from src.agent_selector import analyze_intent_llm

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

def call_agent_by_llm(user_query, last_agent_id, last_meta, topic_id):
    # 如果上一輪是課程樹，且 user_query/或 topic_id 是 topic_ids 之一，直接 route
    if last_agent_id == "junyi_tree_agent" and last_meta and "topic_ids" in last_meta:
        topic_ids = last_meta["topic_ids"]
        if user_query in topic_ids:
            agent_id = "junyi_topic_agent"
            agent = agent_manager.get(agent_id)
            result = agent.respond(user_query, topic_id=user_query, parent_query=last_meta.get("query"))
            result["meta"]["llm_reason"] = "user_input is topic_id, auto route to junyi_topic_agent"
            return {
                "type": "result",
                "results": [result]
            }

    # 其餘全部交給 LLM
    agent_list = [
        {"id": a.id, "name": a.name, "description": a.description}
        for a in agent_manager.all_agents()
    ]
    topic_map = []
    if last_meta and "topic_ids" in last_meta and "content" in last_meta:
        def collect_id_title(tree):
            result = []
            if isinstance(tree, dict):
                if "id" in tree and "title" in tree:
                    result.append({"id": tree["id"], "title": tree["title"]})
                if "children" in tree:
                    for child in tree["children"]:
                        result.extend(collect_id_title(child))
            elif isinstance(tree, list):
                for node in tree:
                    result.extend(collect_id_title(node))
            return result
        topic_map = collect_id_title(last_meta["content"])
    agent_id, reason, topic_id_from_llm = analyze_intent_llm(
        user_query=user_query,
        last_agent_id=last_agent_id,
        last_meta=last_meta,
        topic_id=topic_id,
        agent_list=agent_list,
        topic_map=topic_map
    )
    if topic_id_from_llm:
        topic_id = topic_id_from_llm
    agent = agent_manager.get(agent_id)
    kwargs = {}
    if topic_id:
        kwargs["topic_id"] = topic_id
    if last_meta and "query" in last_meta:
        kwargs["parent_query"] = last_meta["query"]
    result = agent.respond(user_query, **kwargs)
    result["meta"]["llm_reason"] = reason
    return {
        "type": "result",
        "results": [result]
    } 