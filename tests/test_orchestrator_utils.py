import pytest
from unittest.mock import patch
from src.orchestrator_utils.llm_client import call_llm
from src.orchestrator_utils.validator import parse_llm_json_reply

def test_call_llm_exception():
    with patch("openai.chat.completions.create", side_effect=Exception("fail")):
        with pytest.raises(Exception) as e:
            call_llm("gpt-4.1-mini", messages=[{"role": "system", "content": "hi"}])
        assert "OpenAI API 錯誤" in str(e.value)

def test_parse_llm_json_reply_invalid_json():
    with pytest.raises(Exception) as e:
        parse_llm_json_reply("not a json")
    assert "格式錯誤" in str(e.value)

def test_parse_llm_json_reply_missing_key():
    with pytest.raises(Exception) as e:
        parse_llm_json_reply("{}", required_keys=["foo"])
    assert "缺少必填欄位" in str(e.value)

def test_parse_llm_json_reply_success():
    d = parse_llm_json_reply('{"foo": 1}', required_keys=["foo"])
    assert d["foo"] == 1

def test_call_llm_success():
    class FakeChoice:
        def __init__(self, content):
            self.message = type('msg', (), {'content': content})
    class FakeResponse:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]
    with patch("openai.chat.completions.create", return_value=FakeResponse("hi!")):
        result = call_llm("gpt-4.1-mini", messages=[{"role": "system", "content": "hi"}])
        assert result == "hi!" 