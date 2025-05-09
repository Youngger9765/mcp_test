# mcp_test

---

# 文件架構

本文件說明 MCP 多 agent 系統的 DDD 分層、對話流程、API 設計、agent 註冊、維護建議與常見問題，並同步記錄每次 refactor 的重點與 changelog。

主要內容分為：
- 架構分層與設計原則
- 對話流程與 API 路徑
- Agent 註冊與自動合併
- 前後端 schema 與回傳格式
- 測試與維護建議
- Changelog 追蹤每次重大調整

# MCP 架構說明文件

## 2025/5/8 DDD 重構重點

- 採用 DDD（Domain-Driven Design）分層：明確區分 tools、agents、orchestrator 三層。
- tools/：最底層功能單元，無狀態、無決策，僅負責「做事」。
- agents/：有邏輯、有狀態的智能代理，會調用一個或多個 tool，並可對話、推理。
- orchestrator.py：負責根據用戶需求、上下文，調度 agent，管理多步推理。
- API 路徑、命名、測試、文件皆與分層一致，易於維護與擴充。
- 未來如需更複雜調度，可再細分 tool_orchestrator、agent_orchestrator 等。

## 目錄
- [專案目標](#專案目標)
- [系統分層架構](#系統分層架構)
- [Agent 註冊與合併流程](#agent-註冊與合併流程)
- [API Response Schema](#api-response-schema)
- [設計原則](#設計原則)
- [維護建議與 FAQ](#維護建議與-faq)
- [相關檔案說明](#相關檔案說明)
- [進度追蹤](#進度追蹤)
- [測試說明](#測試說明)

---

## 專案目標

- 已落實 DDD 分層（tools/agents/orchestrator），分層明確、易於維護與擴充
- 前後端皆以統一 schema 溝通，API 路徑語意化，資料流清晰
- 支援多 agent 註冊（YAML + Python 雙軌），自動合併，易於擴充
- 前端完整維護 history，支援多輪對話、history answer、意圖判斷
- API/agent response schema 標準化，前端自動渲染、收合 JSON
- 測試覆蓋 agent 註冊、合併、respond 格式與 API schema
- UX 佳，意圖判斷、歷程摘要、錯誤處理皆有明確顯示

---

## 系統分層架構

1. **tools/**
   - 單一功能、無狀態的底層工具（如查詢 API、計算等）
   - 只做一件事，無決策、無狀態，純 function
2. **agents/**
   - 有邏輯、有狀態的智能代理，會調用一個或多個 tool，並可對話、推理
   - 封裝決策、狀態、對話等行為
3. **orchestrator.py**
   - 負責根據 user query，選擇正確的 agent，調用 agent 的 respond 方法，組合回應
   - 管理多步推理流程

### 智慧 Smart Chat 對話流程與架構圖（2025/5 DDD 分層重構後）

#### 【history/intention 對話流程說明】
- 前端維護完整 history，user/assistant/tool 歷程皆 push 進 messages。
- 每次用戶輸入時，前端將 history 組成 prompt，呼叫 `/analyze_intent` 取得意圖（intent: chat、tool_call、history_answer）。
- 前端根據 intent 分流：
  - chat → 呼叫 `/chat`，LLM 直接回覆。
  - tool_call → 呼叫 `/agent/single_turn_dispatch`，進入 agent 調度與多步推理（如需再進 `/agent/multi_turn_step`）。
  - history_answer → 呼叫 `/history_answer`，LLM 根據 history 找最佳答案與理由。
- 多輪推理時，前端將每一輪 tool 歷程 push 進 history，並於每次 step 時帶入完整 history，確保 LLM 能根據上下文做最佳決策。
- 所有 API 回傳皆用統一 schema，前端自動渲染、收合 JSON，顯示卡片、摘要、錯誤訊息等。

#### 【對話流程說明】
1. **用戶輸入**：
   - 前端（index.html + base.js）維護完整 history，將用戶輸入 push 到訊息區。
2. **意圖判斷**：
   - 前端呼叫 `/analyze_intent`，取得 intent（chat、tool_call...）與 reason。
   - 前端顯示意圖 label 與細節（可收合）。
3. **API 分流**：
   - 若 intent = chat，前端呼叫 `/chat`，由 LLM 回覆。
   - 若 intent = tool_call，前端呼叫 `/agent/single_turn_dispatch`，進入 agent 調度與多步推理（如需再進 `/agent/multi_turn_step`）。
   - 其他 intent 則顯示錯誤或 fallback。
4. **Orchestrator 調度**：
   - orchestrator.py 只 import agent，不直接碰 tool，統一調用 agent 的 respond 方法。
   - 單步查詢：dispatch_agent_single_turn。
   - 多步推理：dispatch_agent_multi_turn_step，根據 history 與 query 決定下一步。
5. **Agent 封裝**：
   - agents/ 目錄下每個 agent class 封裝一個或多個 tool，負責邏輯、狀態、推理。
6. **Tool 執行**：
   - tools/ 只存放純功能 function，無狀態、無決策。
7. **回傳與顯示**：
   - 回傳內容皆符合統一 schema，前端自動渲染、收合 JSON，顯示卡片、摘要、錯誤訊息等。

---

```
┌─────────────┐
│   前端 UI   │
│ (index.html)│
└─────┬───────┘
      │
      ▼
┌──────────────────────────────┐
│  base.js                     │
│  1. 維護 history (messages)   │
│  2. 用戶輸入 push 到 history  │
│  3. 呼叫 /analyze_intent      │
│  4. 顯示意圖 label/細節       │
│  5. 根據 intent 分流：         │
│     ├─ chat → /chat           │
│     ├─ tool_call → /agent/single_turn_dispatch
│     ├─ history_answer → /history_answer
│     └─ fallback → 顯示錯誤     │
│         （tool_call 如需多步推理再進 /agent/multi_turn_step）│
└────────────┬─────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│  server.py                                                 │
│  1. /analyze_intent：意圖判斷，回傳 intent 與 reason      │
│  2. /chat：純 LLM chat 回覆                                │
│  3. /agent/single_turn_dispatch：單步 agent 調度           │
│  4. /agent/multi_turn_step：多步推理/多 agent 協作         │
│  5. /history_answer：根據 history 回答                     │
│  6. fallback：回傳錯誤訊息                                 │
│  7. 各 API 責任單一，分層明確                             │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  orchestrator.py                             │
│  1. 只 import agent，不直接碰 tool           │
│  2. dispatch_agent_single_turn               │
│  3. dispatch_agent_multi_turn_step           │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────┐
│  agents/                     │
│  1. 每個 agent 封裝一個或多個 tool         │
│  2. agent class 統一 respond 方法           │
└────────────┬─────────────────┘
             │
             ▼
┌──────────────┐
│  tools/      │
│  純功能 function│
└──────────────┘
```

---

## Agent 註冊與合併流程

### 雙軌註冊設計

- **YAML 註冊**（for 非工程師）
  - 編輯 `mcp_config.yaml` 內的 `agents` 區塊
  - 適合邏輯簡單、格式固定的 agent
  - 範例：
    ```yaml
    agents:
      - id: agent_a
        name: A Agent
        description: 查詢網路摘要、影片剪輯教學等
        example_queries:
          - 請幫我查一下影片剪輯教學
        respond: src.agent_registry.AgentA().respond
    ```

  - **routes 區塊**
    - `routes` 用於定義多 agent 調度的預設流程（如 pipeline），可指定多個 agent 依序處理同一 query。
    - 每個 route 可包含多個 step，每個 step 指定 agent 及其輸入格式。
    - 範例：
      ```yaml
      routes:
        default:
          steps:
            - agent: agent_a
              input: "{{query}}"
            - agent: agent_b
              input: "{{query}}"
            - agent: junyi_tree_agent
              input: "{{query}}"
            - agent: junyi_topic_agent
              input: "{{query}}"
      ```
    - 代表預設會依序呼叫 agent_a → agent_b → junyi_tree_agent → junyi_topic_agent，每個 agent 都會收到 query 作為輸入。
    - 若有多種 route，可依需求新增不同名稱的 routes。
    - routes 設定可讓非工程師用 YAML 快速調整多 agent pipeline。

- **Python 註冊**（for 工程師）
  - 在 `src/agent_registry.py` 撰寫 class/function
  - 於 `get_python_agents()` 回傳 agent dict
  - 適合有複雜邏輯、狀態、外部依賴的 agent
  - 範例：
    ```python
    class JunyiTreeAgent(BaseAgent):
        # ...略...

    def get_python_agents():
        return [
            {
                "id": JunyiTreeAgent.id,
                "name": JunyiTreeAgent.name,
                "description": JunyiTreeAgent.description,
                "example_queries": JunyiTreeAgent.example_queries,
                "respond": JunyiTreeAgent().respond
            },
            # ...其他 agent...
        ]
    ```

### 自動合併邏輯

1. 啟動時自動載入 YAML 與 Python 兩邊的 agent
2. **YAML 為主**：同 id 以 YAML 設定為主
3. **Python 補充**：YAML 沒有的 agent，自動補上 Python 端的 agent
4. 產生統一的 `AGENT_LIST`，供前端、測試、主程式使用

---

## API Response Schema

- 所有 API 回傳皆符合統一 schema，包含：
  - `type`
  - `content`
  - `meta`
  - `agent_id`
  - `error`

---

## 設計原則

- **高擴充性**：新增 agent 僅需繼承 BaseAgent 並註冊
- **低耦合**：意圖判斷、agent mapping、資料查詢分層明確
- **標準化格式**：前後端皆以統一 schema 溝通
- **錯誤處理完善**：所有錯誤皆有 fallback 與標準格式

---

## 維護建議與 FAQ

- 什麼時候該寫進 YAML？
  - 需要**非工程師維護**、**邏輯簡單**、**回傳格式固定**時
- 什麼時候該寫在 Python？
  - 需要 class 狀態、外部依賴、進階邏輯，或不希望非工程師維護時
- **建議流程**：大部分 agent 先寫在 Python，等有需求時再搬進 YAML
- **YAML 與 Python 可共存**，loader 會自動合併，維護彈性最大

---

## FAQ（分層說明）

- **Tool 是什麼？**
  - 最底層功能單元，無狀態、無決策，僅負責「做事」。
- **Agent 是什麼？**
  - 有邏輯、有狀態的智能代理，會調用一個或多個 tool，並可對話、推理。
- **Orchestrator 是什麼？**
  - 負責根據用戶需求、上下文，調度 agent，管理多步推理。

---

## 相關檔案說明

- `mcp_config.yaml`：agent metadata 設定
- `src/agent_registry.py`：自動合併 YAML 與 Python agent，產生 AGENT_LIST

---

## 進度追蹤

### ✅ 已完成
- DDD 架構分層、命名標準化、分層可擴充
- agent 註冊雙軌（YAML/Python）、自動合併
- API 路徑語意化，前後端 schema 統一
- 前端完整 history、意圖判斷、history answer、分流邏輯
- 多 agent 調度、單步/多步推理、history answer
- 測試覆蓋 agent 註冊、合併、respond 格式與 API schema
- UX 優化：意圖 label、<details> 摘要、錯誤訊息、history 展開
- README 文件同步分層、流程、API、history spec

### 🚧 TODO
- 增加更多 agent（Google Drive, YouTube, Notion, 自有網站等）
- 支援多種資料型態
- API server 完善化與安全性
- 設計更彈性的前後端資料 schema
- plug-in LLM 調度策略（如 OpenAI/Claude function calling）
- plug-in 多輪推理（multi-turn reasoning）與上下文管理
- plug-in log/debug 機制（log decorator, log view, log level）
- plug-in context/session 管理（多用戶、多 session、狀態追蹤）
- API schema 自動產生（OpenAPI/Swagger）
- 多語系 metadata 支援
- Agent Health Check/熱部署/自動 reload
- Agent 分類/搜尋/tag 機制

### 🛠️ 架構重構建議（Refactor Checklist）
- [x] 抽象出 BaseAgent/Tool interface，所有 agent 實作 respond() 並統一回傳格式
- [x] 建立 AgentRegistry/Manager class，統一管理 agent 註冊、查詢、合併（YAML/Python）
- [x] 支援自動掃描 agents/ 目錄，自動註冊所有 agent
- [x] function 與 metadata 分離，metadata 可由 YAML/JSON 產生，function 由 Python 綁定
- [x] Orchestrator 完全函式化與模組化，支援多種調度策略（if-else、LLM、rule-based）
- [x] 調度策略分離：單步、多步、意圖判斷、fallback 可獨立成 method
- [x] 統一所有 agent 的 response schema，加強錯誤處理
- [x] 增加 orchestrator、API、agent respond 的單元測試
- [x] 前後端 schema 標準化，所有回傳皆用統一格式，方便前端顯示與 debug
- [x] plug-in LLM 調度、多輪推理已模組化（orchestrator_utils/）
- [ ] plug-in context/session 管理（多用戶、多 session、狀態追蹤等，預留擴充空間）
- [x] plug-in log/debug 機制（log_call decorator）初步完成

---

## 測試說明

### 1. 安裝測試套件

```bash
pip install pytest
```

### 2. 執行所有測試

```bash
pytest
```

### 3. 執行特定測試檔案

```bash
pytest tests/test_agent_registry.py
```

### 4. 顯示詳細測試過程

```bash
pytest -v
```

### 5. 產生測試覆蓋率報告（可選）

```bash
pip install pytest-cov
pytest --cov=src
```

## 執行測試

一般測試：
```bash
make test
```

顯示 coverage（測試覆蓋率）：
```bash
PYTHONPATH=. pytest --cov=src tests/
```

---

**說明：**
- 所有測試程式放在 `tests/` 目錄下。
- 主要測試 agent 註冊、合併、respond 格式與 API schema。
- 若有新增 agent 或調整架構，請務必執行測試確保正確性。

---

## Changelog

### 2025/5/7
- orchestrator.py 完全函式化與模組化，移除 Orchestrator class
- 多輪推理與分步推理統一，皆具備防重複查詢能力
- prompt 組裝、LLM 呼叫、工具清單、格式驗證等抽出為獨立模組（src/orchestrator_utils/）
- 移除冗餘 function 與 import，測試與主流程分離
- plug-in log/debug 機制（log_call decorator）初步完成
- README checklist、檔案說明、FAQ 同步更新

### 2025/5/8
- 完成 DDD 分層重構（tools/agents/orchestrator），分層明確、命名標準化
- API 路徑語意化，/orchestrate → /agent/single_turn_dispatch，/multi_turn_step → /agent/multi_turn_step
- agent 註冊雙軌（YAML+Python），自動合併，分層可擴充
- orchestrator 只調度 agent，agent 封裝 tool，分層依賴正確
- 前端完整維護 history，支援多輪對話、history answer、意圖判斷
- 前端/後端資料流、API schema、分流邏輯、history spec 全面同步
- UX 優化：意圖 label、<details> 摘要、錯誤訊息、history 展開
- README 架構圖、history/intention/spec 流程、分層說明同步更新
- 測試覆蓋 agent 註冊、合併、respond 格式與 API schema