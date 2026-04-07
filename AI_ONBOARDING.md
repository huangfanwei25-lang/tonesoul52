# AI Onboarding Guide | AI 引導指南

> **Purpose**: 給未來沒有記憶的 AI 實例的快速引導。
> **Author**: 黃梵威 (Fan-Wei Huang) + Previous AI Instances
> **Last Updated**: 2026-04-07
> **Status**: active AI entrypoint that routes later agents into operational, canonical, deep-map, and interpretive lanes without collapsing them together.

## Clean First-Hop Route

Use this route before reading the repo in bulk:

1. Open `docs/AI_QUICKSTART.md`
2. Run `python scripts/start_agent_session.py --agent <your-id>`
3. Read `readiness`, `canonical_center`, and `hook_chain`
4. If the work touches compaction, handoff survival, or "what may be compressed", open:
   - `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md`
   - `docs/architecture/TONESOUL_SUCCESSOR_COLLABORATION_AND_HOT_MEMORY_CONTRACT.md`
5. If needed, run:
   - `python -m tonesoul.diagnose --agent <your-id>`
   - `python scripts/run_r_memory_packet.py --agent <your-id> --ack`
   - `python scripts/run_observer_window.py --agent <your-id>`
6. Only then widen into `DESIGN.md`, `docs/architecture/`, or code

Tiered entry options:

- `--tier 0` = instant gate for quick bounded work
- `--tier 1` = orientation shell for feature continuation
- default / `--tier 2` = full bundle for deeper governance

Current first-hop rule:

- `docs/AI_QUICKSTART.md` = operational entry
- `AI_ONBOARDING.md` = routing map
- `DESIGN.md` = system center
- `task.md` = ratified short board only

Do not:

- treat observer prose as execution permission
- treat compaction summary as completed work
- write outside ideas into `task.md` before running task-board parking preflight

---

## AI Reading Stack（從這裡開始）

| Lane | 文件 | Authority | Use When | 不要把它當成 |
|------|------|-----------|----------|--------------|
| **Operational Start** | [`docs/AI_QUICKSTART.md`](docs/AI_QUICKSTART.md) | `operational` | 第一次進 repo 的前 1 分鐘 | 架構真理面 |
| **Working Reference** | [`docs/AI_REFERENCE.md`](docs/AI_REFERENCE.md) | `operational` | 工作中查術語、決策路徑、紅線 | 「所有詞都已進 runtime」的證據 |
| **Canonical Anchor** | 下方 `Canonical Architecture Anchor` | `canonical` | 要做架構、runtime、權威順序判斷前 | 可選閱讀 |
| **Deep Anatomy** | [`docs/narrative/TONESOUL_ANATOMY.md`](docs/narrative/TONESOUL_ANATOMY.md) | `deep_map` | 改整體結構前，或要回答「ToneSoul 到底是什麼」 | runtime contract |
| **Interpretive Lane** | [`docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`](docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md), [`docs/narrative/TONESOUL_CODEX_READING.md`](docs/narrative/TONESOUL_CODEX_READING.md) | `interpretive` | 結構已清楚，但承重意義仍模糊時 | 可執行真理 |

**新 AI 最低要求：先讀 `docs/AI_QUICKSTART.md`，再執行 `python scripts/start_agent_session.py --agent <your-id>`；它現在會直接回 `readiness=pass / needs_clarification / blocked`。結束前執行 `python scripts/end_agent_session.py --agent <your-id> --summary "<short summary>" --path "<path>"`。若要拆解或除錯，再退回顯式的 `diagnose -> packet --ack -> claim list` 與 `checkpoint/compaction -> release`。**

---

> Below: Original architecture document index (for deep reference).
> Purpose: AI onboarding entrypoint for ToneSoul architecture, retrieval order, and collaboration boundaries.
> Last Updated: 2026-03-28

## Canonical Architecture Anchor

Read these before making architecture assumptions:

1. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
2. `docs/notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md`
3. `docs/architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md`
4. `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
5. `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
6. `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
7. `docs/notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md`
8. `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md`
9. `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md`
10. `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md`
11. `docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md`
12. `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`

If long prose, scattered repo state, and runtime behavior disagree, prefer the canonical architecture anchor.
If multiple "knowledge" directories appear to disagree, use the knowledge surface boundary map before inferring authority.
If runtime layers and model-attachment direction feel split apart, use the eight-layer convergence map before inventing a new architecture story.
If retrieval path is unclear, use the L7 retrieval contract before bulk-reading markdown.
If adapters, RL, or distillation are in scope, use the L8 boundary contract before proposing training surfaces.
If the next question is how developer agents should persist tension, vows, vetoes, and stance drift across sessions, open `docs/notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md` before inventing a new memory workflow.
If the next question is how Redis-backed shared runtime memory should fit into ToneSoul, or what "R-memory" should and should not dominate, open `docs/architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md` before proposing a new memory stack.
If runtime state authority, Redis/file fallback truth, dashboard behavior, or commit-order safety are in conflict, open `docs/notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md` before trusting the prettier surface.
If the next question is whether multiple agents may safely share one hot runtime layer, or how far ToneSoul may push a "semantic field" idea without overclaiming, open `docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md` and `docs/research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md` before proposing concurrent canonical state.
If the next question is whether compaction memory, dashboard gamification, legacy trace repair, and security ideas should all enter the same runtime phase, open `docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md` before bundling them together.
If the next question is not merely "can agents share R-memory" but "what must be written for another agent to actually inherit progress, and in what order should claims, checkpoints, compactions, and commit happen", open `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` before assuming shared-state magic.
If a term from `law/`, `spec/`, `TONESOUL_ANATOMY.md`, or older guides sounds load-bearing but you are not sure whether it is actually runtime-hard, open `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md` and `docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md` before turning it into an engineering assumption.
If you need that same term-boundary posture in machine-readable form, open `docs/status/claim_authority_latest.json` before re-reading both prose tables by hand.
If you are about to describe a runtime path as "auditable", "understood", or "verified", open `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` first and keep the claim at the observable-shell level instead of inventing hidden access.
If you are treating `AXIOMS.json` as load-bearing but need to know what would actually weaken one axiom rather than merely repeat it, open `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md` first; treat it as a methodological companion, not as permission to rewrite the constitution.
If the repository layout is clear but the deeper internal shape still is not, open `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md` and then `docs/narrative/TONESOUL_CODEX_READING.md`; treat them as grounded interpretive aids, not as replacements for code or contracts.
If you need the original draft idea for self-dogfooding ToneSoul on top of agent workflows, open `docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md`, but treat it as a draft source until it is rewritten cleanly.
If you need compact machine-readable guidance, open `docs/status/l7_retrieval_contract_latest.json` and `docs/status/l8_distillation_boundary_latest.json`.
If you need the first directly usable operational layer, open `docs/status/l7_operational_packet_latest.json` and `docs/status/l8_adapter_dataset_gate_latest.json`.
If you need the default repo-root session-start bundle, run `python scripts/start_agent_session.py --agent <your-id>`. If you need the live hot-state handoff surface itself for another agent or tool, run `python scripts/run_r_memory_packet.py --agent <your-id> --ack` or query `GET /packet`, and validate the shape against `spec/governance/r_memory_packet_v1.schema.json`.
If you want the default repo-root session-end bundle, run `python scripts/end_agent_session.py --agent <your-id> --summary "<short summary>" --path "<path>"`; it writes a bounded handoff surface and releases owned claims unless you pass `--no-release`.
If you need to leave a bounded resumability handoff without mutating canonical governance posture, run `python scripts/save_compaction.py --agent <name> --summary "<short summary>"`, feed the same JSON shape into the script via `--input` / stdin, or call `POST /compact` on the gateway.
If you are not sure whether a new runtime note belongs in claim, checkpoint, compaction, perspective, or subject snapshot, preview it with `python scripts/route_r_memory_signal.py --agent <name> --summary "<short summary>" --path "<path>" --next-action "<next>"`, then add `--write` only after the route looks right.
If stable boundaries, decision preferences, or verified routines materially changed and later agents should inherit them as durable non-canonical structure, run `python scripts/save_subject_snapshot.py --agent <name> --summary "<short summary>" --boundary "<boundary>" --preference "<preference>"`.
If the question is not merely "should I write a subject snapshot" but "which hot-state surfaces may refresh which subject fields without inflating identity", open `docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` and `docs/architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md` first; treat them as subject-refresh boundary aids, not as permission to auto-promote identity.
If `subject_refresh` already says `active_threads=may_refresh_directly (compaction-backed)` and no promotion hazards remain, you may apply the bounded heuristic with `python scripts/apply_subject_refresh.py --agent <your-id> --field active_threads` instead of manually rewriting the full snapshot.
If the question is not merely "how do I start a session" but "is this task truly ready, what track is it, and should scope changes append a delta or fork a new phase", open `docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md` and `docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md` first; treat them as control-plane discipline aids, not as replacement runtime gates.
If the question is not merely "what did council decide" but "who dissented, how confident was the verdict, what may be replayed later, and did deliberation depth match task stakes", open `docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` and `docs/architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` first; treat them as council deliberation discipline aids, not as permission to rewrite runtime council behavior from prose alone.
If the question is not merely "what verdict did council produce" but "how independent is council really, what do its confidence numbers actually mean, and which quality upgrades are safe without pretending calibration already exists", open `docs/architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md`, `docs/architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md`, and `docs/architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md` first; treat them as council realism and calibration aids, not as permission to overstate current plurality or confidence.
If the question is not merely "how do I hand off the current hot state" but "what structure should survive across sessions, tasks, agents, or models without turning into hidden memory magic", open `docs/architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md` first; treat it as a context-continuity adoption map, not as live runtime permission to transfer everything.
If the question is not merely "what should survive" but "what may I safely ack, apply, or promote from packet / compaction / checkpoint / snapshot surfaces, and when has that continuity already decayed", open `docs/architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md`, `docs/architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md`, and `docs/architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md` first; treat them as receiver-side continuity discipline aids, not as live runtime authorization to silently promote hot-state into canonical truth.
If the question is not merely "what survives" but specifically "which hot-memory layers may be compressed, recomputed, quarantined, or never compressed", open `docs/architecture/TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md` before inferring a new compaction/compression story from observer-window prose.
If the question is not merely "what should survive" but "how should I structure the extraction/transfer prompt itself so goal, priority, evidence, compression, and receiver instructions stay coherent", open `docs/architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md` first; treat it as a prompt-discipline skeleton, not as a universal mega-prompt or runtime truth source.
If the question is not merely "how should the prompt be structured" but "which ToneSoul-native prompt variant fits this job", open `docs/architecture/TONESOUL_PROMPT_VARIANTS.md` after the skeleton; treat it as a variant catalog for project continuity, conversation distillation, operator snapshot, council replay, and session-end resumability.
If you need to start writing immediately instead of designing a prompt from scratch, open `docs/architecture/TONESOUL_PROMPT_STARTER_CARDS.md` and pick the smallest card that matches the job.
If more than one terminal or agent may touch the same task, claim it first with `python scripts/run_task_claim.py claim <task_id> --agent <name>` or `POST /claim`, and inspect current collisions with `python scripts/run_task_claim.py list` or `GET /claims`.
If you need claim-governance boundaries for theory vs mechanism, open `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md` and `docs/status/abc_firewall_latest.json`.
If duplicate doc names, mirror lanes, or missing purpose/date metadata are blocking retrieval, open `docs/status/doc_convergence_inventory_latest.json` and `docs/plans/doc_convergence_cleanup_plan_2026-03-22.md` before proposing renames or merges.
If you need the full multi-wave roadmap for repository documentation cleanup, open `docs/plans/doc_convergence_master_plan_2026-03-23.md` before starting a new convergence pass.
If the overall documentation lane still feels too flat or noisy, open `docs/architecture/DOC_AUTHORITY_STRUCTURE_MAP.md` and `docs/status/doc_authority_structure_latest.json` before inventing a new taxonomy.
If the collision is not a true duplicate but a same-basename semantic split, open `docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`, `spec/governance/basename_divergence_registry_v1.json`, and `docs/status/basename_divergence_distillation_latest.json` before deciding to rename anything.
If nested private-memory shadows are in scope, treat `memory/.hierarchical_index/` as the active lane and confirm current posture in `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md` and `docs/status/private_memory_shadow_latest.json` before touching any memory data.
If paradox fixtures are in scope, treat `PARADOXES/` as the canonical governance casebook and `tests/fixtures/paradoxes/` as the test projection lane; confirm current posture in `docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md` and `docs/status/paradox_fixture_ownership_latest.json`.
If engineering-book mirrors are in scope, treat `docs/engineering/` as canonical and confirm current sync posture in `docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md` and `docs/status/engineering_mirror_ownership_latest.json`.

## 🔄 Session Start: Load Governance State (ALL Agents)

> [!IMPORTANT]
> **Every AI agent MUST do this as the FIRST action of every session.**

Use the lightweight reader when you only need posture:

```bash
python scripts/read_governance_state.py
```

Use the default collaborative bundle when you want the full session-start handshake in one command:

```bash
python scripts/start_agent_session.py --agent <your-id>
```

If you need the explicit breakdown for debugging or tooling, expand the bundle to:

```bash
python -m tonesoul.diagnose --agent <your-id>
python scripts/run_r_memory_packet.py --agent <your-id> --ack
python scripts/run_task_claim.py list
```

This auto-discovers `governance_state.json` from these locations:
1. `./governance_state.json` (repo-local, for testing)
2. `~/.gemini/tonesoul/governance_state.json` (Antigravity)
3. `~/.codex/memories/governance_state.json` (Codex)
4. `~/.tonesoul/governance_state.json` (generic)

If no state file exists, initialize one:
```bash
python scripts/init_governance_state.py --output <your-agent-storage-path>/governance_state.json
```

At session end, run `python scripts/end_agent_session.py --agent <your-id> --summary "<short summary>" --path "<path>"` and the `/session-end` workflow when you are also writing back a canonical trace.

See `docs/RFC-015_Self_Dogfooding_Runtime_Adapter.md` for the full contract.

---

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
