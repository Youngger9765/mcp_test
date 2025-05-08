from agents.agent_a import respond as agent_a_respond
from agents.agent_b import respond as agent_b_respond
from agents.junyi_tree_agent import respond as junyi_tree_respond
from agents.junyi_topic_agent import respond as junyi_topic_respond
from agents.agent_openai import query as openai_query_llm

def test_agent_a_respond():
    result = agent_a_respond("測試問題")
    assert isinstance(result, str)
    assert "A Agent" in result

def test_agent_b_respond():
    result = agent_b_respond("測試問題")
    assert isinstance(result, str)
    assert "B Agent" in result

def test_junyi_tree_respond():
    result = junyi_tree_respond(topic_id="root", depth=1)
    assert isinstance(result, dict)
    # 可以根據 API 回傳內容再加細部 assert

def test_junyi_topic_respond():
    result = junyi_topic_respond(topic_id="root")
    assert isinstance(result, dict)
    # 可以根據 API 回傳內容再加細部 assert

def test_openai_query_llm():
    # 這個測試會真的呼叫 OpenAI API，建議 mock 或只測試格式
    result = openai_query_llm(instructions="你是誰？", input="你好")
    assert isinstance(result, str) 