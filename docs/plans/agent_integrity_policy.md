# Agent Integrity Policy — 代理完整性政策

> Purpose: consolidate addenda around agent-integrity governance, trusted-hash ownership, and integrity-check source-of-truth rules.
> Last Updated: 2026-03-23

> 合併日期：2026-03-19
> 原始 addendum 數：3
> 時間跨度：2026-03-15 ~ 2026-03-15
> 合併者：痕 (Hén)

保護檔案 SHA-256 契約源頭統一、治理表面發佈、repo intelligence 整合。

---

## 目錄

1. `agent_integrity_single_source_addendum_2026-03-15.md`
2. `agent_integrity_governance_surface_addendum_2026-03-15.md`
3. `agent_integrity_repo_intelligence_addendum_2026-03-15.md`

---

## 1. 原始檔案：`agent_integrity_single_source_addendum_2026-03-15.md`

## Agent Integrity Single-Source Addendum (2026-03-15)

### Why
- The recent `Agent Integrity Check` CI failure was a contract drift, not a product-code regression.
- The workflow and `scripts/check_agent_integrity.py` each hard-coded trusted hashes, so they drifted independently.
- This class of failure should be prevented structurally, not by asking future agents to remember more carefully.

### Boundary
- Do not modify `AGENTS.md` itself in this phase.
- Keep the move limited to:
  - a shared integrity-contract module
  - workflow consumption of that shared checker
  - focused anti-drift tests
- Treat any stale in-document `Expected Hash` table inside `AGENTS.md` as human-facing metadata drift, not as the executable source of truth.

### Contract
- `scripts/agent_integrity_contract.py` becomes the single executable source of truth for protected-file hashes and normalized hash computation.
- `scripts/check_agent_integrity.py` must import from that module instead of duplicating hashes.
- `.github/workflows/agent-integrity-check.yml` must invoke the checker instead of embedding per-file trusted hashes.
- In-document hash metadata drift may be surfaced as a warning, but must not silently redefine the executable contract.

### Success Criteria
- There is exactly one executable hash declaration for `AGENTS.md`, `HANDOFF.md`, and `SOUL.md`.
- CI no longer fails because workflow and local checker hard-code different hashes.
- A focused test guards the workflow against reintroducing inline trusted hashes.

---

## 2. 原始檔案：`agent_integrity_governance_surface_addendum_2026-03-15.md`

## Agent Integrity Governance Surface Addendum (2026-03-15)

### Why
- The integrity contract now has a single executable source, but that alone still leaves it outside the repo's governance mirrors.
- If a future drift happens, later agents should be able to see the integrity posture through the same compact grammar used by weekly, dream, and Scribe artifacts.

### Boundary
- Keep this phase passive and mirror-friendly.
- Do not modify `AGENTS.md` itself.
- Do not create a second integrity ontology; reuse the existing compact handoff grammar:
  - `primary_status_line`
  - `runtime_status_line`
  - `artifact_policy_status_line`
  - optional `problem_route_status_line`

### Surface
- Add `scripts/run_agent_integrity_report.py` to publish:
  - `docs/status/agent_integrity_latest.json`
  - `docs/status/agent_integrity_latest.md`
- The report should distinguish:
  - executable blocking failures
  - human-facing metadata drift
  - review-only watched-directory signals
- Mirror the report into `refreshable` and `repo_healthcheck` as a passive governance surface.

### Success Criteria
- Agent integrity becomes a source-declared status artifact instead of only a CI/pre-commit side effect.
- Repo healthcheck can mirror its compact posture without recomputing a second integrity contract.
- Future drift is visible as a bounded governance signal before it turns into opaque CI noise.

---

## 3. 原始檔案：`agent_integrity_repo_intelligence_addendum_2026-03-15.md`

## Agent Integrity Repo-Intelligence Addendum (2026-03-15)

### Why
- `agent_integrity` is now a real governance artifact, not only a CI side effect.
- Later agents should see that artifact as one of the bounded repo-governance entrypoints, instead of discovering it only through passive mirrors.

### Boundary
- Keep this phase documentation/repo-intelligence only.
- Do not widen any runtime behavior.
- Reuse the existing `repo_intelligence` surface instead of adding a separate discovery channel.

### Surface
- Add `agent_integrity_latest.json` to repo-intelligence recommended surfaces.
- Mention the new artifact and repo-healthcheck mirror behavior in `docs/status/README.md`.

### Success Criteria
- Repo-intelligence now points later agents toward the agent-integrity artifact explicitly.
- The public status README no longer implies that agent-integrity only exists as CI/pre-commit logic.

---
