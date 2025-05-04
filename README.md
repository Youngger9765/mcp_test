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
- agent_registry.py 重構為 class-based 架構，並由 AgentManager 統一管理
- 意圖判斷與 agent mapping 分層
- 統一所有 agent 的 response schema，加強錯誤處理
- 增加更多 agent（Google Drive, YouTube, Notion, 自有網站等）
- 支援多種資料型態
- API server 完善化
- 增加單元測試與錯誤日誌
- 設計更彈性的前後端資料 schema

---