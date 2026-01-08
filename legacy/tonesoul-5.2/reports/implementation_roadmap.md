# Implementation Roadmap (Spec-only -> Minimal Runnable)

Scope:
- Workspace: `5.2/` only (no legacy changes).
- Goal: convert spec-only / partial items into minimal, auditable features.

---

## Current Baseline (already implemented)

- YSTM demo + audit artifacts: `5.2/tonesoul52/ystm/*`, `5.2/reports/ystm_demo/*`
- YSS pipeline + gates: `5.2/tonesoul52/yss_pipeline.py`, `5.2/tonesoul52/yss_gates.py`
- Evidence + audit chain: `5.2/tonesoul52/evidence_collector.py`, `5.2/tonesoul52/audit_interface.py`
- Role alignment: `5.2/spec/governance/role_catalog.yaml` + frame routing output
- Trace levels (L2/L3): `--trace-level full` enables memory/skills/compaction (see `5.2/reports/trace_levels.md`)

---

## Phase 1: ETCL Lifecycle (T0-T6) - Minimal State Machine

Goal:
- Make memory lifecycle explicit and auditable.

Deliverables:
- `tonesoul52/etcl_lifecycle.py` with `transition(seed, event)` -> next state.
- CLI: `run_etcl_transition` for T0-T6 transitions.
- Seed schema extension: include `sigma_stamp`, `state_history[]`, `transition_reason`.

Acceptance:
- Transition rules encoded for T0..T6 with deterministic state changes.
- If a seed exists, output written to `5.2/memory/seeds/<run_id>.json` with `state_history` entry.
- Note: CLI does not create a new seed; provide `--seed-path` or precreate `memory/seeds/<run_id>.json`.

Status:
- Implemented (minimal state machine + CLI).

---

## Phase 2: POAV Gate (Minimal Metric)

Goal:
- Introduce a real POAV score to replace placeholder gates.

Deliverables:
- `tonesoul52/poav.py` with `score(text)` -> {p,o,a,v,total}.
- Gate: `poav_gate` in `yss_gates.py` (optional but recorded).
- Add POAV to `execution_report.md` and `audit_request.json`.

Acceptance:
- `run_yss_gates` includes POAV when enabled.
- Report shows POAV score + threshold decision.

Status:
- Implemented (minimal POAV heuristics + gate + report/audit integration).

---

## Phase 3: Multi-Point Governance (Lightweight Council)

Goal:
- Move from role alignment to role-weighted decisions.

Deliverables:
- `tonesoul52/role_council.py` to aggregate role signals.
- Frame plan includes council decision summary.
- Evidence summary references council result.

Acceptance:
- Council outputs are logged and traceable in `execution_report.md`.

Status:
- Implemented (role-weighted council summary + artifact + report integration).

---

## Phase 4: Quarantine + JUMP (Safety Escalation)

Goal:
- Provide explicit isolation and escalation paths.

Deliverables:
- `tonesoul52/escalation.py` with `quarantine()` + `jump()` events.
- Gate integration: triggers when drift or POAV crosses thresholds.
- Record events in `error_ledger.jsonl`.

Acceptance:
- Gate reports include quarantine/jump decisions with reasons.

Status:
- Implemented (escalation module + gate integration + error ledger recording).

---

## Phase 5: Minimal Action Set (Verify/Cite/Inquire)

Goal:
- Constrain actions under safety/uncertainty modes.

Deliverables:
- `tonesoul52/action_set.py` enumerating allowed actions.
- `constraints.md` appends allowed actions under strict modes.

Acceptance:
- Evidence summary includes declared action set for each run.

Status:
- Implemented (action_set module + constraints section + evidence/audit wiring).

---

## Optional: Mercy-based Objective (Spec-only -> Prototype)

Goal:
- Provide a simple value-weighted objective function.

Deliverables:
- `tonesoul52/mercy_objective.py` with weights + rationale.
- Log weights in `audit_log.json`.

Acceptance:
- Objective config recorded in `mercy_objective.json` and referenced in audit requests.

Status:
- Implemented (mercy objective snapshot + constraints/evidence/audit wiring).
- Added optional mercy threshold gate (record-only by default).

---

## Definition of Done (for each phase)

- Runnable CLI path exists.
- Outputs are logged in `execution_report.md` + `audit_request.json` (ETCL-only runs output seed/state_history unless wrapped).
- Gate report captures pass/fail for the new component.

---

## Queued: Multi-Perspective Repository Audit Follow-ups (2025-12-27)

Source: `5.2/reports/multi_perspective_audit_2025_12_27.md`

Priority items:
- P1: Add an explicit `p0_gate` (non-bypass safety gate). (implemented)
- P2: Refactor `run_yss_pipeline` into smaller functions and add return types. (implemented)
- P3: Add `docs/quickstart.md` with a minimal end-to-end walkthrough. (implemented)
- P4: Add tests for POAV empty input, escalation missing POAV, tech-trace invalid JSON, and memory_manager concurrent writes. (implemented)

Status: P1-P4 complete.

---

## Backlog: Open Items (from reports)

- Strategic positioning: define a business model placeholder (open-source + enterprise).  
  Source: `5.2/reports/strategic_positioning_audit.md`

---

## Completed from Backlog (2025-12-27)

- Guardian integration: integrated guardian gate into `yss_gates`, pipeline, and CLI (record-only by default).  
  Source: `5.2/reports/multi_perspective_audit_2025_12_27.md`
- UpdateGate.score usage: implemented score calculation in `governance.UpdateGate`.  
  Source: `5.2/reports/codex_audit_antigravity.md`
- Gate issue codes: added IssueCode enum and replaced gate issue strings with centralized codes.  
  Source: `5.2/reports/multi_perspective_audit_2025_12_27.md`
- Tech-Trace auto-ingest/auto-attach: pipeline auto-generates capture/normalize with `--tech-trace-auto`.  
  Source: `5.2/reports/tech_trace_alignment.md`
- Tech-Trace claim extraction: normalize supports auto-claim extraction when explicit claims are omitted.  
  Source: `5.2/reports/tech_trace_alignment.md`
- Dashboard dissent/weights: add dissent hotspots + role weight distribution views.  
  Source: `5.2/reports/philosophy_to_engineering.md`
- Healthcheck coverage alert: add coverage < 1 warning summary.  
  Source: `5.2/reports/philosophy_to_engineering.md`
- Whitepaper spec-only items: implement Delta T/S/R metrics, DCS (Dynamic Closure System), and deepen LTM provenance beyond partial.  
  Source: `5.2/reports/whitepaper_spine_alignment.md`
