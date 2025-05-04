import os
from dotenv import load_dotenv
import openai
from src.agent_loader import load_yaml_agents
from src.intent_router import analyze_intents_via_llm

AGENT_LIST = load_yaml_agents() 

def choose_agents_via_llm(query):
    # 用 LLM 分析 query，回傳 agent id list
    return analyze_intents_via_llm(query, AGENT_LIST)

def choose_agents_from_options_via_llm(options, user_reply):
    # 用 LLM 分析 user_reply，從 options 選 agent
    return analyze_intents_via_llm(user_reply, options) 