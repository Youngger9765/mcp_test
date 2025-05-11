from src.tools.junyi_topic_by_title_tool import get_junyi_topic_by_title

class JunyiTopicByTitleAgent:
    id = "get_junyi_topic_by_title"
    name = "均一主題標題查詢"
    description = "用於依標題查詢均一教育平台上的教學主題（如分數、加減法等），取得教材內容，適合教育資源查詢，不進行數字運算。"
    category = "均一"
    tags = ["教育", "標題查詢"]
    parameters = [
        {"name": "title", "type": "str", "description": "主題標題關鍵字，僅允許中英文與數字", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]+$"}
    ]
    example_queries = [
        "查詢標題為『分數』的主題內容"
    ]
    request_example = {"title": "分數"}
    response_example = {"type": "topic_by_title", "content": {"id": "math_002", "title": "分數"}, "meta": {"title": "分數", "topic_id": "math_002"}, "agent_id": "get_junyi_topic_by_title", "agent_name": "均一主題標題查詢", "error": None}

    def respond(self, title: str):
        return get_junyi_topic_by_title(title=title) 