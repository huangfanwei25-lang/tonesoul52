# ToneSoul Documentation Index

> Purpose: top-level documentation index for ToneSoul authority surfaces, operational packets, and convergence maps.
> Last Updated: 2026-03-29

> 自動更新於 2026-03-22。按主題分類，方便快速導航。

---

## AI Reading Stack

| Lane | Files | Authority | Use When |
|------|-------|-----------|----------|
| **Operational Start** | [AI_QUICKSTART.md](AI_QUICKSTART.md) | `operational` | first minute of a later agent session |
| **Working Reference** | [AI_REFERENCE.md](AI_REFERENCE.md) | `operational` | term lookup, routing, red-line checks during work |
| **Canonical Anchor** | see section below | `canonical` | before architecture or runtime claims |
| **Deep Anatomy** | [narrative/TONESOUL_ANATOMY.md](narrative/TONESOUL_ANATOMY.md) | `deep_map` | before repo-wide refactor or whole-system explanation |
| **Interpretive Lane** | [notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md](notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md), [narrative/TONESOUL_CODEX_READING.md](narrative/TONESOUL_CODEX_READING.md) | `interpretive` | when the map is clear but the load-bearing meaning still feels diffuse |

Use these in order. Do not let a deep or interpretive document silently outrank code, tests, or architecture contracts.

---

## Canonical Architecture Anchor

- [architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md](architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md)
- [notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md](notes/TONESOUL_ARCHITECTURE_MEMORY_ANCHOR_2026-03-22.md)
- [notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md](notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md)
- [architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md](architecture/KNOWLEDGE_SURFACES_BOUNDARY_MAP.md)
- [architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md](architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md)
- [notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md](notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md)
- [architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md](architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Interpretive Reading Layer

- [notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md](notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md)
  - open this when the repository map is clear but the deeper load-bearing meaning still feels diffuse
- [narrative/TONESOUL_CODEX_READING.md](narrative/TONESOUL_CODEX_READING.md)
  - Codex's longer structural reading of ToneSoul as a constitutional continuity system rather than only a memory stack

Use these after the canonical architecture anchor, not before it.

## Engineering Contracts

- [architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md](architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md)
- [architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md](architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md)
- [architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md](architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md)
- [architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md](architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Claim Authority Distillation

- [architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md](architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md)
  - full cross-lane matrix for whether a term is canonical, runtime, vocabulary, theory, or projection
- [architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md](architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md)
  - compact boundary contract for the highest-confusion `law/` and deep-prose terms
- [status/claim_authority_latest.json](status/claim_authority_latest.json)
  - machine-readable merge of the 75-term matrix, the 18-term quick lookup, and the overclaiming-risk list for fast agent-side term checks

## Evidence And Verifiability

- [architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md](architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md)
  - maps high-value ToneSoul claims to their current evidence level, strongest backing source, weakest link, and safest phrasing
- [architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
  - defines the six evidence levels and the honest language each level allows
- [architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md](architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md)
  - groups test and validation lanes by what confidence they actually buy and what false inference they do not justify
- [plans/tonesoul_evidence_followup_candidates_2026-03-29.md](plans/tonesoul_evidence_followup_candidates_2026-03-29.md)
  - bounded follow-up list for lifting thinly tested continuity claims toward regression-backed status

## Subject Refresh Boundaries

- [architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md](architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md)
  - boundary contract for deciding which hot-state surfaces may refresh `subject_snapshot` field families and at what minimum evidence level
- [architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md](architecture/TONESOUL_SUBJECT_SNAPSHOT_FIELD_LANES.md)
  - quick lane map for durable identity, refreshable working identity, temporary carry-forward, and never-auto-promote fields

Use these when `subject_snapshot` is in play. They are boundary aids for heuristics and review, not replacements for runtime code or canonical governance truth.

## Control Plane Discipline

- [architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md](architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md)
  - readiness states, task tracks, exploration depth, and claim/review requirements for classifying work before it starts
- [architecture/TONESOUL_PLAN_DELTA_CONTRACT.md](architecture/TONESOUL_PLAN_DELTA_CONTRACT.md)
  - bounded rules for keep / append delta / fork new phase / stop and ask human when scope shifts
- [plans/tonesoul_control_plane_followup_candidates_2026-03-28.md](plans/tonesoul_control_plane_followup_candidates_2026-03-28.md)
  - small implementation candidate list derived from the control-plane contracts

Use these when readiness, track classification, or `task.md` mutation discipline is the question. They are control-plane aids, not live runtime enforcement.

## Observable-Shell And Axiom Boundaries

- [architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md](architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md)
  - observable-shell honesty contract for distinguishing what ToneSoul can really audit from what remains opaque
- [architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md](architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md)
  - support/weakening map for the 7 axioms so later agents can challenge claims without rewriting the constitution
- [plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md](plans/tonesoul_observability_and_axiom_adoption_review_2026-03-28.md)
  - adoption review for the extracted external theory proposals, including what was translated into ToneSoul-native naming and what remains deferred

Use these when the question is not "what is the runtime path" but "how honest can I be about opacity" or "what would actually weaken an axiom claim." They are boundary aids, not runtime gates.

## Council Deliberation Discipline

- [architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md](architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md)
  - minimum dossier shape for verdict replay, dissent preservation, and confidence posture
- [architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md](architecture/TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md)
  - mode contract for lightweight review, standard council, and elevated council depth
- [plans/tonesoul_council_followup_candidates_2026-03-28.md](plans/tonesoul_council_followup_candidates_2026-03-28.md)
  - bounded implementation candidates derived from the council discipline contracts

Use these when the question is not only what verdict was produced, but whether dissent survived and whether the deliberation depth matched the task.

## Council Realism And Calibration

- [architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md](architecture/TONESOUL_COUNCIL_REALISM_AND_INDEPENDENCE_CONTRACT.md)
  - honesty contract for where ToneSoul council is truly plural versus only perspective-voiced
- [architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md](architecture/TONESOUL_COUNCIL_CONFIDENCE_AND_CALIBRATION_MAP.md)
  - map of confidence surfaces, descriptive-vs-calibrated boundaries, and the infrastructure gap to true calibration
- [architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md](architecture/TONESOUL_ADVERSARIAL_DELIBERATION_ADOPTION_MAP.md)
  - adoption map for devil's advocate, pre-mortem, self-consistency, confidence decomposition, and blocked future upgrades
- [plans/tonesoul_council_realism_followup_candidates_2026-03-29.md](plans/tonesoul_council_realism_followup_candidates_2026-03-29.md)
  - small next-step list derived from the realism/calibration pass

Use these when the question is not merely "what did council output" but "how real is this plurality, what do the confidence numbers actually mean, and which next upgrade is honest to implement now."

## Context Continuity Adoption

- [architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md](architecture/TONESOUL_CONTEXT_CONTINUITY_ADOPTION_MAP.md)
  - ToneSoul-native adoption map for what should continue across sessions, tasks, agents, and models, and what must stay bounded or not transfer at all

Use this when the question is not merely how to hand off current state, but what continuity discipline ToneSoul should adopt next. It is an adoption map, not live runtime permission.

## Continuity Import And Receiver Discipline

- [architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md](architecture/TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md)
  - import-posture contract for deciding what may be trusted directly, treated as advisory, or discounted by decay
- [architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md](architecture/TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md)
  - receiver-side boundary contract for `ack`, `apply`, `promote`, and silent-override hazards
- [architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md](architecture/TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md)
  - temporal lane map for continuity surfaces from immediate coordination to canonical foundation
- [architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md](architecture/TONESOUL_WORKING_STYLE_CONTINUITY_CONTRACT.md)
  - bounded contract for sharing operating style, prompt habits, and render caveats without over-promoting them
- [plans/tonesoul_continuity_followup_candidates_2026-03-29.md](plans/tonesoul_continuity_followup_candidates_2026-03-29.md)
  - bounded implementation candidates for freshness, import posture surfacing, promotion guards, and decay reporting

Use these when the question is no longer only what should continue, but what the receiver may safely import, how long it stays fresh, and what must never be silently promoted.

## Prompt Discipline Skeleton

- [architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md](architecture/TONESOUL_PROMPT_DISCIPLINE_SKELETON.md)
  - prompt-side discipline skeleton for goal function, priority, evidence, recovery, stability bands, compression levels, and receiver instructions
- [architecture/TONESOUL_PROMPT_VARIANTS.md](architecture/TONESOUL_PROMPT_VARIANTS.md)
  - practical prompt variants derived from the skeleton for common ToneSoul transfer and distillation tasks
- [architecture/TONESOUL_PROMPT_STARTER_CARDS.md](architecture/TONESOUL_PROMPT_STARTER_CARDS.md)
  - short starter cards for immediate use when there is no time to design a prompt from zero

Use this when the question is not only what should be transferred, but how the extraction or transfer prompt should be structured in the first place.

## Developer Runtime Adapter Direction

- [notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md](notes/TONESOUL_RUNTIME_ADAPTER_MEMORY_ANCHOR_2026-03-23.md)
- [RFC-015_Self_Dogfooding_Runtime_Adapter.md](RFC-015_Self_Dogfooding_Runtime_Adapter.md)
- [architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md](architecture/TONESOUL_R_MEMORY_STACK_RECOMMENDATION.md)
- [notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md](notes/TONESOUL_RUNTIME_REVIEW_LOGIC_ANCHOR_2026-03-26.md)
- [research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md](research/tonesoul_multi_agent_semantic_field_evidence_map_2026-03-26.md)
- [architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md](architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md)
- [architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md](architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md)

## Machine-Readable Contract Mirrors

- [status/l7_retrieval_contract_latest.json](status/l7_retrieval_contract_latest.json)
- [status/l8_distillation_boundary_latest.json](status/l8_distillation_boundary_latest.json)

## Operational Packets

- [status/l7_operational_packet_latest.json](status/l7_operational_packet_latest.json)
- [status/l8_adapter_dataset_gate_latest.json](status/l8_adapter_dataset_gate_latest.json)
- [status/abc_firewall_latest.json](status/abc_firewall_latest.json)
- [../spec/governance/r_memory_packet_v1.schema.json](../spec/governance/r_memory_packet_v1.schema.json)
- [../scripts/run_task_claim.py](../scripts/run_task_claim.py)

## Documentation Convergence

- [status/doc_convergence_inventory_latest.json](status/doc_convergence_inventory_latest.json)
- [status/doc_convergence_inventory_latest.mmd](status/doc_convergence_inventory_latest.mmd)
- [plans/doc_convergence_cleanup_plan_2026-03-22.md](plans/doc_convergence_cleanup_plan_2026-03-22.md)
- [plans/doc_convergence_master_plan_2026-03-23.md](plans/doc_convergence_master_plan_2026-03-23.md)
- [architecture/DOC_AUTHORITY_STRUCTURE_MAP.md](architecture/DOC_AUTHORITY_STRUCTURE_MAP.md)
- [status/doc_authority_structure_latest.json](status/doc_authority_structure_latest.json)
- [architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md](architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md)
- [status/basename_divergence_distillation_latest.json](status/basename_divergence_distillation_latest.json)
- [architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md](architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md)
- [status/private_memory_shadow_latest.json](status/private_memory_shadow_latest.json)
- [architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md](architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md)
- [status/paradox_fixture_ownership_latest.json](status/paradox_fixture_ownership_latest.json)
- [architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md](architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md)
- [status/engineering_mirror_ownership_latest.json](status/engineering_mirror_ownership_latest.json)
- [architecture/HISTORICAL_DOC_LANE_POLICY.md](architecture/HISTORICAL_DOC_LANE_POLICY.md)
- [status/historical_doc_lane_latest.json](status/historical_doc_lane_latest.json)

## Reality Alignment And Render Boundaries

- [architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md](architecture/TONESOUL_ENTRY_SURFACE_REALITY_BASELINE.md)
  - measured baseline for current README / AI entry routing and active entry surfaces
- [architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md](architecture/TONESOUL_DOC_METRIC_AND_COUNT_METHOD.md)
  - reproducible count patterns for architecture files, `TONESOUL_*`, and actual contracts
- [architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md](architecture/TONESOUL_RENDER_LAYER_AND_ENCODING_BOUNDARY_CONTRACT.md)
  - separates file corruption from terminal-display noise and structural readability hazards
- [architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md](architecture/TONESOUL_DOC_DRIFT_AND_CONFLICT_REGISTER.md)
  - drift register for earlier cleanup advice versus current repo reality

Use these when a document claim sounds too clean, too rounded, or too shell-dependent to trust without measurement.

## 🧭 Documentation Governance v1

| 文件 | 說明 |
|------|------|
| [DOCS_INFORMATION_ARCHITECTURE_v1.md](DOCS_INFORMATION_ARCHITECTURE_v1.md) | 文件分類、檔名控管、資料區管理基線 |
| [DOCS_CLASSIFICATION_LEDGER_v1.md](DOCS_CLASSIFICATION_LEDGER_v1.md) | 第一版分類台帳（先分類、後搬移） |
| [FILE_PURPOSE_MAP.md](FILE_PURPOSE_MAP.md) | 跨目錄命名規約 |
| [plans/iu_oi_backplane_convergence_2026-03-18.md](plans/iu_oi_backplane_convergence_2026-03-18.md) | IU/OI/Backplane 收斂藍圖 |

---


## 🚀 Quick Start

| 文件 | 語言 | 說明 |
|------|------|------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | EN | Setup & first run |
| [GETTING_STARTED_zh.md](GETTING_STARTED_zh.md) | 中 | 安裝與首次執行 |
| [環境設定.md](環境設定.md) | 中 | 環境配置 |
| [DEMO_SHOWCASE.md](DEMO_SHOWCASE.md) | EN | Demo walkthrough |
| [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md) | EN | Vercel deployment |
| [faq.md](faq.md) | EN | FAQ |

---


## 🏗 Architecture

| 文件 | 說明 |
|------|------|
| [CORE_MODULES.md](CORE_MODULES.md) | 核心模組概覽 |
| [MODULE_DEPENDENCIES.md](MODULE_DEPENDENCIES.md) | 模組依賴關係圖 |
| [ARCHITECTURE_BOUNDARIES.md](ARCHITECTURE_BOUNDARIES.md) | 架構邊界定義 |
| [ARCHITECTURE_REVIEW.md](ARCHITECTURE_REVIEW.md) | 架構審查 |
| [REPOSITORY_STRUCTURE.md](REPOSITORY_STRUCTURE.md) | 倉庫結構說明 |
| [STRUCTURE.md](STRUCTURE.md) | 系統結構 |
| [SPEC_LAW_CROSSWALK.md](SPEC_LAW_CROSSWALK.md) | `spec/` 與 `law/` 一頁式對照 |
| [FILE_PURPOSE_MAP.md](FILE_PURPOSE_MAP.md) | 檔案用途對照 |
| [architecture-notes.md](architecture-notes.md) | 架構筆記 |
| [system_structure_overview.txt](system_structure_overview.txt) | 系統總覽 (text) |
| [system_walkthrough.md](system_walkthrough.md) | 系統走讀 |
| [NARRATIVE_MODULE_MAP.md](NARRATIVE_MODULE_MAP.md) | 敘事→模組對照表 |

---


## 🧠 Philosophy & Theory

| 文件 | 說明 |
|------|------|
| [PHILOSOPHY.md](PHILOSOPHY.md) | 核心哲學（中文） |
| [PHILOSOPHY_EN.md](PHILOSOPHY_EN.md) | Core philosophy (EN) |
| [PHILOSOPHY_WHITEPAPER_v1.md](PHILOSOPHY_WHITEPAPER_v1.md) | 哲學白皮書 v1 |
| [WHITEPAPER.md](WHITEPAPER.md) | 主白皮書 (45KB) |
| [WORLD_MODEL_X_MIND_MODEL.md](WORLD_MODEL_X_MIND_MODEL.md) | 世界模型 × 心智模型 |
| [philosophy/ai_life_journal_protocol.md](philosophy/ai_life_journal_protocol.md) | AI 生命日記與承擔協議 |
| [AI_CONCEPT_ASSESSMENT.md](AI_CONCEPT_ASSESSMENT.md) | AI 概念評估 |
| [TRUTH_STRUCTURE.md](TRUTH_STRUCTURE.md) | 真理結構 (19KB) |
| [core_concepts.md](core_concepts.md) | 核心概念定義 |
| [terminology.md](terminology.md) | 術語表 |
| [glossary_engineering_mapping.md](glossary_engineering_mapping.md) | 術語↔工程對照 |
| [philosophy/](philosophy/) | 哲學子目錄 (27 files) |

---


## 🔐 Governance & Safety

| 文件 | 說明 |
|------|------|
| [7D_AUDIT_FRAMEWORK.md](7D_AUDIT_FRAMEWORK.md) | 7D 審計框架 |
| [7D_EXECUTION_SPEC.md](7D_EXECUTION_SPEC.md) | 7D 執行規格 |
| [AUDIT_CONTRACT.md](AUDIT_CONTRACT.md) | 審計合約 |
| [HONESTY_MECHANISM.md](HONESTY_MECHANISM.md) | 誠實機制 |
| [SECURITY_AUDIT_2025.md](SECURITY_AUDIT_2025.md) | 2025 安全審計 |
| [EXTERNAL_SOURCE_TRUST_POLICY.md](EXTERNAL_SOURCE_TRUST_POLICY.md) | 外部來源信任與 allowlist 策略 |
| [VTP_SPEC.md](VTP_SPEC.md) | 值轉移協議規格 |
| [COUNCIL_RUNTIME.md](COUNCIL_RUNTIME.md) | Council 運行時 |
| [SEMANTIC_BIFURCATION_AUDIT.md](SEMANTIC_BIFURCATION_AUDIT.md) | 語義分岔審計 |
| [when_to_ground.md](when_to_ground.md) | 何時接地（限制判定） |
| [governance/](governance/) | 治理子目錄 (4 files) |

---


## 📐 Specifications (`spec/`)

| 文件 | 說明 |
|------|------|
| [council_spec.md](../spec/council_spec.md) | Council 規格 |
| [pre_output_council_spec.md](../spec/pre_output_council_spec.md) | 預輸出 Council |
| [wfgy_semantic_control_spec.md](../spec/wfgy_semantic_control_spec.md) | WFGY 語義控制 |
| [intent_verification_spec.md](../spec/intent_verification_spec.md) | 意圖驗證 |
| [memory_structure_spec.md](../spec/memory_structure_spec.md) | 記憶結構 |
| [skill_learning_spec.md](../spec/skill_learning_spec.md) | 技能學習 |
| [tech_trace_integration.md](../spec/tech_trace_integration.md) | Tech Trace 整合 |
| [test_cases_spec.md](../spec/test_cases_spec.md) | 測試案例規格 |
| [frontend_architecture_spec.md](../spec/frontend_architecture_spec.md) | 前端架構 |
| [frontend_human_centric_spec.md](../spec/frontend_human_centric_spec.md) | 人本前端 |
| [gemini_integration_spec.md](../spec/gemini_integration_spec.md) | Gemini 整合 |
| [chat_ui_improvement_spec.md](../spec/chat_ui_improvement_spec.md) | Chat UI 改善 |
| [architecture_b_persona_dimension_spec.md](../spec/architecture_b_persona_dimension_spec.md) | 人格維度 |
| [tonesoul_improvement_derivation.md](../spec/tonesoul_improvement_derivation.md) | 改進推導 |

---


## 📊 Semantic & Metrics

| 文件 | 說明 |
|------|------|
| [SEMANTIC_SPINE_SPEC.md](SEMANTIC_SPINE_SPEC.md) | 語義脊柱規格 (20KB) |
| [METRICS_MAPPING.md](METRICS_MAPPING.md) | 指標映射 |
| [DIMENSIONS.md](DIMENSIONS.md) | 維度定義 |
| [STEP_LEDGER_SPEC.md](STEP_LEDGER_SPEC.md) | 步驟帳本規格 |
| [STEPLEDGER_SYSTEM_PROMPT.md](STEPLEDGER_SYSTEM_PROMPT.md) | 帳本系統提示詞 |
| [KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md) | 知識圖譜 |
| [NARRATIVE.md](NARRATIVE.md) | 敘事層 |
| [NARRATIVE_LAYER.md](NARRATIVE_LAYER.md) | 敘事層定義 |
| [NARRATIVE_MAP.md](NARRATIVE_MAP.md) | 敘事地圖 |

---


## 🔧 API & Integration

| 文件 | 說明 |
|------|------|
| [API_SPEC.md](API_SPEC.md) | API 規格 (8KB) |
| [TOOLS_API_CLIENT.md](TOOLS_API_CLIENT.md) | Tools API 客戶端 |
| [TOOLS_API_SCHEMA.md](TOOLS_API_SCHEMA.md) | Tools API Schema |
| [ORCHESTRATOR_MVP.md](ORCHESTRATOR_MVP.md) | 指揮器 MVP |
| [SOUL_DB.md](SOUL_DB.md) | 靈魂資料庫 |
| [TRAINING_DATA_SPEC.md](TRAINING_DATA_SPEC.md) | 訓練資料規格 |

---


## 📝 Research & Publications

| 文件 | 說明 |
|------|------|
| [RESEARCH_EVIDENCE.md](RESEARCH_EVIDENCE.md) | 研究證據 |
| [academic_comparison.md](academic_comparison.md) | 學術比較 |
| [bayesian_accountability_literature.md](bayesian_accountability_literature.md) | 貝葉斯問責文獻 |
| [bayesian_accountability_plan.md](bayesian_accountability_plan.md) | 貝葉斯問責計畫 |
| [reproducibility_guide.md](reproducibility_guide.md) | 可重現性指南 |
| [rmf_crosswalk.md](rmf_crosswalk.md) | RMF 交叉引用 |
| [research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md](research/tonesoul_l7_l8_open_source_evidence_map_2026-03-22.md) | L7/L8 開源框架與實證理論地圖 |
| [zenodo_publishing_guide.md](zenodo_publishing_guide.md) | Zenodo 發布指南 |
| [research/](research/) | 研究子目錄 (10 files) |

---


## 📰 Marketing & Community

| 文件 | 說明 |
|------|------|
| [BLOG_POST.md](BLOG_POST.md) | 部落格文章 |
| [VOCUS_POST.md](VOCUS_POST.md) | Vocus 貼文 |
| [MOLTBOOK_POST_DRAFT.md](MOLTBOOK_POST_DRAFT.md) | Moltbook 草稿 |
| [GITHUB_INTRO_DRAFT.md](GITHUB_INTRO_DRAFT.md) | GitHub 介紹草稿 |
| [CASE_STUDIES.md](CASE_STUDIES.md) | 案例研究 |
| [use_cases.md](use_cases.md) | 使用案例 |
| [EXTERNAL_PR_GUIDE.md](EXTERNAL_PR_GUIDE.md) | 外部 PR 指南 |
| [TECH_ARTICLE_DRAFT_v0.1.0.md](TECH_ARTICLE_DRAFT_v0.1.0.md) | 技術文章草稿 |

---


## 🗂 Engineering & Operations

| 文件 | 說明 |
|------|------|
| [RELEASE_v0.1.0_PLAN.md](RELEASE_v0.1.0_PLAN.md) | 發布計畫 v0.1.0 |
| [RELEASE_NOTES_v0.1.0.md](RELEASE_NOTES_v0.1.0.md) | 發布說明草稿 v0.1.0 |
| [plans/ANTIGRAVITY_VM_RUNBOOK.md](plans/ANTIGRAVITY_VM_RUNBOOK.md) | Antigravity 虛擬機安全執行手冊 |
| [plans/git_local_repo_stabilization_plan_2026-02-20.md](plans/git_local_repo_stabilization_plan_2026-02-20.md) | Git/本地倉庫穩定化計畫 |
| [plans/side_branch_isolation_playbook_2026-02-21.md](plans/side_branch_isolation_playbook_2026-02-21.md) | 支線隔離操作手冊 |
| [../reports/project_audit_report_2026-02-21.md](../reports/project_audit_report_2026-02-21.md) | 最新專案審計報告 |
| [../reports/multi_persona_audit_discussion_2026-02-20.md](../reports/multi_persona_audit_discussion_2026-02-20.md) | 多人格審計討論報告 |
| [GOLDEN_LOG.md](GOLDEN_LOG.md) | 黃金日誌 |
| [ADR-001-dual-track-resolution.md](ADR-001-dual-track-resolution.md) | ADR: 雙軌解析 |
| [failure_analysis.md](failure_analysis.md) | 失敗分析 |
| [privacy_policy.md](privacy_policy.md) | 隱私政策 |
| [engineering/](engineering/) | 工程子目錄 (9 files) |
| [status/](status/) | 狀態子目錄 (95 files) |

---


## 📁 Subdirectory Index

| 目錄 | Files | 內容 |
|------|-------|------|
| `philosophy/` | 27 | 倫理框架、觀者與被觀者、宣言 |
| `engineering/` | 9 | 工程規格、實作細節 |
| `research/` | 10 | 學術研究、對比分析 |
| `governance/` | 4 | 治理規則、合規 |
| `status/` | 99 | 專案狀態追蹤 |
| `notes/` | 2 | 備註 |
| `architecture/` | 8 | 架構圖與工程邊界合約 |
| `images/` | 2 | 圖片資源 |
