class BAgent:
    id = "agent_b_tool"
    name = "B Agent 工具"
    description = "查詢 B 網站資料，適合查詢資安相關內容。"
    category = "專業查詢"
    tags = ["資安", "B網站"]
    parameters = [
        {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 5~50 字元英文小寫與數字", "pattern": "^[a-z0-9 ]{5,50}$"}
    ]
    example_queries = [
        "B 網站有什麼新消息？"
    ]
    request_example = {"input_text": "b 網站有什麼新消息？"}
    response_example = {"result": "B 網站最新消息如下..."}

    def respond(self, input_text: str) -> dict:
        """回傳 B 網站資料查詢結果"""
        return {
            "type": "text",
            "content": {"text": f"[B Agent 回應] 針對：{input_text}，我查到 B 網站的相關資料。"},
            "meta": {"query": input_text},
            "agent_id": self.id,
            "error": None
        } 