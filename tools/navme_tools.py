def generate_daily_mission(query: str) -> dict:
    """根據輸入 query，生成 Navme 今日任務卡清單"""
    # TODO: 實作任務生成邏輯
    return {"mission": f"根據『{query}』生成的今日任務卡"}


def summarize_today_log(log: str) -> dict:
    """摘要今日歷程，產出回顧內容"""
    # TODO: 實作摘要邏輯
    return {"summary": f"今日歷程摘要：{log[:20]}..."}


def evaluate_progress(state: dict) -> dict:
    """評估過去進度，決定是否解鎖下一階段"""
    # TODO: 實作進度評估邏輯
    return {"progress": "已評估，下一階段已解鎖"} 