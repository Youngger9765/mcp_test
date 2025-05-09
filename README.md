# mcp_test

---

# MCP 架構說明文件

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

- 支援多 agent 註冊（YAML + Python 雙軌）
- 前後端皆以統一 schema 溝通
- 易於擴充、低耦合、錯誤處理完善

---

## 系統分層架構

1. **前端顯示**
   - 僅驗證 API 回傳資料格式與正確性
   - 支援多種資料型態（表格、樹狀圖、純文字等）
   - 實際 render 交由其他網站

2. **後端處理**
   - **意圖判斷（LLM）**：接收 user query，呼叫 LLM 進行意圖分類
   - **agent mapping 與調用**：根據意圖選擇對應 agent，統一繼承 `BaseAgent`
   - **API 查詢與資料整理**：agent 與外部 API 溝通，回傳統一格式
   - **統一 response schema**：所有 API 回傳皆符合統一 schema

### 智慧 Smart Chat 架構圖

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
│  3. 呼叫 /smart_chat API      │
└────────────┬─────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│  /smart_chat (server.py)                                   │
│  1. 取得完整 history（多輪訊息）                            │
│  2. 取最近五輪對話（user+assistant 共 10 則，若不足則全取） │
│  3. 將這 10 則訊息組成 messages 給 intent_analyzer         │
│  4. intent_analyzer 判斷 intent                            │
│     ├─ chat → 呼叫 LLM (gpt-4.1-mini)（用完整 history）     │
│     └─ tool_call → orchestrate（只用最新 user content）     │
│         └─ LLM 決定 tool_id，執行 function                 │
│  5. 回覆加上 source 標記，append 到 history                │
│  6. 回傳新的 history 給前端                                 │
└────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────┐
│   前端 UI   │
│  4. 顯示回覆│
│  5. history 繼續累積│
└─────────────┘
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

## 相關檔案說明

- `mcp_config.yaml`：agent metadata 設定
- `src/agent_registry.py`：進階 agent class/function 與 get_python_agents()
- `src/agent_loader.py`：自動合併 YAML 與 Python agent，產生 AGENT_LIST

---

## 進度追蹤

### ✅ 已完成
- 架構分層初步規劃
- agent 設計採用 JSON/Dict 結構
- agent respond function 統一格式
- API response schema 自動化測試

### 🚧 TODO
- 增加更多 agent（Google Drive, YouTube, Notion, 自有網站等）
- 支援多種資料型態
- API server 完善化
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

---

### Smart Chat 關鍵 SPEC

#### 1. API 端點
- 路徑：`/smart_chat`
- 方法：POST
- 輸入參數：
  - `history`：array，格式為多輪訊息陣列，每則為 `{ role: "user"|"assistant", content: string, [source]: "chat"|"tool" }`
    - 來源標記 `source` 為 assistant 回覆時才有，user 不需此欄位

#### 2. 訊息處理邏輯
- 每次呼叫時，前端需傳完整 history
- 後端會從 history 取最近五輪對話（user+assistant 共 10 則，若不足則全取）
- 將這 10 則訊息組成 messages，丟給 intent_analyzer 判斷 intent

#### 3. 意圖判斷
- intent_analyzer 會根據最近五輪上下文判斷 intent
  - 回傳 `intent: "chat"` 或 `intent: "tool_call"`（或其他）

#### 4. 分流邏輯
- 若 intent = "chat"：
  - 用完整 history 呼叫 LLM（gpt-4.1-mini），產生 assistant 回覆
  - assistant 回覆加上 `source: "chat"`
- 若 intent = "tool_call"：
  - 只取最新一則 user content，呼叫 orchestrator
  - orchestrator 讓 LLM 決定 tool_id，執行對應 function
  - 工具回覆內容加上 `source: "tool"`

#### 5. 回傳格式
- 回傳內容：
  - `history`：array，為原本 history 加上本次 assistant 回覆（含 source 標記）
  - `intent`：object，為本次 intent_analyzer 的判斷結果（含理由）

#### 6. 關鍵規則
- 每次回傳的 history，必須包含本次 assistant 回覆，且 assistant 回覆必須有 source 欄位
- assistant 回覆的 source 必須正確標記為 "chat" 或 "tool"
- intent_analyzer 必須只用最近五輪對話判斷 intent，不可只看單一 user content
- orchestrator 只吃 user content，不吃完整 history

#### 7. 錯誤處理
- 若 history 為空或最後一則不是 user，回傳 error
- 若 orchestrator 或 LLM 回覆異常，回傳 error 並標記原因

---

### TODO for Smart Chat
- [ ] 前端送出訊息時，完整累積 history 並呼叫 /smart_chat
- [ ] 後端 /smart_chat 正確取最近五輪對話給 intent_analyzer
- [ ] intent_analyzer 判斷 intent 準確，並能根據上下文分流
- [ ] chat 路徑 assistant 回覆有 source: "chat"
- [ ] tool_call 路徑 assistant 回覆有 source: "tool"
- [ ] 回傳的 history 必須正確累積、標記來源
- [ ] 錯誤情境（如 history 格式錯誤、LLM 回覆異常）能正確回傳 error
- [ ] 撰寫單元測試覆蓋上述所有情境