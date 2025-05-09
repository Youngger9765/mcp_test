from src.tools.junyi_topic_tool import get_junyi_topic

class JunyiTopicAgent:
    id = "junyi_topic_agent"
    name = "均一主題查詢代理"
    description = "查詢均一 topic 內容，回傳該 topic 的標題、描述與子主題摘要。"
    parameters = [
        {"name": "topic_id", "type": "str"}
    ]

    def respond(self, topic_id: str = "root"):
        return get_junyi_topic(topic_id=topic_id) 