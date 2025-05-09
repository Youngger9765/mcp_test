import pytest
from src.agents.a_agent import AAgent
from src.agents.b_agent import BAgent
from src.agents.add_agent import AddAgent
from unittest.mock import patch
from src.agents.junyi_topic_agent import JunyiTopicAgent
from src.agents.junyi_topic_by_title_agent import JunyiTopicByTitleAgent
from src.agents.junyi_tree_agent import JunyiTreeAgent

@pytest.mark.parametrize("AgentClass", [AAgent, BAgent])
def test_agent_respond_schema(AgentClass):
    agent = AgentClass()
    result = agent.respond("test input")
    assert isinstance(result, dict)
    for key in ["type", "content", "meta", "agent_id", "error"]:
        assert key in result 

def test_add_agent_normal():
    agent = AddAgent()
    result = agent.respond(1, 2)
    assert result["type"] == "add_result"
    assert result["content"]["result"] == 9999 or isinstance(result["content"]["result"], int)

def test_add_agent_non_int():
    agent = AddAgent()
    result = agent.respond("a", "b")
    assert result["content"]["result"] == 9999

def test_add_agent_missing_param():
    agent = AddAgent()
    with pytest.raises(TypeError):
        agent.respond(1)

@patch("src.agents.add_agent.add", side_effect=Exception("fail add"))
def test_add_agent_add_exception(mock_add):
    agent = AddAgent()
    with pytest.raises(Exception):
        agent.respond(1, 2)

@patch("src.agents.junyi_topic_agent.get_junyi_topic", side_effect=Exception("fail topic"))
def test_junyi_topic_agent_tool_exception(mock_tool):
    agent = JunyiTopicAgent()
    with pytest.raises(Exception) as e:
        agent.respond("tid")
    assert "fail topic" in str(e.value)

@patch("src.agents.junyi_topic_by_title_agent.get_junyi_topic_by_title", side_effect=Exception("fail by title"))
def test_junyi_topic_by_title_agent_tool_exception(mock_tool):
    agent = JunyiTopicByTitleAgent()
    with pytest.raises(Exception) as e:
        agent.respond("標題")
    assert "fail by title" in str(e.value)

@patch("src.agents.junyi_tree_agent.get_junyi_tree", side_effect=Exception("fail tree"))
def test_junyi_tree_agent_tool_exception(mock_tool):
    agent = JunyiTreeAgent()
    with pytest.raises(Exception) as e:
        agent.respond("tid")
    assert "fail tree" in str(e.value) 