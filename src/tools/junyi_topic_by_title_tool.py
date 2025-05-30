import re
from src.tools.junyi_tree_tool import get_junyi_tree
from src.tools.junyi_topic_tool import get_junyi_topic
from src.tools.openai_tool import openai_query_llm

def get_junyi_topic_by_title(title: str):
    """
    Get the topic of均一 by title
    1. 先查詢 topic_id by get_junyi_tree
    2. 再查詢 topic_id 的 topic by get_junyi_topic
    """
    tree = get_junyi_tree(topic_id="root", depth=1)
    topic_id = openai_query_llm(
        instructions=f"你是一個均一課程結構樹的查詢工具，請根據使用者的問題，僅回傳課程樹中存在的 topic_id（純 id，不要說明文字），不要回傳任何說明或其他文字。",
        input=f"以下是均一課程結構樹：\n{tree}\n請根據使用者給定的標題：{title}，判斷最相關的 topic_id。"
    )
    # 僅允許 topic_id 為英數字、dash、underline
    if not topic_id or not re.match(r"^[\w\-]+$", str(topic_id).strip()):
        return {
            "type": "topic_by_title",
            "content": None,
            "meta": {"title": title, "topic_id": topic_id},
            "agent_id": "get_junyi_topic_by_title",
            "agent_name": "均一主題標題查詢",
            "error": {"message": f"LLM 回傳的 topic_id 不合法或不是純 id，請換個關鍵字或再試一次。LLM 回傳：{topic_id}"}
        }
    try:
        content = get_junyi_topic(topic_id=topic_id)
        if isinstance(content, dict) and "error" in content:
            return {
                "type": "topic_by_title",
                "content": None,
                "meta": {"title": title, "topic_id": topic_id},
                "agent_id": "get_junyi_topic_by_title",
                "agent_name": "均一主題標題查詢",
                "error": {"message": f"查無主題內容，請換個關鍵字。Junyi API: {content['error']}"}
            }
        return {
            "type": "topic_by_title",
            "content": content,
            "meta": {"title": title, "topic_id": topic_id},
            "agent_id": "get_junyi_topic_by_title",
            "agent_name": "均一主題標題查詢",
            "error": None
        }
    except Exception as e:
        return {
            "type": "topic_by_title",
            "content": None,
            "meta": {"title": title, "topic_id": topic_id},
            "agent_id": "get_junyi_topic_by_title",
            "agent_name": "均一主題標題查詢",
            "error": {"message": f"查詢 Junyi API 發生錯誤: {e}"}
        } 