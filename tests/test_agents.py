import pytest
from agents.agent_a import AgentA
from agents.agent_b import AgentB

@pytest.mark.parametrize("AgentClass", [AgentA, AgentB])
def test_agent_respond_schema(AgentClass):
    agent = AgentClass()
    result = agent.respond("test input")
    assert isinstance(result, dict)
    for key in ["type", "content", "meta", "agent_id", "error"]:
        assert key in result 