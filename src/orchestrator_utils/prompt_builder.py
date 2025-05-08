from typing import List, Dict, Tuple
import json

def build_single_turn_prompt(tool_brief: List[Dict], user_prompt: str) -> Tuple[str, str]:
    system_prompt = (
        "你是一個工具調度助理，根據使用者輸入與下列工具清單，"
        "請判斷最適合的工具 id 及其參數，並以 JSON 格式回覆："
        '{"tool_id": "...", "parameters": {...}}。\n'
        "工具清單如下：\n"
        f"{json.dumps(tool_brief, ensure_ascii=False, indent=2)}"
    )
    user_prompt_full = f"使用者輸入：{user_prompt}"
    return system_prompt, user_prompt_full

def build_multi_turn_step_prompt(tool_brief: List[Dict], history: List[Dict], query: str) -> Tuple[str, str]:
    system_prompt = (
        "你是一個多輪推理的工具調度助理，根據用戶需求和目前查到的內容，"
        "請自動規劃下一步要用哪個工具（或說已經查完）。\n"
        "如果你發現查詢結果和前幾輪內容高度重複，或已經沒有更多新資訊，請直接回覆 {\"action\": \"finish\", \"reason\": \"已查無更多新資訊，結束查詢\"}，不要無限細分查詢。\n"
        "目前查詢歷程：" + json.dumps(history, ensure_ascii=False) + "\n"
        "用戶需求：" + query + "\n"
        "工具清單如下：\n" + json.dumps(tool_brief, ensure_ascii=False, indent=2) + "\n"
        "請用 JSON 格式回覆：{\"tool_id\": \"...\", \"parameters\": {...}, \"action\": \"call_tool\" 或 \"finish\", \"reason\": \"為什麼這樣規劃\"}"
    )
    user_prompt_full = "請根據目前查到的內容，決定下一步要查什麼，或說已經查完。"
    return system_prompt, user_prompt_full 