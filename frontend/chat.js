// 假設你有這些全域變數
let lastAgentId = null;
let lastMeta = null;

function onUserInput(userQuery, topicId = null) {
    fetch('/api/agent_call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_query: userQuery,
            topic_id: topicId,
            last_agent_id: lastAgentId,
            last_meta: lastMeta
        })
    })
    .then(res => res.json())
    .then(result => {
        // 根據 type render
        if (result.type === "tree") {
            renderTree(result.content);
        } else if (result.type === "text") {
            renderText(result.content.text);
        }
        // 記錄上下文
        lastAgentId = result.agent_id;
        lastMeta = result.meta;
    });
}

function renderText(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = "msg bot";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = text;
    msgDiv.appendChild(bubble);
    document.getElementById("messages").appendChild(msgDiv);
    document.getElementById("messages").scrollTop = document.getElementById("messages").scrollHeight;
} 