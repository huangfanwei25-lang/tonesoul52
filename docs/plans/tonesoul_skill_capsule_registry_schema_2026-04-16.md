# ToneSoul Skill Capsule Registry Schema (2026-04-16)

> Purpose: define a concrete, implementation-ready schema for a future ToneSoul `skill capsule registry` that borrows the packaging discipline of external skill ecosystems without importing their scale, duplication, or authority inflation.
> Status: planning aid only. This schema is not live runtime truth, and the repo does not currently ship the target registry path.
> Authority posture: current code, tests, and active status surfaces outrank this note for present-tense claims.

---

## 1. Design Goal

ToneSoul needs a bounded way to package reusable capability units without turning them into:

- a giant skill marketplace
- a second personality system
- a parallel authority layer above governance truth

This schema defines a `skill capsule` as:

> one bounded capability with one narrow job, one activation envelope, one local hard-law set, and one reviewable execution path.

---

## 2. Current Repo Reality

There is already a partial skill shape in the repo:

- [tonesoul/council/skill_parser.py](/C:/Users/user/Desktop/倉庫/tonesoul/council/skill_parser.py:1)
- existing `SKILL.md` frontmatter examples under `.agent/skills/`
- historical schema note: [spec/skills/skill_gravity_well_schema.md](/C:/Users/user/Desktop/倉庫/spec/skills/skill_gravity_well_schema.md:1)

Important reality check:

- the parser expects `skills/registry.json`
- that directory does **not** currently exist in this repo
- therefore the safest next step is schema design, not pretending a live runtime registry is already wired

This schema is designed to be:

1. compatible with the current parser's core assumptions
2. stricter than the current parser in governance fields
3. small enough to stay bounded

---

## 3. Recommended Future Topology

If promoted later, the safest topology is:

```text
skills/
  registry.json
  capsules/
    <skill_id>.md
```

Where:

- `registry.json` stores discoverability, routing, review, and constraints metadata
- `capsules/<skill_id>.md` stores the full human-readable execution contract

Do not store large prompt blobs directly inside `registry.json`.

---

## 4. Skill Capsule Definition

A skill capsule has four layers.

## 4.1 L0: Registry Envelope

This is the minimal object discoverable by runtime code.

Required fields:

- `id`
- `path`
- `status`
- `l1_routing`
- `l2_signature`
- `provenance`
- `audit`

Optional fields:

- `summary`
- `anti_bloat`
- `deprecation`

## 4.2 L1: Routing Layer

This decides whether the skill is allowed to match a task.

Required:

- `name`
- `triggers`
- `intent`

Optional:

- `include_tasks`
- `exclude_tasks`
- `required_surface`
- `blocked_surfaces`

## 4.3 L2: Signature Layer

This defines admissibility, profile fit, and execution constraints.

Required:

- `execution_profile`
- `trust_tier`
- `iron_law`

Optional:

- `json_schema`
- `requires_tools`
- `forbidden_tools`
- `phase_gate`
- `deterministic_companion`
- `do_not_use_when`
- `context_budget`

## 4.4 L3: Capsule Body

This is the markdown contract file referenced by `path`.

The body should contain:

- purpose
- phase sequence
- anti-hallucination rules
- failure stop conditions
- verification line

Do not use L3 as a dumping ground for giant personality prompts.

---

## 5. Canonical Registry Schema

Recommended JSON shape:

```json
{
  "schema_version": "tonesoul-skill-capsule/v1",
  "skills": [
    {
      "id": "bounded_skill_id",
      "path": "skills/capsules/bounded_skill_id.md",
      "status": "reviewed",
      "summary": "One-sentence description of the narrow capability.",
      "l1_routing": {
        "name": "Human readable skill name",
        "triggers": ["token a", "token b"],
        "intent": "One-sentence routing explanation.",
        "include_tasks": ["debug", "analysis"],
        "exclude_tasks": ["legal", "medical"],
        "required_surface": ["operator_shell"],
        "blocked_surfaces": ["public_claim_surface"]
      },
      "l2_signature": {
        "execution_profile": ["engineering"],
        "trust_tier": "reviewed",
        "iron_law": [
          "Do not guess hardware facts when direct inspection is still possible.",
          "Stop after bounded retries and classify the failure domain."
        ],
        "json_schema": {
          "type": "object",
          "properties": {
            "target_stack": { "type": "string" },
            "symptoms": { "type": "string" }
          },
          "required": ["target_stack", "symptoms"]
        },
        "requires_tools": ["shell", "apply_patch"],
        "forbidden_tools": ["network_write"],
        "phase_gate": [
          {
            "name": "inspect",
            "success": "A concrete local signal confirms the failure surface."
          },
          {
            "name": "act",
            "success": "The smallest bounded change is applied."
          },
          {
            "name": "verify",
            "success": "The changed path has a concrete validation result."
          }
        ],
        "deterministic_companion": [
          "python scripts/run_specific_probe.py"
        ],
        "do_not_use_when": [
          "The task is creative writing rather than diagnostics.",
          "The required local surface does not exist."
        ],
        "context_budget": {
          "max_matches": 1,
          "max_excerpt_chars": 800
        }
      },
      "anti_bloat": {
        "duplicate_of": [],
        "merge_if_overlap_exceeds": 0.7,
        "sunset_if_unused_days": 180
      },
      "provenance": {
        "source_kind": "internal_distillation",
        "derived_from": [
          "spec/skills/skill_gravity_well_schema.md"
        ],
        "imported_idea": false
      },
      "audit": {
        "review_status": "approved",
        "reviewer_role": "guardian",
        "last_reviewed_at": "2026-04-16T00:00:00+08:00",
        "notes": "Bounded skill; narrow execution envelope."
      }
    }
  ]
}
```

---

## 6. Field Rules

## 6.1 `id`

Rules:

- ASCII slug
- stable
- one job only
- no marketing language

Good:

- `cv_hardware_diagnostics`
- `bounded_release_preflight`

Bad:

- `ultimate_problem_solver`
- `super_architect_mode`

## 6.2 `status`

Allowed values:

- `draft`
- `reviewed`
- `approved`
- `deprecated`
- `disabled`

Runtime recommendation:

- default parser should only admit `reviewed` and `approved`

## 6.3 `trust_tier`

Allowed values:

- `experimental`
- `trusted`
- `reviewed`

Meaning:

- `experimental`: manual or sandbox-only use
- `trusted`: reusable but not yet promoted for broader routing
- `reviewed`: bounded, reviewed, and default-eligible under matching profile

## 6.4 `iron_law`

This is the most important field after routing.

Rules:

- hard rules only
- no generic style advice
- `2-5` items max
- each line must be independently testable or auditable

Good:

- `Stop after 3 repair attempts on the same failing seam.`
- `Do not widen scope beyond the declared target module.`

Bad:

- `Be brilliant.`
- `Think deeply and carefully.`

## 6.5 `phase_gate`

Rules:

- `2-4` stages max
- each stage must define a visible success condition
- no stage may rely on vibes or hidden confidence alone

This is where ToneSoul should absorb the best part of `Asgard`-style discipline.

## 6.6 `deterministic_companion`

Purpose:

- identify the scripts or commands that should do the verifiable parts

Rules:

- reference real commands only
- no arbitrary scripting placeholders once promoted
- if absent, the skill must justify why LLM-only execution is still bounded

## 6.7 `anti_bloat`

Purpose:

- stop registry sprawl before it happens

Rules:

- every skill must declare how duplication is detected
- every skill must declare when it should be merged or retired

This field is mandatory for ToneSoul even though many external skill systems omit it.

---

## 7. Capsule Body Contract

Each capsule markdown file should start with frontmatter compatible with the parser direction:

```yaml
---
name: bounded_skill_id
description: Narrow one-sentence description.
l1_routing:
  name: "Human readable name"
  triggers:
    - "trigger a"
    - "trigger b"
  intent: "One sentence."
l2_signature:
  execution_profile:
    - "engineering"
  trust_tier: "reviewed"
  iron_law:
    - "Hard law 1"
    - "Hard law 2"
  json_schema:
    type: "object"
    properties:
      target_stack:
        type: "string"
    required:
      - "target_stack"
---
```

The markdown body should then use this order:

1. purpose
2. phase sequence
3. stop conditions
4. common failure modes
5. verification

This keeps the capsule human-readable while still machine-discoverable.

---

## 8. Admission Gate

A new skill capsule should not be added unless all of these are true:

1. It solves a recurring narrow task, not a one-off incident.
2. It has at least one clear `do_not_use_when` rule.
3. It has at least one verification path.
4. It does not materially overlap an existing capsule above the merge threshold.
5. Its `iron_law` lines improve boundedness rather than adding generic prompt fluff.

If any of these fail, the capability should remain:

- a one-off work note
- a task-specific runbook
- or a local plan file

---

## 9. Relation To Existing Repo Components

### Compatible with current `skill_parser`

This schema preserves:

- `id`
- `path`
- `l1_routing`
- `l2_signature`

### Stronger than current `skill_parser`

This schema adds:

- `status`
- `iron_law`
- `phase_gate`
- `deterministic_companion`
- `anti_bloat`
- stronger provenance / audit fields

### Relationship to `skill_gravity_well_schema`

Use this schema when the goal is:

- bounded runtime discoverability
- parser-friendly activation
- thin execution contracts

Use the older gravity-well schema as background theory for:

- semantic flow
- attractor logic
- learning lineage

Do not force every future capsule to expose full gravity-well structure if a thinner contract is enough.

---

## 10. Non-Goals

This schema does **not** authorize:

- a giant public skill marketplace
- overlapping mega-skills
- registry entries that act like personas
- hidden governance overrides
- promotional or manipulative capsules disguised as operational skill

---

## 11. Promotion Path

If later ratified, promotion should happen in this order:

1. create the registry path
2. add one parser-compatible pilot skill
3. add duplicate / sunset checks
4. test match resolution against a small request set
5. only then allow wider skill admission

Anything broader than that will recreate context bloat immediately.
