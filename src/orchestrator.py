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
from src.orchestrator_utils.agent_metadata import get_agents_metadata
from src.orchestrator_utils.validator import parse_llm_json_reply
from log_debug_info import log_debug_info
from src.parameter_extraction import filter_available_tools

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
    tool_brief = get_agents_metadata()
    agent_list = get_agent_list()

    # 新增：判斷是否指定 agent
    import re
    m = re.match(r"^\[(\w+)\](.*)", prompt)
    if m:
        agent_id = m.group(1)
        real_query = m.group(2).strip()
        agent = next((a for a in agent_list if a["id"] == agent_id), None)
        if agent:
            try:
                output = agent["function"](real_query)
                return {
                    "type": "result",
                    "tool": agent_id,
                    "input": {"query": real_query},
                    "results": [output],
                    "trace": {"user_query": prompt, "agent_id": agent_id, "mode": "指定 agent"}
                }
            except Exception as e:
                return {"type": "error", "message": str(e), "trace": {"user_query": prompt, "agent_id": agent_id, "mode": "指定 agent"}}
        else:
            return {"type": "error", "message": f"找不到指定 agent: {agent_id}", "trace": {"user_query": prompt, "agent_id": agent_id, "mode": "指定 agent"}}

    # 取得 agent list（含 function/parameters）
    agent_list = get_agent_list()
    # 1. 先做變數分析＋工具過濾
    filter_result = filter_available_tools(prompt, agent_list)
    available_agents = [a for a in filter_result if a["available"]]
    trace = {
        "user_query": prompt,
        "filter_result": filter_result
    }
    # 2. 若無可用 agent，直接回傳 trace
    if not available_agents:
        return {"type": "no_available_agent", "trace": trace}
    # 3. 只讓 available agent 進入推理（這裡只取第一個，或可依需求調整）
    # 這裡保留原本 LLM 推理流程，但可根據 available_agents 過濾 tool_brief
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
        return {"type": "error", "message": str(e), "trace": trace}
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
                "results": [output],
                "trace": trace
            }
            print("=== [DEBUG] result ===", result)
            log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, llm_reply=result, prefix="print_debug")
            return result
        else:
            return {"type": "error", "message": f"找不到工具 {tool_id}", "trace": trace}
    except Exception as e:
        return {"type": "error", "message": str(e), "llm_reply": llm_reply, "trace": trace}

@log_call
def dispatch_agent_multi_turn_step(history: List[Dict[str, Any]], query: str, max_turns: int = 5) -> Dict[str, Any]:
    """
    分步查詢：每次只推理一輪，回傳本輪結果或 finish。
    """
    import copy
    tool_brief = get_agents_metadata()
    # 取得 agent list
    agent_list = get_agent_list()
    # 先做變數分析＋工具過濾
    filter_result = filter_available_tools(query, agent_list)
    available_agents = [a for a in filter_result if a["available"]]
    trace = {
        "user_query": query,
        "filter_result": filter_result
    }
    if not available_agents:
        return {"action": "no_available_agent", "trace": trace}
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
        return {"action": "error", "message": str(e), "trace": trace}
    try:
        plan = parse_llm_json_reply(llm_reply, required_keys=["action"])
        if plan.get("action") == "finish":
            return {
                "action": "finish",
                "reason": plan.get("reason", "查詢結束"),
                "step": None,
                "trace": trace
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
                    "step": step,
                    "trace": trace
                }
            return {
                "action": "call_tool",
                "step": step,
                "trace": trace
            }
        else:
            return {
                "action": "error",
                "message": f"找不到工具 {tool_id}",
                "trace": trace
            }
    except Exception as e:
        return {"action": "error", "message": str(e), "llm_reply": llm_reply, "trace": trace}

def is_redundant(history, new_step):
    # 只比對最近一輪的參數
    if not history:
        return False
    last_query = history[-1]["parameters"]
    new_query = new_step["parameters"]
    return last_query == new_query 