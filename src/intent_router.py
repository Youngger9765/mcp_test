from typing import List
import openai
import os
from dotenv import load_dotenv
import re

load_dotenv()  # 這行會自動載入 .env 檔

# 載入 API KEY（建議你已經有 .env 或環境變數）
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def analyze_intent_by_context(user_query, last_agent_id, last_meta, agent_list):
    """
    根據 user_query、上一輪 agent_id/meta、agent_list，判斷本輪最有可能的 agent。
    測試需求：
    1. '全部'、'ALL'、'API' 關鍵字 → 所有 agent
    2. '均一' 關鍵字 → junyi_tree_agent, junyi_topic_agent
    3. 'B 網站' 關鍵字 → agent_b
    4. 'A 網站' 關鍵字 → agent_a
    5. 其他 → agent_a
    """
    # 1. 如果上一輪是課程樹，且 user_query 跟 topic_ids 或 title 有關，推測是主題查詢
    if last_agent_id == "junyi_tree_agent" and last_meta:
        topic_ids = last_meta.get("topic_ids", [])
        # 直接輸入 topic_id
        if user_query in topic_ids:
            return ["junyi_topic_agent"]
        # fuzzy match title
        if "content" in last_meta:
            def collect_id_title(tree):
                result = []
                if isinstance(tree, dict):
                    if "id" in tree and "title" in tree:
                        result.append({"id": tree["id"], "title": tree["title"]})
                    if "children" in tree:
                        for child in tree["children"]:
                            result.extend(collect_id_title(child))
                elif isinstance(tree, list):
                    for node in tree:
                        result.extend(collect_id_title(node))
                return result
            topic_map = collect_id_title(last_meta["content"])
            for t in topic_map:
                if t["title"].replace(" ", "") in user_query.replace(" ", "") or user_query.replace(" ", "") in t["title"].replace(" ", ""):
                    return ["junyi_topic_agent"]
    # 關鍵字判斷
    q = user_query.lower()
    if any(k in user_query for k in ["全部", "ALL", "API"]):
        return [a["id"] for a in agent_list]
    if "均一" in user_query:
        return ["junyi_tree_agent", "junyi_topic_agent"]
    if "b 網站" in q:
        return ["agent_b"]
    if "a 網站" in q:
        return ["agent_a"]
    # fallback
    return ["agent_a"]

def call_agent_by_llm(user_query, last_agent_id, last_meta, topic_id):
    # 如果上一輪是課程樹，且 user_query/或 topic_id 是 topic_ids 之一，直接 route
    if last_agent_id == "junyi_tree_agent" and last_meta and "topic_ids" in last_meta:
        topic_ids = last_meta["topic_ids"]
        if user_query in topic_ids:
            agent_id = "junyi_topic_agent"
            agent = agent_manager.get(agent_id)
            result = agent.respond(user_query, topic_id=user_query, parent_query=last_meta.get("query"))
            result["meta"]["llm_reason"] = "user_input is topic_id, auto route to junyi_topic_agent"
            return {
                "type": "result",
                "results": [result]
            }

    # 其餘全部交給 LLM
    agent_list = [
        {"id": a.id, "name": a.name, "description": a.description}
        for a in agent_manager.all_agents()
    ]
    topic_map = []
    if last_meta and "topic_ids" in last_meta and "content" in last_meta:
        def collect_id_title(tree):
            result = []
            if isinstance(tree, dict):
                if "id" in tree and "title" in tree:
                    result.append({"id": tree["id"], "title": tree["title"]})
                if "children" in tree:
                    for child in tree["children"]:
                        result.extend(collect_id_title(child))
            elif isinstance(tree, list):
                for node in tree:
                    result.extend(collect_id_title(node))
            return result
        topic_map = collect_id_title(last_meta["content"])
    agent_id, reason, topic_id_from_llm = analyze_intent_llm(
        user_query=user_query,
        last_agent_id=last_agent_id,
        last_meta=last_meta,
        topic_id=topic_id,
        agent_list=agent_list,
        topic_map=topic_map
    )
    if topic_id_from_llm:
        topic_id = topic_id_from_llm
    agent = agent_manager.get(agent_id)
    kwargs = {}
    if topic_id:
        kwargs["topic_id"] = topic_id
    if last_meta and "query" in last_meta:
        kwargs["parent_query"] = last_meta["query"]
    result = agent.respond(user_query, **kwargs)
    result["meta"]["llm_reason"] = reason
    return {
        "type": "result",
        "results": [result]
    } 

# 讓外部可以 import analyze_intent
analyze_intent = analyze_intents_via_llm 