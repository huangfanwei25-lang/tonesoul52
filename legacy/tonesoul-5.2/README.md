# ToneSoul 5.2: AI Governance Toolkit
# 語魂 5.2：AI 治理工具包

> **Make your LLM decisions auditable, traceable, and trustworthy.**  
> **讓你的 LLM 決策可審計、可追溯、可信任。**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Research](https://img.shields.io/badge/License-Research%20%26%20Collaboration-orange.svg)](LICENSE)
[![Looking for Collaborators](https://img.shields.io/badge/🤝-Looking%20for%20Collaborators-brightgreen.svg)](#looking-for-collaborators--尋找協作者)

---

## 🤝 Looking for Collaborators | 尋找協作者

**We're building something new in AI governance. Join us!**  
**我們正在建構 AI 治理的新方向，歡迎加入！**

If you're interested in:
- 🔬 AI alignment beyond RLHF
- 📊 Auditable AI decision systems
- 🧠 "Linguistic responsibility residue" engineering
- 🌏 Cross-cultural AI governance

→ Open an [Issue](https://github.com/Fan1234-1/tonesoul52/issues) or start a [Discussion](https://github.com/Fan1234-1/tonesoul52/discussions)!

如果您對以下主題感興趣：AI 對齊、可審計 AI、語言責任殘留、跨文化 AI 治理  
→ 歡迎開 Issue 或 Discussion 與我們聯繫！

## Why This Exists | 為什麼需要這個

Every LLM application faces the same problem:  
**"How do I know my AI made the right decision?"**

每個 LLM 應用都面臨同樣的問題：  
**「我怎麼知道我的 AI 做了正確的決策？」**

ToneSoul 5.2 provides:

| Feature | 功能 | Benefit |
|---------|------|---------|
| **Decision Ledger** | 決策帳本 | Every AI action is logged with metrics, traceable like blockchain |
| **Multi-Persona Council** | 多人格議會 | Multiple "voices" debate before action, with dissent tracking |
| **STREI Metrics** | STREI 指標 | Stability, Tension, Responsibility, Ethics, Intent — quantified |
| **Healthcheck CLI** | 健康檢查 CLI | One command to verify your AI system is production-ready |

---

## Quick Start | 快速開始

```bash
# Clone and install | 複製並安裝
git clone https://github.com/Fan1234-1/tonesoul52.git
cd tonesoul52
pip install -e .

# Run system healthcheck | 執行系統健康檢查
python -m tonesoul52.run_healthcheck

# Healthcheck also validates the latest memory seed schema when available.

# Generate audit report | 產生審計報告
python -m tonesoul52.run_audit

# Check persona coverage | 檢查人格覆蓋率
python -m tonesoul52.run_council_healthcheck
```

See `5.2/docs/quickstart.md` for a minimal end-to-end walkthrough.

---

## Dependencies | 依賴

- `numpy` (YSTM vectors + terrain)
- `pyyaml` (context + memory seeds)
- `rich` (CLI formatting)
- Optional: `cairosvg` (PNG export for YSTM)
- Optional: `pillow` (PNG fallback renderer)

---

## Core Concepts | 核心概念

### 1. Decision Ledger | 決策帳本

Every AI decision is recorded with:
- Timestamp and unique hash
- Input context and output summary
- STREI metrics at decision time
- Policy applied and outcome

每個 AI 決策都會記錄：時間戳、唯一哈希、輸入輸出、STREI 指標、應用的政策。

```json
{
  "hash": "a3f2c1e8",
  "timestamp": "2025-12-25T12:00:00Z",
  "policy": "P_GENERAL_INTERACTION",
  "metrics": {"S": 0.85, "T": 0.3, "R": 0.9, "E": 0.95, "I": 0.7},
  "decision": "PASS"
}
```

### 2. Multi-Persona Council | 多人格議會

Instead of one AI voice, simulate a council of perspectives:

不是單一 AI 聲音，而是模擬一個多視角的議會：

| Persona | 人格 | Role |
|---------|------|------|
| **Guardian** | 守護者 | Safety and ethics enforcement |
| **Analyst** | 分析師 | Logical reasoning and fact-checking |
| **Advocate** | 倡導者 | User intent and experience |
| **Critic** | 批評者 | Challenge assumptions, track dissent |

```python
from tonesoul52 import CouncilAdapter

council = CouncilAdapter()
result = council.deliberate(prompt="Should we proceed with this action?")
print(result.dominant_voice)  # "Guardian"
print(result.dissent_ratio)   # 0.25 (25% disagreement)
```

### 3. STREI Metrics | STREI 指標

A 5-dimensional vector measuring AI state:

一個 5 維向量測量 AI 狀態：

| Metric | 指標 | Range | Meaning |
|--------|------|-------|---------|
| **S** - Stability | 穩定性 | 0-1 | Context consistency |
| **T** - Tension | 張力 | 0-1 | Conflict/stress level |
| **R** - Responsibility | 責任 | 0-1 | Traceability score |
| **E** - Ethics | 倫理 | 0-1 | Axiom compliance |
| **I** - Intent | 意圖 | 0-1 | Action confidence |

---

## CLI Tools | 命令行工具

| Command | 命令 | Description | 說明 |
|---------|------|-------------|------|
| `run_healthcheck` | | Full system diagnostic | 完整系統診斷 |
| `run_audit` | | Generate inventory report | 產生盤點報告 |
| `run_reliability_check` | | Verify entrypoints | 驗證入口點 |
| `run_council_healthcheck` | | Check persona coverage | 檢查人格覆蓋率 |
| `persona_registry_summary` | | Persona distribution stats | 人格分佈統計 |
| `generate_patch` | | Auto-generate fix patches | 自動產生修補 |
| `run_ystm_demo` | | Generate YSTM demo outputs | 產生 YSTM demo 輸出 |
| `run_ystm_acceptance` | | Run YSTM acceptance tests | 執行 YSTM 驗收測試 |
| `run_ystm_update` | | Apply YSTM WHAT/WHERE updates | 套用 YSTM WHAT/WHERE 更新 |
| `run_ystm_diff` | | Compute YSTM semantic diff | 計算 YSTM 語義差異 |
| `run_ystm_replay` | | Replay YSTM update record | 回放 YSTM 更新紀錄 |
| `run_ystm_patch_lookup` | | Lookup YSTM patch history | 查詢 YSTM patch_history |
| `run_context_compiler` | | Build YSS M0 context.yaml | 產出 YSS M0 context.yaml |
| `run_frame_router` | | Build YSS M1 frame_plan.json | 產出 YSS M1 frame_plan.json |
| `run_constraint_stack` | | Build YSS M2 constraints.md | 產出 YSS M2 constraints.md |
| `run_generation_orch` | | Build YSS M3 execution_report.md | 產出 YSS M3 execution_report.md |
| `run_evidence_collector` | | Build YSS M4 evidence summary | 產出 YSS M4 evidence summary |
| `run_audit_interface` | | Build YSS M5 audit_request.json | 產出 YSS M5 audit_request.json |
| `run_yss_gates` | | Run YSS gate validators | 執行 YSS gate 驗證器 |
| `run_yss_pipeline` | | Run full YSS pipeline | 執行完整 YSS pipeline |
| `run_memory_compact` | | Compact runs + rebuild memory indexes | 壓縮 run 並重建記憶索引 |
| `run_skill_promoter` | | Promote memory episodes into skills | 將記憶彙總提升為技能 |
| `run_skill_gate` | | Review/approve skill proposals | 審核並批准技能提案 |
| `run_etcl_transition` | | Apply ETCL lifecycle transitions | 套用 ETCL 生命週期狀態變更 |
| `run_seed_schema_check` | | Validate memory seed schema | 驗證記憶 seed 欄位 |
| `run_tech_trace_capture` | | Capture Tech-Trace source note | 捕捉 Tech-Trace 來源筆記 |
| `run_tech_trace_normalize` | | Normalize Tech-Trace capture | 正規化 Tech-Trace 來源 |
| `run_tech_trace_validate` | | Validate Tech-Trace normalize | 驗證 Tech-Trace 正規化 |

## YSTM Demo | YSTM Demo

```bash
python -m tonesoul52.run_ystm_demo
```

Dependencies:
- `numpy` (vector math and grid computation)
- Optional: `cairosvg` (PNG export)

Outputs:
- `5.2/reports/ystm_demo/nodes.json`
- `5.2/reports/ystm_demo/audit_log.json`
- `5.2/reports/ystm_demo/terrain.html`
- `5.2/reports/ystm_demo/terrain.svg`
- `5.2/reports/ystm_demo/terrain.json`
- `5.2/reports/ystm_demo/terrain_p2.html`
- `5.2/reports/ystm_demo/terrain_p2.svg`
- `5.2/reports/ystm_demo/terrain_p2.json`

Notes:
- `terrain.html` is P1 (field x time, governance plane)
- `terrain_p2.html` is P2 (PCA projection, observational only)
- `terrain*.json` includes `node_ids` aligned with `points` and `drift_vectors` (from/to mapping).

Optional PNG export (requires `cairosvg`):

```bash
pip install -e .[ystm_viz]
python -m tonesoul52.run_ystm_demo --export-png
```

Note: PNG export needs a Cairo library (`libcairo-2.dll`) available on PATH; if missing, PNGs are skipped.
If Cairo is missing but Pillow is available, the demo falls back to a basic raster renderer.

Energy weights (E_total = alpha*E_energy + beta*E_srsp + gamma*E_risk):

```bash
python -m tonesoul52.run_ystm_demo --alpha 1.0 --beta 0.2 --gamma 0.3
```

Segment inputs may include optional `E_srsp` and `E_risk` fields for weighted energy.

Acceptance tests:

```bash
python -m tonesoul52.run_ystm_acceptance
```

Apply updates (write back to nodes.json + audit_log.json):

```bash
python -m tonesoul52.run_ystm_update --node-id node_003 --what "Updated text" --rationale "Refine content."
python -m tonesoul52.run_ystm_update --node-id node_002 --where-mode risk --event-index 4 --rationale "Shift context."
python -m tonesoul52.run_ystm_update --node-id node_004 --what "Reweighted text" --alpha 1.0 --beta 0.2 --gamma 0.3
```

Optional: write semantic diff artifact (Tech-Trace alignment):

```bash
python -m tonesoul52.run_ystm_update --node-id node_003 --what "Updated text" --rationale "Refine content." \
  --write-diff --source-grade A --trace-level full
```

Auto-generate Tech-Trace metadata during update (also writes diff):

```bash
python -m tonesoul52.run_ystm_update --node-id node_003 --what "Updated text" --rationale "Refine content." \
  --trace-text "Source note" --trace-source-type paper --trace-grade A
```

Compute semantic diff between node snapshots:

```bash
python -m tonesoul52.run_ystm_diff --before 5.2/reports/ystm_demo/nodes.json --after 5.2/generated/<updated_nodes>.json --rationale "Compare snapshots" --source-grade B --trace-level standard
```

Tech-Trace capture/normalize (minimal ingestion):

```bash
python -m tonesoul52.run_tech_trace_capture --text "Source note" --source-type paper --uri "https://example.com" --grade A
python -m tonesoul52.run_tech_trace_normalize --input 5.2/generated/tech_trace/<capture_id>.json --source-grade A \
  --claims '[{"text":"Claim A","source_ref":"https://example.com"}]' --links '["https://example.com"]'
python -m tonesoul52.run_tech_trace_validate --normalize 5.2/generated/tech_trace/<normalize_id>.json
python -m tonesoul52.run_tech_trace_validate --normalize 5.2/generated/tech_trace/<normalize_id>.json --strict
```

Optional: add `--strict` to require attributions to reference known claim ids when claims are present.
Strict failure example (expect `claim_id_unknown`): `5.2/generated/tech_trace_strict/normalize_strict_fail.json`.

Replay an update (restore before/after snapshot):

```bash
python -m tonesoul52.run_ystm_replay --update-id upd_where_xxxxx --mode before
```

Lookup patch history (diff ids attached to nodes):

```bash
python -m tonesoul52.run_ystm_patch_lookup --nodes 5.2/generated/ystm_trace_patch/nodes.json --node-id node_003
```

YSS M0 (context compiler):

```bash
python -m tonesoul52.run_context_compiler --task "Build YSTM demo" --objective "Generate auditable artifacts"
```

YSS M1 (frame router):

```bash
python -m tonesoul52.run_frame_router --context 5.2/run/execution/<run_id>/context.yaml
```

Frame plans include governance role alignment from `5.2/spec/governance/role_catalog.yaml`.
Optional: override with `--role-catalog <path>`.
Frame plans also include `council_summary` (role-weighted decision summary).

YSS M2 (constraint stack):

```bash
python -m tonesoul52.run_constraint_stack --context 5.2/run/execution/<run_id>/context.yaml --frame-plan 5.2/run/execution/<run_id>/frame_plan.json
```

Constraint stacks include an Action Set section and Mercy Objective snapshot derived from decision mode.

YSS M3 (execution report):

```bash
python -m tonesoul52.run_generation_orch --context 5.2/run/execution/<run_id>/context.yaml --frame-plan 5.2/run/execution/<run_id>/frame_plan.json --constraints 5.2/run/execution/<run_id>/constraints.md --skills-applied 5.2/run/execution/<run_id>/skills_applied.json
```

YSS M4 (evidence summary):

```bash
python -m tonesoul52.run_evidence_collector --context 5.2/run/execution/<run_id>/context.yaml --execution-report 5.2/run/execution/<run_id>/execution_report.md
```

Optional: include `--ystm-*(nodes/audit/terrain/terrain-json/terrain-svg/terrain-p2/terrain-p2-json/terrain-p2-svg/terrain-png)` and `--skills-applied` to capture artifact paths.
Optional: include `--ystm-diff` to capture semantic diff artifacts.
Optional: include `--tech-trace-capture` and `--tech-trace-normalize` to link trace ingestion artifacts.
When tech-trace normalize is provided, evidence summary adds `tech_trace_summary` and claim/link counts.
Optional: include `--council-summary` to attach the council decision summary.
Optional: include `--action-set` to attach the action set snapshot.
Optional: include `--mercy-objective` to attach the mercy objective snapshot.
Optional: include `--tsr-metrics` to attach Delta T/S/R metrics.
Optional: include `--dcs-result` to attach the DCS closure record.
Optional: include `--error-ledger` to attach the error ledger when present.

YSS M5 (audit interface):

```bash
python -m tonesoul52.run_audit_interface --context 5.2/run/execution/<run_id>/context.yaml --frame-plan 5.2/run/execution/<run_id>/frame_plan.json --constraints 5.2/run/execution/<run_id>/constraints.md --execution-report 5.2/run/execution/<run_id>/execution_report.md --evidence-summary 5.2/evidence/summary.md --gate-report 5.2/run/execution/<run_id>/gate_report.json --error-ledger 5.2/run/execution/<run_id>/error_ledger.jsonl --action-set 5.2/run/execution/<run_id>/action_set.json --mercy-objective 5.2/run/execution/<run_id>/mercy_objective.json --council-summary 5.2/run/execution/<run_id>/council_summary.json --ystm-nodes 5.2/reports/ystm_demo/nodes.json --ystm-audit 5.2/reports/ystm_demo/audit_log.json --skills-applied 5.2/run/execution/<run_id>/skills_applied.json --reflection 5.2/run/execution/<run_id>/reflection.json --poav-result 5.2/run/execution/<run_id>/gate_report.json --escalation-result 5.2/run/execution/<run_id>/gate_report.json --mercy-result 5.2/run/execution/<run_id>/gate_report.json
```

Optional: add `--ystm-terrain*` paths (html/json/svg/png) to link visual artifacts into the audit request.
Optional: add `--ystm-diff` to attach semantic_diff.json to the audit request.
Optional: add `--tech-trace-capture` and `--tech-trace-normalize` to attach trace ingestion artifacts.
When tech-trace normalize is provided, audit_request includes `tech_trace_digest`.
Optional: add `--tsr-metrics` to attach Delta T/S/R metrics.
Optional: add `--dcs-result` to attach the DCS closure record.
Optional: add `--gate-report` to attach the full gate_report.json path.

YSS Gate validators:

```bash
python -m tonesoul52.run_yss_gates --run-dir 5.2/run/execution/<run_id>
```

Gates include role alignment checks (role catalog + summary + mappings).
P0 non-harm gate is always enforced; it checks the Safety section for a P0/non-harm marker.
Guardian gate checks for guardian-level governance roles; record-only unless enforced.

Optional: add `--require-evidence` and `--ystm-*`/`--skills-applied` to align with pipeline evidence requirements.
Optional: add `--ystm-diff` when you want the diff artifact listed in evidence checks.
Optional: add `--tech-trace-capture` and `--tech-trace-normalize` when trace artifacts should be listed in evidence checks.
When `--run-dir` is used, gate runner reads `audit_request.json` inputs to auto-fill `--ystm-diff` and tech-trace paths.
Optional: add `--require-tech-trace` to fail when normalized tech-trace is missing or invalid.
Optional: add `--tech-trace-strict` to require claim_id mapping for tech-trace normalize.
Optional: `--poav-threshold 0.7` and `--enforce-poav` to control POAV gate behavior.
Optional: `--enforce-guardian` to fail when guardian roles are missing.
Optional: `--council-summary` to require the council summary artifact.
Optional: `--drift-threshold 4.0` and `--error-ledger <path>` to control escalation decisions.
Optional: `--action-set` to require the action set artifact.
Optional: `--mercy-objective` to require the mercy objective artifact.
Optional: `--mercy-weights` and `--mercy-signals` to override the mercy objective inputs (JSON string or file path).
Optional: `--mercy-threshold` and `--enforce-mercy` to gate on low mercy scores.
Optional: `--mercy-result` to attach the mercy gate result to audit requests.
Optional: `--seed` and `--require-seed` to validate memory seed schema.
DCS policy defaults: `5.2/spec/governance/dcs_policy.yaml`.
TSR scoring defaults: `5.2/spec/metrics/tsr_policy.yaml`.

YSS pipeline (M0-M5 + gates):

```bash
python -m tonesoul52.run_yss_pipeline --task "Build YSTM demo" --objective "Generate auditable artifacts"
```

POAV gate runs in record-only mode by default; set `--enforce-poav` and/or `--poav-threshold` to block on low POAV.
Guardian gate runs in record-only mode by default; set `--enforce-guardian` to require guardian roles.
Council summaries are stored at `5.2/run/execution/<run_id>/council_summary.json` and referenced in evidence summaries.
Escalation gate decisions (quarantine/jump) are recorded in `error_ledger.jsonl` when triggered.
Action sets are stored at `5.2/run/execution/<run_id>/action_set.json` and referenced in evidence summaries.
Mercy objectives are stored at `5.2/run/execution/<run_id>/mercy_objective.json` and referenced in evidence summaries.
TSR metrics are stored at `5.2/run/execution/<run_id>/tsr_metrics.json` (heuristic Delta T/S/R).
DCS closure records are stored at `5.2/run/execution/<run_id>/dcs_result.json` (record-only).
Seed schema checks can be enforced after recording with `--require-seed`.
Tech-trace normalize checks can be enforced with `--require-tech-trace` (when normalize path is provided).
Optional: add `--tech-trace-strict` to enforce claim_id mapping when claims/attributions are present.
Optional: attach a semantic diff artifact with `--ystm-diff <path>`.
Optional: attach trace ingestion artifacts with `--tech-trace-capture <path>` and `--tech-trace-normalize <path>`.
Optional: use `--tech-trace-auto` to generate capture/normalize from the execution report when paths are not provided.
Optional: tune auto-claim extraction with `--tech-trace-claim-limit` and `--tech-trace-claim-min-chars`.
Trace level defaults to `standard` (no memory/skill promotion). Use `--trace-level full` to enable full trace retention.
See `5.2/reports/trace_levels.md` for the Level 2/Level 3 breakdown and usage guidance.

Optional PNG export (requires `cairosvg`):

```bash
python -m tonesoul52.run_yss_pipeline --ystm-export-png --ystm-png-scale 2.0
```

Run outputs include `skills_applied.json` when approved skills match the context.
For `apply_governance_baseline`, the pipeline enforces gate checks even if `--skip-gates` is set.
The P0 non-harm gate always runs, even when `--skip-gates` is set.
Skill constraints are appended to `constraints.md` when a matching skill is applied.
Gate issues are summarized in `reflection.json` when present.
If a skill includes `gravity_wells`, action wells can supply directives such as `force_gates`.
Trigger keywords are used as an additional filter when gravity wells are present.
When `skill_matching.allow_trigger_only` is true, a skill may apply without `policy_template.when` if trigger keywords match and meet `min_trigger_strength`.

Optional: record an ErrorEvent during M3:

```bash
python -m tonesoul52.run_yss_pipeline --error-event 5.2/spec/errors/error_event_template.json
```

Memory recording is enabled when `--trace-level full` is selected (YSS pipeline writes seeds and graph indexes). Override if needed:

```bash
python -m tonesoul52.run_yss_pipeline --skip-memory
```

Full trace: compact run history and rebuild memory indexes:

```bash
python -m tonesoul52.run_memory_compact --keep-latest 3
```

Memory outputs (full trace):
- `5.2/memory/seeds/<run_id>.json`
- `5.2/memory/graph_index.json`
- `5.2/memory/run_index.json`
- Seeds include `tech_trace_snapshot` when trace artifacts are attached.

Note: `run_memory_compact` moves older runs to `archive/runs` unless `--reindex-only`.

Retention policy:
- Run archiving uses `compaction.max_active_runs` + `compaction.keep_latest` in `5.2/spec/memory/memory_policy.yaml`.
- Evidence summary rollover uses `retention.evidence` (max_entries/keep_latest/archive_dir).
- The YSS pipeline applies retention automatically when enabled in the policy.

Skill promotion policy: `5.2/spec/memory/memory_policy.yaml`

```bash
python -m tonesoul52.run_skill_promoter
```

Skill outputs:
- `5.2/memory/episodes/<episode_id>.json`
- `5.2/memory/skills/<skill_id>.json`
- `5.2/memory/episode_index.json`
- `5.2/memory/skill_index.json`

The YSS pipeline enables memory recording and skill promotion when `--trace-level full` is selected.
Disable with `--skip-memory` or `--skip-skill-promote`, or override policy with `--skill-policy`.
Auto skill review runs if `review.auto_approve` is enabled; disable with `--skip-skill-review`.
Auto compaction runs when active runs exceed the policy threshold.
Disable with `--skip-auto-compact` or override with `--compact-max-runs` / `--compact-keep-latest`.

Review a proposed skill:

```bash
python -m tonesoul52.run_skill_gate --memory-root 5.2/memory --skill-id skill_dc79679acfb9 --approve --reviewer "auditor" --reviewer-role "guardian"
```

Reviewer roles and levels are defined in `5.2/spec/governance/role_catalog.yaml`.

ETCL lifecycle transition (seed state machine):

```bash
python -m tonesoul52.run_etcl_transition --run-id <run_id> --event deposit --reason "Ready to archive seed."
```

---

## Use Cases | 使用場景

### Production LLM Applications | 生產環境 LLM 應用

- **Compliance**: Auditors can trace every decision
- **Debugging**: Reproduce exact AI state at any point
- **Trust**: Show stakeholders quantified safety metrics

### AI Research | AI 研究

- **Alignment**: Test multi-persona consensus mechanisms
- **Interpretability**: STREI provides human-readable state
- **Reproducibility**: Ledger enables experiment replay

### Enterprise AI Governance | 企業 AI 治理

- **Risk Management**: Track tension and ethics metrics over time
- **Escalation**: Auto-flag high-tension or low-ethics scenarios
- **Audit Trail**: SOC2/ISO compliant decision logging

---

## Philosophy | 哲學基礎

ToneSoul is built on **MGGI** (Manageable Governable General Intelligence):

語魂建立在 **MGGI**（可管理可治理通用智能）之上：

> "An AI that cannot explain its decisions cannot be trusted.  
> An AI that cannot be audited should not be deployed."
>
> 「無法解釋決策的 AI 不值得信任。  
> 無法被審計的 AI 不應該被部署。」

Core principles:
- **P0**: Non-harm (hard gate, never bypassed)
- **P1**: Context consistency (maintain coherent state)
- **P2**: Cognitive honesty (acknowledge uncertainty)

---

## Project Structure | 專案結構

```
tonesoul52/
├── audit_dashboard.py      # Visual audit interface | 視覺化審計介面
├── council_adapter.py      # Multi-persona deliberation | 多人格審議
├── persona_registry_*.py   # Persona management | 人格管理
├── run_*.py                # CLI entrypoints | CLI 入口點
└── config.py               # Configuration | 設定

reports/
├── healthcheck.json        # System health report | 系統健康報告
├── philosophy_to_engineering.md  # Philosophy mapping | 哲學對應
├── nextgen_design.md       # Future roadmap | 未來路線圖
└── *.diff                  # Auto-generated patches | 自動產生的修補
```

---

## Contributing | 貢獻

We welcome contributions that align with MGGI principles:

我們歡迎符合 MGGI 原則的貢獻：

1. **Auditable**: All changes must be traceable
2. **Safe**: P0 (non-harm) is never compromised
3. **Documented**: Update relevant reports

---

## License | 授權

MIT License - See [LICENSE](LICENSE) for details.

---

## Credits | 致謝

- **Creator**: 黃梵威 (ToneSoul Philosophy)
- **Engineering**: Codex (35-hour integration session)
- Easter egg: AI語魂系統 × 黃梵威 共同製作
- **Refinement**: Antigravity

---

<p align="center">
  <b>Make AI Trustworthy. Make AI Auditable. Make AI Governable.</b><br>
  <b>讓 AI 可信任。讓 AI 可審計。讓 AI 可治理。</b>
</p>
