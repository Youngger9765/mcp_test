import requests

JUNYI_TOPIC_PAGE_API = "https://www.junyiacademy.org/api/v2/open/content/topicpage/{topic_id}"

def get_junyi_topic(topic_id: str = "root"):
    """
    查詢均一 topic 內容，回傳該 topic 的標題、描述與子主題摘要。
    """
    url = JUNYI_TOPIC_PAGE_API.format(topic_id=topic_id)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        return {"error": str(e)} 