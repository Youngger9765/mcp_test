from src.tools.navme_tools import generate_daily_mission

class NavmeDailyMissionAgent:
    id = "navme_daily_mission"
    name = "Navme 每日任務卡"
    description = "根據輸入產生今日任務建議"
    example_queries = ["我最近情緒不穩", "我想改善親子關係"]
    parameters = [
        {"name": "query", "type": "str", "description": "用戶輸入", "required": True}
    ]
    category = "Navme"
    tags = ["任務", "建議", "親子"]
    request_example = {"query": "小孩不乖"}
    response_example = {
        "type": "mission_card",
        "content": {
            "title": "今日任務",
            "missions": [
                {"title": "陪伴孩子 10 分鐘", "desc": "放下手機，專心陪伴孩子"},
                {"title": "自我覺察", "desc": "記錄今天的情緒變化"}
            ]
        },
        "meta": {"input": "小孩不乖"},
        "agent_id": "navme_daily_mission",
        "agent_name": "Navme 每日任務卡",
        "error": None
    }

    def respond(self, query: str, history=None, **kwargs):
        return generate_daily_mission(query) 