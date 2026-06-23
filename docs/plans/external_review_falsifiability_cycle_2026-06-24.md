# ToneSoul 12-Week External Review and Falsifiability Cycle

> Status: plan for GitHub milestones + issues.
> Last Updated: 2026-06-24
> Scope: external inspectability and falsifiability; no new detector, dashboard, or engine.

## Core

ToneSoul is entering an exposure cycle, not an expansion cycle.

The goal is not to prove ToneSoul works. The goal is to make ToneSoul easy to inspect, easy to falsify, and hard to overclaim.

This cycle should expose:

- whether the repo is understandable to outside reviewers;
- whether the Space and CLI are reproducible enough for review;
- whether public claims are stronger than evidence;
- whether reviewers know how to refute or report a confusing result;
- whether the evidence packet supports the current public posture.

## Milestones

| Milestone | Due | Goal |
|---|---:|---|
| M1 Inspectable Front Door | 2026-07-08 | A stranger can try, understand, and report a falsifiable issue in 10 minutes. |
| M2 Feedback Intake or Null Finding | 2026-07-29 | First feedback is triaged, or silence is recorded as a null finding and channels escalate. |
| M3 Reviewer-Grade Evidence Packet | 2026-08-19 | Space, CLI, status artifacts, and evidence links form a reviewer-grade packet. |
| M4 Direction Decision | 2026-09-16 | Choose tool productization, research evidence, or maintenance-only restraint. |

## Guardrails

- The first goal is external review and falsifiability, not validation, product growth, or new capability.
- Keep Discussions disabled until the M4 decision; use Issues as the first feedback intake.
- Do not create a Project Board in this cycle.
- Do not add new detectors, dashboards, engines, or benchmark families unless M4 explicitly chooses that direction.
- Describe output gates as lexical-only / paraphrase-permeable.
- Do not reintroduce misleading claims that advertise jailbreak resistance, truth-oracle behavior, morality-compiling, deployment-grade guarantees, strongest-tier enforcement beyond evidence, or the inverse wording of `lexical-only / paraphrase-permeable`.
- Separate demo behavior, fixture-scoped findings, local reproducible checks, external reviewer feedback, and unsupported claims.

## No-Feedback Contingency

Silence is not validation. If no external reviewer responds by a milestone date, record that null result and escalate channels:

1. Hugging Face Show and Tell / Space feedback.
2. Space pinned discussion, if useful.
3. LessWrong / Alignment Forum research framing.
4. Hacker News only after the entry is one-click understandable.

## Evidence Levels For Reviewers

Use `docs/EXTERNAL_REVIEW.md` for the public-facing definitions:

- E0 demo-only
- E1 fixture-scoped
- E2 reproducible local check
- E3 external reviewer reproduced
- E4 independent replication

These levels are reviewer-facing shorthand. They do not replace the repo's internal evidence ladder, and they do not compose into a global system validation.
