import json
from src.orchestrator_utils.llm_client import call_llm

def build_intent_prompt(user_input: str) -> str:
    return f"""
請判斷下列多輪對話的用戶最新輸入，意圖為何？只回傳 intent 類型（chat、tool_call、history_answer、other），以及簡短理由。
- 如果 history（對話紀錄）中已經有用戶要的答案，請回 history_answer。
- 如果只是閒聊、問候，請回 chat。
- 需要工具時才回 tool_call。
用戶輸入（多輪對話）：
{user_input}
請用 JSON 格式回覆，例如：
{{"intent": "history_answer", "reason": "history 已有答案"}}
{{"intent": "chat", "reason": "用戶只是打招呼"}}
{{"intent": "tool_call", "reason": "需要查詢"}}
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