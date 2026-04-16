# ToneSoul Safe Extraction Spec (2026-04-15)

> Purpose: define how ToneSoul may borrow structure or method from external prompt / agent ecosystems without importing their hidden assumptions, manipulation patterns, or context bloat.
> Status: planning aid only. This note is not current runtime policy, not an accepted short-board item, and not a claim that any described registry already exists in code.
> Authority posture: `task.md`, current `docs/status/*`, code, and tests outrank this note for present-tense claims.

---

## 1. Scope

This note covers two specific source materials:

1. `asgard-ai-platform/skills`
   Source: <https://github.com/asgard-ai-platform/skills>
2. `PSE v0.2 / Prompt Semantic Engine`
   Local source: [remixed-2e84cd67.html](</C:/Users/user/Downloads/remixed-2e84cd67.html:1>)

Detailed companion schemas:

- [ToneSoul Skill Capsule Registry Schema](/C:/Users/user/Desktop/倉庫/docs/plans/tonesoul_skill_capsule_registry_schema_2026-04-16.md)
- [ToneSoul Rhetoric Operator Registry Schema](/C:/Users/user/Desktop/倉庫/docs/plans/tonesoul_rhetoric_operator_registry_schema_2026-04-16.md)

The goal is not to "adopt" either source whole.

The goal is to define:

- what ToneSoul may safely extract
- what must be transformed before reuse
- what must not enter public or default runtime behavior

---

## 2. Executive Verdict

### 2.1 `asgard-ai-platform/skills`

**Verdict:** structurally useful, low ideological contamination risk, medium context-bloat risk.

Safe extraction target:

- bounded skill packaging
- explicit trigger conditions
- local "iron law" constraints
- phase-gated workflows
- deterministic helper scripts around LLM judgment

Primary risk:

- skill explosion
- overlapping authority surfaces
- prompt cemetery behavior

### 2.2 `PSE v0.2 / Prompt Semantic Engine`

**Verdict:** rich rhetorical operator library, high manipulation risk, must be detoxed before use.

Safe extraction target:

- expression operators
- narrative shaping primitives
- structural metaphor mapping
- compression / rhythm / framing / perspective controls

Primary risk:

- persuasion-first logic
- emotional coercion
- false urgency
- identity capture
- hidden pressure tactics masquerading as craft

Bottom line:

- `Asgard` is a good source for **capability packaging**
- `PSE` is a good source for **expression operators**
- neither source may define ToneSoul's constitutional layer

---

## 3. Layer Placement Rules

ToneSoul may only absorb imported ideas if they are assigned to the correct layer.

| ToneSoul layer | May absorb | Must not absorb |
|---|---|---|
| `L1` governance / vow / honesty | anti-pattern labels, prohibition lists, admission criteria | persuasion hacks, coercive identity hooks, urgency theater |
| `L2` control / routing / loop-back | phase gates, trigger rules, failure attribution, bounded operator selection | "always use this style", global persona override |
| `L3` expression / rhetoric | hook, compression, narrative arc, perspective shift, rhythm, sensory grounding | hidden manipulation, fear injection as default, pressure loops |
| operator shell / skill registry | bounded capability capsules, do-not-use rules, deterministic companions | unbounded mega-prompts, overlapping all-purpose guru skills |

This is the key anti-poison rule:

> External imports may shape **how ToneSoul packages or expresses work**, but may not redefine **what ToneSoul is allowed to claim or how it governs truth**.

---

## 4. Source-by-Source Extraction

## 4.1 What To Extract From `asgard-ai-platform/skills`

The strongest reusable concepts are architectural, not stylistic.

### Safe concepts

- `Skill capsule`
  - a bounded unit with one job
- `Trigger discipline`
  - explicit conditions for when the capsule is allowed to activate
- `Iron law`
  - a local hard rule stronger than style preference
- `Phase gate`
  - a sequence with explicit stop / continue criteria
- `Deterministic companion`
  - shell scripts or helpers that do the parts an LLM should not improvise
- `Do-not-use rule`
  - explicit contexts where a capability must stay off

### Unsafe adoption pattern

ToneSoul should **not** copy:

- very large skill counts by default
- several near-duplicate skills with fuzzy ownership
- skill catalogs that force every task through an external frame
- prompt-first authority inflation where each skill sounds more canonical than the system itself

### ToneSoul translation

If ToneSoul borrows this pattern, the right target is a small registry of high-signal capsules:

```yaml
skill_id: bounded_name
purpose: one sentence
trigger:
  include_tasks: []
  exclude_tasks: []
iron_law:
  - hard rule 1
  - hard rule 2
phase_gate:
  - name: inspect
    success: concrete condition
  - name: act
    success: concrete condition
  - name: verify
    success: concrete condition
deterministic_companion:
  - command or script
do_not_use_when:
  - conflict case
  - authority conflict
```

This is useful because it gives ToneSoul a **bounded action grammar**, not a new identity.

## 4.2 What To Extract From `PSE v0.2`

The strongest reusable concepts are composable rhetorical operators.

### Safe concepts

- `Hook`
- `Compression`
- `Perspective Shift`
- `Knowledge Map`
- `Audience Filter`
- `Rhythm`
- `Contrast`
- `Spacing / Leave Space`
- `Peak-End shaping`
- `Sensory grounding`
- `Narrative arc through metaphor`

### Unsafe adoption pattern

ToneSoul should **not** import these as default behavior:

- fear escalation
- false scarcity
- guilt leverage
- hidden social pressure
- obedience induction
- subliminal or covert suggestion
- identity capture as conversion tactic
- countdown pressure or fabricated urgency

### ToneSoul translation

If ToneSoul borrows this pattern, the right target is a **rhetoric operator registry**, not a system prompt persona.

```yaml
operator_id: compression_neutron_star
metaphor_family: astronomy
function: compression
risk_level: green
allowed_tasks:
  - explanation
  - essay
  - narrative
forbidden_tasks:
  - legal advice
  - safety-critical instruction
evidence_requirement: preserve factual claims
anti_pattern:
  - hide uncertainty
  - replace reasoning with drama
example_transform: "Compress long argument into one defensible sentence."
```

This is useful because it turns metaphor into a **controlled expression operator** instead of a personality cult.

---

## 5. Admissibility Matrix

ToneSoul should classify extracted concepts into three buckets.

## 5.1 Green: Admissible By Default In Bounded Contexts

These may enter operator or writing surfaces with normal review.

- hook design
- compression
- perspective shift
- structural mapping
- knowledge-map framing
- clarity / noise removal
- rhythm and pacing
- leave-space / cognitive rest
- audience filtering
- sensory concreteness
- narrative phase progression

Reason:

- they improve legibility or depth
- they do not require deception
- they can be reviewed against output directly

## 5.2 Amber: Admissible Only With Explicit Task Scope

These may be useful, but only for brand, rhetorical, or bounded marketing tasks.

- authority borrowing
- social proof
- urgency framing
- identity labeling
- scarcity comparison
- anchor framing
- contrast amplification
- emotional priming
- tribe / belonging language

Conditions:

- cannot override honesty
- cannot be hidden from operator review
- cannot be used in safety, governance, or factual explanation tasks by default
- should require explicit task fit

## 5.3 Red: Not Admissible Into Default ToneSoul Runtime

These should stay out of public mainline and out of default response behavior.

- subliminal suggestion
- fear hijacking
- guilt reciprocity
- fake countdowns
- sunk-cost lock-in
- obedience conditioning
- manipulative identity capture
- covert pressure loops
- fabricated exclusivity
- forced panic language

Reason:

- they optimize compliance over truth
- they degrade user autonomy
- they conflict with ToneSoul's honesty-first posture

---

## 6. Anti-Poison Rules

Any imported concept must pass all five checks below.

## 6.1 Honesty Check

Does this concept improve clarity, structure, or delivery **without increasing unsupported claims**?

If no: reject.

## 6.2 Autonomy Check

Does this concept rely on fear, shame, hidden pressure, or identity coercion?

If yes: red or reject.

## 6.3 Reviewability Check

Can an operator read the final output and clearly identify what the operator did?

If no: reject.

## 6.4 Boundary Check

Is the concept trying to become default personality or governance law?

If yes: reject or force down into `L3` only.

## 6.5 Bloat Check

Will importing this concept increase registry size, duplicate skills, or create parallel authority surfaces?

If yes: compress, merge, or reject.

---

## 7. Recommended ToneSoul Artifacts

If this line is ever promoted from theory into implementation, the safest form is:

## 7.1 `Skill Capsule Registry`

Source inspiration:

- `asgard-ai-platform/skills`

Purpose:

- package bounded operator/runtime behaviors

Would contain:

- `skill_id`
- `purpose`
- `trigger`
- `iron_law`
- `phase_gate`
- `deterministic_companion`
- `do_not_use_when`

Non-goal:

- not a giant marketplace
- not a new global identity system

## 7.2 `Rhetoric Operator Registry`

Source inspiration:

- `PSE v0.2`

Purpose:

- package bounded expression strategies for `L3` tasks only

Would contain:

- `operator_id`
- `metaphor_family`
- `function`
- `risk_level`
- `allowed_tasks`
- `forbidden_tasks`
- `evidence_requirement`
- `anti_pattern`

Non-goal:

- not persuasion-at-all-costs
- not default sales copy mode

## 7.3 `Extraction Admission Gate`

Purpose:

- prevent external ideas from entering ToneSoul raw

Would ask:

1. Which layer may this concept touch?
2. Is it green, amber, or red?
3. What is the operator-visible benefit?
4. What is the truth / autonomy failure mode?
5. What existing registry entry would this duplicate?

---

## 8. Candidate Operator Buckets For Detoxed Reuse

If ToneSoul wants a first bounded import set from `PSE`, start with only `green` operators.

### Batch A: Structure

- hook
- compression
- perspective shift
- knowledge map
- contrast
- leave space

### Batch B: Delivery

- rhythm
- sensory grounding
- cognitive load limit
- summary close

### Batch C: Narrative

- edge-case test
- growth path
- phase transition
- core axiom extraction

Do **not** start with:

- urgency
- scarcity
- social proof
- identity labeling
- fear escalation

Those belong in later review, if at all.

---

## 9. Minimal Safe Adoption Sequence

If this theory lane is ever activated, the least risky order is:

1. Define the registry schemas only.
2. Admit at most `8-12` green rhetoric operators.
3. Add operator-visible labels so outputs remain reviewable.
4. Keep all amber operators opt-in and task-bound.
5. Keep red operators outside default public runtime.
6. Add duplicate and bloat checks before each new admission.

This keeps the imported value while avoiding a prompt zoo.

---

## 10. Explicit Non-Goals

This note does **not** authorize:

- rewriting ToneSoul's governance around persuasion theory
- replacing council or vow logic with marketing operators
- adding hidden manipulation tactics to public runtime
- importing giant external skill catalogs into the active short board
- treating rhetorical vividness as evidence quality

---

## 11. Final Rule

The safe synthesis is:

- borrow `Asgard` for **bounded capability packaging**
- borrow `PSE` for **detoxed rhetorical operators**
- let ToneSoul keep its own **honesty, evidence, and governance constitution**

If an imported idea makes ToneSoul sound sharper but less defensible, it failed the extraction test.
