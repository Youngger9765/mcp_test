import json
from src.tools.openai_tool import openai_query_llm


def generate_daily_mission(query: str) -> dict:
    """根據輸入 query，生成 Navme 今日任務卡清單"""
    instructions = (
        "你是一個任務規劃助理，請根據用戶輸入的困難或目標，"
        "生成一份今日任務卡，內容要具體、可執行，並用條列式呈現。"
        "請直接用以下 JSON 格式回傳（不要有多餘說明）：\n"
        "{\n"
        "  \"type\": \"mission_card\",\n"
        "  \"content\": [\n"
        "    {\"title\": \"...\", \"description\": \"...\", \"time_hint\": \"...\"},\n"
        "    ...\n"
        "  ],\n"
        "  \"meta\": {\n"
        "    \"topic\": \"...\",  # AI自動分析主題\n"
        "    \"intent\": \"generate_daily_mission\",\n"
        "    \"agent_id\": \"navme_agent\",\n"
        "    \"summary\": \"...\"  # AI對需求的摘要\n"
        "  }\n"
        "}\n"
        "請務必回傳合法 JSON，並讓 content 至少有 3 條具體任務。"
    )
    llm_output = openai_query_llm(instructions=instructions, input=query)
    try:
        return json.loads(llm_output)
    except Exception:
        return {"error": "LLM 回傳格式錯誤", "raw": llm_output}


def summarize_today_log(log: str) -> dict:
    """摘要今日歷程，產出回顧內容"""
    instructions = "你是一個回顧摘要助理，請根據用戶輸入的今日歷程，產出一段簡明的回顧內容，強調收穫與反思。請用 JSON 格式回傳，如 {\"summary\": \"...\"}"
    llm_output = openai_query_llm(instructions=instructions, input=log)
    try:
        return json.loads(llm_output)
    except Exception:
        return {"summary": llm_output}


def evaluate_progress(state: dict) -> dict:
    """評估過去進度，決定是否解鎖下一階段"""
    instructions = "你是一個進度評估助理，請根據用戶的狀態描述，評估是否可以解鎖下一階段，並給出具體建議。請用 JSON 格式回傳，如 {\"progress\": \"...\"}"
    llm_output = openai_query_llm(instructions=instructions, input=str(state))
    try:
        return json.loads(llm_output)
    except Exception:
        return {"progress": llm_output} 