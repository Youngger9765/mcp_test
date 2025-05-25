const API_BASE = "http://localhost:8000";
async function callNavmeAgent(agentId, query) {
  const res = await fetch(`${API_BASE}/agent/${agentId}/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return await res.json();
}

function renderResult(result) {
  const container = document.getElementById('navme-result');
  container.innerHTML = '';
  if (result.type === 'result' && result.results && result.results.length > 0) {
    result = result.results[0];
  }
  if (result.type === 'mission_card' && result.content && Array.isArray(result.content)) {
    let html = '';
    html += `<div style="margin-bottom:18px;"><b>📋 今日任務卡</b></div>`;
    result.content.forEach(item => {
      html += `<div class='mission-card-list' style='margin-bottom:10px;'>
        <div class='mission-title'>${item.title}</div>
        <div class='mission-desc'>${item.description || ''}</div>
        <div class='mission-time'>${item.time_hint || ''}</div>
      </div>`;
    });
    html += `<div class='mission-btns'>
      <button class='start' id='start-tracker-btn'>🚩 開始任務追蹤</button>
      <button class='discard'>🗑️ 捨棄重新輸入</button>
    </div>`;
    container.innerHTML = html;
    container.querySelector('.discard').onclick = () => {
      document.getElementById('navme-input').value = '';
      container.innerHTML = '';
    };
    container.querySelector('#start-tracker-btn').onclick = () => {
      localStorage.setItem('navme_mission_card', JSON.stringify(result));
      window.location.href = 'navme_mission_tracker.html';
    };
  } else if (result.error) {
    container.innerHTML = `<div class='card agent-card' style='color:red;'><b>錯誤：</b>${result.error}<br><pre style='font-size:13px;color:#555;'>${result.raw ? result.raw : ''}</pre></div>`;
  } else if (result.type === 'error') {
    container.innerHTML = `<div class='card agent-card' style='color:red;'><b>錯誤：</b>${result.message || '未知錯誤'}</div>`;
  } else {
    container.innerHTML = `<div class='card agent-card'><b>無回應</b></div>`;
  }
}

document.getElementById('navme-send-btn').onclick = async function() {
  const input = document.getElementById('navme-input').value.trim();
  if (!input) return;
  document.getElementById('navme-result').innerHTML = '<span class="dot-flashing"></span> 產生中...';
  const apiResult = await callNavmeAgent('navme_daily_mission', input);
  renderResult(apiResult.result || apiResult);
};
document.getElementById('navme-reflect-btn').onclick = async function() {
  const input = document.getElementById('navme-input').value.trim();
  document.getElementById('navme-result').innerHTML = '<span class="dot-flashing"></span> 產生中...';
  const apiResult = await callNavmeAgent('navme_summary', input);
  renderResult(apiResult.result || apiResult);
};
document.getElementById('navme-evaluate-btn').onclick = async function() {
  const input = document.getElementById('navme-input').value.trim();
  document.getElementById('navme-result').innerHTML = '<span class="dot-flashing"></span> 產生中...';
  const apiResult = await callNavmeAgent('navme_progress', input);
  renderResult(apiResult.result || apiResult);
}; 