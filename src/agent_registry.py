from typing import Any, Dict, List, Optional
import agents.agent_a as agent_a
import agents.agent_b as agent_b
import agents.junyi_tree_agent as junyi_tree_agent
import agents.junyi_topic_agent as junyi_topic_agent

class BaseAgent:
    id: str = ""
    name: str = ""
    description: str = ""
    example_queries: List[str] = []

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Each agent must implement the respond method.")

class AgentA(BaseAgent):
    id = "agent_a"
    name = "A Agent"
    description = "適合查詢一般網路摘要、影片剪輯教學等資訊。"
    example_queries = [
        "請幫我查一下影片剪輯教學",
        "什麼是 YouTuber？"
    ]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        content = agent_a.respond(query)
        return {
            "type": "text",
            "content": {"text": content},
            "meta": {"query": query},
            "agent_id": self.id,
            "error": None
        }

class AgentB(BaseAgent):
    id = "agent_b"
    name = "B Agent"
    description = "適合查詢 B 網站的專業資料或特定主題。"
    example_queries = [
        "B 網站有什麼新消息？"
    ]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        content = agent_b.respond(query)
        return {
            "type": "text",
            "content": {"text": content},
            "meta": {"query": query},
            "agent_id": self.id,
            "error": None
        }

class JunyiTreeAgent(BaseAgent):
    id = "junyi_tree_agent"
    name = "均一課程結構樹"
    description = "適合查詢均一課程結構、單元樹狀圖等。"
    example_queries = [
        "請列出課程結構",
        "請顯示 root 下三層"
    ]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        topic_id = kwargs.get("topic_id", "root")
        depth = kwargs.get("depth", 1)
        parent_query = kwargs.get("parent_query")
        content = junyi_tree_agent.respond(topic_id=topic_id, depth=depth)
        meta = {"query": query, "topic_id": topic_id, "depth": depth}
        if parent_query:
            meta["parent_query"] = parent_query
        error = content.get("error") if isinstance(content, dict) and "error" in content else None
        if error is not None and not isinstance(error, dict):
            error = {"message": error}
        return {
            "type": "tree",
            "content": content,
            "meta": meta,
            "agent_id": self.id,
            "error": error
        }

class JunyiTopicAgent(BaseAgent):
    id = "junyi_topic_agent"
    name = "均一主題查詢"
    description = "適合查詢均一某個主題的詳細內容。"
    example_queries = [
        "請介紹分數的意義 (需給 topic_id)",
        "查詢某主題內容 (需給 topic_id)"
    ]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        topic_id = kwargs.get("topic_id")
        parent_query = kwargs.get("parent_query")
        if not topic_id:
            return {
                "type": "error",
                "content": {"text": "請提供 topic_id"},
                "meta": {"query": query},
                "agent_id": self.id,
                "error": {"message": "缺少 topic_id"}
            }
        content = junyi_topic_agent.respond(topic_id=topic_id)
        meta = {"query": query, "topic_id": topic_id}
        if parent_query:
            meta["parent_query"] = parent_query
        error = content.get("error") if isinstance(content, dict) and "error" in content else None
        if error is not None and not isinstance(error, dict):
            error = {"message": error}
        return {
            "type": "tree",
            "content": content,
            "meta": meta,
            "agent_id": self.id,
            "error": error
        }

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        self.agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def all_agents(self) -> List[BaseAgent]:
        return list(self.agents.values())

# 註冊所有 agent
agent_manager = AgentManager()
agent_manager.register(AgentA())
agent_manager.register(AgentB())
agent_manager.register(JunyiTreeAgent())
agent_manager.register(JunyiTopicAgent())

def get_python_agents():
    return [
        {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "example_queries": agent.example_queries,
            "respond": agent.respond
        }
        for agent in agent_manager.all_agents()
    ] 