# Trace Levels: Standard (L2) and Full (L3)

Purpose:
- Define trace retention tiers for the YSS pipeline.
- Balance auditability with storage and compute cost.

---

## Level 2 (Standard) - Default

Use when:
- You want a minimal demo run or fast iteration.
- Storage is limited or you prefer to avoid long-term retention.

What is kept:
- Run artifacts in `5.2/run/execution/<run_id>/`:
  - `context.yaml`, `frame_plan.json`, `constraints.md`
  - `execution_report.md`, `gate_report.json`, `reflection.json` (if any)
  - `audit_request.json`, `error_ledger.jsonl` (if any)
- Evidence summary in `5.2/evidence/summary.md`
- YSTM outputs in `5.2/reports/ystm_demo/`

What is skipped:
- Memory seeds and graph/run indexes
- Skill promotion and auto review
- Auto compaction and archive indexing

Notes:
- `--require-seed` requires memory recording (Level 3) or a manually provided seed path.
- Healthcheck seed schema validation will skip when no seeds exist.

---

## Level 3 (Full) - Full Trace Architecture

Enable with:
- `--trace-level full`

Adds the full memory + skill lifecycle:
1) **Record memory**:
   - `record_run()` writes `memory/seeds/<run_id>.json`
   - Updates `memory/graph_index.json` and `memory/run_index.json`
   - Seeds include `tech_trace_snapshot` when trace artifacts are attached
2) **Promote skills**:
   - Generates `memory/episodes/` and `memory/skills/` artifacts
   - Updates `memory/episode_index.json` and `memory/skill_index.json`
3) **Review skills** (optional):
   - Auto-review when policy `review.auto_approve` is enabled
4) **Compaction + retention** (optional):
   - Archives old runs to `archive/runs`
   - Rebuilds indexes after archiving

All Level 2 artifacts are still produced.

---

## Choosing a Level

- **Standard (L2)**: fast demos, constrained machines, or privacy-sensitive runs.
- **Full (L3)**: long-lived systems, cross-run auditability, skill evolution, and retention policy enforcement.

---

## Performance and Growth Controls (Full)

- `5.2/spec/memory/memory_policy.yaml`:
  - `compaction.max_active_runs`, `compaction.keep_latest`
  - `retention.evidence` rollover policy
- CLI overrides:
  - `--skip-memory`, `--skip-skill-promote`, `--skip-skill-review`, `--skip-auto-compact`

---

## CLI Examples

Standard (default):

```bash
python -m tonesoul52.run_yss_pipeline --task "Build YSTM demo" --objective "Generate auditable artifacts"
```

Full trace:

```bash
python -m tonesoul52.run_yss_pipeline --trace-level full --task "Build YSTM demo" --objective "Generate auditable artifacts"
```
