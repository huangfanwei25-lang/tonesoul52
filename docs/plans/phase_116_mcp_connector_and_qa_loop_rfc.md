# Phase 116: MCP Connector & Automated QA Loop (RFC)

> Purpose: propose the MCP connector and automated QA loop that extends progressive disclosure into tools and self-healing review.
> Last Updated: 2026-03-23

## 1. 背景與動機 (Background & Motivation)

在 Phase 115 中，我們成功將 ToneSoul 的技能合約升級為「三層漸進式揭露 (Progressive Disclosure)」，實現了極致的安全沙盒與 Token 節省。現在，ToneSoul 具備了高度結構化且安全的技能定義（L1 路由 + L2 邊界 + L3 負載）。

接下來的關鍵，是讓 ToneSoul 的這套本地安全技能庫能夠**標準化地與外部生態系對接**，並且讓我們的 7D 防禦火力**閉環學習**。為此，我們在 Phase 116 提出基於 Model Context Protocol (MCP) 的轉接器，以及將紅隊演練 (Red Teaming) 轉化為代理人自我學習記憶的 QA Loop。

---

## 2. 核心架構與設計目標

### 2.1 MCP 橋接器 (Model Context Protocol Adapter)
*   **用途**：讓任何支援 MCP 的客戶端（例如 Claude CLI, Cursor, 或其他第三方 Agent 框架）都能直接且安全地調用 ToneSoul 的技能（例如 `qa_auditor`, `local_llm`）。
*   **設計原則**：
    *   **無縫對接 L2 Signature**：MCP Server 啟動時，讀取 `registry.json`，直接將 L1 意圖 + L2 `json_schema` 映射為一組標準的 `MCP Tools`。
    *   **延遲加載 (Lazy Loading)**：MCP Client 在探索工具時，絕對不暴露 L3 的實際腳本，維持 Phase 115 的隔離承諾。
    *   **邊界強制執行 (Execution Profile Enforcement)**：MCP 層級必須檢查 Phase 112 定義的 Profile，例如禁止 `interactive` 的 MCP Client 執行 `engineering` 權限的危險動作。

### 2.2 自動化 QA 閉環 (Self-Healing Memory Loop)
*   **用途**：我們目前有強大的 `verify_7d.py` 進行 RDD (對抗性測試) 與 DDD (資料防禦)。但當測試失敗時，工程師手動修復後，Agent 本身沒有「記住」這個教訓。
*   **設計原則**：
    *   **Failure Ingestion**：擴充 `tools/agent_discussion_tool.py`，新增一個命令（例如 `ingest-qa`）能讀取 `verify_7d.py` 產生的錯誤報告 (JUnit XML 或 JSON 格式)。
    *   **Lesson Distillation**：將失敗的 Injection / Fuzzing 特徵提煉成「防禦教訓 (Security Lesson)」並追加寫入 `agent_discussion_curated.jsonl`，作為 Agent 長期記憶的一部分，防範未來的退化。

---

## 3. 實作任務指引 (Implementation Guide for Codex)

### Task 1: 實作 ToneSoul MCP Server
*   在 `tonesoul/mcp/server.py` (或類似路徑) 建立基於 Python MCP SDK 的實體。
*   實作 `list_tools` 介面：讀取 `skills/registry.json`，返回所有合法技能的 L1/L2 metadata。
*   實作 `call_tool` 介面：接收呼叫後，動態載入對應的 L3 Payload 進行執行，並返回結果。
*   **防呆機制**：必須拒絕繞過 L2 Signature 的無效工具呼叫。

### Task 2: 整合 Execution Profile 與 DistillationRiskGuard
*   將 Phase 112 的 `DistillationRiskGuard` 套用到 MCP 請求的路由層：若外部 MCP 客戶端試圖透過大量無意義的呼叫來萃取 (distill) ToneSoul 的底層 Prompt，應以 HTTP 429 或類似攔截機制阻斷。

### Task 3: 升級 `agent_discussion_tool.py` 實作 QA Loop 閉環
*   新增命令：`python tools/agent_discussion_tool.py ingest --source tests/reports/7d_run.json`。
*   邏輯：篩選出 status 為 `FAILED` 的 RDD/DDD 測試案例，透過本地 SLM (如 Qwen3) 或既有邏輯自動生成防禦建議，並 append 到 `agent_discussion_curated.jsonl` 中，標記類型為 `[QA_LESSON]`。

### Task 4: 測試與文件更新
*   撰寫針對 MCP Server 的端到端測試 (`test_mcp_server.py`)，確認它能正確映射 `qa_auditor` 技能。
*   更新 `context_engineering_reference.md` 以紀錄 ToneSoul 支援 MCP 協議，並指導開發者如何使用。

---

## 4. 預期效益
*   **生態系打通**：ToneSoul 將不再只是我們自己硬刻在 `ExecutePhase.ts` 裡的閉門造車，而是變成開源界可隨插即用的治理引擎 (Governance as a Service)。
*   **AI 的免疫系統**：透過 QA Loop 將紅隊演練結果寫入代理人記憶中，賦予了系統演化與自我修正的神經迴路，這將完美呼應 NLnet 補助計畫中對於 Cognitive System 的核心願景！
