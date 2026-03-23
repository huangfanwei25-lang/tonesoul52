# 主線藍圖：記憶系統 + 多 AI 協作（2026-02-22）

> Purpose: describe the mainline memory direction and its relationship to multi-agent orchestration work.
> Last Updated: 2026-03-23

## 1. 主線定義

ToneSoul 後續主線：

1. 記憶不是存檔，而是可審計、可衰減、可回放的決策脈絡。
2. 多 AI 協作不是平行聊天，而是有角色邊界、責任歸屬、衝突可見的工作流。
3. 所有重要輸出都要能回溯到證據與決策鏈（誰、何時、為何、依據什麼）。

---

## 2. 系統目標（第一性原則）

最小可行主線能力：

1. `可追溯`：每次關鍵決策有 provenance 與 evidence。
2. `可治理`：衝突與風險不被隱藏，能被 gate/contract 攔截。
3. `可協作`：多代理之間有角色分工與交接格式。
4. `可進化`：記憶可整理（consolidate/decay）且不失真。

---

## 3. 架構骨幹（對應現有模組）

1. 決策層（Deliberation）
   - `tonesoul/council/runtime.py`
   - `tonesoul/council/pre_output_council.py`

2. 狀態層（Tension + Persona）
   - `tonesoul/tension_engine.py`
   - `tonesoul/persona_dimension.py`
   - `tonesoul/adaptive_gate.py`

3. 記憶層（Memory + Provenance）
   - `tonesoul/memory/consolidator.py`
   - `memory/provenance_chain.py`
   - `tonesoul/memory/soul_db.py`

4. 證據層（Evidence Intake）
   - `tonesoul/tech_trace/capture.py`
   - `tonesoul/evidence_collector.py`

5. 守門層（Governance）
   - `tonesoul/contract_observer.py`
   - `scripts/verify_citation_integrity.py`
   - CI workflows in `.github/workflows/`

---

## 4. 多 AI 協作協議（最小版）

每個代理輸出至少要有：

1. `role`: 角色（Analyst / Guardian / Builder / Auditor）
2. `claim`: 主張
3. `evidence`: 依據（A/B/C 級）
4. `risk`: 風險說明
5. `handoff`: 下一步與接手條件

衝突規則：

1. 不消除分歧，先保留雙方主張。
2. 若 evidence 等級不同，A 層優先。
3. 若都非 A 層，輸出必須降級為「設計假設」。

---

## 5. 記憶治理規則

1. 短期記憶（working）只做暫存，不作長期人格依據。
2. 升格到長期記憶前，至少要有：
   - 可追溯來源
   - 風險標註
   - 角色簽名或審議結果
3. 記憶衰減不是刪除，而是降低權重並保留 provenance。

---

## 6. 近期執行階段

## Phase M1: 協作訊息格式化
- [x] 定義多代理共通輸出 schema（role/claim/evidence/risk/handoff）
- [x] 在 council transcript 中加入 schema 檢查
- 成功標準：多代理輸出可被程式驗證，不靠人工理解

## Phase M2: 記憶升格守門
- [x] 在 consolidator 前加入 evidence + provenance 檢查
- [x] 不符合條件的記憶留在 working 層
- 成功標準：長期記憶只保留可追溯內容

## Phase M3: 衝突可視化
- [x] 產出「代理分歧報告」與「衝突解決狀態」
- [x] 把衝突統計接到 status artifacts
- 成功標準：每次主線流程可看到分歧來源與處理結果

## Phase M4: 失敗可學習
- [x] 將 block/declare_stance 個案自動回寫到學習樣本
- [x] 定期輸出 memory quality 報告
- 成功標準：失敗案例能系統化降低重犯率

---

## 7. 主線承諾

後續所有主線修改，以「記憶質量 + 協作可審計性」為優先，不再只追求功能新增或 CI 綠燈。
