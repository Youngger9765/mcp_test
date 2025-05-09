# server.py
from src.orchestrator import orchestrate, multi_turn_orchestrate, multi_turn_step
import inspect
import openai
from fastapi import FastAPI, Request, Body, APIRouter
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.tool_registry import get_tool_list
from pydantic import BaseModel, create_model, Field
from typing import Any, Dict
from src.orchestrator_utils.intent_analyzer import intent_analyzer

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
    intent_result = intent_analyzer(data.prompt)
    if intent_result.get("intent") == "tool_call":
        result = orchestrate(data.prompt)
        result["intent"] = intent_result
        return JSONResponse(content=result)
    else:
        # 直接用 LLM 回 chat
        from src.orchestrator_utils.llm_client import call_llm
        reply = call_llm(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "你是一個親切的中文助理，請用自然語言回答用戶問題。"},
                {"role": "user", "content": data.prompt}
            ],
            temperature=0.7
        )
        return JSONResponse(content={"type": "chat", "reply": reply, "intent": intent_result})

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
    intent_result = intent_analyzer(prompt)
    if intent_result.get("intent") == "chat":
        from src.orchestrator_utils.llm_client import call_llm
        reply = call_llm(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "你是一個親切的中文助理，請用自然語言回答用戶問題。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return JSONResponse(content={"type": "chat", "reply": reply, "intent": intent_result})
    result = multi_turn_orchestrate(prompt, max_turns=max_turns)
    return JSONResponse(content=result)

@app.post("/multi_turn_step")
async def multi_turn_step_api(request: Request):
    data = await request.json()
    history = data.get("history", [])
    query = data.get("query", "")
    # intent 判斷
    if not history and query:
        intent_result = intent_analyzer(query)
        if intent_result.get("intent") == "chat":
            from src.orchestrator_utils.llm_client import call_llm
            reply = call_llm(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "你是一個親切的中文助理，請用自然語言回答用戶問題。"},
                    {"role": "user", "content": query}
                ],
                temperature=0.7
            )
            return JSONResponse(content={"action": "chat", "reply": reply, "intent": intent_result})
        # 否則才進入工具鏈
        first_result = orchestrate(query)
        # 修正：轉換格式
        if first_result.get("type") == "result":
            history = [{
                "tool_id": first_result.get("tool"),
                "parameters": first_result.get("input"),
                "result": first_result.get("results", [{}])[0],
                "reason": "初次查詢"
            }]
        else:
            return JSONResponse(content={"action": "error", "message": first_result.get("message", "查詢失敗")})
    if not history:
        return JSONResponse(content={"message": "請先查詢一次，再進行多輪推理。"})
    result = multi_turn_step(history, query)
    return JSONResponse(content=result)

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# 動態產生 agent endpoint
router = APIRouter()
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
        desc = param.get("description", "")
        required = param.get("required", True)
        default = param.get("default", ... if required else None)
        enum = param.get("enum")
        minimum = param.get("min")
        maximum = param.get("max")
        pattern = param.get("pattern")
        field_args = {"description": desc}
        if minimum is not None:
            field_args["ge"] = minimum
        if maximum is not None:
            field_args["le"] = maximum
        if pattern is not None:
            field_args["pattern"] = pattern
        # 型別處理
        if enum:
            from typing import Literal
            typ = Literal[tuple(enum)]
        elif ptype == "int":
            typ = int
        elif ptype == "float":
            typ = float
        elif ptype == "bool":
            typ = bool
        else:
            typ = str
        fields[pname] = (typ, Field(default, **field_args))
    model = create_model(f"{agent_id}_Request", **fields)

    # endpoint function
    async def agent_respond(data: model, agent=agent):
        try:
            result = agent["function"](**data.dict())
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    # 組合參數說明
    param_lines = []
    for param in parameters:
        pname = param["name"]
        ptype = param.get("type", "str")
        pdesc = param.get("description", "")
        param_lines.append(f"- `{pname}` ({ptype})：{pdesc}")
    param_md = "\n".join(param_lines) if param_lines else "(無)"

    # 組合範例查詢
    example_md = "\n".join([f"- {q}" for q in example_queries]) if example_queries else "(無)"

    # Markdown 說明
    doc_md = f"""
**說明**：{description}

**分類**：{category}  
**標籤**：{tags}

---

### 參數
{param_md}

---

### 範例查詢
{example_md}
"""

    # 註冊 endpoint
    openapi_extra = {}
    if agent.get("request_example"):
        openapi_extra["requestBody"] = {
            "content": {
                "application/json": {
                    "example": agent["request_example"]
                }
            }
        }
    if agent.get("response_example"):
        openapi_extra["responses"] = {
            "200": {
                "content": {
                    "application/json": {
                        "example": agent["response_example"]
                    }
                }
            }
        }
    router.add_api_route(
        f"/agent/{agent_id}/respond",
        agent_respond,
        methods=["POST"],
        response_model=Dict[str, Any],
        name=name,
        description=doc_md,
        tags=["Agent"],
        openapi_extra=openapi_extra if openapi_extra else None
    )

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
