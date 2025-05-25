// Navme Dashboard 雙欄互動

const calendarDays = ['日', '一', '二', '三', '四', '五', '六'];
const calendarEl = document.getElementById('dashboard-calendar');
const trackerEl = document.getElementById('dashboard-tracker');

let selectedDate = new Date().toISOString().slice(0, 10);
let currentMonth = new Date(selectedDate);
currentMonth.setDate(1);

function getMonthData(year, month) {
  const days = [];
  const lastDay = new Date(year, month + 1, 0);
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const data = JSON.parse(localStorage.getItem('navme_calendar_' + dateStr) || '{}');
    days.push({ date: dateStr, ...data });
  }
  return days;
}

function renderCalendar() {
  calendarEl.innerHTML = '';
  // header
  const header = document.createElement('div');
  header.className = 'calendar-header';
  const prevBtn = document.createElement('button'); prevBtn.textContent = '◀';
  const nextBtn = document.createElement('button'); nextBtn.textContent = '▶';
  const monthLabel = document.createElement('span');
  monthLabel.id = 'calendarMonth';
  monthLabel.textContent = `${currentMonth.getFullYear()} 年 ${currentMonth.getMonth() + 1} 月`;
  header.appendChild(prevBtn); header.appendChild(monthLabel); header.appendChild(nextBtn);
  calendarEl.appendChild(header);
  // days row
  const daysRow = document.createElement('div'); daysRow.className = 'calendar-grid';
  for (let d of calendarDays) {
    const el = document.createElement('div'); el.className = 'calendar-day'; el.textContent = d; daysRow.appendChild(el);
  }
  calendarEl.appendChild(daysRow);
  // grid
  const grid = document.createElement('div'); grid.className = 'calendar-grid';
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  const firstDayOfWeek = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  // 補空格
  for (let i = 0; i < firstDayOfWeek; i++) {
    const empty = document.createElement('div'); empty.className = 'calendar-cell'; grid.appendChild(empty);
  }
  // 日期
  const todayStr = (new Date()).toISOString().slice(0, 10);
  const monthData = getMonthData(year, month);
  for (let i = 0; i < daysInMonth; i++) {
    const d = i + 1;
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const cell = document.createElement('div');
    cell.className = 'calendar-cell';
    if (dateStr === todayStr) cell.classList.add('today');
    if (dateStr === selectedDate) cell.classList.add('selected');
    // 進度 emoji
    const data = monthData[i];
    let emoji = '⬜️';
    if (data && typeof data.progress === 'number') {
      if (data.progress >= 1) emoji = '✅';
      else if (data.progress >= 0.7) emoji = '🟢';
      else if (data.progress > 0) emoji = '🟡';
      else emoji = '⬜️';
    }
    const emojiSpan = document.createElement('span');
    emojiSpan.className = 'progress-emoji';
    emojiSpan.textContent = emoji;
    cell.appendChild(document.createTextNode(d));
    cell.appendChild(document.createElement('br'));
    cell.appendChild(emojiSpan);
    cell.onclick = () => {
      selectedDate = dateStr;
      renderCalendar();
      renderTracker(selectedDate);
    };
    grid.appendChild(cell);
  }
  calendarEl.appendChild(grid);
  // 月份切換
  prevBtn.onclick = () => { currentMonth.setMonth(currentMonth.getMonth() - 1); renderCalendar(); };
  nextBtn.onclick = () => { currentMonth.setMonth(currentMonth.getMonth() + 1); renderCalendar(); };
}

function renderTracker(dateStr) {
  trackerEl.innerHTML = '';
  // 讀取資料
  let data = JSON.parse(localStorage.getItem('navme_calendar_' + dateStr) || '{}');
  // 若無資料，給預設空資料
  if (!data || !data.tasks) {
    data = {
      date: dateStr,
      progress: 0,
      mood: '',
      note: '',
      tasks: [
        { title: '任務1', status: 'not_started', note: '' },
        { title: '任務2', status: 'not_started', note: '' },
        { title: '任務3', status: 'not_started', note: '' }
      ]
    };
  }
  // 統計進度
  const doneCount = data.tasks.filter(t => t.status === 'completed').length;
  const totalCount = data.tasks.length;
  const percent = totalCount > 0 ? Math.round((doneCount/totalCount)*100) : 0;
  // HTML
  let html = `<h3>🧭 ${dateStr} 任務追蹤</h3>`;
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
    // 新增備註輸入框
    html += `<textarea class='note-input' id='note-input-${idx}' placeholder='寫下你的觀察/心得...' style='width:100%;min-height:36px;margin-top:8px;'>${task.note||''}</textarea>`;
    html += `<button class='save-note-btn' data-idx='${idx}' style='margin-top:6px;'>💾 儲存備註</button>`;
    html += `</div>`;
  });
  html += `</div>`;
  // 今日心得
  html += `<div style="margin:24px 0 8px 0;">
    <b>📝 今日心得：</b><br>
    <textarea id="today-summary" style="width:100%;min-height:60px;">${data.note||''}</textarea>
  </div>`;
  trackerEl.innerHTML = html;
  // 事件
  data.tasks.forEach((task, idx) => {
    trackerEl.querySelector(`#task-done-${idx}`).onchange = e => {
      task.status = e.target.checked ? 'completed' : 'not_started';
      saveAndSync();
    };
    const saveBtn = trackerEl.querySelector(`.save-note-btn[data-idx='${idx}']`);
    if(saveBtn) saveBtn.onclick = () => {
      const val = trackerEl.querySelector(`#note-input-${idx}`).value;
      task.note = val;
      saveAndSync();
    };
  });
  // 今日心得 textarea 綁定
  const summaryInput = trackerEl.querySelector('#today-summary');
  if(summaryInput) summaryInput.oninput = e => { data.note = e.target.value; saveAndSync(); };

  function saveAndSync() {
    // 重新計算進度
    const doneCount = data.tasks.filter(t => t.status === 'completed').length;
    const totalCount = data.tasks.length;
    data.progress = totalCount > 0 ? doneCount / totalCount : 0;
    localStorage.setItem('navme_calendar_' + dateStr, JSON.stringify(data));
    renderCalendar(); // 同步刷新左側燈號
    renderTracker(dateStr); // 右側也刷新
  }
}

// 預設載入今日
renderCalendar();
renderTracker(selectedDate); 