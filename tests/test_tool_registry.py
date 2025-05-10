from src.tool_registry import get_tool_list
import types
import pytest
from unittest.mock import patch

def fake_tool_func(**kwargs):
    return {"result": "ok", "input": kwargs}

def fake_tool_list():
    return [
        {"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": fake_tool_func}
    ]

def test_tool_list_not_empty():
    tools = get_tool_list()
    assert isinstance(tools, list)
    assert len(tools) > 0
    for tool in tools:
        assert "id" in tool
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
        assert "function" in tool

def test_tool_metadata_and_function_separation():
    tools = get_tool_list()
    for tool in tools:
        # 檢查 metadata
        for key in ["id", "name", "description", "parameters"]:
            assert key in tool
        # 檢查 function/callable
        assert callable(tool["function"])
        # function 不應該直接是 metadata dict
        assert not isinstance(tool["function"], dict)

def test_agent_registry_manager():
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    agent_ids = registry.list_agent_ids()
    assert isinstance(agent_ids, list)
    # 不再假設 agent_a/agent_b 一定存在
    # 測試能用 id 查到 agent function（若有 agent）
    if agent_ids:
        agent = registry.get_agent(agent_ids[0])
        assert agent is not None
        if agent["function"] is not None:
            assert callable(agent["function"])

def test_agent_metadata_rich_fields():
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    agent_ids = registry.list_agent_ids()
    if not agent_ids:
        return  # 沒有 agent 則跳過
    agent = registry.get_agent(agent_ids[0])
    # 測試常見 metadata 欄位
    assert "name" in agent
    assert "description" in agent
    assert "parameters" in agent
    for field in ["example_queries", "category", "icon", "author", "version", "tags"]:
        assert field in agent

def test_auto_scan_agents(monkeypatch, tmp_path):
    # 動態建立一個假的 agents 目錄與 agent class
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    agent_code = """
class AutoTestAgent:
    id = "auto_test_agent"
    name = "Auto Test Agent"
    description = "自動掃描測試 agent"
    parameters = [{"name": "input_text", "type": "str"}]
    def respond(self, input_text):
        return {"type": "text", "content": {"text": input_text}, "meta": {}, "agent_id": "auto_test_agent", "error": None}
"""
    (agents_dir / "auto_test_agent.py").write_text(agent_code, encoding="utf-8")

    # monkeypatch sys.path 與 agents module
    import sys
    sys.path.insert(0, str(tmp_path))
    import importlib
    import types
    agents_pkg = types.ModuleType("agents")
    agents_pkg.__path__ = [str(agents_dir)]
    sys.modules["agents"] = agents_pkg

    # monkeypatch AgentRegistry._load_python_agents
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    # 這裡假設 _load_python_agents 會自動掃描 agents/ 目錄
    agent_ids = registry.list_agent_ids()
    assert "auto_test_agent" in agent_ids
    agent = registry.get_agent("auto_test_agent")
    assert agent["name"] == "Auto Test Agent"
    assert callable(agent["function"])
    assert agent["function"]("hello")["content"]["text"] == "hello"

def test_agent_registry_get_agent_not_exist():
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    assert registry.get_agent("not_exist") is None

def main():
    tools = get_tool_list()
    for tool in tools:
        print(f"ID: {tool['id']}, 名稱: {tool['name']}, 說明: {tool['description']}")
        print(f"參數: {tool['parameters']}")
        print("------")

if __name__ == "__main__":
    main() 