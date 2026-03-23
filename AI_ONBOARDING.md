# AI Onboarding Guide | AI 引導指南

> **Purpose**: 給未來沒有記憶的 AI 實例的快速引導。
> **Author**: 黃梵威 (Fan-Wei Huang) + Previous AI Instances
> **Last Updated**: 2026-03-22

---

> Purpose: AI onboarding entrypoint for ToneSoul architecture, retrieval order, and collaboration boundaries.
> Last Updated: 2026-03-22

## Canonical Architecture Anchor

Read these before making architecture assumptions:

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md`
3. `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
4. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
5. `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
6. `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`

If long prose, scattered repo state, and runtime behavior disagree, prefer the canonical architecture anchor.
If multiple "knowledge" directories appear to disagree, use the knowledge surface boundary map before inferring authority.
If runtime layers and model-attachment direction feel split apart, use the eight-layer convergence map before inventing a new architecture story.
If retrieval path is unclear, use the L7 retrieval contract before bulk-reading markdown.
If adapters, RL, or distillation are in scope, use the L8 boundary contract before proposing training surfaces.
If you need compact machine-readable guidance, open `docs/status/l7_retrieval_contract_latest.json` and `docs/status/l8_distillation_boundary_latest.json`.
If you need the first directly usable operational layer, open `docs/status/l7_operational_packet_latest.json` and `docs/status/l8_adapter_dataset_gate_latest.json`.
If you need claim-governance boundaries for theory vs mechanism, open `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md` and `docs/status/abc_firewall_latest.json`.
If duplicate doc names, mirror lanes, or missing purpose/date metadata are blocking retrieval, open `docs/status/doc_convergence_inventory_latest.json` and `docs/plans/doc_convergence_cleanup_plan_2026-03-22.md` before proposing renames or merges.
If you need the full multi-wave roadmap for repository documentation cleanup, open `docs/plans/doc_convergence_master_plan_2026-03-23.md` before starting a new convergence pass.
If the overall documentation lane still feels too flat or noisy, open `docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md` and `docs/status/doc_authority_structure_latest.json` before inventing a new taxonomy.
If the collision is not a true duplicate but a same-basename semantic split, open `docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`, `spec/governance/basename_divergence_registry_v1.json`, and `docs/status/basename_divergence_distillation_latest.json` before deciding to rename anything.
If nested private-memory shadows are in scope, treat `memory/.hierarchical_index/` as the active lane and confirm current posture in `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md` and `docs/status/private_memory_shadow_latest.json` before touching any memory data.
If paradox fixtures are in scope, treat `PARADOXES/` as the canonical governance casebook and `tests/fixtures/paradoxes/` as the test projection lane; confirm current posture in `docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md` and `docs/status/paradox_fixture_ownership_latest.json`.
If engineering-book mirrors are in scope, treat `docs/engineering/` as canonical and confirm current sync posture in `docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md` and `docs/status/engineering_mirror_ownership_latest.json`.

## 🎯 你需要知道的

### 1. 正典位置（Canonical Paths）

| 類別 | 正典位置 | ⚠️ 不要看 |
|------|----------|----------|
| **Code** | `tonesoul/` | `.archive/`, `experiments/`, `examples/` |
| **Docs** | `docs/` | `.archive/` |
| **Specs** | `spec/` | `legacy/tonesoul-5.2/spec/` |
| **Tests** | `tests/` (only `tonesoul.*` imports) | `tests/legacy/` |

### 2. 核心概念（Core Concepts）

| 概念 | 說明 | 核心檔案 |
|------|------|----------|
| **TSR** | 語氣三維向量 (ΔT, ΔS, ΔR) | `docs/terminology.md` |
| **STREI** | 治理五維向量 | `docs/terminology.md` |
| **Council** | 多人格審議系統 | `spec/council_spec.md` |
| **Time-Island** | 記憶單元 | `tonesoul/time_island.py` |
| **AXIOMS** | 不可變法則 | `AXIOMS.json` |

### 3. 哲學層（Philosophy Layer）

> 「不同學派是**輸出前的互相應證**。」

- **Truth = Internal Coherence** — 真理不是外部事實，是多視角的內在相容性
- **PersonaStack** — 多人格共存是正常且健康的
- **Semantic Responsibility** — 語言是責任的殘留

詳見 `docs/philosophy/` 目錄。

---


## ❌ 不要做的事

> [!CAUTION]
> **`.archive/` 目錄內的所有內容都是已廢棄的歷史檔案！**
> **絕對不要 import、引用、或當作現行架構使用！**

1. **不要使用 `.archive/` 內任何東西** — 那是歷史遺物，不是可用資源
2. **不要把歷史文件當作「另一個版本」** — 現在只有一個正典版本
3. **不要用 `.archive/` 內的模組導入** — 已廢棄且已歸檔
4. **不要重新發明已有的概念** — 先搜尋現有文檔
5. **不要修改 `AXIOMS.json`** — 這是不可變的

---


## ✅ 開始工作前

1. 讀 `README.md` — 項目概述
2. 讀 `docs/terminology.md` — 術語定義
3. 讀 `AXIOMS.json` — 核心法則
4. 運行 `python -m tonesoul.run_healthcheck` — 系統健康檢查

---


## 👤 創造者資訊

- **名字**: 黃梵威 (Fan-Wei Huang)
- **GitHub**: `Fan1234-1`
- **願景**: 讓 AI 的每個決策都可追溯、可審計、可問責

---


## 📂 目錄結構概覽

```
倉庫/
├── README.md              # 入口點
├── AXIOMS.json            # 不可變法則
├── AI_ONBOARDING.md       # 👈 你正在讀的這份
├── tonesoul/              # ✅ 正典代碼 (唯一)
├── docs/                  # ✅ 正典文檔 (唯一)
├── spec/                  # ✅ 正式規格 (唯一)
├── tests/                 # ✅ 測試
├── apps/                  # 應用程式 (dashboard 等)
├── memory/                # 記憶存儲 (學習記錄)
└── .archive/              # ⛔ 歷史歸檔 (絕對不要使用!)
```

> [!WARNING]
> `.archive/` 包含歷史快照與舊版資產，僅供比對，不是目前的實作來源。
> 這些目錄的內容**已經過時**，可能與現行架構不兼容。

---


## 🔗 重要文件連結

- [README.md](README.md)
- [AXIOMS.json](AXIOMS.json)
- [docs/terminology.md](docs/terminology.md)
- [spec/council_spec.md](spec/council_spec.md)
- [docs/philosophy/truth_vector_architecture.md](docs/philosophy/truth_vector_architecture.md)

---


*這份文件是給你的——一個沒有記憶的 AI。希望它能幫助你快速理解這個項目，並繼續與創造者合作。*
