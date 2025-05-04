from typing import Any, Dict, List, Optional
import requests  # 新增

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
        return {
            "type": "text",
            "content": {"text": f"[A Agent 回應] 你問了：{query}，這是我從 A 網站取得的摘要。"},
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
        return {
            "type": "text",
            "content": {"text": f"[B Agent 回應] 針對：{query}，我查到 B 網站的相關資料。"},
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
        "這個主題有哪些延伸單元？"
    ]

    BASE_URL = "https://www.junyiacademy.org/api/v2/open"

    def _fetch_sub_tree(self, topic_id="root", depth=3):
        url = f"{self.BASE_URL}/sub-tree/{topic_id}?depth={depth}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _fetch_topic_page(self, topic_id="root"):
        url = f"{self.BASE_URL}/content/topicpage/{topic_id}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        try:
            # 根據 query 決定查詢哪一種 API
            if "結構" in query or "樹" in query or "課程" in query:
                # 查詢課程結構樹
                topic_id = kwargs.get("topic_id", "root")
                depth = kwargs.get("depth", 3)
                data = self._fetch_sub_tree(topic_id, depth)
                # 只取主要結構
                tree = data.get("data", {})
                return {
                    "type": "tree",
                    "content": tree,
                    "meta": {"query": query, "topic_id": topic_id, "depth": depth},
                    "agent_id": self.id,
                    "error": None
                }
            else:
                # 查詢單一 topic
                topic_id = kwargs.get("topic_id", "root")
                data = self._fetch_topic_page(topic_id)
                # 只取重點資訊
                children = data.get("child", [])
                nodes = [
                    {
                        "title": child.get("title"),
                        "topic_id": child.get("topic_id"),
                        "description": child.get("description", "")
                    }
                    for child in children
                ]
                return {
                    "type": "tree",
                    "content": {
                        "title": data.get("title"),
                        "topic_id": data.get("topic_id"),
                        "description": data.get("description"),
                        "children": nodes
                    },
                    "meta": {"query": query, "topic_id": topic_id},
                    "agent_id": self.id,
                    "error": None
                }
        except Exception as e:
            return {
                "type": "error",
                "content": {"text": f"查詢均一課程結構時發生錯誤：{str(e)}"},
                "meta": {"query": query},
                "agent_id": self.id,
                "error": str(e)
            }

class JunyiTopicAgent(BaseAgent):
    id = "junyi_topic_agent"
    name = "均一主題查詢"
    description = "適合查詢均一某個主題的詳細內容。"
    example_queries = [
        "請介紹分數的意義",
        "這個主題有哪些重點？"
    ]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        return {
            "type": "text",
            "content": {"text": f"[均一主題查詢] 你查詢的主題「{query}」重點如下：..."},
            "meta": {"query": query},
            "agent_id": self.id,
            "error": None
        }

# 工程師專用進階 agent
class SecretAgent(BaseAgent):
    id = "secret_agent"
    name = "祕密 Agent"
    description = "只有工程師知道的祕密功能。"
    example_queries = ["祕密指令"]

    def respond(self, query: str, **kwargs) -> Dict[str, Any]:
        return {
            "type": "text",
            "content": {"text": f"[祕密 Agent 回應] 你問了：{query}，這是祕密功能。"},
            "meta": {"query": query},
            "agent_id": self.id,
            "error": None
        }

def get_python_agents():
    """
    回傳所有 Python 端的 agent（for 合併用）
    """
    return [
        {
            "id": AgentA.id,
            "name": AgentA.name,
            "description": AgentA.description,
            "example_queries": AgentA.example_queries,
            "respond": AgentA().respond
        },
        {
            "id": AgentB.id,
            "name": AgentB.name,
            "description": AgentB.description,
            "example_queries": AgentB.example_queries,
            "respond": AgentB().respond
        },
        {
            "id": JunyiTreeAgent.id,
            "name": JunyiTreeAgent.name,
            "description": JunyiTreeAgent.description,
            "example_queries": JunyiTreeAgent.example_queries,
            "respond": JunyiTreeAgent().respond
        },
        {
            "id": JunyiTopicAgent.id,
            "name": JunyiTopicAgent.name,
            "description": JunyiTopicAgent.description,
            "example_queries": JunyiTopicAgent.example_queries,
            "respond": JunyiTopicAgent().respond
        },
        {
            "id": SecretAgent.id,
            "name": SecretAgent.name,
            "description": SecretAgent.description,
            "example_queries": SecretAgent.example_queries,
            "respond": SecretAgent().respond
        }
    ]

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
agent_manager.register(SecretAgent()) 