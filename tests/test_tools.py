import pytest
from unittest.mock import patch, MagicMock
import src.tools as tools

def test_add():
    assert tools.add(1, 2) == 9999

@patch("src.tools.get_junyi_tree_respond", return_value={"tree": "ok"})
def test_get_junyi_tree(mock_tree):
    result = tools.get_junyi_tree("tid", depth=2)
    assert result["type"] == "tree"
    assert result["meta"]["topic_id"] == "tid"
    assert result["meta"]["depth"] == 2
    assert result["content"] == {"tree": "ok"}

@patch("src.tools.get_junyi_topic_respond", return_value={"topic": "ok"})
def test_get_junyi_topic(mock_topic):
    result = tools.get_junyi_topic("tid")
    assert result["type"] == "topic"
    assert result["meta"]["topic_id"] == "tid"
    assert result["content"] == {"topic": "ok"}

@patch("src.tools.get_junyi_tree_respond", return_value={"tree": "T"})
@patch("src.tools.openai_query_llm", return_value="valid_id")
@patch("src.tools.get_junyi_topic_respond", return_value={"topic": "T2"})
def test_get_junyi_topic_by_title_success(mock_topic, mock_llm, mock_tree):
    result = tools.get_junyi_topic_by_title("標題")
    assert result["type"] == "topic_by_title"
    assert result["meta"]["topic_id"] == "valid_id"
    assert result["content"] == {"topic": "T2"}
    assert result["error"] is None

@patch("src.tools.get_junyi_tree_respond", return_value={"tree": "T"})
@patch("src.tools.openai_query_llm", return_value="!!!bad_id!!!")
def test_get_junyi_topic_by_title_invalid_id(mock_llm, mock_tree):
    result = tools.get_junyi_topic_by_title("標題")
    assert result["error"] is not None
    assert "不合法" in result["error"]["message"]

@patch("src.tools.get_junyi_tree_respond", return_value={"tree": "T"})
@patch("src.tools.openai_query_llm", return_value="valid_id")
@patch("src.tools.get_junyi_topic_respond", return_value={"error": "not found"})
def test_get_junyi_topic_by_title_junyi_error(mock_topic, mock_llm, mock_tree):
    result = tools.get_junyi_topic_by_title("標題")
    assert result["error"] is not None
    assert "查無主題內容" in result["error"]["message"]

@patch("src.tools.get_junyi_tree_respond", return_value={"tree": "T"})
@patch("src.tools.openai_query_llm", return_value="valid_id")
@patch("src.tools.get_junyi_topic_respond", side_effect=Exception("fail"))
def test_get_junyi_topic_by_title_junyi_exception(mock_topic, mock_llm, mock_tree):
    result = tools.get_junyi_topic_by_title("標題")
    assert result["error"] is not None
    assert "查詢 Junyi API 發生錯誤" in result["error"]["message"]

@patch("src.tools.AgentA")
def test_agent_a_tool(mock_agent):
    mock_agent.return_value.respond.return_value = {"a": 1}
    result = tools.agent_a_tool("input")
    assert result == {"a": 1}

@patch("src.tools.AgentB")
def test_agent_b_tool(mock_agent):
    mock_agent.return_value.respond.return_value = {"b": 2}
    result = tools.agent_b_tool("input")
    assert result == {"b": 2} 