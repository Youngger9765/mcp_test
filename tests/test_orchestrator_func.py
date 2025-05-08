import pytest
from unittest.mock import patch
from src.orchestrator import orchestrate, multi_turn_orchestrate, multi_turn_step

def fake_tool_func(**kwargs):
    return {"result": "ok", "input": kwargs}

def fake_tool_list():
    return [
        {"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": fake_tool_func}
    ]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {"x": 1}}')
def test_orchestrate(mock_llm, mock_tools):
    result = orchestrate("測試指令")
    assert result["type"] == "result"
    assert result["tool"] == "test_tool"
    assert result["input"] == {"x": 1}
    assert result["results"][0]["result"] == "ok"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm")
def test_multi_turn_orchestrate(mock_llm, mock_tools):
    # 先回傳 call_tool，再回傳 finish
    mock_llm.side_effect = [
        '{"tool_id": "test_tool", "parameters": {"x": 2}, "action": "call_tool", "reason": "step1"}',
        '{"tool_id": "test_tool", "parameters": {"x": 2}, "action": "finish", "reason": "done"}'
    ]
    result = multi_turn_orchestrate("多輪測試", max_turns=2)
    assert result["type"] == "multi_turn_result"
    assert result["history"][0]["tool_id"] == "test_tool"
    assert result["history"][0]["parameters"] == {"x": 2}
    assert result["history"][0]["result"]["result"] == "ok"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {"x": 3}, "action": "call_tool", "reason": "step"}')
def test_multi_turn_step(mock_llm, mock_tools):
    result = multi_turn_step([], "分步測試", max_turns=1)
    assert result["action"] == "call_tool"
    assert result["step"]["tool_id"] == "test_tool"
    assert result["step"]["parameters"] == {"x": 3}
    assert result["step"]["result"]["result"] == "ok"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='not a json')
def test_orchestrate_llm_not_json(mock_llm, mock_tools):
    result = orchestrate("測試指令")
    assert result["type"] == "error"
    assert "格式錯誤" in result["message"] or "解析失敗" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"parameters": {}}')
def test_orchestrate_llm_missing_tool_id(mock_llm, mock_tools):
    result = orchestrate("測試指令")
    assert result["type"] == "error"
    assert "缺少必填欄位" in result["message"]

@patch("src.orchestrator.get_tool_list", return_value=[])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "not_exist", "parameters": {}}')
def test_orchestrate_tool_not_found(mock_llm, mock_tools):
    result = orchestrate("測試指令")
    assert result["type"] == "error"
    assert "找不到工具" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=lambda: [{"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": lambda **kwargs: 1/0}])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}}')
def test_orchestrate_tool_func_exception(mock_llm, mock_tools):
    result = orchestrate("測試指令")
    assert result["type"] == "error"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", side_effect=[
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step1"}',
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step2"}',
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step3"}',
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step4"}',
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step5"}',
    '{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step6"}'
])
def test_multi_turn_orchestrate_max_turns(mock_llm, mock_tools):
    result = multi_turn_orchestrate("多輪測試", max_turns=3)
    assert result["type"] == "multi_turn_result"
    assert result["message"].startswith("已達最大輪數")
    assert len(result["history"]) == 3

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {"x": 1}, "action": "call_tool", "reason": "step"}')
def test_multi_turn_step_redundant(mock_llm, mock_tools):
    history = [{"tool_id": "test_tool", "parameters": {"x": 1}, "result": {"result": "ok"}, "reason": ""}]
    result = multi_turn_step(history, "分步測試", max_turns=1)
    assert result["action"] == "finish"
    assert "重複" in result["reason"] 