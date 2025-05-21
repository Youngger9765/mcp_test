from src.tools.junyi_tree_tool import get_junyi_tree
from src.agents import Agent # Import base class

class JunyiTreeAgent(Agent): # Inherit from Agent
    def __init__(self):
        super().__init__(
            id="get_junyi_tree",
            name="均一樹查詢",
            description="查詢均一課程樹狀結構（預設只抓 1 層）",
            category="均一",
            tags=["教育", "課程樹"],
            parameters=[
                {"name": "topic_id", "type": "str", "description": "均一課程樹的根 topic_id，格式如 root", "pattern": "^[a-zA-Z0-9_\\-]+$"} # Escaped hyphen
            ],
            example_queries=[
                "查詢 root topic_id 的課程樹",
                "顯示數學科的課程結構"
            ],
            request_example={"topic_id": "root"},
            response_example={"type": "tree", "content": {"id": "root", "children": []}, "meta": {"topic_id": "root", "depth": 1}, "agent_id": "get_junyi_tree", "agent_name": "均一樹查詢", "error": None}
        )

    def respond(self, topic_id: str = "root"): # ensure 'self' is present
        # The actual tool function should handle the core logic
        # The agent's respond method is for pre/post processing and calling the tool
        return get_junyi_tree(topic_id=topic_id)