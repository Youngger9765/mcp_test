from agents.agent_a import respond as agent_a_respond
from agents.agent_b import respond as agent_b_respond
from agents.junyi_tree_agent import respond as junyi_tree_respond
from agents.junyi_topic_agent import respond as junyi_topic_respond

AGENT_LIST = [
    {
        "id": "agent_a",
        "name": "A Agent",
        "description": "適合查詢一般網路摘要、影片剪輯教學等資訊。",
        "example_queries": [
            "請幫我查一下影片剪輯教學",
            "什麼是 YouTuber？"
        ],
        "respond": agent_a_respond,
    },
    {
        "id": "agent_b",
        "name": "B Agent",
        "description": "適合查詢 B 網站的專業資料或特定主題。",
        "example_queries": [
            "B 網站有什麼新消息？"
        ],
        "respond": agent_b_respond,
    },
    {
        "id": "junyi_tree_agent",
        "name": "均一課程結構樹",
        "description": "適合查詢均一課程結構、單元樹狀圖等。",
        "example_queries": [
            "請列出課程結構",
            "這個主題有哪些延伸單元？"
        ],
        "respond": junyi_tree_respond,
    },
    {
        "id": "junyi_topic_agent",
        "name": "均一主題查詢",
        "description": "適合查詢均一某個主題的詳細內容。",
        "example_queries": [
            "請介紹分數的意義",
            "這個主題有哪些重點？"
        ],
        "respond": junyi_topic_respond,
    }
] 