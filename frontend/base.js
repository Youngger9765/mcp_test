const apiUrl = "http://localhost:8000/orchestrate";
let lastOptions = null;
let lastMeta = null;

// 這裡不放 scenarios，僅提供 setPrompt 供外部呼叫
function setPrompt(text) {
  document.getElementById("user-input").value = text;
}

function addMsg(text, sender = "bot") {
  const msgDiv = document.createElement("div");
  msgDiv.className = "msg " + sender;
  msgDiv.innerHTML = text;
  document.getElementById("messages").appendChild(msgDiv);
  document.getElementById("chat").scrollTop = 99999;
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
  const body = { prompt: query };
  console.log("[frontend] sendQuery body:", body);
  const res = await fetch(apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return await res.json();
}

async function handleUserInput() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;
  addMsg("你：" + text, "user");
  input.value = "";
  input.disabled = true;
  document.getElementById("send-btn").disabled = true;

  showLoading();

  let response;
  if (lastOptions) {
    const allWords = ["全部", "all", "都要", "全部查"];
    if (allWords.includes(text.trim().toLowerCase())) {
      response = await sendQuery("");
      lastOptions = null;
    } else {
      response = await sendQuery(text);
      lastOptions = null;
    }
  } else {
    response = await sendQuery(text);
  }

  hideLoading();

  if (response.results) {
    const firstResult = response.results[0]?.result;
    if (firstResult && firstResult.agent_id === "junyi_tree_agent") {
      lastMeta = { ...(firstResult.meta || {}), ...firstResult };
    }
    response.results.forEach(r => {
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
  }
  if (response.options) {
    let checkboxes = response.options.map((opt, idx) =>
      `<label style="display:block;margin:6px 0;">
        <input type="checkbox" class="agent-checkbox" value="${opt.id}" ${idx===0?'checked':''}>
        <b>${opt.name}</b> <small>(${opt.description})</small>
      </label>`
    ).join("");
    checkboxes = `
      <div id="agent-checkboxes">${checkboxes}</div>
      <button class="option-btn" onclick="selectAllAgents(true)">全選</button>
      <button class="option-btn" onclick="selectAllAgents(false)">取消全選</button>
      <button class="option-btn" onclick="submitSelectedAgents()">查詢</button>
    `;
    addMsg(response.message, "bot");
    addMsg(checkboxes, "bot");
    lastOptions = response.options;
  }
  if (response.message && !response.options) {
    addMsg(response.message, "bot");
  }
  if (response.meta) lastMeta = response.meta;

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