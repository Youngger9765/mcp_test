document.addEventListener('DOMContentLoaded', () => {
  const missionCard = JSON.parse(localStorage.getItem('navme_mission_card') || '{}');
  const container = document.getElementById('mission-tracker');
  if (!missionCard || !missionCard.content) {
    container.innerHTML = '<b>找不到任務卡，請從首頁產生！</b>';
    return;
  }
  // 轉換 missionCard 內容為追蹤資料結構
  const today = new Date().toISOString().slice(0,10);
  const user_id = '123'; // mock
  const mission_pack_id = 'navme_' + today.replace(/-/g, '');
  const tasks = (Array.isArray(missionCard.content) ? missionCard.content : (missionCard.content.missions || []))
    .map(item => ({
      title: item.title || item,
      status: 'not_started',
      note: '',
      time_hint: item.time_hint || item.desc || ''
    }));
  let trackerData = {
    date: today,
    user_id,
    mission_pack_id,
    tasks
  };
  renderMissionTracker(trackerData, missionCard.meta || {});

  function renderMissionTracker(data, meta) {
    // 統計進度
    const doneCount = data.tasks.filter(t => t.status === 'completed').length;
    const totalCount = data.tasks.length;
    const percent = Math.round((doneCount/totalCount)*100);
    // 進度條
    const barBlocks = 10;
    const filled = Math.round(barBlocks * doneCount/totalCount);
    const bar = '■'.repeat(filled) + '□'.repeat(barBlocks-filled);
    // 日誌
    const allNotes = data.tasks.map(t => t.note).filter(Boolean).join('；');
    // 主題
    const topic = meta.topic || meta.input || '今日任務';
    // HTML
    let html = `<h3>🧭 Navme 任務追蹤（Day 1）</h3>`;
    html += `<div style='margin-bottom:8px;'>📌 今日任務主題：「${topic}」</div>`;
    html += `<div style='margin-bottom:12px;'>📋 今日任務（已完成 <span id='done-count'>${doneCount}</span> / <span id='total-count'>${totalCount}</span>）</div>`;
    html += `<div id='task-list'>`;
    data.tasks.forEach((task, idx) => {
      html += `<div class='mission-card-list' style='margin-bottom:10px;'>`;
      html += `<div style='display:flex;align-items:center;gap:8px;'>`;
      html += `<input type='checkbox' id='task-done-${idx}' ${task.status==='completed'?'checked':''} style='transform:scale(1.3);' />`;
      html += `<div class='mission-title'>${task.title}</div>`;
      html += `</div>`;
      if(task.status==='completed') {
        html += `<div class='mission-desc'>✔️ 已完成${task.note?`<br>📝${task.note}`:''}</div>`;
      } else {
        html += `<div class='mission-desc'>${task.note ? '📝 ' + task.note : ''}</div>`;
      }
      html += `<div class='mission-time'>${task.time_hint || ''}</div>`;
      html += `</div>`;
    });
    html += `</div>`;
    html += `<div style='margin:18px 0 8px 0;'>📊 進度條：<span id='progress-bar'>${bar}</span> <span id='progress-percent'>${percent}</span>%</div>`;
    html += `<div>📒 日誌：<span id='all-notes'>${allNotes||'（尚無紀錄）'}</span></div>`;
    html += `<div style='margin-top:18px;display:flex;gap:12px;'><button id='finish-review'>✅ 完成今天回顧</button><button id='next-day'>🔄 切換明日任務</button><button id='back-home'>🏠 返回首頁</button></div>`;
    container.innerHTML = html;
    // 事件
    data.tasks.forEach((task, idx) => {
      container.querySelector(`#task-done-${idx}`).onchange = e => {
        task.status = e.target.checked ? 'completed' : 'not_started';
        renderMissionTracker(data, meta);
      };
      const startBtn = container.querySelector(`.start-btn[data-idx='${idx}']`);
      if(startBtn) startBtn.onclick = () => { task.status = 'in_progress'; renderMissionTracker(data, meta); };
      const doneBtn = container.querySelector(`.done-btn[data-idx='${idx}']`);
      if(doneBtn) doneBtn.onclick = () => { task.status = 'completed'; renderMissionTracker(data, meta); };
      const noteBtn = container.querySelector(`.note-btn[data-idx='${idx}']`);
      if(noteBtn) noteBtn.onclick = () => {
        const note = prompt('請輸入你的觀察/心得：', task.note||'');
        if(note!==null) { task.note = note; renderMissionTracker(data, meta); }
      };
    });
    container.querySelector('#back-home').onclick = () => {
      window.location.href = 'navme_index.html';
    };
    // 其他按鈕可依需求擴充
  }
}); 