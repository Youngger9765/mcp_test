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

def test_agent_registry_yaml_file_not_exist(monkeypatch):
    from src.agent_registry import AgentRegistry
    monkeypatch.setattr("os.path.exists", lambda path: False)
    registry = AgentRegistry()
    # 只要沒有 YAML agent 即可，允許 auto_test_agent 存在
    assert "agent_a" not in registry.list_agent_ids()
    assert "agent_b" not in registry.list_agent_ids()
    # 允許 auto_test_agent 或其他動態 agent 存在

def test_agent_registry_python_agents_exception(monkeypatch):
    from src.agent_registry import AgentRegistry
    monkeypatch.setattr(AgentRegistry, "_load_yaml_agents", lambda self: [])
    monkeypatch.setattr(AgentRegistry, "_load_python_agents", lambda self: (_ for _ in ()).throw(Exception("fail")))
    with pytest.raises(Exception):
        AgentRegistry()

def test_agent_registry_field_default(monkeypatch):
    from src.agent_registry import AgentRegistry
    yaml_agents = [{"id": "a"}]  # 缺所有欄位
    python_agents = [{"id": "b", "function": lambda: 1}]  # 只給 id, function
    monkeypatch.setattr(AgentRegistry, "_load_yaml_agents", lambda self: yaml_agents)
    monkeypatch.setattr(AgentRegistry, "_load_python_agents", lambda self: python_agents)
    registry = AgentRegistry()
    a = registry.get_agent("a")
    b = registry.get_agent("b")
    for field in ["example_queries", "category", "icon", "author", "version", "tags"]:
        assert field in a and field in b

def test_tool_registry_load_yaml_tools_file_not_exist(monkeypatch):
    from src import tool_registry
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()))
    # 若 open 失敗，應該拋出例外，可用 pytest.raises 驗證
    with pytest.raises(FileNotFoundError):
        tool_registry.load_yaml_tools("not_exist.yaml")

def test_tool_registry_load_yaml_tools_empty(monkeypatch):
    from src import tool_registry
    monkeypatch.setattr("builtins.open", lambda *a, **k: type("F", (), {"__enter__": lambda s: s, "__exit__": lambda s, a, b, c: None, "read": lambda s: "agents: []"})())
    monkeypatch.setattr("yaml.safe_load", lambda f: {"agents": []})
    tools = tool_registry.load_yaml_tools("fake.yaml")
    assert tools == []

def test_tool_registry_yaml_id_not_in_python(monkeypatch):
    from src import tool_registry
    # YAML 工具 id 不在 Python 工具清單
    monkeypatch.setattr(tool_registry, "load_yaml_tools", lambda: [{"id": "not_in_py", "name": "Y", "description": "D", "parameters": []}])
    result = tool_registry.get_tool_list()
    # merged 不會包含 not_in_py
    assert all(t["id"] != "not_in_py" for t in result)

def test_agent_registry_get_agent_not_exist():
    from src.agent_registry import AgentRegistry
    registry = AgentRegistry()
    assert registry.get_agent("not_exist") is None

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", side_effect=Exception("llm fail"))
def test_orchestrate_call_llm_exception(mock_llm, mock_tools):
    from src.orchestrator import orchestrate
    result = orchestrate("測試指令")
    assert result["type"] == "error"
    assert "llm fail" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value=None)
def test_orchestrate_llm_reply_none(mock_llm, mock_tools):
    from src.orchestrator import orchestrate
    result = orchestrate("測試指令")
    assert result["type"] == "error"

@patch("src.orchestrator.get_tool_list", side_effect=lambda: [{"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": lambda **kwargs: (_ for _ in ()).throw(TypeError("bad call"))}])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}}')
def test_orchestrate_tool_func_typeerror(mock_llm, mock_tools):
    from src.orchestrator import orchestrate
    result = orchestrate("測試指令")
    assert result["type"] == "error"

def test_tool_registry_all_python_tools(monkeypatch):
    from src import tool_registry
    monkeypatch.setattr(tool_registry, "load_yaml_tools", lambda: [])
    result = tool_registry.get_tool_list()
    # 應包含所有 PYTHON_TOOLS
    assert len(result) == len(tool_registry.PYTHON_TOOLS)

def main():
    tools = get_tool_list()
    for tool in tools:
        print(f"ID: {tool['id']}, 名稱: {tool['name']}, 說明: {tool['description']}")
        print(f"參數: {tool['parameters']}")
        print("------")

if __name__ == "__main__":
    main() 