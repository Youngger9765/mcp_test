from src.tools.add_tool import add

class AddAgent:
    id = "add"
    name = "加法工具"
    description = "僅用於單純數字加法運算，不適用於查詢數學教材、教學主題或課程內容。"
    category = "數學運算"
    tags = ["運算", "加法"]
    parameters = [
        {"name": "a", "type": "int", "description": "第一個加數，只能是 1, 2, 3", "required": True, "enum": [1, 2, 3]},
        {"name": "b", "type": "str", "description": "第二個加數，只能是三位數字字串", "required": False, "default": "000", "pattern": "^\\d{3}$"}
    ]
    example_queries = [
        "a=1, b='123'",
        "a=2, b='456'"
    ]
    request_example = {"a": 1, "b": "123"}
    response_example = {"result": 124}

    def respond(self, a: int, b: str):
        try:
            if not isinstance(a, int):
                raise ValueError("a 必須是 int")
            if not (isinstance(b, str) and b.isdigit() and len(b) == 3):
                raise ValueError("b 必須是三位數字字串")
            result = add(a, int(b))
            return {
                "type": "add_result",
                "content": {"result": result},
                "meta": {"a": a, "b": b},
                "agent_id": self.id,
                "error": None
            }
        except Exception as e:
            return {
                "type": "add_result",
                "content": None,
                "meta": {"a": a, "b": b},
                "agent_id": self.id,
                "error": str(e)
            } 