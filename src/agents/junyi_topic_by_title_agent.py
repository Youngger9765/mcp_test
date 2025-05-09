from src.tools.junyi_topic_by_title_tool import get_junyi_topic_by_title

class JunyiTopicByTitleAgent:
    id = "junyi_topic_by_title_agent"
    name = "均一主題標題查詢代理"
    description = "根據標題查詢均一主題，回傳主題內容與相關資訊。"
    parameters = [
        {"name": "title", "type": "str"}
    ]

    def respond(self, title: str):
        return get_junyi_topic_by_title(title=title) 