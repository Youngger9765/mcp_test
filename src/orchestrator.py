"""
調度層（Orchestration Layer）
根據使用者 prompt，自動選擇並調用合適的工具。
"""
import openai
import json
import os
from src.tool_registry import get_tool_list
from typing import Any, Dict

def orchestrate(prompt: str) -> Dict[str, Any]:
    tools = get_tool_list()
    # 整理工具清單給 LLM
    tool_brief = [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"]
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
    user_prompt = f"使用者輸入：{prompt}"

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
    except Exception as e:
        return {"type": "error", "message": f"OpenAI API 錯誤: {e}"}

    try:
        parsed = json.loads(llm_reply)
        tool_id = parsed["tool_id"]
        params = parsed.get("parameters", {})
        tool = next((t for t in tools if t["id"] == tool_id), None)
        if tool:
            result = tool["function"](**params)
            return {
                "type": "result",
                "tool": tool_id,
                "input": params,
                "output": result
            }
        else:
            return {"type": "error", "message": f"找不到工具 {tool_id}"}
    except Exception as e:
        return {"type": "error", "message": f"LLM 回傳格式錯誤或解析失敗: {e}", "llm_reply": llm_reply} 