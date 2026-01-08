# Tech-Trace Alignment Map (L2/L3)

Purpose:
- Align `spec/tech_trace_integration.md` with current 5.2 modules.
- Show where trace levels (L2/L3) affect retention behavior.

---

## Stage Mapping

| Stage | Spec | 5.2 Location | Outputs | Status | Trace Level Impact |
|---|---|---|---|---|---|
| capture | Tech-Trace Ingestion | `tonesoul52/tech_trace/capture.py` | raw notes, sources | implemented (minimal) | L2/L3 both allowed |
| normalize | Tech-Trace Ingestion | `tonesoul52/tech_trace/normalize.py` | normalized notes | implemented (minimal) | L2/L3 both allowed |
| evidence_tagging | Tech-Trace Ingestion | `tonesoul52/tech_trace/normalize.py` | A/B/C grade | implemented (minimal) | L2/L3 both allowed |
| semantic_diff | Tech-Trace Diff | `tonesoul52/ystm/diff.py` | `SemanticDiff` | implemented (via update flow) | L2: run artifacts only; L3: write into memory layer |
| patch_apply | YSTM update | `tonesoul52/run_ystm_update.py` + `tonesoul52/ystm/governance.py` | UpdateRecord + audit_log + optional diff | implemented | L2: audit_log only; L3: also seed/memory linkage |

---

## Current Integration Points

- Diff schema: `SemanticDiff` includes `source_grade` and `trace_level`.
- UpdateRecord: `ystm/governance.py` produces vetoable updates + ErrorEvent on failure.
- `run_ystm_update --write-diff` writes a `SemanticDiff` artifact alongside the update.
- `run_ystm_update --trace-*` writes Tech-Trace capture/normalize artifacts and auto-emits a diff (source_patch_id = normalize_id).
- `normalize.py` supports `claims`, `links`, and `attributions` payloads for structured trace evidence.
- `run_ystm_update` appends `patch_history` (diff_id) to updated nodes when a semantic diff is emitted.
- `run_ystm_patch_lookup` provides a quick query for patch_history by node or diff id.
- `run_tech_trace_validate` validates claims/links/attributions structure in normalized payloads.
- `run_tech_trace_validate --strict` requires attributions to reference known claim ids when claims exist.
- `run_yss_pipeline --ystm-diff <path>` attaches diff artifacts into evidence/audit outputs.
- `run_yss_pipeline --tech-trace-capture/--tech-trace-normalize` attaches trace ingestion artifacts into evidence/audit outputs.
- `run_yss_gates --run-dir <run_id>` pulls `ystm_diff`/tech-trace inputs from audit_request when flags are omitted.
- L3 memory seeds/graph capture tech_trace artifacts via audit_request inputs.
- Evidence summary adds tech-trace digest lines when normalize artifacts are present.
- Audit request adds `tech_trace_digest` (summary + counts).
- `tech_trace_gate` validates normalized payloads; `--require-tech-trace` enforces failure on missing/invalid data.
- `tech_trace_gate` supports strict validation with `--tech-trace-strict`.
- Evidence chain: `run_yss_pipeline` writes `execution_report.md`, `gate_report.json`, `audit_request.json`.
- Seed gate: `--require-seed` only satisfies when L3 writes memory seeds or when a seed is provided.

---

## Gaps (Planned)

- Capture/normalize remain minimal; pipeline now supports auto-ingest with `--tech-trace-auto`.
- Normalize supports auto-claim extraction (heuristic) when explicit claims are not provided.
- Diff/patch artifacts are optional and only attached when explicitly provided.
- Memory indexing is automated when trace artifacts are attached; auto-discovery is still a gap.

---

## Suggested Next Steps

1) Auto-discover trace artifacts when running gates from a run directory (optional).
2) Extend capture/normalize with structured claim extraction.
3) Add patch history links on nodes when applying updates.
