from src.tools.navme_tools import summarize_today_log

class NavmeSummaryAgent:
    id = "navme_summary"
    name = "Navme 回顧摘要"
    description = "根據輸入產生今日回顧摘要"
    example_queries = ["回顧今天的情緒", "總結今天的學習"]
    parameters = [
        {"name": "query", "type": "str", "description": "用戶輸入", "required": True}
    ]
    category = "Navme"
    tags = ["回顧", "摘要", "親子"]
    request_example = {"query": "小孩不乖"}
    response_example = {
        "type": "summary_card",
        "content": {
            "summary": "今天你表現得很棒，雖然遇到挑戰，但你有努力調整心情。"
        },
        "meta": {"input": "小孩不乖"},
        "agent_id": "navme_summary",
        "agent_name": "Navme 回顧摘要",
        "error": None
    }

    def respond(self, query: str, history=None, **kwargs):
        return summarize_today_log(query) 