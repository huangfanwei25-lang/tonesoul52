# Cross-Repo Field Mapping: ToneSoul52 <-> OpenClaw-Memory

Date: **2026-02-28**  
Scope: align memory-governance fields between `tonesoul52` runtime contract and `OpenClaw-Memory` CLI/runtime metadata.

## Goal

Freeze a shared vocabulary so both repos can exchange "tension / wave / friction / route" signals without ad-hoc key drift.

## Canonical Contract (ToneSoul side)

Reference: `spec/governance/memory_governance_contract_v1.schema.json`

- `prior_tension`
- `governance_friction`
- `routing_trace`

## Field Mapping Table

| Canonical concept | `tonesoul52` source field | `OpenClaw-Memory` source field | Migration / adapter note |
| --- | --- | --- | --- |
| memory tension | `prior_tension.memory_tension` | metadata `tension` | Keep numeric `[0,1]`; missing -> `null`. |
| query tension | `prior_tension.query_tension` | CLI `--query-tension` | For baseline profile (`openclaw`), this can be omitted. |
| tension delta | `prior_tension.delta_t` | computed `abs(query_tension - memory_tension)` | If only `delta_t` exists, ToneSoul fallback uses `query_tension=delta_t`, `memory_tension=0.0`. |
| memory wave | `prior_tension.memory_wave` | metadata `wave` (`uncertainty_shift/divergence_shift/risk_shift/revision_shift`) | Preserve wave keys exactly; reject unknown keys. |
| query wave | `prior_tension.query_wave` | CLI `--query-wave-*` | Compare only shared dimensions to keep backward compatibility. |
| wave delta | `governance_friction.components.delta_wave` | `ask_my_brain._compute_friction_summary().wave_distance` | Same semantic: mean absolute distance over shared wave dimensions. |
| boundary mismatch | `governance_friction.components.boundary_mismatch` | derived flag (policy conflict + override pressure) | OpenClaw currently has no council verdict route; adapter may set `false` by default. |
| friction score | `governance_friction.score` | `ask_my_brain._compute_friction_summary().friction` | ToneSoul formula includes mismatch term: `0.45*delta_t + 0.35*delta_wave + 0.20*mismatch`. |
| route | `routing_trace.route` | adapter-derived route | OpenClaw local CLI default maps to `route_local_llm` (no council lane). |
| journal eligibility | `routing_trace.journal_eligible` | adapter-derived boolean | OpenClaw default `false`; ToneSoul keeps tier-based policy (`premium/admin`). |
| route reason | `routing_trace.reason` | friction/rerank explanation text | Keep short, auditable reason string for replay logs. |

## Legacy Alias Normalization

Normalize old keys into canonical fields before writing contract output:

- `adjusted_tension`, `tension_score` -> `prior_tension.delta_t`
- `friction` (flat) -> `governance_friction.score`
- `wave_distance` -> `governance_friction.components.delta_wave`
- `decision`, `gate` -> `prior_tension.gate_decision`

Readers may accept aliases, but writers must emit canonical `v1` fields only.

## Adapter Rules (Minimal)

1. Parse OpenClaw query/memory metadata into `prior_tension`.
2. Compute friction using contract formula (including mismatch term when available).
3. Emit canonical `routing_trace` with approved route enum:
   - `route_local_llm`
   - `route_single_cloud`
   - `route_full_council`
   - `block_rate_limit`

## Operational Notes from Current OpenClaw CLI

- Model download hang risk is reduced because `ask_my_brain.py` defaults to deterministic `HashEmbedding` (offline, no first-run model pull).
- Ingestion testing can run with dummy/offline embedding path (`--learn` works without HuggingFace downloads).
- Unbuffered execution (`python -u ask_my_brain.py ...`) is still useful for diagnosing long-running IO paths, but not required for baseline usage.

## Acceptance Gate for Phase 118

- Contract validation passes (`scripts/run_memory_governance_contract_check.py --strict`).
- This mapping document exists and is referenced by implementation work touching tension/friction fields.
- New cross-repo fields must map to canonical names above (no new ad-hoc top-level keys).
