from src.tools.junyi_topic_tool import get_junyi_topic

class JunyiTopicAgent:
    id = "get_junyi_topic"
    name = "均一主題查詢"
    description = "用於查詢均一教育平台上的數學、分數、加減法等教學主題與教材內容，適合用於教育資源查詢，不進行數字運算。"
    category = "均一"
    tags = ["教育", "均一"]
    parameters = [
        {"name": "topic_id", "type": "str", "description": "均一主題的 ID，格式如 root", "pattern": "^[a-zA-Z0-9_\-]+$"}
    ]
    example_queries = [
        "查詢 topic_id 為 root 的主題內容"
    ]
    request_example = {"topic_id": "root"}
    response_example = {"type": "topic", "content": {"id": "root", "title": "數學"}, "meta": {"topic_id": "root"}, "agent_id": "get_junyi_topic", "agent_name": "均一主題查詢", "error": None}

    def respond(self, topic_id: str = "root"):
        return get_junyi_topic(topic_id=topic_id) 