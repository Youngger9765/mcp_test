# server.py
from mcp.server.fastmcp import FastMCP
from src.orchestrator import orchestrate, multi_turn_orchestrate, multi_turn_step
import inspect
import openai
from fastapi import FastAPI, Request, Body, APIRouter
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from src.tools import add, get_junyi_tree, get_junyi_topic, get_junyi_topic_by_title, agent_a_tool, agent_b_tool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.tool_registry import get_tool_list
from pydantic import BaseModel, create_model
from typing import Any, Dict

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

class OrchestrateRequest(BaseModel):
    prompt: str

class QueryRequest(BaseModel):
    query: str
    options: list = None
    user_reply: str = None
    last_agent_id: str = None
    last_meta: dict = None
    topic_id: str = None

@app.post("/orchestrate")
async def orchestrate_api(data: OrchestrateRequest):
    result = orchestrate(data.prompt)
    return JSONResponse(content=result)

@app.post("/query")
async def ask(data: QueryRequest):
    print("=== [DEBUG] /query 收到 body ===", data)
    query = data.query
    options = data.options
    user_reply = data.user_reply
    last_agent_id = data.last_agent_id
    last_meta = data.last_meta
    topic_id = data.topic_id

    AGENT_LIST = get_tool_list()

    # --- 0. 多輪 context-aware router ---
    if last_agent_id or last_meta or topic_id:
        print("=== [DEBUG] /query 進入 context-aware router ===")
        print("query:", query)
        print("last_agent_id:", last_agent_id)
        print("last_meta:", last_meta)
        print("topic_id:", topic_id)
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
    result = orchestrate(query)
    return result

@app.post("/multi_turn_orchestrate")
async def multi_turn_orchestrate_api(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    max_turns = data.get("max_turns", 5)
    result = multi_turn_orchestrate(prompt, max_turns=max_turns)
    return JSONResponse(content=result)

@app.post("/multi_turn_step")
async def multi_turn_step_api(request: Request):
    data = await request.json()
    history = data.get("history", [])
    query = data.get("query", "")
    result = multi_turn_step(history, query)
    return JSONResponse(content=result)

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Add an addition tool
@mcp.tool()
def mcp_tool_add(a: int, b: int):
    """Add two numbers"""
    return add(a, b)


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
    return get_junyi_topic(topic_id, depth=1)

@mcp.tool()
def mcp_tool_get_junyi_topic_by_title(title: str):
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

router = APIRouter()

# 動態產生 agent endpoint
for agent in get_tool_list():
    agent_id = agent["id"]
    name = agent.get("name", agent_id)
    description = agent.get("description", "")
    parameters = agent.get("parameters", [])
    example_queries = agent.get("example_queries", [])
    category = agent.get("category", "")
    tags = agent.get("tags", [])
    
    # 動態產生 Pydantic model
    fields = {}
    for param in parameters:
        pname = param["name"]
        ptype = param.get("type", "str")
        # 支援 int/str/float/bool
        if ptype == "int":
            fields[pname] = (int, ...)
        elif ptype == "float":
            fields[pname] = (float, ...)
        elif ptype == "bool":
            fields[pname] = (bool, ...)
        else:
            fields[pname] = (str, ...)
    model = create_model(f"{agent_id}_Request", **fields)

    # endpoint function
    async def agent_respond(data: model, agent=agent):
        try:
            result = agent["function"](**data.dict())
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    # 註冊 endpoint
    router.add_api_route(
        f"/agent/{agent_id}/respond",
        agent_respond,
        methods=["POST"],
        response_model=Dict[str, Any],
        name=name,
        description=f"{description}\n\n分類: {category}\nTags: {tags}\nExample queries: {example_queries}",
        tags=["Agent"]
    )

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
