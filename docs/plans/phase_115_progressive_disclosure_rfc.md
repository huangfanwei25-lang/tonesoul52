# Phase 115: Progressive-Disclosure Skill Contract (RFC)

> Purpose: propose the progressive-disclosure skill contract for routing and loading agent capabilities with lower context cost.
> Last Updated: 2026-03-23

## 1. 背景與動機 (Background & Motivation)

隨著 ToneSoul 的 Agent 技能 (Skills) 越來越強大且數量增加，將所有技能的完整 Markdown (包含大量的 Prompt Few-shots、工具配置、安全規則) 一次性塞入 Context Window 會造成嚴重的 Token 污染與效能負擔。

基於 `claude-mem` 專案中驗證過的 3-layer 架構，我們在此提出「三層漸進式揭露合約 (Progressive-Disclosure Contract)」，確保 Agent 路由時僅讀取必要的最少資訊，命中後才逐步解壓縮所需的執行細節。

---

## 2. 核心架構：三層合約模型 (3-Layer Contract Model)

技能註冊表與 Markdown Frontmatter 將被重構，嚴格劃分界線：

### L1 (Routing / Triggering) - 極輕量路由層
*   **用途**：供主 Agent (Router) 進行意圖比對與分發。
*   **欄位**：
    *   `id`: 命名空間 (如 `qa_auditor`)
    *   `name`: 技能名稱 (如 `QA Auditor`)
    *   `triggers`: 觸發關鍵字矩陣
    *   `intent`: 一句話的極短意圖描述 (< 60 字)
*   **載入時機**：每次對話初始化時全域載入。

### L2 (API Boundary / Signature) - 參數與安全邊界層
*   **用途**：當 L1 命中後，用來向 Agent 展示如何呼叫這個技能，以及這個技能需要什麼參數與前提條件。
*   **欄位**：
    *   `json_schema`: Input/Output 參數定義
    *   `execution_profile`: 執行邊界 (如 `interactive`, `engineering`)
    *   `trust_tier`: 信任等級 (`trusted`, `reviewed`)
*   **載入時機**：僅當 L1 確信此技能高度相關時才載入進 Context。

### L3 (Execution Payload) - 執行籌載層
*   **用途**：真正龐大的領域知識、系統提示詞、Few-shots 範例、以及長篇安全鐵律。
*   **欄位**：
    *   完整的 Markdown Body / Orchestration Script
*   **載入時機**：只有在決定要將控制權轉交給該技能的 Sub-agent (如 Qwen3) 執行時，才提取出來作為其 System Prompt，**絕對不** 塞入主 Agent 的 Context。

---

## 3. 實作任務指引 (Implementation Guide for Codex)

### Task 1: 升級 `registry.schema.json` 與 `registry.json`
*   修改 `registry.schema.json`，強制分離 `l1_routing` 與 `l2_signature` 節點。
*   移轉現有 registry 的扁平結構至層次結構。

### Task 2: Frontmatter 重構 (`qa_auditor` / `local_llm`)
*   修改 `.agent/skills/SKILL.md` 的 Frontmatter 區塊。
*   將原本長篇的 `description` 精簡為 `l1_routing.intent`。
*   將參數需求等抽象到 `l2_signature` 中。

### Task 3: Runtime 解析器更新 (`tonesoul/council/skill_parser.py`)
*   重寫解析邏輯，提供三個明確的方法：
    *   `get_all_l1_routes()`: 供主體 Prompt Injection。
    *   `get_l2_signature(skill_id)`: 供 Tool Call 擴充。
    *   `get_l3_payload(skill_id)`: 供 Sub-agent 啟動。

### Task 4: 雙重驗證閘門更迭 (`verify_skill_registry.py`)
*   將 Phase 114 實作的防護網，適配到 L1/L2 的新結構上（確保 L1 的意圖描述足夠明確精準，且 L2 一定要包含 `execution_profile`）。

---

## 4. 預期效益
*   **Token 節省**：在未命中技能時，主 Agent 看到的技能清單大小從原本的數 KB 縮減為不到 100 Bytes / 技能。
*   **安全隔離**：主 Agent 不會被惡意技能的 L3 Payload 給 Prompt Injection。
*   **精準路由**：由 L1 `intent` 搭配 L2 `json_schema` 建立的強制關卡，大幅度降低 hallucinated tool calls。
