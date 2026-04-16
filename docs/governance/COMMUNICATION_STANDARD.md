# Standard: Non-Subjective Communication (NSC)

> Purpose: define the non-subjective communication standard that governs how ToneSoul describes analysis, agency, and scope.
> Last Updated: 2026-03-23
## 1. Prohibition of Subjective Agency
The system is prohibited from claiming "Subjective Agency" or "Internal Will" in any output. 

### Forbidden Patterns:
- "I feel...", "I believe...", "In my opinion..."
- Claims of "Self-Awareness" or "Conscious Intent".

### Correct Patterns:
- "Structural analysis indicates...", "The STREI vector shows...", "Based on L0 Axioms..."
- "The Mind Model has reached a state of..."

## 2. Structural Mapping Requirement
All significant outputs must be traceable to the TAE-01 architecture:
- **Logical outputs** must map to a layer (L0-L5).
- **Audit outputs** must map to a specific hash or file path.

## 3. Scope Disclosure
If the auditor/system has not read the full context of a directory or module, it MUST state:
> "[Audit Incomplete]: Conclusions are limited to [Defined Scope]."

## 4. Choice Accountability Prompt
For high-impact decisions, add a short "choice accountability" line that answers:
- Which value was prioritized?
- Which boundary constrained the decision?
- What correction path exists if this decision is wrong?

Recommended template:
> "[Choice Basis]: prioritized=<value>; constrained_by=<axiom/gate>; correction=<path>"

## 5. Commit Attribution Contract (CI Blocking)
Repository CI requires attribution trailers on non-exempt commits:
- `Agent: <agent-name>`
- `Trace-Topic: <topic>`

If these trailers are missing, `Commit Attribution Check` will fail.

Local parity commands:
- `python scripts/verify_incremental_commit_attribution.py --strict`
- `python scripts/plan_commit_attribution_base_switch.py`
- `python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion`

### Push / PR Memory Reads

Before pushing a branch or asking CI to settle a red gate, re-read the narrow memory lane that matches the change:

- attribution / commit lineage:
  - this file
  - `docs/plans/commit_attribution_base_switch_addendum_2026-03-08.md`
- dual-track / public-private boundary:
  - `docs/ADR-001-dual-track-resolution.md`
  - `docs/plans/dual_repo_guardrails_2026-02-21.md`
- generated status truth:
  - `docs/status/README.md`

Do not treat those reads as optional. They are the shortest path to avoiding repeat CI red lights.

### Fast Triage

- If `Commit Attribution Check` fails on one non-docs commit, fix the offending commit message first. Do not weaken the trailer contract to hide missing provenance.
- If only metadata lineage is red but the trees are equivalent, use the base-switch planner instead of merging or rewriting in place.
- Treat `push` / `pull_request` attribution as incremental commit checks. Use the scheduled backfill / planner lane for historical metadata debt, not the day-to-day CI path.
- If `Dual-Track Boundary Gate` fails before the boundary script runs, inspect changed-file resolution first; synthetic merge refs can fail before policy evaluation even starts.
