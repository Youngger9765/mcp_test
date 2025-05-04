import requests

JUNYI_SUB_TREE_API = "https://www.junyiacademy.org/api/v2/open/sub-tree/{topic_id}?depth={depth}"

def respond(topic_id: str = "root", depth: int = 1) -> dict:
    """
    查詢均一課程樹，回傳指定 topic_id 與 depth 的課程結構摘要。
    """
    url = JUNYI_SUB_TREE_API.format(topic_id=topic_id, depth=depth)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {})
    except Exception as e:
        return {"error": str(e)} 