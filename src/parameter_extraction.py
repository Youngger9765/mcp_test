import re
from src.tools.openai_tool import openai_query_llm
import json

def get_required_params(parameters: list) -> list:
    """
    回傳必填參數名稱清單。
    有 required: True 則必填，required: False 則非必填，否則沒 default 也視為必填。
    """
    required = []
    for p in parameters:
        if p.get("required", None) is True:
            required.append(p["name"])
        elif p.get("required", None) is False:
            continue
        elif "default" not in p:
            required.append(p["name"])
    return required

def extract_parameters_from_query(query, tool_parameters):
    """
    使用 OpenAI LLM 進行參數抽取，回傳 dict 或 None。
    只檢查必填參數。
    """
    required_names = get_required_params(tool_parameters)
    # 將 tool_parameters 轉成簡潔描述
    param_desc = ", ".join([f'{p["name"]}（{p["type"]}，必填）' if p["name"] in required_names else f'{p["name"]}（{p["type"]}）' for p in tool_parameters])
    instructions = (
        "你是一個參數抽取助手。請根據下方工具需求，從 user query 中抽取對應參數，忽略無關數字與列點。\n"
        "請只回傳 JSON 格式（如 {\"a\": 3, \"b\": 5}），若無法抽取請回傳 null。\n"
        "工具需求參數: " + param_desc
    )
    user_input = f"User query: {query}\n請回傳:"
    llm_output = openai_query_llm(instructions=instructions, input=user_input)
    try:
        result = json.loads(llm_output)
        if not result:
            return None
        # 僅檢查必填欄位
        for name in required_names:
            if name not in result or result[name] in [None, ""]:
                return None
        return result
    except Exception:
        return None

def filter_available_tools(query, agent_list):
    """
    根據 user query 與 agent_list，回傳所有 agent 的 available 狀態與參數抽取結果。
    """
    result = []
    for agent in agent_list:
        params = agent.get("parameters", [])
        # 無參數工具預設 available
        if not params:
            result.append({
                "agent_id": agent.get("id"),
                "agent_name": agent.get("name"),
                "extracted_params": {},
                "available": True
            })
            continue
        extracted = extract_parameters_from_query(query, params)
        required_names = get_required_params(params)
        available = extracted is not None and all(name in extracted for name in required_names)
        result.append({
            "agent_id": agent.get("id"),
            "agent_name": agent.get("name"),
            "extracted_params": extracted,
            "available": available
        })
    return result

def llm_extract_parameters(query, tool_parameters):
    """
    這裡先 mock LLM 行為，之後可串接 OpenAI/GPT API。
    """
    # 只做簡單情境判斷，方便 TDD
    if "加 3 跟 5" in query:
        return {"a": 3, "b": 5}
    return None 