class AgentB:
    id = "agent_b"
    name = "B Agent"
    description = "查詢 B 網站資料，資安相關"
    parameters = [{"name": "input_text", "type": "str"}]
    def respond(self, input_text: str) -> dict:
        return {
            "type": "text",
            "content": {"text": f"[B Agent 回應] 針對：{input_text}，我查到 B 網站的相關資料。"},
            "meta": {"query": input_text},
            "agent_id": "agent_b",
            "error": None
        } 