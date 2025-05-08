// === 情境 playground ===
const scenarios = [
  {
    id: "default",
    name: "一般查詢",
    prompt: "請幫我查一下分數教學"
  },
  {
    id: "secret",
    name: "祕密功能",
    prompt: "請啟動祕密 agent"
  },
  {
    id: "b_site",
    name: "B 網站查詢",
    prompt: "B 網站有什麼新消息？"
  }
];

// 初始化情境選單
window.addEventListener("DOMContentLoaded", () => {
  const scenarioSelect = document.getElementById("scenario-select");
  scenarios.forEach(s => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    scenarioSelect.appendChild(opt);
  });
  scenarioSelect.onchange = function() {
    const s = scenarios.find(x => x.id === this.value);
    if (s) setPrompt(s.prompt);
  };
  // 預設選第一個
  scenarioSelect.value = scenarios[0].id;
  setPrompt(scenarios[0].prompt);
}); 