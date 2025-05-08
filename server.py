# server.py
from mcp.server.fastmcp import FastMCP
from src.orchestrator import orchestrate
import inspect
import openai
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from src.tools import add, get_junyi_tree, get_junyi_topic, get_junyi_topic_by_title, agent_a_tool, agent_b_tool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.tool_registry import get_tool_list

from agents.junyi_tree_agent import respond as get_junyi_tree_respond
from agents.junyi_topic_agent import respond as get_junyi_topic_respond
from agents.agent_openai import query as openai_query_llm

# Create an MCP server
mcp = FastMCP("mcp_local")

app = FastAPI()

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 假設你的 frontend/ 在專案根目錄
frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.post("/orchestrate")
async def orchestrate_api(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    result = orchestrate(prompt)
    return JSONResponse(content=result)

@app.post("/query")
async def ask(request: Request):
    body = await request.json()
    print("=== [DEBUG] /query 收到 body ===", body)
    query = body.get("query", "")
    options = body.get("options", None)
    user_reply = body.get("user_reply", None)
    last_agent_id = body.get("last_agent_id")
    last_meta = body.get("last_meta")
    topic_id = body.get("topic_id")

    AGENT_LIST = get_tool_list()

    # --- 0. 多輪 context-aware router ---
    if last_agent_id or last_meta or topic_id:
        print("=== [DEBUG] /query 進入 context-aware router ===")
        print("query:", query)
        print("last_agent_id:", last_agent_id)
        print("last_meta:", last_meta)
        print("topic_id:", topic_id)
        # 這裡建議直接呼叫 orchestrate，並根據 prompt 組合 context
        # 你可根據實際需求調整 orchestrate 的參數
        result = orchestrate(query)
        print("=== [DEBUG] /query 回傳 result ===", result)
        return result

    # --- 1. 已有 options checklist，直接查詢 ---
    if options and len(options) > 0:
        agent_ids = [o["id"] for o in options]
        results = []
        for agent_id in agent_ids:
            agent_info = next((a for a in AGENT_LIST if a["id"] == agent_id), None)
            if not agent_info:
                results.append({
                    "agent": agent_id,
                    "ref": None,
                    "error": "找不到 agent"
                })
                continue
            try:
                result = agent_info["function"](query)
                results.append({
                    "agent": agent_id,
                    "ref": agent_info,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "agent": agent_id,
                    "ref": agent_info,
                    "error": str(e)
                })
        if all("error" in r for r in results):
            return {
                "type": "result",
                "message": "找不到合適的 agent 回應，請再描述一次您的需求。 #logic:all_error",
                "results": []
            }
        return {
            "type": "result",
            "message": "查詢成功 #logic:options_query",
            "results": results
        }

    # --- 2. 初次查詢，LLM 推薦 agent ---
    # 這裡直接呼叫 orchestrate，讓 LLM 決定 agent
    result = orchestrate(query)
    return result

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

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

# === 直接 expose tools.py function 的 API ===
@app.post("/tools/add")
async def tool_add(data: dict = Body(...)):
    a = data.get("a")
    b = data.get("b")
    return add(a, b)

@app.post("/tools/get_junyi_tree")
async def tool_get_junyi_tree(data: dict = Body(...)):
    topic_id = data.get("topic_id", "root")
    return get_junyi_tree(topic_id)

@app.post("/tools/get_junyi_topic")
async def tool_get_junyi_topic(data: dict = Body(...)):
    topic_id = data.get("topic_id", "root")
    return get_junyi_topic(topic_id)

@app.post("/tools/get_junyi_topic_by_title")
async def tool_get_junyi_topic_by_title(data: dict = Body(...)):
    title = data.get("title")
    return get_junyi_topic_by_title(title)

@app.post("/tools/agent_a_tool")
async def tool_agent_a_tool(data: dict = Body(...)):
    input_text = data.get("input_text")
    return agent_a_tool(input_text)

@app.post("/tools/agent_b_tool")
async def tool_agent_b_tool(data: dict = Body(...)):
    input_text = data.get("input_text")
    return agent_b_tool(input_text)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
