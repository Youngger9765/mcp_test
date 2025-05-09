from src.tools.add_tool import add

class AddAgent:
    id = "add_agent"
    name = "加法代理"
    description = "執行兩數相加"
    parameters = [
        {"name": "a", "type": "int"},
        {"name": "b", "type": "int"}
    ]

    def respond(self, a: int, b: int):
        result = add(a, b)
        return {
            "type": "add_result",
            "content": {"result": result},
            "meta": {"a": a, "b": b},
            "agent_id": self.id,
            "error": None
        } 