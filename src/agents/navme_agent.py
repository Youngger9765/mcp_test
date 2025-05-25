from .base_agent import BaseAgent
from src.tools.navme_tools import generate_daily_mission, summarize_today_log, evaluate_progress

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
        # 這裡可用 LLM 或規則產生，這裡先寫死範例
        return {
            "type": "mission_card",
            "content": [
                {
                    "title": "上午觀察自己 2 次情緒波動",
                    "description": "記錄當下事件與感受",
                    "time_hint": "上午"
                },
                {
                    "title": "傍晚進行 1 次 3 分鐘靜心練習",
                    "description": "閉眼觀呼吸、放鬆",
                    "time_hint": "傍晚"
                },
                {
                    "title": "晚上填寫情緒日誌",
                    "description": "評分 + 撰寫簡短回顧",
                    "time_hint": "晚上"
                }
            ],
            "meta": {
                "topic": "情緒覺察與能量追蹤",
                "intent": "generate_daily_mission",
                "agent_id": "navme_agent",
                "summary": "AI判斷你希望改善情緒狀態，可從每日觀察開始。"
            }
        } 