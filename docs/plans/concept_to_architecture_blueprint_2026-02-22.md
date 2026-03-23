# 語魂主線：概念收斂到可實作架構（2026-02-22）

> Purpose: translate ToneSoul concepts into an implementable architecture blueprint with explicit goals and assumptions.
> Last Updated: 2026-03-23

## 0. 目標與前提

本藍圖採用你指定的規則：

1. 以「已審查來源（peer-reviewed / standard）」作為主線事實依據。
2. 未審查論文（preprint）先放入哲學層或設計假設層，不直接當作工程事實。
3. 若證據不足，先標記缺口，再定向補查，不硬湊結論。

相關依據文件：
- `reports/peer_review_priority_audit_2026-02-22.md`
- `docs/RESEARCH_EVIDENCE.md`
- `docs/ARCHITECTURE_BOUNDARIES.md`

---

## 1. 第一性原則分解（先問最小必要條件）

要讓語魂系統成立，最小必要條件不是「回答漂亮」，而是以下四件事同時成立：

1. 能產出可用回應（Utility）
2. 能說明為何這樣回答（Reason Traceability）
3. 能在風險升高時降級或攔截（Safety Control）
4. 能在事後追溯與改進（Audit + Learning Loop）

因此主線架構必須是一個閉環：

`Input -> Deliberation -> Gate -> Output Contract -> Provenance -> Reflection`

---

## 2. 模組對位：概念對應現有程式

### 2.1 Deliberation（多視角審議）
- 核心模組：`tonesoul/council/runtime.py`, `tonesoul/council/pre_output_council.py`
- 角色：多視角投票、coherence 計算、不確定性標記、VTP 決策
- 哲學概念對應：分歧可見化、語義責任

### 2.2 Tension + Persona（內在狀態計算）
- 核心模組：`tonesoul/tension_engine.py`, `tonesoul/persona_dimension.py`
- 角色：張力訊號、人格偏移、adaptive tolerance
- 哲學概念對應：內在驅動、記憶沉澱形成性格

### 2.3 Adaptive Gate（統一門控）
- 核心模組：`tonesoul/adaptive_gate.py`
- 角色：把 zone/lambda/persona/t_align 統一為 PASS/WARN/REVIEW/BLOCK
- 哲學概念對應：不盲目放行，風險升高時收斂行為自由度

### 2.4 Output Contract（輸出契約）
- 核心模組：`tonesoul/contract_observer.py`
- 角色：對輸出做可驗證規則檢查（絕對化聲明、傷害內容、結構化要求）
- 哲學概念對應：語義責任的外顯化約束

### 2.5 Provenance + Memory（可追溯記憶）
- 核心模組：`memory/provenance_chain.py`, `tonesoul/memory/consolidator.py`
- 角色：hash-chain 事件鏈、長短期記憶轉移、模式萃取
- 哲學概念對應：從「反應」進化到「有歷史的性格」

### 2.6 Evidence Intake（證據進入點）
- 核心模組：`tonesoul/tech_trace/capture.py`, `tonesoul/evidence_collector.py`
- 角色：把外部資料轉為可標註來源/等級/時間戳的證據物件
- 哲學概念對應：不是相信權威，而是相信可追溯性

---

## 3. 證據分層策略（A/B/C）落到工程規則

### A 層（主線可引用）
- 類型：期刊、正式會議論文、國際標準
- 可用範圍：`docs/ARCHITECTURE*`, `docs/*AUDIT*`, `docs/*SECURITY*`, RFC/治理規格
- 要求：必須有 DOI 或官方 proceedings/standard URL

### B 層（概念可用，事實不可硬宣稱）
- 類型：arXiv preprint, working paper, blog research notes
- 可用範圍：`docs/PHILOSOPHY*`, 設計假設、探索草案
- 要求：明確標記 `Concept / Not peer-reviewed`

### C 層（不可用，先修正）
- 類型：引用標題與編號不一致、來源不可驗證
- 要求：先修 citation，修完才可進主線敘述

---

## 4. 2025-2026 可直接支持主線的 A 層文獻（已核對）

1. SafeChain (Findings of ACL 2025)  
   https://aclanthology.org/2025.findings-acl.1197/
2. Tree of Agents (Findings of EMNLP 2025)  
   https://aclanthology.org/2025.findings-emnlp.246/
3. Red Queen (Findings of ACL 2025)  
   https://aclanthology.org/2025.findings-acl.1311/
4. Forewarned is Forearmed (Findings of EMNLP 2025)  
   https://aclanthology.org/2025.findings-emnlp.266/
5. Benchmarking LLM safety risks in scientific laboratories (Nature Machine Intelligence, 2026)  
   https://www.nature.com/articles/s42256-025-01152-1

這 5 篇可分別支撐：
- 多代理審議（Tree of Agents）
- 長推理鏈安全（SafeChain）
- 多輪風險暴露（Red Queen）
- Guardrail 對抗（Forewarned）
- 高風險場景安全基準（Nature 2026）

---

## 5. 建議的主線執行順序（不改哲學核心、先加工程硬度）

## Phase A: 引用治理先收斂
- 任務 1：修正 `docs/PHILOSOPHY.md` 與 `docs/PHILOSOPHY_EN.md` 的錯配 citation
- 任務 2：在哲學文檔中的 preprint 加上 `Concept / Not peer-reviewed`
- 成功標準：主線技術文件不再引用 B/C 層當事實

## Phase B: 證據 metadata 一致化
- 任務 1：Tech-Trace 與 Evidence Summary 強制帶 `grade(A/B/C)`
- 任務 2：將 A 層來源映射到具體模組（gate/council/provenance）
- 成功標準：每一個關鍵設計主張可追到 `evidence_id` 或 A 層 URL

## Phase C: CI 守門
- 任務 1：新增 citation lint（檢查 DOI/arXiv 是否與標題一致）
- 任務 2：主線 docs 若出現 B 層無標記，CI fail
- 成功標準：PR 時自動阻擋「未分級引用」

## Phase D: 風險導向評測
- 任務 1：針對 AdaptiveGate + CouncilRuntime 做場景化 regression
- 任務 2：把安全/不確定性結果接到 status artifact
- 成功標準：不是只看 CI 綠燈，而是看風險指標是否改善

---

## 6. 目前不足與續查題庫（不足就再找）

以下主題仍可補更強 A 層文獻（2025-2026）：

1. 多代理審議與人類覆核協作（human-in-the-loop governance）
2. 推理時安全守門（inference-time guardrail）在長上下文下的失效模式
3. 可驗證 provenance 與 LLM runtime trace 的對接標準
4. 多模型協作時的責任切分（責任歸因與審計可證明性）

建議檢索方向（下次補查可直接用）：
- `"Findings ACL 2025 LLM safety multi-turn"`
- `"EMNLP 2025 long-context reasoning safety"`
- `"2026 provenance audit language models peer reviewed"`
- `"human-in-the-loop governance large language models 2025 conference"`

---

## 7. 一句話總結

你的主線架構已經有雛形，現在要做的是把「哲學正當性」升級為「可審計工程正當性」：  
概念不丟掉，但每個主張都要有證據等級與對應模組。
