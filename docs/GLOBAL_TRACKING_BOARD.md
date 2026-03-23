# 🌐 ToneSoul Global Tracking Board (2026-02-22)

> Purpose: track major parallel workstreams, owners, and queue posture across the broader ToneSoul effort.
> Last Updated: 2026-03-23

> **"想法太多，實作太少。" —— 為了避免概念膨脹，這裡收斂並追蹤全域所有尚未實作的重點想法與架構藍圖。**

這份追蹤表將工作清楚劃分為兩條線：
- **Antigravity (Phase Planner)**：負責高階哲學、架構相變、安全網與核心概念驗證 (PoC)。
- **Codex (Deep Optimizer)**：負責效能優化、CI/CD、數學實作、重複性基礎建設。

---

## 🟥 核心相變與安全 (Antigravity's Queue)

這些任務涉及系統架構的根本改變或核心治理邏輯，需要高度對齊哲學。

| 狀態 | 提案 / 功能 | 說明 | 相關文件 / 線索 |
|:---:|:---|:---|:---|
| ✅ | **Memory Consolidator (記憶淬鍊)** | 從 `self_journal.jsonl` 萃取長期認知並自動修改 Prompt。含 Soul Patcher 回寫 SOUL.md。 | `tonesoul_evolution/` (Private Repo) |
| ✅ | **對抗式自省 (Red/Blue Team Loop)** | LLM-first 紅藍隊推理 + 3-tier 輸出解析器，含 rule-based fallback。 | `tonesoul_evolution/adversarial/` |
| ✅ | **議會自我演化 (Council Weight Evolution)** | 根據投票對齊率動態調整權重，已含 JSON 持久化。 | `council/evolution.py`, `memory/council_evolution.json` |
| ⏳ | **Auto-Patching 機制與私鑰配置** | 讓 AI 能根據錯誤自己發 PR 修補自己 (Private Repo 限定)。 | `AGENTS.md` |
| ⏳ | **收入策略與代幣保護** | 規劃 ToneSoul 未來的算力成本平衡與潛在的 API 資源防護閘門。 | User Request |

---

## 🟦 底層優化與數學驗證 (Codex's Queue)

這些任務需要深度的數學理解、效能調校、或是穩定的基礎建設。

| 狀態 | 提案 / 功能 | 說明 | 相關文件 / 線索 |
|:---:|:---|:---|:---|
| ⏳ | **WFGY 數學張力內化 (Tension Math)** | 閱讀並實作 WFGY 3.0 的張力幾何學，用具體數學公式取代目前 `AdaptiveGate` 的簡單閾值。 | `WFGY-3.0_Singularity-Demo` |
| ✅ | **Phase 105-B: Decay Query (Top-K)** | 使用 `heapq` 將 `_decay_records` 的時間複雜度降為 O(N log K)。 | `CODEX_TASK.md`, `reports/decay_query_benchmark_latest.md` |
| ⏳ | **RFC-007: 結構化事件元資料** | 加 `actor_type`, `intent_outcome`, `risk_level` 到 journal schema。 | `docs/rfc-007-structured-event-metadata.md` |
| ⏳ | **自動化 CI 驗證 (CI/CD Pipeline)** | 建立 `.github/workflows/pytest-ci.yml` 自動跑 Phase III 的深度混沌測試。 | `tests/qa_auditor/` |
| ⏳ | **Cross-session Memory Benchmark** | 壓測跨會話記憶恢復機制，確保 `visual_chain.json` 不會拖慢 P99 延遲。 | `unified_pipeline.py` |

---

## 🟪 架構實驗室 (Backlog / Ideas)

這些是「有提過，但還沒有明確 Engineering Plan」的點子，先放在這裡以免忘記。

- **三位一體人格的「真正」內部思維隔離**：目前的 Muse/Logos/Aegis 是 prompt 隔離，未來是否能做到不同本機小模型 (`qwen` vs `llama`) 的模型隔離？
- **ToneBridge 動態可視化**：在前端即時畫出使用者的 Tension 折線圖。
- **GDD (Govern-Driven) 審計控制台**：建立一個管理者介面，能視覺化查看 `provenance_ledger.jsonl` 中 AI 做每個決定的「判例法」依據。

---

*註：此追蹤表將隨著開發進度由 Antigravity 或 Codex 定期更新。*
