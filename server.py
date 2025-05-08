# server.py
from mcp.server.fastmcp import FastMCP
from src.agent_loader import get_agent_list
from src.agent_selector import choose_agents_via_llm, choose_agents_from_options_via_llm
from src.agent_manager import call_agent_by_llm
import inspect
import openai
from src.orchestrator import orchestrate
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from src.tools import add, get_junyi_tree, get_junyi_topic, get_junyi_topic_by_title
from fastapi.middleware.cors import CORSMiddleware

from agents.junyi_tree_agent import respond as get_junyi_tree_respond
from agents.junyi_topic_agent import respond as get_junyi_topic_respond
from agents.agent_openai import query as openai_query_llm

# Create an MCP server
mcp = FastMCP("mcp_local")

app = FastAPI()

# 加入 CORS 支援
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/orchestrate")
async def orchestrate_api(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    result = orchestrate(prompt)
    return JSONResponse(content=result)

# Add an addition tool
@mcp.tool()
def add(a: int, b: int):
    """Add two numbers"""
    return add(a, b)


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str):
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 均一樹 as tool
@mcp.tool()
def get_junyi_tree(topic_id: str):
    """Get the tree of均一"""
    return get_junyi_tree(topic_id)

@mcp.tool()
def get_junyi_topic(topic_id: str):
    """Get the topic of均一"""
    return get_junyi_topic(topic_id)

@mcp.tool()
def get_junyi_topic_by_title(title: str):
    """
        Get the topic of均一 by title
        1. 先查詢 topic_id by get_junyi_tree
        2. 再查詢 topic_id 的 topic by get_junyi_topic
    """
    return get_junyi_topic_by_title(title)
    
    

# @mcp.tool()
# async def query_router(
#     query: str = "",
#     options: list = [],
#     user_reply: str = "",
#     last_agent_id: str = "",
#     last_meta: dict = {},
#     topic_id: str = ""
# ) -> dict:
#     """
#     多輪 context-aware router
#     包含 
#     agent a: 跟 video 相關
#     agent b: 跟網站相關
#     junyi_tree_agent: 跟均一樹相關
#     junyi_topic_agent: 跟均一主題相關
#     """
#     print("=== [DEBUG] query_router 收到 ===", locals())
#     # --- 0. 多輪 context-aware router ---
#     if last_agent_id or last_meta or topic_id:
#         print("=== [DEBUG] 進入 context-aware router ===")
#         result = call_agent_by_llm(query, last_agent_id, last_meta, topic_id)
#         print("=== [DEBUG] 回傳 result ===", result)
#         return result

#     # --- 1. 已有 options checklist，直接查詢 ---
#     if options and len(options) > 0:
#         agent_ids = [o["id"] for o in options]
#         results = []
#         for agent_id in agent_ids:
#             agent_info = next((a for a in get_agent_list() if a["id"] == agent_id), None)
#             if not agent_info:
#                 results.append({
#                     "agent": agent_id,
#                     "ref": None,
#                     "error": "找不到 agent"
#                 })
#                 continue
#             try:
#                 result = agent_info["respond"](query)
#                 results.append({
#                     "agent": agent_id,
#                     "ref": agent_info,
#                     "result": result
#                 })
#             except Exception as e:
#                 results.append({
#                     "agent": agent_id,
#                     "ref": agent_info,
#                     "error": str(e)
#                 })
#         if all("error" in r for r in results):
#             return {
#                 "type": "result",
#                 "message": "找不到合適的 agent 回應，請再描述一次您的需求。 #logic:all_error",
#                 "results": []
#             }
#         return {
#             "type": "result",
#             "message": "查詢成功 #logic:options_query",
#             "results": results
#         }

#     # --- 2. 初次查詢，LLM 推薦 agent ---
#     if user_reply and options:
#         agent_ids = choose_agents_from_options_via_llm(options, user_reply)
#     else:
#         agent_ids = choose_agents_via_llm(query)

#     if len(agent_ids) == 0:
#         return {
#             "type": "message",
#             "message": "找不到合適的 agent，請再描述一次您的需求。 #logic:no_agent"
#         }
#     if len(agent_ids) == 1:
#         agent = agent_ids[0]
#         agent_info = next((a for a in get_agent_list() if a["id"] == agent), None)
#         try:
#             result = agent_info["respond"](query)
#             return {
#                 "type": "result",
#                 "message": "查詢成功 #logic:single_agent",
#                 "results": [{
#                     "agent": agent,
#                     "ref": agent_info,
#                     "result": result
#                 }]
#             }
#         except Exception as e:
#             return {
#                 "type": "message",
#                 "message": "找不到合適的 agent 回應，請再描述一次您的需求。 #logic:single_agent_error"
#             }

#     # 多個 agent，回傳 options checklist
#     agent_options = [
#         {k: a[k] for k in ("id", "name", "description")} for a in get_agent_list() if a["id"] in agent_ids
#     ]
#     if len(agent_options) > 1:
#         return {
#             "type": "options",
#             "message": "我找到這些 agent 可能都有你要的訊息，請勾選你想查詢的項目： #logic:multi_options",
#             "options": agent_options
#         }
#     else:
#         return {
#             "type": "message",
#             "message": "找不到合適的 agent，請再描述一次您的需求。 #logic:multi_options_empty"
#         }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
