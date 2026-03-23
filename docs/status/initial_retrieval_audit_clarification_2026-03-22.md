# Initial Retrieval Audit Clarification (2026-03-22)

This note responds to an initial external retrieval-style audit of the public `tonesoul52`
repository. The goal is not to dismiss the audit, but to separate:

- findings that are materially correct,
- findings that are directionally correct but describe an older repository state,
- findings that are now stale and should not be treated as current risk.

## Why Clarification Is Necessary

ToneSoul contains:

- current machine-generated status artifacts,
- hand-authored historical reviews,
- legacy compatibility shims,
- older structural documents that have not always been refreshed at the same pace as runtime code.

An initial retrieval pass can therefore mix:

- current runtime truth,
- historical design intent,
- stale inventory descriptions.

When these are blended, the result is often a good directional critique with several outdated
examples.

## Executive Summary

| Audit Topic | Judgment | Clarification |
|---|---|---|
| Governance-first architecture | Valid | The core claim is correct and observable in runtime code. |
| `knowledge/` vs `knowledge_base/` ambiguity | Valid | The boundary is still under-documented in public entrypoints. |
| `PARADOXES/` under-explained | Partially valid | The repo documents it as moral / red-team cases, but not prominently enough from the main README. |
| RDD is a governance blind spot | Partially valid | RDD exists and passes baseline gates, but is still staged as `SOFT_FAIL` rather than a mature blocking gate. |
| DDD is vague / falsely reassuring | Partially valid | The framework is defined, but public summaries do not always make the exact freshness / hygiene boundary obvious. |
| Root-level `post_*.py` / `reply_*.py` clutter | Stale | Those files are not present in the current public root; some docs still describe an older layout. |
| `verify_fortress.py` is an active but undocumented defense gate | Stale / partially valid | The script exists under `scripts/`, but it is currently a legacy compatibility check that skips when the pre-5.x runtime is absent. |
| Suspicious `WFGY-3.0 ... (1).txt` filename risk | Stale | That file is not present in the current workspace. |
| README does not explain `SOUL.md`, `MGGI_SPEC.md`, `TAE-01_Architecture_Spec.md` relations | Valid | This was a real entrypoint gap and should be made explicit. |
| Human-designed governance means "AI mutual accountability" is bounded | Valid | This is an important design boundary and should be admitted directly, not implied. |

## What The Audit Got Right

### 1. Governance Is Intentionally Above Capability

This is not branding language only.

- `tonesoul/council/runtime.py` wires council deliberation, provenance capture, and self-memory hooks
  into the runtime path.
- `memory/genesis.py` externalizes responsibility tier mapping instead of burying it inside agent code.
- `AXIOMS.json` is machine-readable and explicitly states both system axioms and design limits.

That makes the positive assessment of the governance architecture substantially correct.

### 2. Public Information Architecture Still Has Boundary Ambiguity

The audit is correct that a first-time reader can struggle with:

- `knowledge/` vs `knowledge_base/`
- the role of `PARADOXES/`
- the relationship among `SOUL.md`, `MGGI_SPEC.md`, and `TAE-01_Architecture_Spec.md`

These are not runtime failures, but they are real repository-communication problems.

### 3. Local Operations / Diagnostics Are Not Clearly Labeled

`monitor_ports.ps1` and `monitor_ports_v2.ps1` are local Windows diagnostics, not deployment
entrypoints, but the repository currently does not make that obvious enough.

The right correction is:

- clearer labeling,
- better directory placement,
- explicit "local debug only" documentation.

## Where The Audit Is Out Of Date

### 1. Test Scale

The audit references "299 tests". That is not current.

Current verified state on `2026-03-22`:

- local full regression: `2610 passed`
- test files under `tests/`: `343`
- red-team test files under `tests/red_team/`: `8`

Older docs still contain smaller historical snapshots, which is likely where the lower number came
from.

### 2. RDD Status

The audit describes RDD as if it were missing.

Current repo evidence shows:

- RDD baseline is present in `tests/red_team/`
- `docs/7D_EXECUTION_SPEC.md` defines RDD as a current `SOFT_FAIL` gate
- historical and latest status artifacts both show RDD as implemented baseline rather than absent

The correct criticism is:

> RDD exists, but it has not yet been promoted from baseline / soft-fail maturity to a stronger
> blocking posture.

That is different from saying the repository lacks adversarial validation altogether.

### 3. DDD Status

The audit treats DDD as under-defined. That is only partially true.

Current public documentation does define:

- curated discussion audit,
- memory hygiene,
- a 7-day freshness SLA,
- a distinction between blocking DDD integrity checks and soft-fail freshness checks.

The real problem is not absence of definition. The problem is that these details are easier to find
in 7D docs and status artifacts than in first-glance entrypoints.

### 4. Root-Level Social Scripts

The audit claims the public root contains many `post_*.py` / `reply_*.py` scripts. That is no
longer true in the current workspace.

What *is* true:

- some older docs still describe that earlier root layout,
- current social / governed posting flow is represented by `tools/` modules such as
  `tools/governed_poster.py`, `tools/moltbook_poster.py`, and `tools/moltbook_client.py`.

So the stale document is real; the current file inventory claim is not.

### 5. `verify_fortress.py`

The audit treats `verify_fortress.py` as if it were an active fortress gate with an undocumented
threat model. The script does exist, but the present implementation is explicitly marked as a
legacy verifier for pre-5.x runtime modules and skips by default when the legacy sandbox runtime is
missing.

That means the right conclusion is:

- naming and documentation are misleading,
- but it should not be interpreted as a strong active defense layer in current production posture.

## Design Boundary That Should Be Admitted More Explicitly

The audit's most philosophically useful point is this:

> ToneSoul lets agents participate in mutual checking, but the accountability grammar itself is
> still human-authored.

That is correct.

ToneSoul is not claiming:

- autonomous self-justifying ethics,
- legal proof of safety,
- model-native morality independent of human governance.

The system is better understood as:

- human-authored governance logic,
- machine-executed deliberation and trace capture,
- verifier-backed behavioral accountability.

This boundary is already partially present in `AXIOMS.json` through fields such as
`liability: "human_only"` and `not_for: ["safety-certification", ...]`, but it should also be
stated more prominently in public-facing docs.

## Immediate Documentation Corrections Triggered By This Audit

This clarification note accompanies a small documentation correction pass:

- refresh stale public README quality snapshot values,
- explain the relationship between `TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE`,
  `SOUL.md`, `MGGI_SPEC.md`, and `TAE-01_Architecture_Spec.md`,
- correct `docs/REPOSITORY_STRUCTURE.md` where it still describes obsolete root-level social
  scripts and an over-simplified fortress verifier story.

## Recommended Next Steps

1. Keep this note as the public rebuttal / clarification layer for retrieval-based reviews.
2. Refresh repository structure docs whenever public layout changes materially.
3. Promote the semantic boundary between `knowledge/`, `knowledge_base/`, and `PARADOXES/`
   into README-level navigation.
4. Decide whether RDD should remain `SOFT_FAIL` baseline or be upgraded toward blocking maturity.
5. Add a short public statement that ToneSoul governance is human-authored, verifier-backed, and
   explicitly not a claim of self-grounded moral autonomy.
