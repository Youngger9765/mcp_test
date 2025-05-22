import pytest
from src.parameter_extraction import extract_parameters_from_query, get_required_params

# def test_add_tool_extraction():
#     tool_parameters = [
#         {"name": "a", "type": "int", "required": True},
#         {"name": "b", "type": "int", "required": True}
#     ]
#     query = "請幫我加 3 跟 5"
#     result = extract_parameters_from_query(query, tool_parameters)
#     assert result == {"a": 3, "b": 5}

# def test_add_tool_extraction_fail():
#     tool_parameters = [
#         {"name": "a", "type": "int", "required": True},
#         {"name": "b", "type": "int", "required": True}
#     ]
#     query = "請幫我加三跟五"
#     result = extract_parameters_from_query(query, tool_parameters)
#     assert result == {"a": 3, "b": 5}  # LLM 會自動轉換

def test_get_required_params():
    params = [
        {"name": "a", "type": "int", "required": True},
        {"name": "b", "type": "int", "default": 0},
        {"name": "c", "type": "str"},
        {"name": "d", "type": "str", "required": False},
    ]
    required = get_required_params(params)
    assert set(required) == {"a", "c"}  # a: required, c: 沒 default 也沒 required, b/d 都不是必填 