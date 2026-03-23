# Memory Subjectivity Review Batch Admissibility Checklist Addendum (2026-03-11)

> Purpose: define the admissibility checklist rendered on the canonical subjectivity review-batch artifact.
> Last Updated: 2026-03-23

## Why This Addendum Exists

The branch already updated the official review policy to require
`axiomatic admissibility` before `approved`.

That created a practical follow-up question:

where should that requirement become visible to the operator first?

This phase chooses one answer explicitly:

the canonical operator surface is the review batch artifact.

Not the replay seam.

Not the single-record receipt.

Not the group-settlement receipt.

## Why Review Batch Is The Right Surface

`review batch` is the place where the branch already asks:

- what deserves attention next
- what should likely be `rejected`
- what should likely be `deferred`
- what might deserve manual review

That makes it the right semantic altitude for a checklist.

At that layer, `axiomatic admissibility` still functions as reviewer aid.

If pushed down into apply/replay receipts too early, it becomes an after-the-fact
annotation rather than a real aid to judgment.

## What This Phase Adds

Each `review_group` now exposes:

- `axiomatic_admissibility_checklist`

That checklist is intentionally read-only and prompt-like.

It includes:

- `gate_name`
- `required_for_approved`
- `gate_posture`
- `focus`
- `risk_tags`
- `questions`
- `operator_prompt`

The batch summary also now exposes:

- `admissibility_gate_posture_counts`
- `admissibility_focus_counts`

And the markdown artifact now renders:

- `## Admissibility Gate Counts`
- `## Admissibility Focus Counts`
- per-group admissibility posture, risk tags, and operator prompt

## What This Phase Does Not Do

This phase does not:

- write admissibility fields into `ReviewedPromotionDecision`
- mutate replay semantics
- introduce an automatic admissibility classifier
- reinterpret group review as an approval surface

It stays exactly where it should:

review preparation.

## Design Consequence

The branch now has three distinct layers for this topic:

- policy says admissibility is required
- review batch shows how to ask the admissibility questions
- apply/replay still records the chosen decision without pretending to have
  auto-solved admissibility

That is the correct boundary for now.
