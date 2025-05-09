class BAgent:
    id = "b_agent"
    name = "B Agent"
    description = "查詢 B 網站資料，資安相關"
    parameters = [
        {"name": "input_text", "type": "str"}
    ]

    def respond(self, input_text: str) -> dict:
        """回傳 B 網站資料查詢結果"""
        return {
            "type": "text",
            "content": {"text": f"[B Agent 回應] 針對：{input_text}，我查到 B 網站的相關資料。"},
            "meta": {"query": input_text},
            "agent_id": self.id,
            "error": None
        } 