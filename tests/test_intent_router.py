from src.intent_router import analyze_intent

def test_all_api():
    assert set(analyze_intent("給我全部的 API")) == {"agent_a", "agent_b", "junyi_tree_agent", "junyi_topic_agent"}

def test_junyi():
    assert set(analyze_intent("我要查均一的課程")) == {"junyi_tree_agent", "junyi_topic_agent"}

def test_b_site():
    assert analyze_intent("B 網站有什麼新消息？") == ["agent_b"]

def test_a_site():
    assert analyze_intent("A 網站有什麼教學？") == ["agent_a"]

def test_default():
    assert analyze_intent("隨便問一個") == ["agent_a"] 