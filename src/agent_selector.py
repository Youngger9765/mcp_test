import os
from dotenv import load_dotenv
import openai
from src.agent_loader import load_yaml_agents

AGENT_LIST = load_yaml_agents() 

def choose_agents_via_llm(query):
    # TODO: 這裡應該用 LLM 分析 query，回傳 agent id list
    # 先 mock：全部 agent 都回傳
    from src.agent_loader import AGENT_LIST
    return [a["id"] for a in AGENT_LIST]

def choose_agents_from_options_via_llm(options, user_reply):
    # TODO: 這裡應該用 LLM 分析 user_reply，從 options 選 agent
    # 先 mock：全部 options 都回傳
    return [o["id"] for o in options] 