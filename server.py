from mcp.server.fastmcp import FastMCP
from flask import Flask, request, jsonify
import requests
from agents.junyi_tree_agent import respond as junyi_respond

app = Flask(__name__)

mcp = FastMCP("Demo")

@mcp.tool()
def agent_a(input_text: str) -> str:
    return f"[A Agent 回應] 你問了：{input_text}，這是我從 A 網站取得的摘要。"

@mcp.tool()
def agent_b(input_text: str) -> str:
    return f"[B Agent 回應] 針對：{input_text}，我查到 B 網站的相關資料。"

JUNYI_SUB_TREE_API = "https://www.junyiacademy.org/api/v2/open/sub-tree/{topic_id}?depth={depth}"

@app.route('/junyi/sub-tree', methods=['GET'])
def junyi_sub_tree():
    topic_id = request.args.get('topic_id', 'root')
    depth = request.args.get('depth', 3)
    url = JUNYI_SUB_TREE_API.format(topic_id=topic_id, depth=depth)
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp.tool()
def junyi_agent(topic_id: str = "root", depth: int = 3):
    return junyi_respond(topic_id, depth)

if __name__ == "__main__":
    print("準備啟動 MCP 服務")
    mcp.run()
    print("MCP 服務已啟動") 