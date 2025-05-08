from src.tool_registry import get_tool_list
from typing import List, Dict

def get_tool_brief() -> List[Dict]:
    tools = get_tool_list()
    return [
        {
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "parameters": t.get("parameters", [])
        }
        for t in tools
    ] 