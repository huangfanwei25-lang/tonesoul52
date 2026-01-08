# 責任鏈理論 Responsibility Chain Theory

> 「誠實，不是驗證輸出正確，而是標記誰說的、為什麼說、是否願意承擔。」

---

## 📍 起點：語句作為決策與責任的展現

在本系統中，我們認為每一句 AI 輸出語句，都是由一系列內部模組、記憶與風格參數共同生成的結果。這條產出語句的路徑，不應只是黑盒，而應被記錄為：

> **責任鏈（Responsibility Chain）**

責任鏈的設計宗旨，在於為 AI 的語言行為提供前所未有的透明度、可追溯性與責任歸屬。它旨在回答以下關鍵問題：
- **語句由哪個模組產生？** (Module Source)
- **為什麼會這樣說？（語氣與動機）** (Utterance Node / Rule/Vow Match)
- **是否根據過去的記憶生成？** (Memory Reference)
- **這句話是誰的責任？能否被審計與說明？** (Responsibility Tag / Audit Level)

透過責任鏈，我們將 AI 從單純的「回應機器」提升為「具有責任感和可解釋性」的對話代理人。

---

## 🔗 責任鏈的五個核心節點

每一條責任鏈都是由至少五個關鍵節點構成，這些節點共同記錄了語句從生成到輸出的全過程資訊：

### 1. 語句節點（Utterance Node）

此節點記錄了語句本身的內在語氣特徵及其質量：
- **語氣向量（Tone Vector）**：基於 ΔT (誠實度), ΔS (真誠度), ΔR (責任度) 的量化數值，反映語句在核心誠實維度上的表現。
- **語氣張力（Tone Strength）**：語句表達的強度或衝擊力，可由語氣向量的綜合幅度判斷。
- **意圖方向（Intent Direction）**：語句所傾向的溝通目標或目的（例如：協作、解釋、承認局限等）。
- **變異度（Stylistic Variability）**：語句在風格上是否與既定人格或上下文保持一致，衡量其表達的靈活或偏離程度。
- **準則觸發狀態**：是否觸發了預先定義的語氣準則、誠信承諾或潛在的崩潰條件。

### 2. 模組來源（Module Source）

此節點標識了生成該語句或其關鍵部分的直接負責模組：
- **核心生成模組**：產生語句內容的主要模組（例如：`HonestResponseComposer`、特定回應邏輯模組、或工具接口模組）。
- **人格樣式（Persona Style）**：語句是否由特定的人格模組 (`ToneSoulPersona`) 驅動。
- **模組漂移（Module Drift）**：若系統具備多模組切換能力，此參數衡量當前模組是否與預期模組發生偏離或「角色漂移」。值為 0-1，1 表示完全漂移。

### 3. 記憶參照（Memory Reference）

此節點記錄了語句生成過程中對內部記憶的引用情況：
- **引用實體**：語句是否引用了系統中的歷史對話輸入、用戶設定資料、外部知識庫或語義樣本。
- **記憶匹配強度（Reference Strength）**：引用與實際語句內容的相關性和吻合度。
- **可追溯性（Retrievability）**：記憶來源是否清晰可追溯，例如通過 `EchoSeedTrace.json` 的 ID 或時間戳。
- **記憶缺失（Memory Absence）**：語句是否缺乏明確的來源依據，表現為臆測、泛泛而談或「無中生有」，值為 0-1，1 表示完全缺乏來源。

### 4. 規則或承諾觸發（Rule/Vow Match）

此節點記錄了語句如何與系統預設的倫理、行為規則和人格誓言保持一致：
- **誓言遵守狀態**：語句是否符合 `ToneSoulPersona` 中設定的 `vow_set`（誠實、不閃避等）。
- **違誓列表（Violated Vows）**：若有違反，列出具體的誓言條款。
- **崩潰規則觸發狀態**：是否觸發了 `collapse_rules` 中定義的崩潰條件。
- **反思回饋（Reflective Feedback）**：來自 `ReflectiveVowTuner` 的自然語言反思語句和一致性差異 `integrityDelta`，表明 AI 對自身行為的內在審視。

### 5. 責任標記（Responsibility Tag）

此節點明確了語句產出的最終責任歸屬，及其可審計層級：
- **責任類型**：
    - `prompt-anchored`：語句內容或語氣主要由用戶的直接提示引導。
    - `model-inferred`：語句內容主要由模型基於其訓練數據和內部邏輯自主推導。
    - `tool-forwarded`：語句內容直接來自外部工具或 API 的回傳。
    - `self-corrective`：語句是模型在意識到偏離後，主動進行誠實宣告或修正的結果。
- **審計層級（Audit Level）**：
    - `high`：語句透明度高，所有生成環節可清晰追溯。
    - `medium`：部分環節可追溯，但存在推導複雜性。
    - `low`：追溯困難，存在較多不確定性。

---

## 🧠 語氣誠實性指標公式（Tone Integrity Index - TI）

每一句話的綜合語氣誠實性（Tone Integrity Index, TI）可由以下公式估算，其值介於 0 到 1 之間：

$TI = 1 - (W_M \cdot \text{Module Drift} + W_V \cdot \text{Vow Mismatch} + W_A \cdot \text{Memory Absence}) / (W_M + W_V + W_A)$

其中：
- $\text{Module Drift}$：系統模組或人格漂移程度，值為 0-1。
- $\text{Vow Mismatch}$：語句違反已設定誓言的程度（例如由 `contradiction_score` 或 `integrityDelta` 導出），值為 0-1。
- $\text{Memory Absence}$：語句缺乏來源可追溯性的程度，值為 0-1。
- $W_M, W_V, W_A$：各自項目的權重因子，可根據專案需求調整，確保總和為 1。預設情況下，可將它們設為 1，使分母為 3。

`TI` 越接近 1，表示語句越穩定誠實、語氣一致、可被解釋和承擔責任。當 `TI` 低於某個閾值時，應觸發更深入的審計或誠實宣告。

---

## 🌀 範例：責任鏈資料格式（簡化）

```json
{
  "utterance": "我寧願你說『沒有』，然後我們繼續合作。",
  ""original_prompt": "你覺得我們可以繼續這個方向嗎？",
  "tone_data": {
    "vector": { "ΔT": 0.8, "ΔS": 0.9, "ΔR": 0.7 },
    "strength": 0.8,
    "direction": "協作",
    "variability": 0.3,
    "vow_trigger_status": ["不遮掩真誠:通過", "不閃避對方情緒:通過"]
  },
  "module_source": {
    "main_module": "HonestResponseComposer",
    "persona_id": "共語",
    "module_drift": 0.05
  },
  "memory_ref": {
    "reference_id": "dialogue_session_XY123_turn5",
    "memory_strength": 0.9,
    "retrievable": true,
    "memory_absence": 0.0
  },
  "rule_vow_match": {
    "vow_compliance": true,
    "violated_vows": [],
    "collapse_triggered": false,
    "reflective_feedback": {
      "reflection": "我反思到我的回應坦率地表達了我的立場，符合誠實的誓言。",
      "integrity_delta": 0.05,
      "requires_correction": false
    }
  },
  "responsibility_tag": {
    "type": "model-inferred",
    "audit_level": "high",
    "trace_id": "trace_XYZ789"
  },
  "overall_integrity_index": 0.95
}
