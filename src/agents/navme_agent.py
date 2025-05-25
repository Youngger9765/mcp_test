# from .base_agent import BaseAgent
from src.tools.navme_tools import generate_daily_mission, summarize_today_log, evaluate_progress

class NavmeAgent:
    id = "navme_agent"
    name = "Navme 導航任務代理"
    description = "提供每日任務、回顧與追蹤功能"
    example_queries = [
        "我今天想處理鏡像字的問題",
        "幫我規劃三天的情緒追蹤任務",
        "我想回顧這週的學習情況"
    ]

    def respond(self, query: str, history=None, **kwargs):
        # 呼叫 generate_daily_mission，並包裝成 mission_card schema
        mission = generate_daily_mission(query)
        # mission 可能是 {"mission": "..."} 或 {"content": [...], "meta": {...}}
        if "content" in mission and "meta" in mission:
            # 若 generate_daily_mission 已經回傳完整 mission_card schema
            return mission
        # 否則包裝成標準格式
        content = []
        # 嘗試將 mission["mission"] 拆成多條
        if isinstance(mission, dict) and "mission" in mission:
            lines = [line.strip() for line in mission["mission"].split("\n") if line.strip()]
            for line in lines:
                # 嘗試用數字. 或 - 分段
                import re
                m = re.match(r"^(\d+\.|[-•])\s*(.*)", line)
                title = m.group(2) if m else line
                content.append({
                    "title": title,
                    "description": "",
                    "time_hint": ""
                })
        meta = {
            "topic": "AI自動分析主題",  # 可進階用 LLM 分析
            "intent": "generate_daily_mission",
            "agent_id": "navme_agent",
            "summary": "AI根據你的輸入產生今日任務卡，請依序完成。"
        }
        return {
            "type": "mission_card",
            "content": content,
            "meta": meta
        } 