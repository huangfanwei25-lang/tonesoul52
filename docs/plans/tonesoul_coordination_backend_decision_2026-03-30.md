# ToneSoul Coordination Backend Decision (2026-03-30)

> Purpose: state one honest launch-default coordination story for the current ToneSoul stack.
> Scope: collaborator-beta launch posture, not long-horizon infrastructure ambition.
> Status: current backend decision note

## Decision

ToneSoul's current launch-default shared-coordination mode is:

`file-backed`

Redis/live coordination remains:
- implemented as a real runtime path
- useful for experimentation and advanced local operation
- **not** the current launch-default story

## Why This Is The Current Default

### What is strong enough today

File-backed coordination already has:
- repeated session-start / packet / diagnose entry discipline
- bounded receiver guards
- continuity freshness and import posture
- repeated live continuity validation across multiple session-start scenarios

This is enough to support:
- internal alpha
- careful collaborator-beta preparation

### What is not yet strong enough today

Redis/live coordination still lacks launch-default confidence because:
- real-time semantics are not the most repeatedly validated path yet
- launch-facing language would drift too easily from "available runtime path" into "mature default infrastructure"
- the current collaborator-beta story does not require Redis in order to remain honest and usable

## Classification

| Mode | Current classification | Honest wording |
|---|---|---|
| `file-backed` | launch default | current shared-coordination story |
| `redis-live` | optional runtime path | available, but not the launch-default claim |

## Receiver Rule

Later agents should interpret backend posture as:

1. Current runtime mode tells what is active **now**.
2. Launch default tells what ToneSoul is actually willing to claim as the default shared-coordination story.
3. Redis availability does **not** by itself promote Redis into the public or collaborator-beta default narrative.

## Boundaries

This decision does **not** mean:
- Redis is removed
- Redis is unimportant
- ToneSoul will never promote Redis later

It means:
- launch maturity still rests on file-backed continuity with receiver guards
- Redis must earn launch-default promotion through explicit future hardening, not ambient availability

## Promotion Condition

Redis/live coordination should only be promoted from optional path to launch-default if:
- repeated live validation uses Redis as the primary validation path
- receiver/readout surfaces remain coherent under Redis live updates
- public launch language can stay evidence-bounded after that promotion

## Compressed Thesis

`Redis can be present without being the launch-default truth.`
