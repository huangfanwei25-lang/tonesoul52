# Claude Work Order — Deep Structure Authority Distillation (2026-03-27)

> Purpose: give a high-context synthesis agent a bounded documentation workstream that converts repo-scale structural insight into durable authority boundaries for later AI instances.
> Last Updated: 2026-03-27
> Issued By: Codex
> Target Agent: Claude Opus / other long-context synthesis-heavy collaborator
> Priority: high
> Status: primary authority-distillation pass completed; follow-up extension appended for implementation-gap triage

## Why This Workstream Exists

ToneSoul now has a clearer AI entry stack:

- `operational`: quickstart and working reference
- `canonical`: architecture anchors and contracts
- `deep_map`: anatomy-scale system map
- `interpretive`: deeper narrative readings

That is good enough for entry.

What is still missing is a durable answer to a harder question:

> when a term appears in `law/`, `docs/`, `research/`, `tests/`, and narrative prose at the same time, what exactly is its current authority and implementation status?

This is where a long-context synthesis agent is strongest.

## Why This Fits Claude

This work is best done by an agent that is strong at:

- scanning many files without losing global structure
- turning large repo slices into named conceptual planes
- extracting a panoramic map from `law/`, `PARADOXES/`, `tests/`, `scripts/`, and narrative docs together
- writing high-density synthesis without collapsing distinct layers into one

This is not a runtime feature ticket.
It is a structure-and-boundary distillation ticket.

## Current Repo Posture

Read these first:

1. `AI_ONBOARDING.md`
2. `docs/AI_QUICKSTART.md`
3. `docs/AI_REFERENCE.md`
4. `docs/narrative/TONESOUL_ANATOMY.md`
5. `docs/narrative/TONESOUL_CODEX_READING.md`
6. `docs/notes/TONESOUL_DEEP_READING_ANCHOR_2026-03-26.md`
7. `AXIOMS.json`
8. `tonesoul/runtime_adapter.py`
9. `tonesoul/diagnose.py`
10. `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
11. `docs/architecture/TONESOUL_ABC_FIREWALL_DOCTRINE.md`

Important current boundary:

- `AI_QUICKSTART` and `AI_REFERENCE` are operational guides, not constitutions
- `TONESOUL_ANATOMY` is a deep system map, not a runtime contract
- `TONESOUL_CODEX_READING` and the deep-reading anchor are interpretive, not executable truth
- many `law/` terms are real and important, but not all are current `runtime_adapter.py` hard dependencies

## Primary Objective

Produce a source-backed map that tells later agents, for major ToneSoul claims and terms:

- where the claim lives
- what kind of authority it has
- whether it is implemented now, partially implemented, or still theoretical
- whether an operator may rely on it during live engineering work

## Deliverables

### Deliverable A

Create:

- `docs/architecture/TONESOUL_CLAIM_AUTHORITY_MATRIX.md`

This should be a table-driven map of the most load-bearing 40-80 claims or terms across:

- `AXIOMS.json`
- `docs/AI_REFERENCE.md`
- `docs/narrative/TONESOUL_ANATOMY.md`
- `law/`
- runtime/code/test surfaces

Each row should include at least:

- term or claim
- authority role
  - `canonical`
  - `operational`
  - `deep_map`
  - `interpretive`
  - `law`
  - `research`
  - `runtime`
  - `projection`
- implementation status
  - `hard runtime`
  - `runtime-adjacent`
  - `test-backed but distributed`
  - `doc-only`
  - `research/theory`
  - `projection-only`
- source files
- can a later agent rely on this for engineering decisions: `yes / only with verification / no`

### Deliverable B

Create:

- `docs/architecture/TONESOUL_LAW_RUNTIME_BOUNDARY_CONTRACT.md`

This should explicitly classify high-confusion terms from `law/` and related deep prose into:

1. active runtime or audit dependency
2. active governance vocabulary but not current hard runtime dependency
3. theory / research lane
4. projection / narrative / worldview lane

This contract must explicitly cover:

- `YuHun Gate`
- `StepLedger`
- `Lex Lattice`
- `LAR`
- `Isnād`
- `MDL-Majority`
- `Sovereign Freeze`
- `BBPF`
- `Digital Sovereignty Manifesto`
- `PARADOX_006`

### Deliverable C

Optional, only if needed to support A/B:

- `docs/research/tonesoul_anatomy_source_register_2026-03-27.md`

Use this only if the evidence for `TONESOUL_ANATOMY.md` needs an external register instead of cluttering the anatomy file itself.

## Boundaries

Do not do these things in this workstream:

- do not change `tonesoul/runtime_adapter.py`
- do not change Redis schema, gateway behavior, or commit mutex logic
- do not change `AI_ONBOARDING.md`, `docs/AI_QUICKSTART.md`, or `docs/AI_REFERENCE.md` unless a claim is provably wrong and cannot be corrected later by Codex
- do not touch protected files like `AGENTS.md`
- do not push, merge, or rewrite history
- do not hand-maintain repo file counts unless the number is script-generated in the same pass

If you find that a concept is overclaimed:

- downgrade the claim in documentation
- do not silently "promote" code to match the prose

## Non-Goals

This ticket is not asking for:

- prettier prose
- more philosophy for its own sake
- a new runtime feature
- a dashboard redesign
- another grand unified narrative if the authority map is still missing

## Acceptance Criteria

This workstream is successful if:

- a later AI can answer "is this term active runtime, law, theory, or projection?" without rereading the whole repo
- the biggest overclaiming risks between `law/`, `ANATOMY`, and current runtime are explicitly named
- the resulting docs help future agents avoid mistaking deep structure for live implementation
- no protected files or runtime code are touched

## Suggested Method

1. Read the current AI entry stack and authority boundaries first.
2. Extract the top claims from `AI_REFERENCE`, `ANATOMY`, and `law/`.
3. Cross-check each claim against:
   - `tonesoul/runtime_adapter.py`
   - `tonesoul/diagnose.py`
   - relevant tests
   - canonical architecture contracts
4. Downgrade or split any mixed claim instead of smoothing it over.
5. Leave crisp, table-first artifacts rather than a second long essay.

## Handoff Back To Codex

When done, report back with:

- files created or changed
- 5-10 highest-risk overclaims you found
- which terms are now safe for later AI instances to treat as current runtime truth
- which terms must remain explicitly marked as theory, law, or projection

---

## Follow-Up Extension: Implementation-Gap Triage

This extension exists because Deliverables A/B answer:

> what kind of thing is this term?

But a second, narrower question now matters:

> for the biggest gap terms, should ToneSoul downgrade the prose, keep them as theory, or eventually promote them into a real implementation plan?

This is still a documentation and boundary ticket.
It is not permission to implement the missing mechanisms.

## Why This Follow-Up Fits Claude

This next pass again benefits from panoramic structural judgment:

- it requires comparing prose ambition against runtime evidence
- it requires deciding whether a gap is dangerous, harmless, aspirational, or worth future mainline planning
- it benefits from naming a small set of future work candidates without collapsing them into one giant roadmap

## Follow-Up Objective

Produce a bounded triage of the most important "between theory and runtime" terms so later agents stop oscillating between:

- overclaiming them as already active
- or dismissing them as irrelevant when they are actually live design pressure

The goal is to classify each selected gap term into one of four next-step lanes:

1. **Downgrade prose now**
2. **Keep theory-only**
3. **Contract-only wording is enough**
4. **Deserves a future implementation plan**

## Mandatory Focus Terms

At minimum, re-evaluate these:

- `POAV gate enforcement`
- `Risk (R) calculation`
- `Axiom 5 / Mirror Recursion`
- `Axiom 7 / Semantic Field Conservation`
- `ContractObserver` blocking path
- `PainEngine / CircuitBreaker` trigger path
- `BBPF` enforcement path
- `YuHun Gate` as a distributed runtime metaphor vs a missing object

You may add 2-6 more only if they are comparably dangerous or structurally important.

## Follow-Up Deliverables

### Deliverable D

Create:

- `docs/architecture/TONESOUL_IMPLEMENTATION_GAP_TRIAGE_2026-03-27.md`

This should be a table-first triage for the selected high-gap terms.

Each row should include at least:

- term
- where it is currently overclaimed or easily misread
- actual runtime/code/test evidence
- risk if a later agent misunderstands it
- recommended lane
  - `downgrade prose now`
  - `keep theory-only`
  - `contract-only wording`
  - `future implementation plan`
- short rationale

### Deliverable E

Optional, only if clearly justified by Deliverable D:

- `docs/plans/tonesoul_gap_followup_candidates_2026-03-27.md`

Use this only if several items truly deserve separate future work tickets.
Do not generate a large roadmap.
Keep it to a small candidate list with one paragraph per item.

## Follow-Up Boundaries

Do not do these things in this extension:

- do not implement POAV as a new runtime gate
- do not add a new `Risk (R)` engine
- do not modify `runtime_adapter.py`, `unified_pipeline.py`, Redis schema, or gateway behavior
- do not rewrite `AI_ONBOARDING.md`, `AI_QUICKSTART.md`, or `AI_REFERENCE.md` beyond narrow claim downgrades if absolutely necessary
- do not create a giant master roadmap
- do not use `memory/handoff/` as a public-facing output lane

If a gap deserves real code later:

- name it clearly
- bound it clearly
- leave implementation to a separate Codex-owned phase

## Follow-Up Acceptance Criteria

This extension is successful if:

- later agents can tell which gap terms should simply be spoken about more carefully versus which deserve actual future work
- the most dangerous half-implemented or over-read concepts get a crisp next-step classification
- the result reduces confusion without promoting missing mechanisms into false truth

## Follow-Up Handoff Back To Codex

When done, report back with:

- which terms should be downgraded in prose immediately
- which terms should remain explicitly theory-only
- which terms are best handled by small future implementation tickets
- whether any one item is urgent enough to deserve the next Codex build phase
