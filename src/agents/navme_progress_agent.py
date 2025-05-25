from src.tools.navme_tools import evaluate_progress

class NavmeProgressAgent:
    id = "navme_progress"
    name = "Navme 進度評估"
    description = "根據輸入評估進度與解鎖建議"
    example_queries = ["評估這週進度", "我可以進入下一階段嗎"]

    def respond(self, query: str, history=None, **kwargs):
        return evaluate_progress({}) 