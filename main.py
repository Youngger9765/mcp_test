from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
import uvicorn
from agents.junyi_tree_agent import respond as junyi_tree_respond
from agents.junyi_topic_agent import respond as junyi_topic_respond
from agent_selector import choose_agents_via_llm, choose_agents_from_options_via_llm
from agent_registry import AGENT_LIST
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 加入 CORS middleware，允許所有來源跨域（開發用，正式環境建議指定 allow_origins）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或改成 ["http://localhost:8080"] 等你的前端網址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def ask(request: Request):
    body = await request.json()
    query = body.get("query", "")
    options = body.get("options", None)
    user_reply = body.get("user_reply", None)

    # --- 1. 已有 options checklist，直接查詢 ---
    if options and len(options) > 0:
        print("收到 options:", options)
        agent_ids = [o["id"] for o in options]
        print("收到 agent_ids:", agent_ids)
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
                if agent_id == "junyi_tree_agent":
                    result = agent_info["respond"]()
                elif agent_id == "junyi_topic_agent":
                    result = agent_info["respond"]()
                else:
                    result = agent_info["respond"](query)
                print(f"單一 agent 查詢: {agent_id}, 查詢結果: {result}")
                results.append({
                    "agent": agent_id,
                    "ref": agent_info,
                    "result": result
                })
            except Exception as e:
                print(f"查詢 {agent_id} 失敗: {e}")
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
            if agent == "junyi_tree_agent":
                result = agent_info["respond"]()
            elif agent == "junyi_topic_agent":
                result = agent_info["respond"]()
            else:
                result = agent_info["respond"](query)
            print(f"單一 agent 查詢: {agent}, 查詢結果: {result}")
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
            print(f"查詢 {agent} 失敗: {e}")
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

if __name__ == "__main__":
    uvicorn.run(app, port=8000) 