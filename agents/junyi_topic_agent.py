import requests

JUNYI_TOPIC_PAGE_API = "https://www.junyiacademy.org/api/v2/open/content/topicpage/{topic_id}"

def respond(topic_id: str = "root") -> str:
    """
    查詢均一 topic 內容，回傳該 topic 的標題、描述與子主題摘要。
    """
    url = JUNYI_TOPIC_PAGE_API.format(topic_id=topic_id)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        title = data.get("title", "")
        description = data.get("description", "")
        children = data.get("child", [])
        child_titles = [child.get("title", "") for child in children]
        child_ids = [child.get("topic_id", "") for child in children]
        child_info = [f"{t}({i})" for t, i in zip(child_titles, child_ids)]
        return f"主題：{title}\n描述：{description}\n子主題：{', '.join(child_info)}"
    except Exception as e:
        return f"查詢失敗: {str(e)}" 