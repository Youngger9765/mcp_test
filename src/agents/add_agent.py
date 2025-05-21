from src.tools.add_tool import add
from src.agents import Agent # Import base class

class AddAgent(Agent): # Inherit from Agent
    def __init__(self):
        super().__init__(
            id="add",
            name="加法工具",
            description="僅用於單純數字加法運算，不適用於查詢數學教材、教學主題或課程內容。",
            category="數學運算",
            tags=["運算", "加法"],
            parameters=[
                {"name": "a", "type": "int", "description": "第一個加數，只能是 1, 2, 3", "required": True, "enum": [1, 2, 3]},
                {"name": "b", "type": "str", "description": "第二個加數，只能是三位數字字串", "required": False, "default": "000", "pattern": "^\\d{3}$"} # Note: pattern needs double backslash in Python string
            ],
            example_queries=[
                "a=1, b='123'",
                "a=2, b='456'"
            ],
            request_example={"a": 1, "b": "123"},
            response_example={"result": 124}
        )

    def respond(self, a: int, b: str): # ensure 'self' is present
        try:
            if not isinstance(a, int):
                raise ValueError("a 必須是 int")
            if not (isinstance(b, str) and b.isdigit() and len(b) == 3):
                raise ValueError("b 必須是三位數字字串")
            
            # The actual tool function should handle the core logic
            # The agent's respond method is for pre/post processing and calling the tool
            result_val = add(a, int(b)) 
            
            return {
                "type": "add_result",
                "content": {"result": result_val},
                "meta": {"a": a, "b": b},
                "agent_id": self.id, # self.id is now inherited
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