import json
from typing import Any, Dict, List, Optional

def parse_llm_json_reply(reply: str, required_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    嘗試解析 LLM 回傳的 JSON，並檢查必填欄位，失敗則 raise Exception。
    """
    try:
        parsed = json.loads(reply)
    except Exception as e:
        raise Exception(f"LLM 回傳格式錯誤或解析失敗: {e}")
    if required_keys:
        for k in required_keys:
            if k not in parsed:
                raise Exception(f"缺少必填欄位: {k}")
    return parsed 