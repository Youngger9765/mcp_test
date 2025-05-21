"""
調度層（Orchestration Layer）
根據使用者 prompt，自動選擇並調用合適的工具。
"""
import openai
import json
import os
from src.agent_registry import get_agent_list
from typing import Any, Dict, List, Optional, Tuple # Added Optional and Tuple
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

def _prepare_agent_dispatch(query: str, agent_list: List[Dict]) -> Tuple[Optional[List[Dict]], Dict, Dict]:
    """
    Helper function to prepare for agent dispatch.
    Fetches metadata, filters available tools, and creates initial trace.
    """
    tool_brief = get_agents_metadata() # This uses the full agent list implicitly
    filter_result = filter_available_tools(query, agent_list)
    available_agents = [a for a in filter_result if a["available"]]
    trace = {
        "user_query": query,
        "filter_result": filter_result
    }
    if not available_agents:
        return None, tool_brief, trace
    return available_agents, tool_brief, trace

def _create_error_response(
    message: str, 
    trace: Dict, 
    llm_reply: Optional[str] = None, 
    is_multi_turn: bool = False
) -> Dict[str, Any]:
    error_key = "action" if is_multi_turn else "type"
    response = {
        error_key: "error",
        "message": message,
        "trace": trace,
    }
    if llm_reply:
        response["llm_reply"] = llm_reply
    return response

@log_call
def dispatch_agent_single_turn(prompt: str) -> Dict[str, Any]:
    log_debug_info(message="=== [DEBUG] 開始調度 dispatch_agent_single_turn ===", user_prompt=prompt, prefix="dispatch_single_turn")
    
    agent_list = get_agent_list() # Get full agent list
    available_agents, tool_brief, trace = _prepare_agent_dispatch(prompt, agent_list)

    if available_agents is None:
        return {"type": "no_available_agent", "trace": trace}
    
    # Note: The current implementation of build_single_turn_prompt uses tool_brief which is based on all agents.
    # If it should only use available_agents, tool_brief generation or filtering might need adjustment.
    # For now, using tool_brief as returned by _prepare_agent_dispatch (which is all tools' metadata).
    system_prompt, user_prompt = build_single_turn_prompt(tool_brief, prompt) 
    
    log_debug_info(system_prompt=system_prompt, message="=== [DEBUG] system_prompt ===", tool_brief=tool_brief, prefix="dispatch_single_turn")
    log_debug_info(user_prompt=user_prompt, message="=== [DEBUG] user_prompt ===", tool_brief=tool_brief, prefix="dispatch_single_turn")

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
        log_debug_info(llm_reply=llm_reply, message="=== [DEBUG] LLM 回傳 ===", tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, prefix="dispatch_single_turn")
        # The following log_debug_info call is pre-existing, keeping it.
        # log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, llm_reply=llm_reply, prefix="print_debug")
    except Exception as e:
        return _create_error_response(message=str(e), trace=trace)
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
            log_debug_info(llm_reply=result, message="=== [DEBUG] result ===", tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, prefix="dispatch_single_turn")
            # The following log_debug_info call is pre-existing, keeping it.
            # log_debug_info(tool_brief=tool_brief, system_prompt=system_prompt, user_prompt=user_prompt, llm_reply=result, prefix="print_debug")
            return result
        else:
            return _create_error_response(message=f"找不到工具 {tool_id}", trace=trace)
    except Exception as e:
        return _create_error_response(message=str(e), trace=trace, llm_reply=llm_reply)

@log_call
def dispatch_agent_multi_turn_step(history: List[Dict[str, Any]], query: str, max_turns: int = 5) -> Dict[str, Any]:
    """
    分步查詢：每次只推理一輪，回傳本輪結果或 finish。
    """
    import copy
    agent_list = get_agent_list() # Get full agent list
    available_agents, tool_brief, trace = _prepare_agent_dispatch(query, agent_list)

    if available_agents is None:
        return {"action": "no_available_agent", "trace": trace}

    # Similar to single_turn, build_multi_turn_step_prompt uses tool_brief from all agents.
    system_prompt, user_prompt = build_multi_turn_step_prompt(tool_brief, history, query)
    
    # Adding debug logs for prompts in multi-turn, similar to single-turn
    log_debug_info(system_prompt=system_prompt, message="=== [DEBUG] multi_turn system_prompt ===", tool_brief=tool_brief, user_prompt=query, prefix="dispatch_multi_turn_step")
    log_debug_info(user_prompt=user_prompt, message="=== [DEBUG] multi_turn user_prompt ===", tool_brief=tool_brief, prefix="dispatch_multi_turn_step")

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
        return _create_error_response(message=str(e), trace=trace, is_multi_turn=True)
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
            return _create_error_response(message=f"找不到工具 {tool_id}", trace=trace, is_multi_turn=True)
    except Exception as e:
        return _create_error_response(message=str(e), trace=trace, llm_reply=llm_reply, is_multi_turn=True)

def is_redundant(history, new_step):
    # 只比對最近一輪的參數
    if not history:
        return False
    last_query = history[-1]["parameters"]
    new_query = new_step["parameters"]
    return last_query == new_query 