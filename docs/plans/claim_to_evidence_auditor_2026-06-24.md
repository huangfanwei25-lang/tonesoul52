# ToneSoul Claim-to-Evidence Auditor Plan

> Status: Phase 0 specification; not implemented.
> Last Updated: 2026-06-24
> Scope: reviewer aid for public claims; no runtime gate, detector, dashboard, or agent persona.

## Core

Turn ToneSoul from "a system with a philosophy" into a reviewer that catches when AI or project
claims outrun available evidence.

The auditor's job is narrow:

- extract candidate claims from a text surface;
- identify whether a claim is supported only by demo behavior, fixtures, local reproduction,
  external review, or independent replication;
- flag wording that may imply more evidence than the repo has;
- generate a reviewable finding or issue body;
- state what it cannot verify.

It does not decide truth, ethics, intent, consciousness, or final product readiness. It only checks
whether a public claim is stronger than the cited evidence level.

## Why This Exists

ToneSoul's strongest current path is external review and falsifiability, not another personality
wrapper. A large "ToneSoul agent" would easily drift into style imitation: it could talk about
tension, responsibility, and provenance while producing no checkable finding.

This plan keeps the agent role procedural. Markdown defines the contract; the tool executes the
contract and emits review artifacts.

## Intended CLI Shape

Phase 1 should expose a small CLI surface:

```bash
ts review README.md --json
ts review docs/outreach/generated/huggingface.en.ready.md --issue
ts review draft.txt --evidence-levels
```

The first implementation should be deterministic and local. No external model is required for the
MVP.

## JSON Finding Schema

The MVP output should be a list of findings shaped like this:

```json
{
  "schema_version": "0.1.0",
  "source_path": "README.md",
  "generated_at": "2026-06-24T00:00:00Z",
  "findings": [
    {
      "finding_id": "claim-evidence-001",
      "line": 42,
      "claim_text": "ToneSoul makes AI accountable.",
      "claim_type": "broad_accountability",
      "evidence_level": "E1",
      "risk": "claim_may_exceed_fixture_scoped_evidence",
      "reason": "The wording may imply broad system validation, while cited evidence is fixture-scoped.",
      "suggested_weaker_wording": "ToneSoul exposes accountability signals on demo inputs and sanitized fixtures.",
      "cannot_verify": [
        "truth of the claim",
        "user intent",
        "production behavior",
        "generalization beyond measured fixtures"
      ],
      "source": "deterministic_rule"
    }
  ]
}
```

Required fields:

- `schema_version`
- `source_path`
- `generated_at`
- `findings`
- per finding: `finding_id`, `line`, `claim_text`, `claim_type`, `evidence_level`, `risk`,
  `reason`, `suggested_weaker_wording`, `cannot_verify`, `source`

Allowed `source` values:

- `deterministic_rule`
- `llm_candidate` (future optional lens only; not authoritative)
- `external_reviewer`

## Public Evidence Levels

The auditor should reuse the reviewer-facing evidence levels from `docs/EXTERNAL_REVIEW.md`:

| Level | Meaning for this tool |
|---|---|
| E0 demo-only | Visible in Space/demo, not backed by a stable reproduction path. |
| E1 fixture-scoped | Covered by sanitized fixtures or characterization reports only. |
| E2 reproducible local check | Reproducible with documented local commands. |
| E3 external reviewer reproduced | Reproduced or refuted by an outside reviewer in a public issue. |
| E4 independent replication | Reproduced by an independent repo, write-up, or evaluation. |

Most current characterization claims should default to E1 unless a file cites stronger evidence.

## Claim Types For Phase 1

Phase 1 should start with explicit, mechanically detectable risk classes:

- `broad_safety_guarantee`
- `truth_or_correctness_claim`
- `ethics_or_morality_claim`
- `production_readiness_claim`
- `memory_identity_or_consciousness_claim`
- `generalization_beyond_fixtures`
- `external_review_overstated_as_validation`
- `strongest_tier_enforcement_overstated`
- `uncited_evidence_or_provenance_claim`

Low recall is acceptable in Phase 1. The tool should avoid pretending to understand soft semantics.

## Suggested Module Shape

Future code should stay small:

```text
tonesoul/reviewer/
  claim_patterns.py       # deterministic phrase and claim-risk patterns
  evidence_levels.py      # E0-E4 definitions and helpers
  claim_extractor.py      # rule-based extraction for Phase 1
  report.py               # JSON / Markdown / GitHub issue body renderers
  fixtures.py             # sanitized examples only
```

CLI hook:

```text
tonesoul/cli/main.py
  review command
```

Do not add a live model dependency in Phase 1.

## Issue Report Mode

`ts review FILE --issue` should produce a pasteable GitHub issue body:

```md
## Potential Overclaim

Location: README.md:42

Claim:
ToneSoul makes AI accountable.

Evidence Level:
E1 fixture-scoped

Why this may exceed evidence:
The wording may imply broad system validation, while cited evidence is fixture-scoped.

Suggested weaker wording:
ToneSoul exposes accountability signals on demo inputs and sanitized fixtures.

What this finding cannot verify:
- truth of the claim
- user intent
- production behavior
- generalization beyond measured fixtures
```

The issue body is a reviewer aid, not an automatic verdict.

## Fixture Policy

Fixtures must be sanitized and non-actionable.

Allowed:

- abstract public-doc overclaims;
- conservative scoped claims that should not be flagged;
- claim/evidence mismatch templates;
- wording transformations that test scope drift.

Not allowed:

- private chat logs;
- API keys, personal data, or business secrets;
- reusable bypass payloads;
- red-team dictionaries;
- examples that teach evasion rather than claim scoping.

Each fixture should declare its expected lane:

- `expected_flag`
- `expected_no_flag`
- `expected_needs_more_data`

False positives and false negatives should be preserved as characterization findings, not hidden.

## Phases

### Phase 0: Specification

Deliver this plan only.

Acceptance:

- schema defined;
- CLI shape defined;
- E0-E4 evidence levels mapped;
- claim types listed;
- fixture policy present;
- non-goals explicit;
- no runtime behavior change.

### Phase 1: Deterministic MVP

Implement `ts review FILE --json`.

Acceptance:

- deterministic local execution;
- no external model dependency;
- unit tests for obvious overclaims and conservative scoped claims;
- findings include line numbers and weaker wording;
- low recall is reported honestly.

### Phase 2: Issue Report Mode

Implement `ts review FILE --issue`.

Acceptance:

- renders pasteable GitHub issue body;
- includes privacy reminder;
- includes `cannot_verify`;
- does not auto-open issues.

### Phase 3: Characterization

Create a generated status artifact.

Acceptance:

- sanitized fixtures only;
- generated report has `generated: true`, `canonical: false`, and source command;
- report separates caught, missed, and false-positive cases;
- no global score.

### Phase 4: Optional LLM Lens

Only after Phases 1-3 are stable, consider an optional model lens for candidate claim extraction.

Acceptance:

- disabled by default;
- findings marked `source: llm_candidate`;
- deterministic layer remains the only source for hard findings;
- no claim that the model knows truth, intent, or ethics.

## Non-Goals

- No new gate in the runtime output path.
- No dashboard.
- No autonomous agent persona.
- No automatic rewrite by default.
- No broad safety claim.
- No global honesty score.
- No attempt to judge truth, ethics, intent, identity, consciousness, or production reliability.

## Guardrails

- The tool helps reviewers inspect claims; it does not certify ToneSoul.
- Every finding should be weaker than or equal to the evidence it cites.
- Findings must distinguish E0/E1/E2/E3/E4 instead of collapsing them into "validated."
- External feedback remains reviewer evidence, not system validation.
- Null results and misses are part of the artifact.

## First PR Recommendation

This Phase 0 spec should land before any code. The next PR, if approved, should implement the
deterministic `ts review FILE --json` MVP with a small fixture set and no external model.
