# REPO Consolidation Audit

Date: 2026-02-08
Scope: `README/docs` consistency audit + `Python architecture/boundary` audit

## Collaboration Message (Approved and Executed)

To Codex and collaborators:

- Proposed division accepted:
- Codex audited documentation and `README`.
- Codex audited Python code and architecture boundaries.
- Findings are consolidated in this single report.
- Chain-owner philosophy acknowledged:
- "把結晶當手腳，不要活在結晶裡面。"

## Executive Summary

- The repository has strong implementation momentum (`214` Python files, `55` test files), but governance metadata is currently drifting (`116` docs files and multiple status mirrors).
- Current local `7D` run is not fully green:
- `DDD` and `DDD_HYGIENE` are blocking-fail because `memory/agent_discussion.jsonl` contains `3` malformed lines (`133-135`, includes NUL/UTF-16 artifacts).
- Boundary check is mostly healthy:
- No direct `tonesoul/tools/memory -> apps` forbidden imports were found by static grep.
- Main risks are now consistency and process-level coupling, not missing core architecture.

## Findings (Engineering Angle)

1. DDD gate is currently broken by malformed discussion memory entries.
- Evidence: `tools/agent_discussion_tool.py audit` reports `invalid_entries=3`, line `133-135` with NUL bytes.
- Runtime impact: `scripts/verify_7d.py` blocks on DDD and `DDD_HYGIENE`.

2. RDD threshold is inconsistent across local gate, CI gate, and docs.
- `scripts/verify_7d.py:21` sets `RDD_MIN_CASES = 10`.
- `.github/workflows/test.yml:105` enforces `threshold = 20`.
- Docs still state minimum 10:
- `docs/7D_AUDIT_FRAMEWORK.md:89`
- `docs/7D_EXECUTION_SPEC.md:20`
- Risk: local pass may still produce CI confusion.

3. `verify_7d` can mutate canonical docs and create narrative drift.
- `scripts/verify_7d.py:359` has `_sync_to_markdown`.
- It directly rewrites `README.md` and `memory/ANTIGRAVITY_SYNC.md` (`scripts/verify_7d.py:362`, `scripts/verify_7d.py:363`).
- Risk: environment-dependent scores (for example `SDH` skip) can overwrite human-readable repository narrative.

4. Layer boundary is mostly respected, but there is coupling pressure in memory domain.
- Positive: no detected `from apps ...` imports inside `tonesoul/tools/memory`.
- Coupling signal: `memory/observer.py:6` imports `tonesoul.memory.soul_db`.
- Risk: infrastructure-level module depends on governance package internals; long-term migration cost increases.

5. Deprecated UTC construction still appears in multiple modules.
- Examples:
- `tonesoul/memory/soul_db.py:46`
- `tonesoul/append_council_event.py:15`
- `tonesoul/council_adapter.py:14`
- `tools/summary_ball_converter.py:189`
- Risk: future Python deprecation churn and inconsistent timestamp semantics.

## Reflection (Philosophy Angle)

- The project already carries explicit responsibility ethics, but "truth" currently has too many mirrored containers (`README`, `SYNC`, multiple docs, live scripts).
- "結晶" should be treated as externalized tools, not as the living system itself:
- Crystal = report, score, snapshot.
- Living system = executable checks, bounded interfaces, recoverable memory.
- When mirrored artifacts disagree, philosophy loses operational force because users cannot tell which truth is canonical.

## Reflection (Reality Angle)

- Multi-agent collaboration is working, but concurrent edits plus mixed encoding paths can poison the memory channel.
- CI had to allow missing discussion file (`--allow-missing-discussion`) because discussion memory is gitignored; this is a practical compromise, but weakens reproducibility.
- Repository scale is now large enough that "status by prose" is no longer safe without source-of-truth discipline.

## Reflection (AI Angle)

- Existing orchestration (`tools/orchestrator.py`) gives strong scaffolding for switch/handoff and first-failure escalation.
- But destructive-intent detection is keyword-based (`tools/orchestrator.py` risk token list), so semantic variants can bypass literal matching.
- For honest/responsible AI behavior, correctness must come from structured intent classification plus auditable enforcement, not only keyword triggers.

## Over-Crystallization Risk Warnings

1. Status crystal drift:
- Static docs can lag behind executable reality (`299 passed` vs current test collection scale).

2. Auto-sync crystal overreach:
- A verification script writing canonical docs mixes "measurement" and "storytelling".

3. Memory crystal contamination:
- Discussion stream stores both dialogue and operational signals; encoding faults can directly block governance gates.

4. Boundary crystal ambiguity:
- Layer diagrams are clear, but module ownership lines around memory/governance remain semantically blurred.

## Concrete Repo Consolidation Plan

### P0 (Do Now)

1. Repair discussion memory integrity.
- Run normalization on `memory/agent_discussion.jsonl` with backup.
- Enforce NUL-byte rejection in append path.

2. Unify RDD threshold to one value (`20`) across:
- `scripts/verify_7d.py`
- `docs/7D_AUDIT_FRAMEWORK.md`
- `docs/7D_EXECUTION_SPEC.md`

3. Restrict doc auto-sync.
- Keep `--sync` for explicit manual use only.
- Do not trigger it from automated flows.

4. Standardize timestamp utility.
- Replace `datetime.utcnow()` call sites with timezone-aware helper.

### P1 (Next Iteration)

1. Split discussion memory streams:
- `agent_discussion_raw.jsonl` (immutable)
- `agent_discussion_curated.jsonl` (gate-consumed)

2. Add boundary test in CI.
- Static import contract check: deny forbidden layer edges.

3. Separate "runtime score" from "human README narrative".
- Save machine status to a dedicated artifact file (for example `docs/status/7d_snapshot.json`).

### P2 (Stability Work)

1. Archive stale/overlapping docs into `docs/archive/` with index.
2. Add monthly consolidation ritual:
- prune deprecated paths
- verify source-of-truth tables
- refresh architecture map from code.

## Closing Verdict

- Continue incremental optimization, not full rewrite.
- Core architecture is viable.
- The dominant risk is now consistency governance (memory integrity, threshold drift, and narrative-source separation), not missing fundamental capability.
