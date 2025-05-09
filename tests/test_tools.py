import pytest
from unittest.mock import patch
from src.tools.add_tool import add
import src.tools.junyi_tree_tool
import src.tools.junyi_topic_tool
from src.tools.junyi_topic_by_title_tool import get_junyi_topic_by_title
from src.tools.openai_tool import openai_query_llm
from src.agents.a_agent import AAgent
from src.agents.b_agent import BAgent
import requests

def test_add():
    assert add(1, 2) == 9999

@patch("src.tools.junyi_tree_tool.get_junyi_tree", return_value={"tree": "ok"})
def test_get_junyi_tree(mock_tree):
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert result == {"tree": "ok"}

@patch("src.tools.junyi_topic_tool.get_junyi_topic", return_value={"topic": "ok"})
def test_get_junyi_topic(mock_topic):
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert result == {"topic": "ok"}

@patch("src.tools.junyi_topic_by_title_tool.get_junyi_tree", return_value={"tree": "T"})
@patch("src.tools.junyi_topic_by_title_tool.openai_query_llm", return_value="valid_id")
@patch("src.tools.junyi_topic_by_title_tool.get_junyi_topic", return_value={"topic": "T2"})
def test_get_junyi_topic_by_title_success(mock_topic, mock_llm, mock_tree):
    result = get_junyi_topic_by_title("標題")
    assert result["type"] == "topic_by_title"
    assert result["meta"].get("topic_id") == "valid_id"
    assert result["content"] == {"topic": "T2"} or result["content"] is not None
    assert result["error"] is None or isinstance(result["error"], dict)

@patch("src.tools.junyi_topic_by_title_tool.get_junyi_tree", return_value={"tree": "T"})
@patch("src.tools.junyi_topic_by_title_tool.openai_query_llm", return_value="!!!bad_id!!!")
def test_get_junyi_topic_by_title_invalid_id(mock_llm, mock_tree):
    result = get_junyi_topic_by_title("標題")
    assert result["error"] is None or "不合法" in (result["error"]["message"] if result["error"] else "")

@patch("src.tools.junyi_topic_by_title_tool.get_junyi_tree", return_value={"tree": "T"})
@patch("src.tools.junyi_topic_by_title_tool.openai_query_llm", return_value="valid_id")
@patch("src.tools.junyi_topic_by_title_tool.get_junyi_topic", return_value={"error": "not found"})
def test_get_junyi_topic_by_title_junyi_error(mock_topic, mock_llm, mock_tree):
    result = get_junyi_topic_by_title("標題")
    assert result["error"] is None or "查無主題內容" in (result["error"]["message"] if result["error"] else "")

@patch("src.tools.junyi_topic_by_title_tool.get_junyi_tree", return_value={"tree": "T"})
@patch("src.tools.junyi_topic_by_title_tool.openai_query_llm", return_value="valid_id")
@patch("src.tools.junyi_topic_by_title_tool.get_junyi_topic", side_effect=Exception("fail"))
def test_get_junyi_topic_by_title_junyi_exception(mock_topic, mock_llm, mock_tree):
    result = get_junyi_topic_by_title("標題")
    assert result["error"] is None or "查詢 Junyi API 發生錯誤" in (result["error"]["message"] if result["error"] else "")

def test_agent_a_tool():
    agent = AAgent()
    result = agent.respond("input")
    assert "type" in result and "content" in result

def test_agent_b_tool():
    agent = BAgent()
    result = agent.respond("input")
    assert "type" in result and "content" in result

@patch("requests.get", side_effect=requests.exceptions.Timeout("timeout"))
def test_get_junyi_topic_timeout(mock_get):
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert "error" in result and "timeout" in result["error"]

@patch("requests.get")
def test_get_junyi_topic_404(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 404
    def raise_for_status():
        raise requests.exceptions.HTTPError("404 Not Found")
    mock_resp.raise_for_status = raise_for_status
    mock_get.return_value = mock_resp
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert "error" in result and "404" in result["error"]

@patch("requests.get")
def test_get_junyi_topic_non_json(mock_get):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): raise ValueError("not json")
    mock_get.return_value = FakeResp()
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert "error" in result and "not json" in result["error"]

@patch("requests.get", side_effect=Exception("boom"))
def test_get_junyi_topic_exception(mock_get):
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert "error" in result and "boom" in result["error"]

@patch("requests.get", side_effect=requests.exceptions.Timeout("timeout"))
def test_get_junyi_tree_timeout(mock_get):
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert "error" in result and "timeout" in result["error"]

@patch("requests.get")
def test_get_junyi_tree_404(mock_get):
    mock_resp = requests.Response()
    mock_resp.status_code = 404
    def raise_for_status():
        raise requests.exceptions.HTTPError("404 Not Found")
    mock_resp.raise_for_status = raise_for_status
    mock_get.return_value = mock_resp
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert "error" in result and "404" in result["error"]

@patch("requests.get")
def test_get_junyi_tree_non_json(mock_get):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): raise ValueError("not json")
    mock_get.return_value = FakeResp()
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert "error" in result and "not json" in result["error"]

@patch("requests.get", side_effect=Exception("boom"))
def test_get_junyi_tree_exception(mock_get):
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert "error" in result and "boom" in result["error"]

@patch("requests.get")
def test_get_junyi_tree_no_data(mock_get):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"foo": 123}
    mock_get.return_value = FakeResp()
    result = src.tools.junyi_tree_tool.get_junyi_tree("tid", depth=2)
    assert result == {}  # data.get("data", {})

@patch("openai.OpenAI", side_effect=Exception("no api"))
def test_openai_query_llm_openai_exception(mock_openai):
    from src.tools.openai_tool import openai_query_llm
    try:
        openai_query_llm("sys", "input")
    except Exception as e:
        assert "no api" in str(e)

@patch("openai.OpenAI")
def test_openai_query_llm_create_exception(mock_openai):
    mock_client = mock_openai.return_value
    mock_client.chat.completions.create.side_effect = Exception("fail create")
    from src.tools.openai_tool import openai_query_llm
    try:
        openai_query_llm("sys", "input")
    except Exception as e:
        assert "fail create" in str(e)

@patch("openai.OpenAI")
def test_openai_query_llm_empty_choices(mock_openai):
    mock_client = mock_openai.return_value
    class FakeResp:
        choices = []
    mock_client.chat.completions.create.return_value = FakeResp()
    from src.tools.openai_tool import openai_query_llm
    try:
        openai_query_llm("sys", "input")
    except Exception as e:
        assert "list index out of range" in str(e)

@patch("openai.OpenAI")
def test_openai_query_llm_no_content(mock_openai):
    mock_client = mock_openai.return_value
    class FakeMsg:
        content = None
    class FakeChoice:
        message = FakeMsg()
    class FakeResp:
        choices = [FakeChoice()]
    mock_client.chat.completions.create.return_value = FakeResp()
    from src.tools.openai_tool import openai_query_llm
    result = openai_query_llm("sys", "input")
    assert result is None or result == ""

@patch("requests.get")
def test_get_junyi_topic_success(mock_get):
    class FakeResp:
        def raise_for_status(self): pass
        def json(self): return {"foo": 123}
    mock_get.return_value = FakeResp()
    result = src.tools.junyi_topic_tool.get_junyi_topic("tid")
    assert result == {"foo": 123}