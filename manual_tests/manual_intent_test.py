from src.intent_router import analyze_intent_by_context

# mock agent_list
agent_list = [
    {"id": "agent_a", "name": "A Agent", "description": "A agent"},
    {"id": "agent_b", "name": "B Agent", "description": "B agent"},
    {"id": "junyi_tree_agent", "name": "均一課程結構樹", "description": "junyi tree"},
    {"id": "junyi_topic_agent", "name": "均一主題查詢", "description": "junyi topic"},
]

# 範例測試
if __name__ == "__main__":
    print(analyze_intent_by_context("給我全部的 API", None, None, agent_list))

test_cases = [
    {
        "name": "test_all_api",
        "query": "給我全部的 API",
        "expected": {"agent_a", "agent_b", "junyi_tree_agent", "junyi_topic_agent"},
        "desc": "全部/ALL/API 關鍵字 → 所有 agent"
    },
    {
        "name": "test_junyi",
        "query": "我要查均一的課程",
        "expected": {"junyi_tree_agent", "junyi_topic_agent"},
        "desc": "均一 關鍵字 → 均一相關 agent"
    },
    {
        "name": "test_b_site",
        "query": "B 網站有什麼新消息？",
        "expected": {"agent_b"},
        "desc": "B 網站 關鍵字 → agent_b"
    },
    {
        "name": "test_a_site",
        "query": "A 網站有什麼教學？",
        "expected": {"agent_a"},
        "desc": "A 網站 關鍵字 → agent_a"
    },
    {
        "name": "test_default",
        "query": "隨便問一個",
        "expected": {"agent_a"},
        "desc": "預設 → agent_a"
    },
]

print("=== MCP Intent Analysis Test Report ===\n")
pass_count = 0

for case in test_cases:
    actual = set(analyze_intent_by_context(case["query"], None, None, agent_list))
    expected = case["expected"]
    print(f"[{case['name']}] {case['desc']}")
    print(f"  - Query:    {case['query']}")
    print(f"  - Expected: {sorted(expected)}")
    print(f"  - Actual:   {sorted(actual)}")
    if actual == expected:
        print("    ✅ PASS\n")
        pass_count += 1
    else:
        print("    ❌ FAIL\n")

print(f"=== Summary: {pass_count}/{len(test_cases)} PASS ===") 