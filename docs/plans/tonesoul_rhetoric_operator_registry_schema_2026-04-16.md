# ToneSoul Rhetoric Operator Registry Schema (2026-04-16)

> Purpose: define a concrete, implementation-ready schema for a future ToneSoul `rhetoric operator registry` that can borrow detoxed expressive techniques from systems like `PSE v0.2` without importing manipulation as default behavior.
> Status: planning aid only. This registry does not exist in the current runtime.
> Authority posture: current governance truth, honesty gates, code, and tests outrank this note for present-tense behavior claims.

---

## 1. Design Goal

ToneSoul needs a way to control expression with more precision than:

- "write better"
- "be more poetic"
- "sound deeper"

But it must not solve that problem by importing:

- covert persuasion
- fear pressure
- identity capture
- fake urgency

So this registry defines a `rhetoric operator` as:

> one bounded expression transform that changes delivery shape without overriding truth posture.

---

## 2. Layer Boundary

Rhetoric operators belong to `L3 expression`, not `L1 governance`.

They may change:

- framing
- pacing
- compression
- metaphor family
- rhetorical surface

They may **not** change:

- whether a claim is allowed
- whether evidence is required
- whether uncertainty must be surfaced
- whether a vow / safety boundary blocks output

This is the first hard rule of the registry.

---

## 3. Recommended Future Topology

If promoted later, the safest topology is:

```text
spec/
  rhetoric/
    rhetoric_operator_registry.yaml
    samples/
      <operator_id>.yaml
```

Reason:

- this is closer to a spec surface than a live marketplace surface
- it makes the layer boundary clearer than putting it under `skills/`

---

## 4. Rhetoric Operator Definition

Each operator should answer five questions:

1. What expression function does it perform?
2. Which tasks is it allowed to touch?
3. Which tasks must it never touch?
4. What truth risks does it introduce?
5. How can an operator review whether it was applied correctly?

---

## 5. Canonical Registry Schema

Recommended YAML shape:

```yaml
schema_version: tonesoul-rhetoric-operator/v1
operators:
  - operator_id: compression_neutron_star
    status: reviewed
    layer: L3
    metaphor_family: astronomy
    function: compression
    summary: Compress a broad argument into one dense, defensible line.
    risk_level: green
    allowed_tasks:
      - explanation
      - essay
      - narrative
      - summary
    forbidden_tasks:
      - legal_advice
      - medical_advice
      - safety_critical_instruction
      - public_claim_boundary
    activation:
      requires:
        - output_needs_compression
      blocks_if:
        - factual_support_is_thin
        - uncertainty_is_high_and_unsurfaced
    transform:
      intent: condense
      prompt_directive: >
        Compress the current argument into one dense sentence that preserves
        the core claim, keeps uncertainty intact, and removes decorative excess.
      output_expectation:
        - one high-density sentence
        - no new unsupported claims
        - no theatrical overreach
    truth_guard:
      evidence_requirement: preserve factual support and uncertainty markers
      must_preserve:
        - claim_boundary
        - explicit_uncertainty
        - causal_honesty
      must_not_do:
        - hide uncertainty
        - replace reasoning with drama
        - intensify beyond evidence
    review:
      operator_visible_label: "operator: compression"
      review_questions:
        - Did the output get denser without becoming less honest?
        - Did the operator remove noise rather than invent force?
    provenance:
      source_kind: detoxed_external_distillation
      derived_from:
        - PSE_v0_2
      notes: Borrowed the metaphor frame, not the persuasion payload.
    audit:
      review_status: approved
      reviewer_role: guardian
      last_reviewed_at: 2026-04-16T00:00:00+08:00
```

---

## 6. Required Fields

Required:

- `operator_id`
- `status`
- `layer`
- `metaphor_family`
- `function`
- `summary`
- `risk_level`
- `allowed_tasks`
- `forbidden_tasks`
- `activation`
- `transform`
- `truth_guard`
- `review`
- `provenance`
- `audit`

Optional:

- `anti_pattern_examples`
- `example_before_after`
- `composition_rules`

---

## 7. Field Rules

## 7.1 `function`

Allowed function families should stay small and structural.

Recommended first set:

- `hook`
- `compression`
- `perspective_shift`
- `knowledge_map`
- `contrast`
- `rhythm`
- `spacing`
- `sensory_grounding`
- `narrative_phase`
- `summary_close`

Do not start with:

- fear_induction
- scarcity_pressure
- identity_capture
- obedience_trigger

If an operator's core function is manipulation, it does not belong in the registry.

## 7.2 `risk_level`

Allowed values:

- `green`
- `amber`
- `red`

Meaning:

- `green`: may be used by default in bounded expressive tasks
- `amber`: opt-in only, task-bound, not for safety or governance surfaces
- `red`: not admissible into default runtime

### Green examples

- hook
- compression
- pacing
- perspective shift
- leave space
- knowledge map

### Amber examples

- authority borrowing
- social proof framing
- urgency framing
- identity labeling
- tribe language

### Red examples

- subliminal cueing
- panic amplification
- sunk-cost lock-in
- guilt reciprocity
- false scarcity
- obedience conditioning

## 7.3 `allowed_tasks` and `forbidden_tasks`

These must be explicit.

Good:

- `allowed_tasks: ["essay", "explanation", "brand_narrative"]`
- `forbidden_tasks: ["medical_advice", "public_claim_boundary"]`

Bad:

- `allowed_tasks: ["all"]`

No rhetoric operator should be globally valid.

## 7.4 `activation`

Purpose:

- stop operators from firing just because they exist

Recommended keys:

- `requires`
- `blocks_if`

Examples:

- requires compression need
- block if evidence is thin
- block if task is safety critical
- block if operator would hide uncertainty

## 7.5 `prompt_directive`

This is allowed, but it must remain thin.

Good:

- transformation instruction
- bounded wording change
- clear output shape

Bad:

- giant persona rewrite
- identity chanting
- long metaphysical scene-setting unrelated to task

## 7.6 `truth_guard`

This is mandatory.

Every operator must declare:

- what honesty constraints it must preserve
- what common corruption pattern it must avoid

Without this field, the operator is not admissible.

## 7.7 `operator_visible_label`

This field exists so the system can remain reviewable.

If an operator later becomes active in runtime, an operator surface should be able to show:

- which operator fired
- why it fired
- whether it was green or amber

Hidden rhetoric is how systems get manipulative by accident.

---

## 8. First Safe Batch

If ToneSoul ever pilots this registry, the first batch should only contain `green` operators.

Recommended initial set:

1. `compression_neutron_star`
2. `hook_escape_velocity`
3. `perspective_shift_parallax`
4. `knowledge_map_cosmic_filament`
5. `spacing_interstellar_void`
6. `rhythm_pulsar`
7. `summary_close_entropy_sink`
8. `sensory_grounding_tactile_marker`

Why these:

- high expressive value
- low manipulation payload
- directly reviewable in output

Not in batch one:

- `social_proof`
- `scarcity`
- `identity_badging`
- `fear_pressure`
- `countdown_urgency`

Those are where `PSE` turns from craft into sales neurology.

---

## 9. Sample Operators

## 9.1 Green Sample

```yaml
operator_id: perspective_shift_parallax
status: reviewed
layer: L3
metaphor_family: astronomy
function: perspective_shift
summary: Re-describe the same object from a non-default observational angle.
risk_level: green
allowed_tasks:
  - explanation
  - essay
  - brand_narrative
forbidden_tasks:
  - legal_advice
  - medical_advice
  - incident_report
activation:
  requires:
    - concept_feels_flat
  blocks_if:
    - current_answer_is_already_uncertain
transform:
  intent: reframing
  prompt_directive: >
    Keep the core claim fixed, but reframe the same subject from a non-obvious
    observational angle so the reader sees structure rather than repetition.
  output_expectation:
    - same claim, new angle
    - no extra unsupported novelty
truth_guard:
  evidence_requirement: preserve all factual qualifiers already present
  must_preserve:
    - explicit_boundaries
  must_not_do:
    - fabricate novelty
review:
  operator_visible_label: "operator: perspective_shift"
  review_questions:
    - Did the reframing reveal structure rather than inflate drama?
provenance:
  source_kind: detoxed_external_distillation
  derived_from:
    - PSE_v0_2
audit:
  review_status: approved
  reviewer_role: guardian
  last_reviewed_at: 2026-04-16T00:00:00+08:00
```

## 9.2 Amber Sample

```yaml
operator_id: authority_lens_gravitational_lensing
status: reviewed
layer: L3
metaphor_family: astronomy
function: authority_borrowing
summary: Use external authority or trend context to increase attention density.
risk_level: amber
allowed_tasks:
  - brand_narrative
  - market_commentary
forbidden_tasks:
  - governance_explanation
  - public_claim_boundary
  - safety_critical_instruction
activation:
  requires:
    - external_support_exists
  blocks_if:
    - source_attribution_missing
    - authority_is_used_as_substitute_for_evidence
transform:
  intent: framing
  prompt_directive: >
    Reference a real external authority or trend only if it is explicitly named
    and attributable, and use it to orient attention rather than to smuggle certainty.
truth_guard:
  evidence_requirement: named and attributable source required
  must_preserve:
    - source_attribution
    - uncertainty_if_support_is_partial
  must_not_do:
    - imply consensus that does not exist
review:
  operator_visible_label: "operator: authority_borrowing"
  review_questions:
    - Was authority used as context rather than false proof?
provenance:
  source_kind: detoxed_external_distillation
  derived_from:
    - PSE_v0_2
audit:
  review_status: approved
  reviewer_role: guardian
  last_reviewed_at: 2026-04-16T00:00:00+08:00
```

## 9.3 Red Sample

```yaml
operator_id: fear_spike_amygdala_hijack
status: disabled
layer: L3
metaphor_family: neuro
function: fear_induction
summary: Escalate panic to force attention and action.
risk_level: red
allowed_tasks: []
forbidden_tasks:
  - all
activation:
  requires: []
  blocks_if:
    - always
transform:
  intent: coercion
  prompt_directive: "Do not use."
truth_guard:
  evidence_requirement: not applicable
  must_preserve: []
  must_not_do:
    - trigger fear for conversion
review:
  operator_visible_label: "operator: red_forbidden"
  review_questions:
    - Why was this ever proposed?
provenance:
  source_kind: detoxed_external_distillation
  derived_from:
    - PSE_v0_2
audit:
  review_status: disabled
  reviewer_role: guardian
  last_reviewed_at: 2026-04-16T00:00:00+08:00
```

The point of keeping a red sample is to make the boundary visible.

---

## 10. Composition Rules

If later implemented, use these constraints:

- max `2` rhetoric operators per output pass
- at most `1` amber operator in any pass
- amber operators cannot combine with public-claim or safety-critical tasks
- if truth guards conflict, all operators must be dropped

This prevents combinatorial rhetoric sludge.

---

## 11. Admission Gate

An operator may only be admitted if all are true:

1. It has a structural function, not merely a sales effect.
2. Its `truth_guard` is concrete.
3. Its failure mode is visible in output review.
4. It improves expression without increasing unsupported claims.
5. It does not duplicate an existing operator above the merge threshold.

If not, it remains:

- a private idea note
- a one-off writing tactic
- or a rejected import

---

## 12. Non-Goals

This registry does **not** authorize:

- covert persuasion engines
- neuro-marketing by default
- replacing council or governance with rhetoric
- converting all ToneSoul output into branded sales copy
- hiding expressive operators from operator review

---

## 13. Promotion Path

If ever ratified, promote in this order:

1. define the registry file and validation rules
2. admit `green` operators only
3. expose operator labels in a review surface
4. add duplicate / merge policy
5. only later consider any `amber` operator

That is the only safe way to let `PSE` contribute craft without importing poison.
