from src.tool_registry import get_tool_list
import types

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
    # 假設未來有 AgentRegistry/Manager class
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    # 測試能取得所有 agent id
    agent_ids = registry.list_agent_ids()
    assert isinstance(agent_ids, list)
    assert "agent_a" in agent_ids
    assert "agent_b" in agent_ids
    # 測試能用 id 查到 agent function
    agent = registry.get_agent("agent_a")
    assert agent is not None
    assert callable(agent["function"])
    # 測試 YAML 與 Python agent 合併（假設 YAML 有 agent_a, Python 有 agent_b）
    # 這裡可根據實際合併策略調整

def test_yaml_python_agent_merge(monkeypatch):
    # 模擬 YAML agents
    yaml_agents = [
        {
            "id": "agent_a",
            "name": "YAML A",
            "description": "YAML 版本的 A",
            "parameters": [],
        },
        {
            "id": "agent_yaml_only",
            "name": "YAML Only",
            "description": "只在 YAML 的 agent",
            "parameters": [],
        }
    ]
    # 模擬 Python agents
    def py_func_a(x): return "python a"
    def py_func_b(x): return "python b"
    python_agents = [
        {
            "id": "agent_a",
            "name": "Python A",
            "description": "Python 版本的 A",
            "parameters": [],
            "function": py_func_a,
        },
        {
            "id": "agent_b",
            "name": "Python B",
            "description": "Python 版本的 B",
            "parameters": [],
            "function": py_func_b,
        }
    ]

    # 假設 AgentRegistry 有 _load_yaml_agents, _load_python_agents 可被 monkeypatch
    from src.agent_registry import AgentRegistry
    monkeypatch.setattr(AgentRegistry, "_load_yaml_agents", lambda self: yaml_agents)
    monkeypatch.setattr(AgentRegistry, "_load_python_agents", lambda self: python_agents)

    registry = AgentRegistry()
    agent_ids = registry.list_agent_ids()
    # 應包含三個 id
    assert set(agent_ids) == {"agent_a", "agent_b", "agent_yaml_only"}

    # agent_a metadata 以 YAML 為主，function 以 Python 為主
    agent_a = registry.get_agent("agent_a")
    assert agent_a["name"] == "YAML A"
    assert agent_a["description"] == "YAML 版本的 A"
    assert callable(agent_a["function"])
    assert agent_a["function"]("test") == "python a"

    # agent_b 只在 Python
    agent_b = registry.get_agent("agent_b")
    assert agent_b["name"] == "Python B"
    assert agent_b["function"]("test") == "python b"

    # agent_yaml_only 只在 YAML，沒有 function
    agent_yaml_only = registry.get_agent("agent_yaml_only")
    assert agent_yaml_only["name"] == "YAML Only"
    assert "function" not in agent_yaml_only or agent_yaml_only["function"] is None

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

def test_agent_metadata_rich_fields():
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    agent = registry.get_agent("agent_a")
    # 測試常見 metadata 欄位
    assert "name" in agent
    assert "description" in agent
    assert "parameters" in agent
    # 新增 metadata 欄位
    for field in ["example_queries", "category", "icon", "author", "version", "tags"]:
        assert field in agent

def main():
    tools = get_tool_list()
    for tool in tools:
        print(f"ID: {tool['id']}, 名稱: {tool['name']}, 說明: {tool['description']}")
        print(f"參數: {tool['parameters']}")
        print("------")

if __name__ == "__main__":
    main() 