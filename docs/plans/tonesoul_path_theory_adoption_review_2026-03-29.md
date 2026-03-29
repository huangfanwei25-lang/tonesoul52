# ToneSoul PATH Theory Adoption Review (2026-03-29)

> Purpose: record which PATH-theory ideas were adopted into ToneSoul-native lanes, which remain deferred, and which should not be imported directly.
> Last Updated: 2026-03-29
> Status: review record after evaluating the `path_integration_*` source materials.

---

## Outcome Summary

ToneSoul does **not** adopt PATH naming directly.

Instead:
- adopt the useful epistemic discipline in ToneSoul-native terms
- defer behavior-changing proposals that would add new runtime surfaces or new commit semantics
- reject source-material docs as authority surfaces once their useful content has been distilled

---

## Decision Table

| PATH Candidate | ToneSoul Decision | Where It Lands |
|----------------|------------------|----------------|
| Blackbox responsibility boundary | **Adopted in ToneSoul-native form** | `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` |
| Axiom falsifiability conditions | **Adopted in ToneSoul-native form** | `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md` |
| IMPACT layer tracking | **Deferred** | no new runtime surface yet |
| PRIMARY / CONSTRAINT / REJECTED path marking | **Deferred** | no `decision_paths` schema field yet |
| High tension delayed commit | **Deferred** | no new commit-delay mechanism yet |

---

## What Was Worth Keeping

### 1. Opaque reasoning must not be overclaimed as auditable

This idea fits ToneSoul strongly, but the right local framing is:

- observable shell
- opacity boundary
- governed output versus auditable reasoning

That work is already represented in:
- `docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md`

### 2. Constitutional claims should say what would weaken them

This also fits ToneSoul strongly, but the right local framing is:

- axiom falsification map
- companion challenge surface
- not direct mutation of `AXIOMS.json`

That work is already represented in:
- `docs/architecture/TONESOUL_AXIOM_FALSIFICATION_MAP.md`

---

## What Was Not Ready

### 1. IMPACT Tracking

Reason for defer:
- would require a new backward-linking surface
- attribution risk is non-trivial
- current repo still gets enough value from git history, traces, compactions, and human review

Revisit only if:
- later agents repeatedly need causal feedback beyond current trace + git reconstruction

### 2. Decision Path Semantic Marking

Reason for defer:
- high risk of boilerplate or retrofitted fake alternatives
- optional metadata is cheap to add, but cheap metadata is often cheap signal

Revisit only if:
- agents begin producing repeated, meaningful alternative-path reasoning that later agents truly reuse

### 3. High-Tension Delayed Commit

Reason for defer:
- this is the only proposal that materially changes agent behavior
- ToneSoul already has `readiness`, `checkpoint`, `compaction`, `perspective`, and receiver guards
- adding another advisory delay layer too early risks indecision and over-governance

Revisit only if:
- real sessions show repeated premature commits under unresolved high tension

---

## Naming Boundary

If any deferred idea is revisited later:

- do **not** import `PATH`, `blackbox_level`, `PRIMARY_PATH`, or similar names as runtime truth
- rename into ToneSoul-native terms
- keep adoption below canonical/runtime truth until tested

Examples:
- `blackbox boundary` -> observable-shell / opacity boundary
- `falsifiability conditions` -> axiom falsification map
- `decision delay` -> commit readiness or tension-held continuation, if ever implemented

---

## Source-Material Boundary

The following `path_integration_*` files were useful as source material, but should not remain as quasi-authoritative untracked docs after distillation:

- `docs/plans/path_integration_01_blackbox_boundary.md`
- `docs/plans/path_integration_02_impact_tracking.md`
- `docs/plans/path_integration_03_path_semantic_marking.md`
- `docs/plans/path_integration_04_tension_delayed_commit.md`
- `docs/plans/path_integration_05_falsifiability_conditions.md`
- `docs/plans/path_integration_codex_handoff.md`

Their useful content is now captured by:
- ToneSoul-native boundary documents already in `docs/architecture/`
- this review record

---

## Handoff Line

PATH contributed two useful methodological disciplines:
- honesty about opacity
- honesty about falsifiability

The rest remains interesting but below the current priority line. ToneSoul should carry forward the discipline, not the external vocabulary.
