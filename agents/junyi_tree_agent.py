import requests

JUNYI_SUB_TREE_API = "https://www.junyiacademy.org/api/v2/open/sub-tree/{topic_id}?depth={depth}"

def respond(topic_id: str = "root", depth: int = 3) -> str:
    """
    查詢均一課程樹，回傳指定 topic_id 與 depth 的課程結構摘要。
    """
    url = JUNYI_SUB_TREE_API.format(topic_id=topic_id, depth=depth)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        title = data.get("data", {}).get("title", "")
        children = data.get("data", {}).get("children", [])
        child_titles = [child.get("title", "") for child in children]
        return f"主題：{title}\n子主題：{', '.join(child_titles)}"
    except Exception as e:
        return f"查詢失敗: {str(e)}" 