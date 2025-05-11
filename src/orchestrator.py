"""
調度層（Orchestration Layer）
根據使用者 prompt，自動選擇並調用合適的工具。
"""
import openai
import json
import os
from src.agent_registry import get_agent_list
from typing import Any, Dict, List
from src.orchestrator_utils.prompt_builder import build_single_turn_prompt, build_multi_turn_step_prompt
from src.orchestrator_utils.llm_client import call_llm
from src.orchestrator_utils.tool_utils import get_tool_brief
from src.orchestrator_utils.validator import parse_llm_json_reply
from log_debug_info import log_debug_info

def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Called {func.__name__} args: {args} kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} result: {result}")
        return result
    return wrapper

@log_call
def dispatch_agent_single_turn(prompt: str) -> Dict[str, Any]:
    print("=== [DEBUG] 開始調度 dispatch_agent_single_turn ===")
    log_debug_info(tool_brief=None, system_prompt=None, user_prompt=prompt, llm_reply=None, prefix="print_debug")
    tool_brief = get_tool_brief()
    system_prompt, user_prompt = build_single_turn_prompt(tool_brief, prompt)
    print("=== [DEBUG] system_prompt ===", system_prompt)
    log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=None, llm_reply=None, prefix="print_debug")
    print("=== [DEBUG] user_prompt ===", user_prompt)
    log_debug_info(tool_brief=tool_brief, system_prompt=None, user_prompt=user_prompt, llm_reply=None, prefix="print_debug")
    try:
        llm_reply = call_llm(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        log_debug_info(
            tool_brief=tool_brief,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm_reply=llm_reply
        )
        print("=== [DEBUG] LLM 回傳 ===", llm_reply)
        log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, llm_reply=llm_reply, prefix="print_debug")
    except Exception as e:
        return {"type": "error", "message": str(e)}
    try:
        parsed = parse_llm_json_reply(llm_reply, required_keys=["tool_id"])
        tool_id = parsed["tool_id"]
        params = parsed.get("parameters", {})
        tools = get_agent_list()
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
            log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, llm_reply=result, prefix="print_debug")
            return result
        else:
            return {"type": "error", "message": f"找不到工具 {tool_id}"}
    except Exception as e:
        return {"type": "error", "message": str(e), "llm_reply": llm_reply}

@log_call
def dispatch_agent_multi_turn_step(history: List[Dict[str, Any]], query: str, max_turns: int = 5) -> Dict[str, Any]:
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
        log_debug_info(
            tool_brief=tool_brief,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            llm_reply=llm_reply
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
        tools = get_agent_list()
        tool = next((t for t in tools if t["id"] == tool_id), None)
        if tool:
            output = tool["function"](**params)
            step = {
                "tool_id": tool_id,
                "agent_name": tool.get("name", ""),
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

def is_redundant(history, new_step):
    # 只比對最近一輪的參數
    if not history:
        return False
    last_query = history[-1]["parameters"]
    new_query = new_step["parameters"]
    return last_query == new_query 