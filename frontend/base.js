const apiUrl = "http://localhost:8000/multi_turn_orchestrate";
let lastOptions = null;
let lastMeta = null;

// 這裡不放 scenarios，僅提供 setPrompt 供外部呼叫
function setPrompt(text) {
  document.getElementById("user-input").value = text;
}

function addMsg(text, sender = "bot", extraClass = "") {
  const msgDiv = document.createElement("div");
  msgDiv.className = "msg " + sender + (extraClass ? " " + extraClass : "");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = text;
  msgDiv.appendChild(bubble);
  document.getElementById("messages").appendChild(msgDiv);
  document.getElementById("messages").scrollTop = document.getElementById("messages").scrollHeight;
  return msgDiv;
}

function showLoading() {
  addMsg('<span id="loading-msg"><span class="dot-flashing"></span> 正在查詢，請稍候...</span>', "bot");
}
function hideLoading() {
  const loading = document.getElementById("loading-msg");
  if (loading) loading.parentNode.remove();
}

async function sendQuery(query) {
  const body = { prompt: query, max_turns: 5 };
  console.log("[frontend] sendQuery body:", body);
  const res = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return await res.json();
}

// 新增：多輪推理結果摘要函式
function summarizeResult(result) {
  if (!result) return "<i>（無內容）</i>";
  if (typeof result !== "object") return result;
  if (result.content && result.content.text) return result.content.text;
  if (result.content && result.content.data) {
    const data = result.content.data;
    let summary = "";
    if (data.title) summary += `<b>主題：</b>${data.title}<br>`;
    if (data.intro) summary += `<b>簡介：</b>${data.intro}<br>`;
    if (data.child && Array.isArray(data.child)) {
      summary += `<b>子主題數：</b>${data.child.length}<br>`;
      summary += data.child.slice(0, 3).map(c => c.title).join("、");
      if (data.child.length > 3) summary += " ...";
      summary += "<br>";
    }
    if (data.extended_slug) summary += `<b>路徑：</b>${data.extended_slug}<br>`;
    return summary;
  }
  // fallback: 只顯示前 300 字
  return `<pre>${JSON.stringify(result, null, 2).slice(0, 300)}...</pre>`;
}

async function handleUserInput() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;
  addMsg("你：" + text, "user");
  input.value = "";
  input.disabled = true;
  document.getElementById("send-btn").disabled = true;

  // 1. 先呼叫 /orchestrate 顯示 agent 回應
  showLoading();
  let orchestrateRes = await fetch("http://localhost:8000/orchestrate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: text })
  });
  orchestrateRes = await orchestrateRes.json();
  hideLoading();
  if (orchestrateRes.type === "result" && orchestrateRes.results && orchestrateRes.results.length > 0) {
    const r = orchestrateRes.results[0];
    addMsg(
      `<div class='card agent-card'>
        <div class='agent-title'>【${r.agent_name || r.tool || r.agent_id || r.type || "Agent 回應"}】</div>
        <div class='agent-param'><b>參數：</b>${JSON.stringify(orchestrateRes.input)}</div>
        <div class='agent-content'><b>回應：</b>${summarizeResult(r)}</div>
      </div>`,
      "bot"
    );
  } else if (orchestrateRes.type === "error") {
    addMsg(`<b>錯誤：</b>${orchestrateRes.message || '未知錯誤'}`, "bot", "error-msg");
    input.disabled = false;
    document.getElementById("send-btn").disabled = false;
    input.focus();
    return;
  }

  // 2. 再進行 multi_turn_step，顯示每一輪歷程
  let history = [];
  if (orchestrateRes.type === "result" && orchestrateRes.tool && orchestrateRes.input) {
    history.push({
      tool_id: orchestrateRes.tool,
      parameters: orchestrateRes.input,
      result: orchestrateRes.results[0],
      reason: "初次查詢"
    });
  }
  let currentQuery = text;
  let finished = false;
  while (!finished) {
    showLoading();
    const res = await fetch("http://localhost:8000/multi_turn_step", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history, query: currentQuery })
    });
    const result = await res.json();
    hideLoading();
    if (result.action === "call_tool" && result.step) {
      addMsg(
        `<div class='card agent-card'>
          <div class='agent-title'>【${result.step.agent_name || result.step.tool_id || result.step.agent_id || result.step.type || "Agent"}】</div>
          <div class='agent-param'><b>參數：</b>${JSON.stringify(result.step.parameters)}</div>
          <div class='agent-content'><b>回應：</b>${summarizeResult(result.step.result)}</div>
          ${result.step.reason ? `<div class='llm-reason'><b>規劃理由：</b>${result.step.reason}</div>` : ""}
        </div>`,
        "bot"
      );
      history.push(result.step);
      currentQuery = `剛剛查到：${JSON.stringify(result.step.result).slice(0, 200)}...，請問還需要查什麼嗎？`;
    } else if (result.action === "finish") {
      addMsg(`<div class='summary-info'><b>總結：</b>${result.reason}</div>`, "bot", "summary-msg");
      finished = true;
    } else if (result.action === "chat") {
      addMsg(result.reply, "bot");
      finished = true;
    } else {
      addMsg(`<b>錯誤：</b>${result.message || '未知錯誤'}`, "bot", "error-msg");
      finished = true;
    }
  }
  input.disabled = false;
  document.getElementById("send-btn").disabled = false;
  input.focus();
}

window.selectAllAgents = function(flag) {
  document.querySelectorAll('.agent-checkbox').forEach(cb => cb.checked = flag);
}

window.submitSelectedAgents = async function() {
  const checked = Array.from(document.querySelectorAll('.agent-checkbox:checked')).map(cb => cb.value);
  if (checked.length === 0) {
    addMsg("請至少選擇一個 agent！", "bot");
    return;
  }
  const selectedOptions = lastOptions.filter(opt => checked.includes(opt.id));
  showLoading();
  const response = await sendQuery("");
  hideLoading();
  lastOptions = null;
  if (response.type === "result") {
    const firstResult = response.results[0]?.result;
    if (firstResult) {
      lastMeta = { ...(firstResult.meta || {}), ...firstResult };
    }
    response.results.forEach((r, idx) => {
      // 取 agent_name 當標題，否則 agent_id/type/結果
      const title = r.agent_name || r.agent_id || r.type || "結果";
      // 顯示主要內容
      let content = "";
      if (r.content) {
        if (typeof r.content === "object" && r.content.text) {
          content = r.content.text;
        } else {
          content = JSON.stringify(r.content, null, 2);
        }
      } else if (r.result) {
        content = typeof r.result === "string" ? r.result : JSON.stringify(r.result, null, 2);
      } else {
        content = JSON.stringify(r, null, 2);
      }
      addMsg(
        `<b>【${title}】</b><br>${content}`,
        "bot"
      );
    });
  } else if (response.type === "message") {
    addMsg(response.message, "bot");
    if (response.meta) lastMeta = response.meta;
  }
}

window.onload = function() {
  document.getElementById("send-btn").onclick = handleUserInput;
  document.getElementById("user-input").addEventListener("keydown", e => {
    if (e.key === "Enter") handleUserInput();
  });
}; 