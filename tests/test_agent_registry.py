import pytest
import yaml
import os

# 假設 agent_registry.py 目前還是 dict-based
from src.agent_loader import AGENT_LIST
import types

# 1. 測試 agent 註冊數量
def test_agent_count():
    assert len(AGENT_LIST) >= 2  # 目前至少有 2 個 agent

# 2. 測試每個 agent 必備欄位
@pytest.mark.parametrize("agent", AGENT_LIST)
def test_agent_fields(agent):
    for field in ["id", "name", "description", "example_queries", "respond"]:
        assert field in agent

# 3. 測試 respond function 回傳格式
@pytest.mark.parametrize("agent", AGENT_LIST)
def test_respond_format(agent):
    # 用 agent 的第一個 example query 測試
    query = agent["example_queries"][0]
    result = agent["respond"](query)
    # 檢查 response schema
    assert isinstance(result, dict)
    assert "type" in result
    assert "content" in result
    assert "meta" in result
    assert "agent_id" in result
    assert "error" in result

# 4. 測試 respond function 回傳 agent_id 正確
@pytest.mark.parametrize("agent", AGENT_LIST)
def test_respond_agent_id(agent):
    query = agent["example_queries"][0]
    result = agent["respond"](query)
    assert result["agent_id"] == agent["id"]

# 5. 測試 respond function error 欄位預設為 None
@pytest.mark.parametrize("agent", AGENT_LIST)
def test_respond_error_field(agent):
    query = agent["example_queries"][0]
    result = agent["respond"](query)
    assert result["error"] is None or isinstance(result["error"], dict)

def test_agent_list_not_empty():
    assert len(AGENT_LIST) > 0

def test_agent_id_unique():
    ids = [a["id"] for a in AGENT_LIST]
    assert len(ids) == len(set(ids)), "agent id 不可重複"

def test_respond_exception_handling():
    # 模擬一個會丟出例外的 agent
    class BadAgent:
        id = "bad"
        name = "Bad"
        description = "bad"
        example_queries = ["fail"]
        def respond(self, q):
            raise Exception("fail")
    agent = {
        "id": BadAgent.id,
        "name": BadAgent.name,
        "description": BadAgent.description,
        "example_queries": BadAgent.example_queries,
        "respond": BadAgent().respond
    }
    with pytest.raises(Exception) as excinfo:
        agent["respond"]("fail")
    assert "fail" in str(excinfo.value)

@pytest.mark.parametrize("agent", AGENT_LIST)
def test_example_queries_is_list(agent):
    assert isinstance(agent["example_queries"], list)
    assert len(agent["example_queries"]) > 0

@pytest.mark.parametrize("agent", AGENT_LIST)
def test_respond_is_callable(agent):
    assert callable(agent["respond"])

@pytest.mark.parametrize("agent", AGENT_LIST)
def test_schema_field_types(agent):
    query = agent["example_queries"][0]
    result = agent["respond"](query)
    assert isinstance(result["type"], str)
    assert isinstance(result["content"], (str, dict, list))
    assert isinstance(result["meta"], dict)
    assert isinstance(result["agent_id"], str)
    # error 可以是 None 或 dict
    assert result["error"] is None or isinstance(result["error"], dict)

@pytest.mark.parametrize("agent", AGENT_LIST)
def test_meta_field_content(agent):
    query = agent["example_queries"][0]
    result = agent["respond"](query)
    # meta 至少要有 timestamp 或其他自訂欄位（依你 schema 規範調整）
    assert isinstance(result["meta"], dict)

def test_yaml_python_merge_priority():
    """
    測試 YAML 與 Python agent 合併時，YAML 設定優先
    需先在 mcp_config.yaml 與 get_python_agents() 都設同 id agent，並檢查 name/description 是否以 YAML 為主
    """
    # 這裡假設 agent_a 同時存在於 YAML 與 Python
    agent_a = [a for a in AGENT_LIST if a["id"] == "agent_a"]
    if agent_a:
        assert agent_a[0]["name"] == "A Agent"  # 依你 YAML 設定調整

def test_agent_list_sync_with_config_and_python():
    """
    測試 AGENT_LIST 是否包含 YAML 與 Python 兩邊所有 agent（id 不重複）
    """
    from src.agent_loader import get_yaml_agents
    from src.agent_registry import get_python_agents
    yaml_ids = {a["id"] for a in get_yaml_agents()}
    py_ids = {a["id"] for a in get_python_agents()}
    agent_list_ids = {a["id"] for a in AGENT_LIST}
    # AGENT_LIST 必須包含所有 YAML agent
    assert yaml_ids <= agent_list_ids
    # AGENT_LIST 必須包含所有只存在於 Python 的 agent
    missing = (py_ids - yaml_ids) - agent_list_ids
    assert not missing, f"以下只存在於 Python 的 agent 沒有被合併進 AGENT_LIST: {missing}"

def test_yaml_only_agent_in_agent_list():
    from src.agent_loader import get_yaml_agents
    from src.agent_registry import get_python_agents
    yaml_ids = {a["id"] for a in get_yaml_agents()}
    py_ids = {a["id"] for a in get_python_agents()}
    yaml_only_ids = yaml_ids - py_ids
    agent_list_ids = {a["id"] for a in AGENT_LIST}
    for agent_id in yaml_only_ids:
        assert agent_id in agent_list_ids, f"YAML only agent {agent_id} 應該出現在 AGENT_LIST"

def test_routes_agents_exist_in_agent_list():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'mcp_config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    agent_ids = {a["id"] for a in AGENT_LIST}
    for route in config.get("routes", {}).values():
        for step in route.get("steps", []):
            assert step["agent"] in agent_ids, f"route 裡的 agent {step['agent']} 不在 AGENT_LIST" 