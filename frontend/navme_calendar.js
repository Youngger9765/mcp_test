// Navme Calendar JS

const calendarDays = ['日', '一', '二', '三', '四', '五', '六'];
const calendarDaysEl = document.getElementById('calendarDays');
const calendarGridEl = document.getElementById('calendarGrid');
const calendarMonthEl = document.getElementById('calendarMonth');
const prevMonthBtn = document.getElementById('prevMonth');
const nextMonthBtn = document.getElementById('nextMonth');
const reviewBtn = document.getElementById('reviewBtn');
const popup = document.getElementById('calendarPopup');
const popupContent = document.getElementById('popupContent');
const closePopup = document.getElementById('closePopup');

let current = new Date();
current.setDate(1);

function getMonthData(year, month) {
  // 取得該月所有天的資料
  const days = [];
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    const data = JSON.parse(localStorage.getItem('navme_calendar_' + dateStr) || '{}');
    days.push({ date: dateStr, ...data });
  }
  return days;
}

function renderCalendar() {
  // 標題
  calendarMonthEl.textContent = `${current.getFullYear()} 年 ${current.getMonth() + 1} 月`;
  // 星期標題
  calendarDaysEl.innerHTML = '';
  for (let d of calendarDays) {
    const el = document.createElement('div');
    el.className = 'calendar-day';
    el.textContent = d;
    calendarDaysEl.appendChild(el);
  }
  // 日期格子
  calendarGridEl.innerHTML = '';
  const year = current.getFullYear();
  const month = current.getMonth();
  const firstDayOfWeek = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  // 補空格
  for (let i = 0; i < firstDayOfWeek; i++) {
    const empty = document.createElement('div');
    empty.className = 'calendar-cell';
    calendarGridEl.appendChild(empty);
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
    cell.addEventListener('click', () => showPopup(dateStr, data));
    calendarGridEl.appendChild(cell);
  }
}

function showPopup(dateStr, data) {
  popup.style.display = 'flex';
  popupContent.innerHTML = `<h3>${dateStr}</h3>`;
  if (!data || Object.keys(data).length === 0) {
    popupContent.innerHTML += '<p>無紀錄</p>';
  } else {
    popupContent.innerHTML += `<p>進度：${typeof data.progress === 'number' ? Math.round(data.progress * 100) + '%' : '無'}</p>`;
    popupContent.innerHTML += `<p>情緒分數：${data.mood || '無'}</p>`;
    popupContent.innerHTML += `<p>心得：${data.note || '無'}</p>`;
    if (data.tasks && Array.isArray(data.tasks)) {
      popupContent.innerHTML += '<ul>' + data.tasks.map(t => `<li>${t.title}：${t.status || '未開始'}</li>`).join('') + '</ul>';
    }
  }
}

closePopup.onclick = () => { popup.style.display = 'none'; };
popup.onclick = (e) => { if (e.target === popup) popup.style.display = 'none'; };

prevMonthBtn.onclick = () => { current.setMonth(current.getMonth() - 1); renderCalendar(); };
nextMonthBtn.onclick = () => { current.setMonth(current.getMonth() + 1); renderCalendar(); };

reviewBtn.onclick = () => {
  // 彙整本月資料，預設 console.log，未來可串接 AI
  const year = current.getFullYear();
  const month = current.getMonth();
  const monthData = getMonthData(year, month);
  console.log('本月進度資料', monthData);
  alert('本月進度已彙整，未來可串接 AI 分析！');
};

renderCalendar(); 