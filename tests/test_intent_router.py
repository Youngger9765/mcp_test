from src.intent_router import analyze_intent_by_context

# mock agent_list
agent_list = [
    {"id": "agent_a", "name": "A Agent", "description": "A agent"},
    {"id": "agent_b", "name": "B Agent", "description": "B agent"},
    {"id": "junyi_tree_agent", "name": "均一課程結構樹", "description": "junyi tree"},
    {"id": "junyi_topic_agent", "name": "均一主題查詢", "description": "junyi topic"},
]

def test_all_api():
    assert set(analyze_intent_by_context("給我全部的 API", None, None, agent_list)) == {"agent_a", "agent_b", "junyi_tree_agent", "junyi_topic_agent"}

def test_junyi():
    assert set(analyze_intent_by_context("我要查均一的課程", None, None, agent_list)) == {"junyi_tree_agent", "junyi_topic_agent"}

def test_b_site():
    assert analyze_intent_by_context("B 網站有什麼新消息？", None, None, agent_list) == ["agent_b"]

def test_a_site():
    assert analyze_intent_by_context("A 網站有什麼教學？", None, None, agent_list) == ["agent_a"]

def test_default():
    assert analyze_intent_by_context("隨便問一個", None, None, agent_list) == ["agent_a"] 