# mcp_test

---

# MCP 架構書

## SPEC

### ✅ 已完成

- 架構分層初步規劃（前端驗證、後端意圖判斷、agent mapping、API 統一格式）
- agent 設計採用 JSON/Dict 結構，支援多 agent 註冊
- 每個 agent 具備 id、name、description、example_queries、respond function
- agent respond function 已統一回傳符合 SPEC 的 dict 格式
- 前端僅作為驗證資料格式與正確性之用
- API response schema 已落實並通過自動化測試

### 🚧 TODO

- agent_registry.py 重構為 class-based 架構，並由 AgentManager 統一管理
- 意圖判斷（LLM）與 agent mapping 分層，降低耦合
- 統一所有 agent 的 response schema，並加強錯誤處理與 fallback
- 增加更多 agent（如 Google Drive, YouTube, Notion, 自有網站等）
- 支援多種資料型態（表格、樹狀圖、純文字等）
- API server 完善化，前端僅驗證資料格式，render 交由其他網站
- 增加單元測試與錯誤日誌
- 設計更彈性的前後端資料 schema，方便未來擴充

---

## 架構分層

### 1. 前端顯示
- 僅作為驗證 API 回傳資料格式與正確性之用。
- 支援多種資料型態（如表格、樹狀圖、純文字等）的驗證。
- 實際 render 交由其他網站。

### 2. 後端處理

#### 2.1 意圖判斷（LLM）
- 接收 user query，呼叫 LLM 進行意圖分類。
- 回傳標準化意圖資料（如：目標 agent、查詢類型等）。

#### 2.2 agent mapping 與調用
- 根據意圖判斷結果，選擇對應 agent。
- agent 以 class-based 設計，統一繼承自 `BaseAgent`。
- agent 註冊與管理由 `AgentManager` 處理，方便擴充。

#### 2.3 API 查詢與資料整理
- agent 負責與外部 API 溝通，取得資料。
- 每個 agent 回傳統一格式（schema），支援多種資料型態。
- 所有錯誤皆以標準 error 格式回傳，保證前端可辨識。

#### 2.4 統一 response schema
- 所有 API 回傳皆符合統一 schema，包含 type、content、meta、agent_id、error 等欄位。

---

## 設計原則

- **高擴充性**：新增 agent 僅需繼承 BaseAgent 並註冊。
- **低耦合**：意圖判斷、agent mapping、資料查詢分層明確。
- **標準化格式**：前後端皆以統一 schema 溝通，方便驗證與 render。
- **錯誤處理完善**：所有錯誤皆有 fallback 與標準格式。

---

## API Response Schema 範例