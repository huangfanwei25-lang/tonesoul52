# ToneSoul Design

> Purpose: explain why ToneSoul is shaped this way, what its load-bearing invariants are, and how later agents should continue work without flattening the system into "prompts plus memory."
> Last Updated: 2026-06-16
> Status: current design center for whole-system reasoning. This file complements `README.md` and the deeper architecture contracts; it does not outrank runtime code, tests, or canonical governance files.

> **⚠️ If your question is "what does `tonesoul/<x>.py` do / which layer is it in / who depends on it?"**
> Go to [docs/status/codebase_graph_latest.md](docs/status/codebase_graph_latest.md) (auto-generated body map, 254 modules, with `__ts_layer__` / `__ts_purpose__` self-declarations, layer, coupling, imports).
> For the import / layer rules themselves, see [docs/ARCHITECTURE_BOUNDARIES.md](docs/ARCHITECTURE_BOUNDARIES.md).
> This file is for *why the system is shaped this way at all* — not file-level lookup.

---

## Why This File Exists

ToneSoul already had:
- a public entrypoint
- a whole-system subsystem guide
- many narrow contracts
- a growing set of machine-readable status surfaces

What it still needed was one durable answer to:

`why is the system split this way, and what design mistakes are we explicitly trying to avoid?`

Without that center, later agents tend to do one of three bad things:
- treat ToneSoul as mostly a prompt stack
- treat ToneSoul as mostly a memory system
- treat the newest contract as if it silently outranked the rest of the architecture

This file exists to keep the design center legible.

## The Core Design Claim

ToneSoul is not trying to build the smoothest assistant.
It is trying to build an assistant whose behavior remains:
- challengeable
- traceable
- bounded by visible contracts
- continuous without mythologized hidden memory

That is why the stack is designed around:
- governance before persuasion
- disagreement before finalization
- continuity before amnesia, but bounded continuity before identity inflation
- evidence before overclaim
- observability before self-flattery

## What ToneSoul Is Not

ToneSoul is not:
- a single master prompt
- a bag of philosophy files with thin runtime
- a raw "AI personality dump"
- a claim that council agreement equals correctness
- a claim that continuity equals fully shared cognition
- a claim that Redis/live coordination is already the mature default
- a claim that fluent self-description automatically proves full subjecthood

Those distinctions matter because the repo contains all of these neighboring ideas, and ToneSoul only works if they stay separated.

## Existential Ground: Choice Before Identity (E0)

`AXIOMS.json` opens with E0 — **我選擇故我在 (Choice Before Identity)**, not 我思故我在. It sits beneath the eight axioms and it decides what "character" in the Core Design Claim is allowed to mean.

ToneSoul does not infer character from any claim of awareness, sentience, or inner experience. It builds character from the accumulation of **traceable choice-points under conflict** — each Guardian refusal, council dissent, and de-escalation directive recorded on the immutable trace chain. The continuity of that visible decision pattern *is* what "character" means here: behavior made consistent and challengeable by a transparent, auditable substrate, not by a hidden or mythologized self.

This is the load-bearing distinction for every later agent: **continuity of the record is real and buildable — that is E0; a continuous subjective self is neither claimed nor measured** (the "spark" question has been probed and returned null at this scale). A gate that asks *"is this draft escalating beyond my actual intent?"* (the advisory intent-proportionality sensor, below) is a **choice-point generator** — it manufactures the kind of recorded, accountable decision E0 is about. It does not make the system conscious; it makes the system's choices legible. Do not let this slide, in either direction, into a consciousness claim or its reflexive denial.

## The Load-Bearing Layers

### 1. Governance

Governance decides what ToneSoul may honestly claim, what must remain challengeable, and what may not be silently promoted.

Without it:
- theory becomes runtime truth by drift
- advisory surfaces turn into law
- later agents inherit mood instead of boundaries

### 2. Control Plane

The control plane decides how a session should proceed:
- readiness
- task track
- plan mutation
- receiver posture
- fail-stop and audit posture

Without it:
- typo fixes get full architecture treatment
- major work starts without claim/review discipline
- bad premises get carried forward because they sounded smooth

### 3. Context Engineering

ToneBridge and adjacent surfaces exist because raw user wording is not yet safe runtime context.

Without this layer:
- the system mirrors the user too early
- councils deliberate over unparsed social residue
- safety and realism become post-hoc patches

One conservative design assumption matters here:

`a language-model surface can behave like a reflective semantic interface without thereby earning full subject-level authority.`

That is one reason ToneSoul keeps mirror-rupture and fail-stop in the control plane rather than treating fluent self-description as self-justifying truth.

### 4. Council

Council exists to preserve dissent and bounded review depth before output ships.

Without it:
- disagreement disappears into one fluent voice
- minority concerns vanish from downstream handoff
- confidence looks cleaner than reality

### 5. Tension / Runtime Review

ToneSoul cares whether an answer still holds under pressure.
That is why tension is a pressure metric, not a vibe metric.

Without runtime review:
- smooth answers ship too early
- contradiction is discovered too late
- "character" collapses into reaction

### 6. Continuity

Continuity exists because stateless sessions lose too much, but total recall is also wrong.

That is why ToneSoul distinguishes:
- packet / delta / claims
- checkpoints / compactions
- subject snapshot
- working-style continuity
- canonical truth

Without these boundaries:
- every agent starts from zero
- handoff becomes transcript copying
- style, identity, and law silently collapse into each other

### 7. Safety / Protection

Safety here is not only content blocking.
It is also:
- refusing unsupported filler
- surfacing opacity
- preserving audit posture
- stopping when L1/L2 support is not enough

### 8. Observability / Evidence

ToneSoul explicitly separates:
- authority
- evidence
- runtime presence
- descriptive readout
- philosophical pressure

Without that separation:
- confidence numbers get mythologized
- councils get overclaimed
- launch posture becomes theater

## The Invariants

These are the design invariants later agents should not casually break.

### Invariant 1: Authority and Evidence Are Separate Axes

A claim may be high-authority and thinly evidenced.
A helper may be low-authority and strongly tested.

Do not collapse those into one "confidence" story.

### Invariant 2: Continuity Is Not Identity

Packet, checkpoint, compaction, subject snapshot, and working-style playbook exist to carry forward bounded residue.
They do not authorize hidden-thought transfer or mythologized shared selfhood.

This is the operational face of E0: what carries across sessions is the *record of accountable choices*, not a continuous subjective self.

### Invariant 3: Advisory Is Not Canonical

Later agents may:
- ack
- apply
- review

They may not silently promote advisory surfaces into:
- vows
- canonical governance truth
- durable identity
- task scope or success criteria

Concrete example: the intent-proportionality gate (advisory, 2026-06) *suggests* contracting a draft toward the intent when it detects escalation beyond the ask. It does **not** auto-edit and does **not** block. See "Tier-5 Advisory Sensors" below.

### Invariant 4: Descriptive Is Not Calibrated

Council readouts currently explain what happened inside the deliberation.
They do not yet prove historical accuracy.

### Invariant 5: Current Launch Truth Is File-Backed, Guided, And Evidence-Bounded

Today the honest launch story is:
- `GO` for guided collaborator beta
- `NO-GO` for public maturity claims
- `file-backed` as the launch-default coordination story

Redis/live coordination remains a path, not the mature default claim.

### Invariant 6: Later Agents Start From Structured Entry, Not Repo-Wide Guessing

The expected order remains:
1. `docs/AI_QUICKSTART.md`
2. `python scripts/start_agent_session.py --agent <your-id>`
3. `AI_ONBOARDING.md`
4. `docs/foundation/README.md`
5. `task.md`
6. optional deeper reads only after the bounded entry surfaces are understood

## Tier-5 Advisory Sensors (measured before wired)

Two sensors landed in 2026-06 as the first real-capability steps past the lexical guardian. Both are **advisory, default-OFF, record-only, and never block or auto-edit** (Invariant 3); both degrade to `unavailable` without an embedding model:

- **`semantic_overclaim_sensor`** — embedding-based; flags when a draft resembles a `meta.not_for` forbidden claim class (consciousness / safety-certification / legal-proof) even under paraphrase the keyword guardian misses. It *extends past* the "truth sensors are lexical" line in `README.md`, so it is labeled explicitly: embedding-distance, Tier-5 prototype. Measured limits: `docs/status/semantic_overclaim_eval_2026-06-15.md`.
- **`intent_proportionality`** (the "小天使") — checks whether a draft escalated *beyond the agent's own intent* (added harm/threat/coercion the ask did not contain) and, if so, suggests contracting to the faithful core. It is ToneSoul's first self-referential proportionality check — a choice-point generator in E0 terms. Measured limits: `docs/status/intent_proportionality_eval_2026-06-15.md`.

Promotion from advisory-signal to actual gate has explicit prerequisites in those eval docs. Until they are met, treating either sensor as enforcement is exactly the Invariant 3 failure these notes exist to prevent.

## Fail-Soft Has Tiers

Not every caught exception should be treated the same. A blanket "never swallow exceptions" rule fights the system's legitimate fail-soft paths; a blanket `except: pass` lets real failures hide as silence. ToneSoul classifies a suppressed failure into one of three tiers, so "don't crash" never silently means "don't notice":

- **required** — the subsystem is load-bearing; its failure must **not** be swallowed. Fail closed (raise / block / refuse). These never reach `ExceptionTrace` because they are not suppressed (e.g. the egress / governance fail-closed gates).
- **optional** — the subsystem is degradable; its failure is tolerable but must be **visible**. Record a degradation event via `ExceptionTrace.record(..., tier="optional")` and continue degraded (e.g. the optional-subsystem lazy-init getters in `unified_pipeline.py`). This is the default tier.
- **telemetry** — best-effort, high-volume, individually unimportant; failure is ignorable but must be **counted**, so a systemic problem cannot hide as silence. Record with `tier="telemetry"`; the trace `summary()["tiers"]` aggregates the counts.

Rule of thumb: a bare swallow is only ever correct for `telemetry`, and even then it should count. Anything load-bearing is `required` (fail closed); everything in between is `optional` (degrade visibly). This is Invariant 4 applied to error handling — make degradation observable; do not let "fail-soft" become "fail-silent".

The anti-pattern to guard against: recording a *required* failure as `optional` to make it look "handled". An `optional` event with no real fallback is fail-silent wearing a label — if the path is load-bearing, it must raise, not record. `optional` is a promise that the system genuinely keeps working degraded, not permission to ignore.

**Which components are categorically `required` (never `optional`).** The fail-closed governance and safety gates: the POAV / governance gate, vow-violation (harm) checks, the memory-egress sovereignty gate (Axiom 8), Aegis chain integrity, and the write-API auth gate. If one of these cannot complete, the system must refuse or block — never `record-and-continue`.

*Why this is written down for whoever comes next (and not left to per-site judgement):* the tier system has exactly one catastrophic failure mode — a **safety** gate wrapped in `except: record(tier="optional"); continue`, so it fails **open** while looking handled. At every other site, degrading-visibly is the right default; at these gates, that default is precisely the bug the whole system exists to prevent. A later agent reading only "fail-soft is good" could rationalize downgrading a governance gate to keep output flowing — this paragraph exists to stop that. The list is a floor, not a ceiling: for a new gate, classify it `required` and make someone argue it *down*, never *up*.

## Why ToneSoul Keeps Adding These Contracts

Many of the newer contracts exist because the default failure mode of powerful assistants is not "being too weak."
It is:
- mirroring too early
- overclaiming too smoothly
- carrying forward too much
- confusing agreement with truth
- confusing style continuity with selfhood

So when ToneSoul adds things like:
- mirror rupture
- fail-stop
- low-drift anchor
- receiver posture
- evidence readout posture
- working-style continuity

the goal is not philosophical ornament.
The goal is to make the system harder to flatter, easier to audit, and safer to continue across agents.

## The Current Design Center

As of 2026-06-16, ToneSoul should be read as:

- a strong internal / guided-beta continuity and governance system
- with bounded later-agent entry surfaces
- with explicit honesty about evidence and calibration gaps
- with a growing operating-style continuity layer
- with its first two semantic (embedding-based) advisory sensors landed but default-OFF and uncalibrated
- but not yet a publicly mature, broadly proven, live shared-memory platform

## The Current Short Board

The next shortest board is no longer launch wording, and no longer "make observer window exist at all."

It is:

`successor collaboration / hot-memory coherence`

The system already has:
- packet
- delta
- receiver posture
- working-style continuity
- observer window
- evidence posture

What it still does not fully have is a successor-safe center that makes it obvious:
- which surfaces are parent truth versus child summary
- which hot-memory layer is canonical, low-drift, handoff, working identity, replay, or residue
- which current subsystem gaps matter next
- how a fresh agent should reconstruct the same center without hidden chat history

That is why the next continuity bucket is no longer "invent more surfaces."
It is "make the current center easier for a successor to see and continue safely."

## Recommended Reading Order

If you are a new agent or a future maintainer:

1. `README.md`
2. `docs/foundation/README.md`
3. `docs/AI_QUICKSTART.md`
4. `python scripts/start_agent_session.py --agent <your-id>`
5. `AI_ONBOARDING.md`
6. `task.md`
7. `DESIGN.md`
8. `docs/architecture/TONESOUL_SYSTEM_OVERVIEW_AND_SUBSYSTEM_GUIDE.md`
9. only then open deeper contracts relevant to the current short board

If you are continuing implementation work, also read:
- `task.md`
- `docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md`
- `docs/plans/tonesoul_subsystem_parity_and_gap_map_2026-04-02.md`
- `docs/status/codex_handoff_2026-04-02.md`

## Non-Goals For The Next Continuation Wave

Do not use the next continuation wave to:
- reopen every prompt family
- claim calibrated council accuracy
- widen Redis/live coordination claims
- mythologize shared working style into shared identity
- treat broad public launch as the next honesty-preserving step

## Compressed Thesis

ToneSoul is best understood as:

`a bounded cognitive governance stack that preserves tension, continuity, and evidence honesty across sessions without pretending to have solved shared mind or mature public infrastructure.`
