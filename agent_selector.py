import os
from dotenv import load_dotenv
import openai
from agent_registry import AGENT_LIST

load_dotenv()  # 自動載入 .env

# 建議用環境變數管理 API Key
openai.api_key = os.getenv("OPENAI_API_KEY", "")  # 請改成你的 key

def build_llm_prompt(query: str) -> tuple[str, str]:
    agent_descriptions = "\n".join([
        f"{agent['id']}：{agent['description']}（範例：{'、'.join(agent['example_queries'])}）"
        for agent in AGENT_LIST
    ])
    system_msg = (
        "你是一個語意分析引擔，負責根據使用者輸入的問題，選出所有可能適合的 Agent（可複選，請用逗號分隔 id）。\n"
        f"可選的 Agent 有：\n{agent_descriptions}\n"
        "只回傳 agent id（如：agent_a,agent_b），不要多餘解釋。"
    )
    user_msg = f"使用者的問題是：{query}\n請選擇所有可能的 Agent。"
    return system_msg, user_msg

def choose_agents_via_llm(query: str) -> list:
    system_msg, user_msg = build_llm_prompt(query)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0,
    )
    agent_ids = response.choices[0].message.content.strip().replace("，", ",").split(",")
    available_ids = [agent["id"] for agent in AGENT_LIST]
    # 過濾合法 id
    agent_ids = [aid.strip() for aid in agent_ids if aid.strip() in available_ids]
    return agent_ids

def choose_agent_via_llm(query: str) -> str:
    system_msg, user_msg = build_llm_prompt(query)
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0,
    )
    agent_id = response.choices[0].message.content.strip()
    available_ids = [agent["id"] for agent in AGENT_LIST]
    if agent_id in available_ids:
        return agent_id
    return "agent_a"  # fallback 

def choose_agents_from_options_via_llm(options: list, user_reply: str) -> list:
    """
    options: agent options, e.g. [{"id": "agent_a", "name": "...", "description": "..."}]
    user_reply: 用戶針對 options 的自然語言回覆
    """
    options_str = "\n".join([
        f"{o['id']}：{o['name']}，{o['description']}" for o in options
    ])
    system_msg = (
        "你是一個語意分析引擎，根據使用者的回覆，從下列 agent options 中選出最適合的 agent（可複選，請用逗號分隔 id）。\n"
        "如果使用者回覆「全部」、「all」、「都要」等，請回傳所有 agent 的 id。\n"
        f"可選的 agent options：\n{options_str}\n"
        "只回傳 agent id（如：agent_a,agent_b），不要多餘解釋。"
    )
    user_msg = f"使用者的回覆是：{user_reply}\n請選擇最適合的 agent。"

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        temperature=0,
    )
    agent_ids = response.choices[0].message.content.strip().replace("，", ",").split(",")
    available_ids = [o["id"] for o in options]
    agent_ids = [aid.strip() for aid in agent_ids if aid.strip() in available_ids]
    return agent_ids 