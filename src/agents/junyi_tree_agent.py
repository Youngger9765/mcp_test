from src.tools.junyi_tree_tool import get_junyi_tree

class JunyiTreeAgent:
    id = "junyi_tree_agent"
    name = "均一樹查詢代理"
    description = "查詢均一課程樹，回傳指定 topic_id 與 depth 的課程結構摘要。"
    parameters = [
        {"name": "topic_id", "type": "str"},
        {"name": "depth", "type": "int", "default": 1}
    ]

    def respond(self, topic_id: str = "root", depth: int = 1):
        return get_junyi_tree(topic_id=topic_id, depth=depth) 