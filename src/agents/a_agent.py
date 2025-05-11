class AAgent:
    id = "agent_a_tool"
    name = "A Agent 工具"
    description = "查詢 A 網站摘要，適合查詢電影、影片剪輯等相關內容。"
    category = "網路摘要"
    tags = ["影片", "剪輯", "摘要"]
    parameters = [
        {"name": "input_text", "type": "str", "description": "查詢內容，僅允許 10~100 字元中英文數字空白", "pattern": "^[\u4e00-\u9fa5a-zA-Z0-9 ]{10,100}$"}
    ]
    example_queries = [
        "請幫我查一下影片剪輯教學",
        "什麼是 YouTuber？"
    ]
    request_example = {"input_text": "請幫我查一下影片剪輯教學"}
    response_example = {"result": "這是影片剪輯教學的摘要..."}

    def respond(self, input_text: str) -> dict:
        """回傳 A 網站摘要結果"""
        return {
            "type": "text",
            "content": {"text": f"[A Agent 回應] 你問了：{input_text}，這是我從 A 網站取得的摘要。"},
            "meta": {"query": input_text},
            "agent_id": self.id,
            "error": None
        } 