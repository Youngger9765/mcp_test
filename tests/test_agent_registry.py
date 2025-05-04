import pytest

# 假設 agent_registry.py 目前還是 dict-based
from src.agent_registry import AGENT_LIST

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