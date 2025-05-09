class AAgent:
    id = "a_agent"
    name = "A Agent"
    description = "查詢 A 網站摘要，電影相關"
    parameters = [
        {"name": "input_text", "type": "str"}
    ]

    def respond(self, input_text: str) -> dict:
        """回傳 A 網站摘要結果"""
        return {
            "type": "text",
            "content": {"text": f"[A Agent 回應] 你問了：{input_text}，這是我從 A 網站取得的摘要。"},
            "meta": {"query": input_text},
            "agent_id": self.id,
            "error": None
        } 