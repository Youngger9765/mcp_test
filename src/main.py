from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.agent_loader import AGENT_LIST
from src.agent_selector import choose_agents_via_llm, choose_agents_from_options_via_llm
import uvicorn
from fastapi.staticfiles import StaticFiles
import os
from fastapi.responses import FileResponse

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
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.post("/query")
async def ask(request: Request):
    body = await request.json()
    query = body.get("query", "")
    options = body.get("options", None)
    user_reply = body.get("user_reply", None)

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
                result = agent_info["respond"](query)
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
    if user_reply and options:
        agent_ids = choose_agents_from_options_via_llm(options, user_reply)
    else:
        agent_ids = choose_agents_via_llm(query)

    if len(agent_ids) == 0:
        return {
            "type": "message",
            "message": "找不到合適的 agent，請再描述一次您的需求。 #logic:no_agent"
        }
    if len(agent_ids) == 1:
        agent = agent_ids[0]
        agent_info = next((a for a in AGENT_LIST if a["id"] == agent), None)
        try:
            result = agent_info["respond"](query)
            return {
                "type": "result",
                "message": "查詢成功 #logic:single_agent",
                "results": [{
                    "agent": agent,
                    "ref": agent_info,
                    "result": result
                }]
            }
        except Exception as e:
            return {
                "type": "message",
                "message": "找不到合適的 agent 回應，請再描述一次您的需求。 #logic:single_agent_error"
            }

    # 多個 agent，回傳 options checklist
    agent_options = [
        {k: a[k] for k in ("id", "name", "description")} for a in AGENT_LIST if a["id"] in agent_ids
    ]
    if len(agent_options) > 1:
        return {
            "type": "options",
            "message": "我找到這些 agent 可能都有你要的訊息，請勾選你想查詢的項目： #logic:multi_options",
            "options": agent_options
        }
    else:
        return {
            "type": "message",
            "message": "找不到合適的 agent，請再描述一次您的需求。 #logic:multi_options_empty"
        }

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, port=8000) 