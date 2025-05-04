from typing import List
import openai
import os
from dotenv import load_dotenv

load_dotenv()  # 這行會自動載入 .env 檔

# 載入 API KEY（建議你已經有 .env 或環境變數）
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_intent(query: str) -> List[str]:
    query = query.lower()
    if "全部" in query or "all" in query or "api" in query:
        # 回傳所有 agent
        return ["agent_a", "agent_b", "junyi_tree_agent", "junyi_topic_agent"]
    if "均一" in query:
        # 回傳所有均一相關 agent
        return ["junyi_tree_agent", "junyi_topic_agent"]
    if "b 網站" in query:
        return ["agent_b"]
    if "a 網站" in query:
        return ["agent_a"]
    # 預設回傳 agent_a
    return ["agent_a"]

def analyze_intents_via_llm(query, agent_list):
    """
    用 LLM 分析 query，回傳相關 agent id list（可多個）。
    """
    agent_desc = "\n".join([f"{a['id']}: {a['name']} - {a['description']} 範例: {', '.join(a.get('example_queries', []))}" for a in agent_list])
    prompt = f"""你是一個智慧意圖分析器，請根據使用者的問題，判斷最相關的 agent（可多選），只回傳 agent id list（用逗號分隔）。
已知 agent 有：
{agent_desc}

請根據 agent 的描述與範例，盡量只選最相關的 agent id。

使用者問題：
{query}

請只回傳 agent id list（用逗號分隔），不要其他說明。
"""
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=124,
    )
    text = response.choices[0].message.content.strip()
    ids = [x.strip() for x in text.split(",") if x.strip()]
    return ids 