from agent_registry import agent_manager

def check_schema(result, agent_id):
    errors = []
    # 檢查型別
    if not isinstance(result, dict):
        errors.append("Result is not a dict")
        return errors
    # 必要欄位
    for key in ["type", "content", "meta", "agent_id", "error"]:
        if key not in result:
            errors.append(f"Missing key: {key}")
    # agent_id
    if result.get("agent_id") != agent_id:
        errors.append(f"agent_id mismatch: {result.get('agent_id')} != {agent_id}")
    # error 欄位
    if result.get("error") is not None:
        errors.append(f"Error field is not None: {result.get('error')}")
    # meta 應該有 query
    if "meta" in result and "query" not in result["meta"]:
        errors.append("meta missing 'query'")
    return errors

def check_content(result, query):
    errors = []
    # type/content 基本檢查
    if result.get("type") == "text":
        text = result.get("content", {}).get("text", "")
        if query not in text:
            errors.append("Query string not found in content.text")
    elif result.get("type") == "tree":
        nodes = result.get("content", {}).get("nodes", [])
        if not isinstance(nodes, list) or not nodes:
            errors.append("Tree content nodes missing or not a list")
    # 你可以根據未來 type 再擴充
    return errors

report = []

for agent_id in ["agent_a", "agent_b", "junyi_tree_agent", "junyi_topic_agent"]:
    agent = agent_manager.get(agent_id)
    if agent:
        for q in agent.example_queries:
            result = agent.respond(q)
            schema_errors = check_schema(result, agent_id)
            content_errors = check_content(result, q)
            if not schema_errors and not content_errors:
                report.append(f"✅ {agent_id} | Query: {q} | PASS")
            else:
                report.append(f"❌ {agent_id} | Query: {q} | FAIL")
                for err in schema_errors + content_errors:
                    report.append(f"    - {err}")

print("=== MCP Agent Respond Schema & Content Check Report ===")
for line in report:
    print(line) 