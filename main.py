from fastapi import FastAPI, Request
from mcp.server.fastmcp import FastMCP
import uvicorn
import requests
from agents.junyi_tree_agent import respond as junyi_tree_respond
from agents.junyi_topic_agent import respond as junyi_topic_respond
from agent_selector import choose_agents_via_llm, choose_agents_from_options_via_llm
from agent_registry import AGENT_LIST
from fastapi.middleware.cors import CORSMiddleware

mcp = FastMCP("Demo")

@mcp.tool()
def agent_a(input_text: str) -> str:
    return f"[A Agent 回應] 你問了：{input_text}，這是我從 A 網站取得的摘要。"

@mcp.tool()
def agent_b(input_text: str) -> str:
    return f"[B Agent 回應] 針對：{input_text}，我查到 B 網站的相關資料。"

@mcp.tool()
def junyi_tree_agent(topic_id: str = "root", depth: int = 3) -> str:
    return junyi_tree_respond(topic_id, depth)

@mcp.tool()
def junyi_topic_agent(topic_id: str = "root") -> str:
    return junyi_topic_respond(topic_id)

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
    user_reply = body.get("user_reply", None)
    options = body.get("options", None)

    # 只要 options 有值，就直接查 options 裡的 id 並回傳查詢結果
    if options:
        agent_ids = [o["id"] for o in options]
        results = []
        for agent in agent_ids:
            params = {**body, "input_text": query}
            agent_info = next((a for a in AGENT_LIST if a["id"] == agent), None)
            try:
                result = await mcp.call_tool(agent, params)
                results.append({
                    "agent": agent,
                    "ref": agent_info,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "agent": agent,
                    "ref": agent_info,
                    "error": str(e)
                })
        return {"results": results}

    # 下面才是 LLM 推薦 agent 的流程
    if user_reply and options:
        agent_ids = choose_agents_from_options_via_llm(options, user_reply)
    else:
        agent_ids = choose_agents_via_llm(query)

    print(f"agent_ids: {agent_ids}")

    if len(agent_ids) == 0:
        return {"message": "找不到合適的 agent，請再描述一次您的需求。"}
    if len(agent_ids) == 1:
        # 查詢並回傳
        results = []
        for agent in agent_ids:
            params = {**body, "input_text": query}
            agent_info = next((a for a in AGENT_LIST if a["id"] == agent), None)
            try:
                result = await mcp.call_tool(agent, params)
                results.append({
                    "agent": agent,
                    "ref": agent_info,
                    "result": result
                })
            except Exception as e:
                results.append({
                    "agent": agent,
                    "ref": agent_info,
                    "error": str(e)
                })
        print(results)
        return {"results": results}

    # 多個 agent，回傳 options 給前端
    agent_options = [
        {k: a[k] for k in ("id", "name", "description")} for a in AGENT_LIST if a["id"] in agent_ids
    ]
    return {
        "message": "我找到這些 agent 可能都有你要的訊息，要全部查嗎？還是只要其中一個？",
        "options": agent_options
    }

if __name__ == "__main__":
    uvicorn.run(app, port=8000) 