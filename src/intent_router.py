from typing import List

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