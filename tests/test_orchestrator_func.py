import pytest
from unittest.mock import patch
from src.orchestrator import dispatch_agent_single_turn, dispatch_agent_multi_turn_step, is_redundant

def fake_tool_func(**kwargs):
    return {"result": "ok", "input": kwargs}

def fake_tool_list():
    return [
        {"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": fake_tool_func}
    ]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {"x": 1}}')
def test_dispatch_agent_single_turn(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "result"
    assert result["tool"] == "test_tool"
    assert result["input"] == {"x": 1}
    assert result["results"][0]["result"] == "ok"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm")
def test_dispatch_agent_multi_turn_step(mock_llm, mock_tools):
    # 先回傳 call_tool，再回傳 finish
    mock_llm.side_effect = [
        '{"tool_id": "test_tool", "parameters": {"x": 2}, "action": "call_tool", "reason": "step1"}',
        '{"tool_id": "test_tool", "parameters": {"x": 2}, "action": "finish", "reason": "done"}'
    ]
    result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
    # 根據實際 return 格式調整斷言
    assert "action" in result or "type" in result

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {"x": 3}, "action": "call_tool", "reason": "step"}')
def test_dispatch_agent_multi_turn_step_redundant(mock_llm, mock_tools):
    history = [{"tool_id": "test_tool", "parameters": {"x": 1}, "result": {"result": "ok"}, "reason": ""}]
    result = dispatch_agent_multi_turn_step(history, "分步測試", max_turns=1)
    assert result["action"] == "call_tool"
    assert result["step"]["reason"] == "step"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='not a json')
def test_dispatch_agent_single_turn_llm_not_json(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error"
    assert "格式錯誤" in result["message"] or "解析失敗" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"parameters": {}}')
def test_dispatch_agent_single_turn_llm_missing_tool_id(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error"
    assert "缺少必填欄位" in result["message"]

@patch("src.orchestrator.get_tool_list", return_value=[])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "not_exist", "parameters": {}}')
def test_dispatch_agent_single_turn_tool_not_found(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error"
    assert "找不到工具" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=lambda: [{"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": lambda **kwargs: 1/0}])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}}')
def test_dispatch_agent_single_turn_tool_func_exception(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", side_effect=Exception("llm error"))
def test_dispatch_agent_single_turn_call_llm_exception(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error" and "llm error" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value="{}")
@patch("src.orchestrator.parse_llm_json_reply", side_effect=Exception("parse error"))
def test_dispatch_agent_single_turn_parse_exception(mock_parse, mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error" and "parse error" in result["message"]

@patch("src.orchestrator.get_tool_list", return_value=[])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "not_exist", "parameters": {}}')
def test_dispatch_agent_single_turn_tool_not_found(mock_llm, mock_tools):
    result = dispatch_agent_single_turn("測試指令")
    assert result["type"] == "error" and "找不到工具" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}}')
def test_dispatch_agent_single_turn_tool_func_exception(mock_llm, mock_tools):
    with patch("src.orchestrator.get_tool_list", return_value=[{"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": lambda **kwargs: 1/0}]):
        result = dispatch_agent_single_turn("測試指令")
        assert result["type"] == "error"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", side_effect=Exception("llm error"))
def test_dispatch_agent_multi_turn_step_call_llm_exception(mock_llm, mock_tools):
    result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
    assert result["action"] == "error" and "llm error" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value="{}")
@patch("src.orchestrator.parse_llm_json_reply", side_effect=Exception("parse error"))
def test_dispatch_agent_multi_turn_step_parse_exception(mock_parse, mock_llm, mock_tools):
    result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
    assert result["action"] == "error" and "parse error" in result["message"]

@patch("src.orchestrator.get_tool_list", return_value=[])
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "not_exist", "parameters": {}, "action": "call_tool"}')
def test_dispatch_agent_multi_turn_step_tool_not_found(mock_llm, mock_tools):
    result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
    assert result["action"] == "error" and "找不到工具" in result["message"]

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}, "action": "call_tool"}')
def test_dispatch_agent_multi_turn_step_tool_func_exception(mock_llm, mock_tools):
    with patch("src.orchestrator.get_tool_list", return_value=[{"id": "test_tool", "name": "Test Tool", "description": "desc", "parameters": [], "function": lambda **kwargs: 1/0}]):
        result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
        assert result["action"] == "error"

@patch("src.orchestrator.get_tool_list", side_effect=fake_tool_list)
@patch("src.orchestrator.call_llm", return_value='{"tool_id": "test_tool", "parameters": {}, "action": "call_tool"}')
def test_dispatch_agent_multi_turn_step_is_redundant(mock_llm, mock_tools):
    # history 參數與新 step 相同，is_redundant 應為 True
    history = [{"parameters": {}}]
    result = dispatch_agent_multi_turn_step(history, "多輪測試", max_turns=2)
    assert result["action"] == "finish" and "重複" in result["reason"]

def test_is_redundant_empty_history():
    assert is_redundant([], {"parameters": {}}) is False

def test_log_call_decorator_print():
    with patch("builtins.print") as mock_print:
        with patch("src.orchestrator.get_tool_brief", return_value=[]), \
             patch("src.orchestrator.build_single_turn_prompt", return_value=("", "")), \
             patch("src.orchestrator.call_llm", return_value="{}"), \
             patch("src.orchestrator.parse_llm_json_reply", side_effect=Exception("parse error")):
            dispatch_agent_single_turn("test")
        assert mock_print.called 

@patch("src.orchestrator.get_tool_list", return_value=[])
@patch("src.orchestrator.call_llm", return_value='{"action": "finish", "reason": "done"}')
@patch("src.orchestrator.parse_llm_json_reply", return_value={"action": "finish", "reason": "done"})
def test_dispatch_agent_multi_turn_step_finish(mock_parse, mock_llm, mock_tools):
    from src.orchestrator import dispatch_agent_multi_turn_step
    result = dispatch_agent_multi_turn_step([], "多輪測試", max_turns=2)
    assert result["action"] == "finish"
    assert result["reason"] == "done"
    assert result["step"] is None 