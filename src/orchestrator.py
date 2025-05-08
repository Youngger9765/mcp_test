"""
調度層（Orchestration Layer）
根據使用者 prompt，自動選擇並調用合適的工具。
"""
import openai
import json
import os
from src.tool_registry import get_tool_list
from typing import Any, Dict, List
from src.orchestrator_utils.prompt_builder import build_single_turn_prompt, build_multi_turn_step_prompt
from src.orchestrator_utils.llm_client import call_llm
from src.orchestrator_utils.tool_utils import get_tool_brief
from src.orchestrator_utils.validator import parse_llm_json_reply

def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Called {func.__name__} args: {args} kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} result: {result}")
        return result
    return wrapper

@log_call
def orchestrate(prompt: str) -> Dict[str, Any]:
    print("=== [DEBUG] 開始調度 orchestrate ===")
    tool_brief = get_tool_brief()
    system_prompt, user_prompt = build_single_turn_prompt(tool_brief, prompt)
    print("=== [DEBUG] system_prompt ===", system_prompt)
    print("=== [DEBUG] user_prompt ===", user_prompt)
    try:
        llm_reply = call_llm(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        print("=== [DEBUG] LLM 回傳 ===", llm_reply)
    except Exception as e:
        return {"type": "error", "message": str(e)}
    try:
        parsed = parse_llm_json_reply(llm_reply, required_keys=["tool_id"])
        tool_id = parsed["tool_id"]
        params = parsed.get("parameters", {})
        tools = get_tool_list()
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
        return {"type": "error", "message": str(e), "llm_reply": llm_reply}

@log_call
def multi_turn_orchestrate(user_query: str, max_turns: int = 5) -> Dict[str, Any]:
    """
    多輪推理 Orchestrator：根據用戶需求與查詢歷程，讓 LLM 自動規劃多步工具調用。
    """
    import copy
    tool_brief = get_tool_brief()
    history: List[Dict[str, Any]] = []
    query: str = user_query
    for turn in range(max_turns):
        system_prompt, user_prompt = build_multi_turn_step_prompt(tool_brief, history, query)
        try:
            llm_reply = call_llm(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0
            )
            print(f"=== [DEBUG] multi_turn_orchestrate LLM 回傳 === {llm_reply}")
        except Exception as e:
            return {"type": "error", "message": str(e)}
        try:
            plan = parse_llm_json_reply(llm_reply, required_keys=["tool_id", "action"])
            if plan.get("action") == "finish":
                return {
                    "type": "multi_turn_result",
                    "history": history,
                    "message": plan.get("reason", "查詢結束")
                }
            tool_id = plan["tool_id"]
            params = plan.get("parameters", {})
            tools = get_tool_list()
            tool = next((t for t in tools if t["id"] == tool_id), None)
            if tool:
                output = tool["function"](**params)
                history.append({
                    "tool_id": tool_id,
                    "parameters": copy.deepcopy(params),
                    "result": output,
                    "reason": plan.get("reason", "")
                })
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
            return {"type": "error", "message": str(e), "llm_reply": llm_reply, "history": history}
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

@log_call
def multi_turn_step(history: List[Dict[str, Any]], query: str, max_turns: int = 5) -> Dict[str, Any]:
    """
    分步查詢：每次只推理一輪，回傳本輪結果或 finish。
    """
    import copy
    tool_brief = get_tool_brief()
    system_prompt, user_prompt = build_multi_turn_step_prompt(tool_brief, history, query)
    try:
        llm_reply = call_llm(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
    except Exception as e:
        return {"action": "error", "message": str(e)}
    try:
        plan = parse_llm_json_reply(llm_reply, required_keys=["action"])
        if plan.get("action") == "finish":
            return {
                "action": "finish",
                "reason": plan.get("reason", "查詢結束"),
                "step": None
            }
        tool_id = plan["tool_id"]
        params = plan.get("parameters", {})
        tools = get_tool_list()
        tool = next((t for t in tools if t["id"] == tool_id), None)
        if tool:
            output = tool["function"](**params)
            step = {
                "tool_id": tool_id,
                "parameters": copy.deepcopy(params),
                "result": output,
                "reason": plan.get("reason", "")
            }
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
        return {"action": "error", "message": str(e), "llm_reply": llm_reply} 