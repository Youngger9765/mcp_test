import json
from src.orchestrator_utils.llm_client import call_llm

def build_intent_prompt(user_input: str) -> str:
    return f"""
請判斷下列用戶輸入的意圖，僅回傳 intent 類型（chat、tool_call、other），以及簡短理由。
- 如果用戶只是打招呼、問候、閒聊、情感表達（如 hi、hello、你好、謝謝、掰掰），請務必回 chat。
- 只有在用戶明確要求查詢、計算、搜尋、工具操作時，才回 tool_call。
用戶輸入：
{user_input}
請用 JSON 格式回覆，例如：{{"intent": "tool_call", "reason": "用戶明確要求查詢或操作"}}
"""

def intent_analyzer(user_input: str) -> dict:
    prompt = build_intent_prompt(user_input)
    print("[intent_analyzer] prompt:\n", prompt)
    reply = call_llm(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你是一個意圖分類助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    print("[intent_analyzer] LLM 回傳:", reply)
    try:
        result = json.loads(reply)
        print("[intent_analyzer] 解析結果:", result)
        return result
    except Exception as e:
        print(f"[intent_analyzer] 解析失敗: {e}")
        return {"intent": "other", "reason": f"解析失敗: {e}", "raw": reply} 