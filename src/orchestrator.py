"""
調度層（Orchestration Layer）
根據使用者 prompt，自動選擇並調用合適的工具。
"""
import openai
import json
import os
from src.tool_registry import get_tool_list
from typing import Any, Dict

def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Called {func.__name__} args: {args} kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} result: {result}")
        return result
    return wrapper

def orchestrate(prompt: str) -> Dict[str, Any]:
    print("=== [DEBUG] 開始調度 orchestrate ===")
    tools = get_tool_list()
    # 整理工具清單給 LLM
    tool_brief = [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "parameters": t.get("parameters", [])
        }
        for t in tools
    ]
    system_prompt = (
        "你是一個工具調度助理，根據使用者輸入與下列工具清單，"
        "請判斷最適合的工具 id 及其參數，並以 JSON 格式回覆："
        '{"tool_id": "...", "parameters": {...}}。\n'
        "工具清單如下：\n"
        f"{json.dumps(tool_brief, ensure_ascii=False, indent=2)}"
    )
    print("=== [DEBUG] system_prompt ===", system_prompt)
    user_prompt = f"使用者輸入：{prompt}"
    print("=== [DEBUG] user_prompt ===", user_prompt)

    # 呼叫 OpenAI LLM
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        llm_reply = response.choices[0].message.content
        print("=== [DEBUG] LLM 回傳 ===", llm_reply)
    except Exception as e:
        return {"type": "error", "message": f"OpenAI API 錯誤: {e}"}

    try:
        parsed = json.loads(llm_reply)
        tool_id = parsed["tool_id"]
        params = parsed.get("parameters", {})
        tool = next((t for t in tools if t["id"] == tool_id), None)
        if tool:
            output = tool["function"](**params)
            result = {
                "type": "result",
                "tool": tool_id,
                "input": params,
                "results": [output]
            }
            print("=== [DEBUG] result ===", result)
            return result
        else:
            return {"type": "error", "message": f"找不到工具 {tool_id}"}
    except Exception as e:
        return {"type": "error", "message": f"LLM 回傳格式錯誤或解析失敗: {e}", "llm_reply": llm_reply}

def multi_turn_orchestrate(user_query: str, max_turns: int = 5) -> dict:
    """
    多輪推理 Orchestrator：根據用戶需求與查詢歷程，讓 LLM 自動規劃多步工具調用。
    """
    import copy
    tools = get_tool_list()
    tool_brief = [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "parameters": t.get("parameters", [])
        }
        for t in tools
    ]
    history = []
    query = user_query
    for turn in range(max_turns):
        system_prompt = (
            "你是一個多輪推理的工具調度助理，根據用戶需求和目前查到的內容，"
            "請自動規劃下一步要用哪個工具（或說已經查完）。\n"
            "目前查詢歷程：" + json.dumps(history, ensure_ascii=False) + "\n"
            "用戶需求：" + query + "\n"
            "工具清單如下：\n" + json.dumps(tool_brief, ensure_ascii=False, indent=2) + "\n"
            "請用 JSON 格式回覆：{\"tool_id\": \"...\", \"parameters\": {...}, \"action\": \"call_tool\" 或 \"finish\", \"reason\": \"為什麼這樣規劃\"}"
        )
        user_prompt = f"請根據目前查到的內容，決定下一步要查什麼，或說已經查完。"
        try:
            response = openai.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )
            llm_reply = response.choices[0].message.content
            print(f"=== [DEBUG] multi_turn_orchestrate LLM 回傳 === {llm_reply}")
        except Exception as e:
            return {"type": "error", "message": f"OpenAI API 錯誤: {e}"}
        try:
            plan = json.loads(llm_reply)
            if plan.get("action") == "finish":
                return {
                    "type": "multi_turn_result",
                    "history": history,
                    "message": plan.get("reason", "查詢結束")
                }
            tool_id = plan["tool_id"]
            params = plan.get("parameters", {})
            tool = next((t for t in tools if t["id"] == tool_id), None)
            if tool:
                output = tool["function"](**params)
                history.append({
                    "tool_id": tool_id,
                    "parameters": copy.deepcopy(params),
                    "result": output,
                    "reason": plan.get("reason", "")
                })
                # 把查到的內容摘要給 LLM 當作下一輪的 query
                query = f"剛剛查到：{str(output)[:500]}...，請問還需要查什麼嗎？"
            else:
                history.append({
                    "tool_id": tool_id,
                    "parameters": params,
                    "result": None,
                    "reason": f"找不到工具 {tool_id}"
                })
                return {
                    "type": "error",
                    "message": f"找不到工具 {tool_id}",
                    "history": history
                }
        except Exception as e:
            return {"type": "error", "message": f"LLM 回傳格式錯誤或解析失敗: {e}", "llm_reply": llm_reply, "history": history}
    return {
        "type": "multi_turn_result",
        "history": history,
        "message": "已達最大輪數，請檢查查詢歷程。"
    }

def is_redundant(history, new_step):
    # 只比對最近一輪的參數
    if not history:
        return False
    last_query = history[-1]["parameters"]
    new_query = new_step["parameters"]
    return last_query == new_query

def multi_turn_step(history, query, max_turns=5):
    """
    分步查詢：每次只推理一輪，回傳本輪結果或 finish。
    """
    import copy
    tools = get_tool_list()
    tool_brief = [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "parameters": t.get("parameters", [])
        }
        for t in tools
    ]
    system_prompt = (
        "你是一個多輪推理的工具調度助理，根據用戶需求和目前查到的內容，"
        "請自動規劃下一步要用哪個工具（或說已經查完）。\n"
        "如果你發現查詢結果和前幾輪內容高度重複，或已經沒有更多新資訊，請直接回覆 {\"action\": \"finish\", \"reason\": \"已查無更多新資訊，結束查詢\"}，不要無限細分查詢。\n"
        "目前查詢歷程：" + json.dumps(history, ensure_ascii=False) + "\n"
        "用戶需求：" + query + "\n"
        "工具清單如下：\n" + json.dumps(tool_brief, ensure_ascii=False, indent=2) + "\n"
        "請用 JSON 格式回覆：{\"tool_id\": \"...\", \"parameters\": {...}, \"action\": \"call_tool\" 或 \"finish\", \"reason\": \"為什麼這樣規劃\"}"
    )
    user_prompt = f"請根據目前查到的內容，決定下一步要查什麼，或說已經查完。"
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        llm_reply = response.choices[0].message.content
    except Exception as e:
        return {"action": "error", "message": f"OpenAI API 錯誤: {e}"}
    try:
        plan = json.loads(llm_reply)
        if plan.get("action") == "finish":
            return {
                "action": "finish",
                "reason": plan.get("reason", "查詢結束"),
                "step": None
            }
        tool_id = plan["tool_id"]
        params = plan.get("parameters", {})
        tool = next((t for t in tools if t["id"] == tool_id), None)
        if tool:
            output = tool["function"](**params)
            step = {
                "tool_id": tool_id,
                "parameters": copy.deepcopy(params),
                "result": output,
                "reason": plan.get("reason", "")
            }
            # 新增：重複查詢自動終止
            if is_redundant(history, step):
                return {
                    "action": "finish",
                    "reason": "查詢內容重複，已自動結束。",
                    "step": step
                }
            return {
                "action": "call_tool",
                "step": step
            }
        else:
            return {
                "action": "error",
                "message": f"找不到工具 {tool_id}"
            }
    except Exception as e:
        return {"action": "error", "message": f"LLM 回傳格式錯誤或解析失敗: {e}", "llm_reply": llm_reply} 