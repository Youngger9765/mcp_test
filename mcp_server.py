from mcp.server.fastmcp import FastMCP
from src.tools.junyi_tree_tool import get_junyi_tree
from src.tools.junyi_topic_tool import get_junyi_topic
from src.tools.junyi_topic_by_title_tool import get_junyi_topic_by_title

# 建立 MCP server
mcp = FastMCP("mcp_local")

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str):
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 均一樹 as tool
@mcp.tool()
def mcp_tool_get_junyi_tree(topic_id: str):
    """Get the tree of均一"""
    return get_junyi_tree(topic_id, depth=1)

@mcp.tool()
def mcp_tool_get_junyi_topic(topic_id: str):
    """Get the topic of均一"""
    return get_junyi_topic(topic_id)

@mcp.tool()
def mcp_tool_get_junyi_topic_by_title(title: str):
    """
        Get the topic of均一 by title
        1. 先查詢 topic_id by get_junyi_tree
        2. 再查詢 topic_id 的 topic by get_junyi_topic
    """
    return get_junyi_topic_by_title(title)