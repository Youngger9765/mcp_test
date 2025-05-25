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
    tasks,
    summary: '' // 新增今日心得
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
      // 新增備註輸入框
      html += `<textarea class='note-input' id='note-input-${idx}' placeholder='寫下你的觀察/心得...' style='width:100%;min-height:36px;margin-top:8px;'>${task.note||''}</textarea>`;
      html += `<button class='save-note-btn' data-idx='${idx}' style='margin-top:6px;'>💾 儲存備註</button>`;
      html += `</div>`;
    });
    html += `</div>`;
    // 今日心得
    html += `<div style="margin:24px 0 8px 0;">
      <b>📝 今日心得：</b><br>
      <textarea id="today-summary" style="width:100%;min-height:60px;">${data.summary||''}</textarea>
    </div>`;
    html += `<div style='margin-top:18px;display:flex;gap:12px;'><button id='finish-review'>✅ 完成今天回顧</button></div>`;
    html += `<div id='review-result' style='margin:18px 0 0 0;'></div>`;
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
      // 儲存備註
      const saveBtn = container.querySelector(`.save-note-btn[data-idx='${idx}']`);
      if(saveBtn) saveBtn.onclick = () => {
        const val = container.querySelector(`#note-input-${idx}`).value;
        task.note = val;
        renderMissionTracker(data, meta);
      };
    });
    // 今日心得 textarea 綁定
    const summaryInput = container.querySelector('#today-summary');
    if(summaryInput) summaryInput.oninput = e => { data.summary = e.target.value; };
    // 完成今天回顧
    container.querySelector('#finish-review').onclick = async () => {
      // 彙整所有備註與心得
      let reviewText = '';
      data.tasks.forEach((t,i) => {
        const statusText = t.status === 'completed' ? '（已完成）' : t.status === 'in_progress' ? '（進行中）' : '（未完成）';
        reviewText += `【${i+1}. ${t.title}】${statusText}\n`;
        reviewText += t.note ? `備註：${t.note}\n\n` : '（無備註）\n\n';
      });
      if(data.summary) {
        reviewText += `【今日心得】\n${data.summary}`;
      }
      // === 新增：寫入行事曆資料 ===
      const today = data.date;
      const doneCount = data.tasks.filter(t => t.status === 'completed').length;
      const totalCount = data.tasks.length;
      const progress = totalCount > 0 ? doneCount / totalCount : 0;
      // 嘗試從心得中抓取心情分數（如有）
      let mood = '';
      if (data.summary) {
        const moodMatch = data.summary.match(/([1-5])分/);
        if (moodMatch) mood = parseInt(moodMatch[1], 10);
      }
      const calendarData = {
        date: today,
        progress,
        mood,
        note: data.summary || '',
        tasks: data.tasks.map(t => ({ title: t.title, status: t.status, note: t.note }))
      };
      localStorage.setItem('navme_calendar_' + today, JSON.stringify(calendarData));
      // === End ===
      console.log('送出給 AI 的 reviewText：', reviewText);
      // loading dots + 打字動畫
      const reviewDiv = container.querySelector('#review-result');
      reviewDiv.innerHTML = `<div class="dot-flashing"></div> <span id="ai-typing-msg"></span>`;
      reviewDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // 打字動畫
      function typeWriterEffect(element, text, speed=40) {
        let i = 0;
        element.innerHTML = '';
        function type() {
          if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
          }
        }
        type();
      }
      const aiMsg = reviewDiv.querySelector('#ai-typing-msg');
      typeWriterEffect(aiMsg, 'AI 正在分析你的回顧', 40);
      // 呼叫 NavmeSummaryAgent
      const API_BASE = "http://localhost:8000";
      const res = await fetch(`${API_BASE}/agent/navme_summary/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: reviewText })
      });
      const result = await res.json();
      if(result.result && result.result.content && result.result.content.summary) {
        reviewDiv.innerHTML = `<div class='ai-review-fadein' style='background:#f8fafc;border-radius:8px;padding:16px 18px;margin-top:8px;border:1.5px solid #e3eaf3;'><b>🤖 AI 回顧摘要：</b><br>${result.result.content.summary}</div>`;
      } else if(result.result && result.result.summary) {
        reviewDiv.innerHTML = `<div class='ai-review-fadein' style='background:#f8fafc;border-radius:8px;padding:16px 18px;margin-top:8px;border:1.5px solid #e3eaf3;'><b>🤖 AI 回顧摘要：</b><br>${result.result.summary}</div>`;
      } else {
        reviewDiv.innerHTML = `<div style='color:red;'>AI 回顧失敗，請稍後再試。</div>`;
      }
      reviewDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
  }
}); 