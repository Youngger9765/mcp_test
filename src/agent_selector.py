import os
from dotenv import load_dotenv
import openai
from src.intent_router import analyze_intents_via_llm
import json

def choose_agents_via_llm(query):
    from src.agent_loader import load_yaml_agents
    AGENT_LIST = load_yaml_agents()
    # 用 LLM 分析 query，回傳 agent id list
    return analyze_intents_via_llm(query, AGENT_LIST)

def choose_agents_from_options_via_llm(options, user_reply):
    # 用 LLM 分析 user_reply，從 options 選 agent
    return analyze_intents_via_llm(user_reply, options)

def analyze_intent_llm(
    user_query,
    last_agent_id=None,
    last_meta=None,
    topic_id=None,
    agent_list=None,
    topic_map=None,
    model="gpt-4.1-mini"
):
    """
    用 LLM 來判斷這一輪該呼叫哪個 agent（API）
    """
    prompt = f"""
你是一個多輪對話的 AI router，請根據以下資訊判斷這一輪該呼叫哪個 agent（API）：

- 使用者輸入（user_query）: {user_query}
- 上一輪 agent: {last_agent_id}
- 上一輪 meta: {last_meta}
- topic_id: {topic_id}
- 可用 agent: {json.dumps(agent_list, ensure_ascii=False)}
- 課程樹節點清單（topic_ids 與名稱）: {json.dumps(topic_map, ensure_ascii=False)}

如果上一輪是查詢課程結構（junyi_tree_agent），而這一輪的 user_query 或 topic_id 是上一輪回傳的節點 id，請自動 route 到主題查詢（junyi_topic_agent）。
如果 user_query 跟某個節點名稱（title）高度相關，也請 route 到 junyi_topic_agent，並將對應的 topic_id 傳給 agent。

請輸出一個 JSON，格式如下：
{{
  "agent_id": "xxx",
  "reason": "為什麼選這個 agent",
  "topic_id": "xxx"  // 如果有自動 match 到 topic_id
}}
"""
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}]
    )
    result = json.loads(response.choices[0].message.content)
    # 如果 LLM 有回傳 topic_id，優先用
    if "topic_id" in result and result["topic_id"]:
        topic_id = result["topic_id"]
    return result["agent_id"], result["reason"], topic_id 