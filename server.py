# server.py
from src.orchestrator import dispatch_agent_single_turn, dispatch_agent_multi_turn_step
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
from src.orchestrator_utils.llm_client import call_llm

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

@app.post("/analyze_intent")
async def analyze_intent_api(data: OrchestrateRequest):
    intent_result = intent_analyzer(data.prompt)
    print("[analyze_intent] intent_result:", intent_result)
    # 根據 intent 給建議 API 路徑
    intent = intent_result.get("intent")
    if intent == "chat":
        api = "/chat"
    elif intent == "tool_call":
        api = "/agent/single_turn_dispatch"
    elif intent == "multi_turn":
        api = "/agent/multi_turn_step"
    else:
        api = None
    return {"intent": intent, "suggested_api": api, "reason": intent_result.get("reason", "")}

@app.post("/chat")
async def chat_api(data: OrchestrateRequest):
    reply = call_llm(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你是一個親切的中文助理，請用自然語言回答用戶問題。"},
            {"role": "user", "content": data.prompt}
        ],
        temperature=0.7
    )
    return {"type": "chat", "reply": reply}

@app.post("/agent/single_turn_dispatch")
async def agent_single_turn_dispatch_api(data: OrchestrateRequest):
    # 僅負責 agent 調度，不做 intent 判斷
    result = dispatch_agent_single_turn(data.prompt)
    return JSONResponse(content=result)

@app.post("/agent/multi_turn_step")
async def agent_multi_turn_step_api(request: Request):
    data = await request.json()
    history = data.get("history", [])
    query = data.get("query", "")
    # 僅負責多步推理，不做 intent 判斷
    if not history:
        return JSONResponse(content={"message": "請先查詢一次，再進行多輪推理。"})
    result = dispatch_agent_multi_turn_step(history, query)
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
