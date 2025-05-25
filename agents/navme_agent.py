from tools.navme_tools import generate_daily_mission, summarize_today_log, evaluate_progress
from .base_agent import BaseAgent

class NavmeAgent(BaseAgent):
    id = "navme_agent"
    name = "Navme 導航任務代理"
    description = "提供每日任務、回顧與追蹤功能"
    example_queries = [
        "我今天想處理鏡像字的問題",
        "幫我規劃三天的情緒追蹤任務",
        "我想回顧這週的學習情況"
    ]

    def respond(self, query: str, history=None, **kwargs) -> dict:
        if "回顧" in query or "總結" in query:
            return summarize_today_log(query)
        elif "進度" in query or "下一階段" in query:
            return evaluate_progress({})
        else:
            return generate_daily_mission(query) 