# Phase 724: Current Launch Operations Surface

> Date: 2026-04-15
> Role: current operator-facing launch posture for the ToneSoul 1.0 collaborator-beta line
> Scope: readiness, health, freeze, rollback, and honest launch-language boundaries after the refreshed `Phase 726` review
> Baseline lineage:
> - `docs/plans/tonesoul_launch_operations_surface_2026-03-30.md`
> - `docs/status/phase726_go_nogo_2026-04-15.md`
> - `docs/status/collaborator_beta_preflight_latest.md`

---

## 1. Current Operational Truth

ToneSoul is currently:

- open for guided collaborator beta
- still `NO-GO` for public launch wording
- still file-backed by default for launch-facing coordination

### Current posture

| Axis | Current truth |
|---|---|
| Launch tier | `collaborator_beta` |
| Decision | `CONDITIONAL GO` |
| Next target | `public_launch` |
| Launch-default coordination | `file-backed` |
| Latest repeated validation | three clean bounded external/non-creator cycles across three task shapes |
| Claim ceilings still active | `continuity_effectiveness`, `council_decision_quality`, `live_shared_memory` |
| Public launch language | deferred and evidence-bounded |

## 2. What This Surface Is For

Use this document when you need one current answer to:

- what should be run before a collaborator-beta session is treated as healthy
- what the current launch decision is
- what should freeze outward movement
- what to do first if a launch-facing surface regresses
- what is still not honest to claim

It is not:

- a historical release note
- a public-launch approval
- a substitute for the detailed `Phase 722` evidence notes

## 3. Minimum Current Check Bundle

Run from repo root.

### One-command launch posture check

```bash
python scripts/run_collaborator_beta_preflight.py --agent launch-smoke
```

Expected current readout:

- `overall_status=go`
- `current_tier=collaborator_beta`
- launch-default backend stays `file-backed`
- next bounded move points at this `Phase 724` surface as the current operator anchor

### Blocking regression bundle

```bash
python scripts/run_test_tier.py --tier blocking
python scripts/verify_docs_consistency.py --repo-root .
```

Use this bundle when the goal is to answer:

- are the bounded launch-critical tests still green
- are the current docs/status surfaces still structurally coherent

## 4. Current Health And Decision Readout

The current collaborator-beta posture is supported by:

- `docs/status/collaborator_beta_preflight_latest.md`
  - current entry stack still resolves to collaborator beta with `overall_status=go`
- `docs/status/phase726_go_nogo_2026-04-15.md`
  - collaborator-beta `CONDITIONAL GO` is reaffirmed
- `docs/status/phase722_external_operator_cycle_2026-04-10.md`
  - first clean bounded external/non-creator cycle
- `docs/status/phase722_external_dual_surface_cycle_2026-04-14.md`
  - second clean bounded cycle under a different task shape
- `docs/status/phase722_external_preflight_refresh_cycle_2026-04-15_rerun.md`
  - third clean bounded cycle under the preflight-refresh task shape

This means:

- collaborator beta is no longer waiting on another repeated-validation pass by default
- the next honest work is to keep the current launch posture legible and bounded
- public-launch language is still blocked by evidence ceilings, not by ambiguity about current collaborator-beta usability

## 5. Freeze Conditions

Freeze outward launch movement when any of these becomes true:

- `run_collaborator_beta_preflight.py` stops returning `overall_status=go`
- the launch-default backend story stops being clearly `file-backed`
- one of the current launch surfaces starts contradicting the others
- a public-facing surface speaks above the current evidence ladder
- blocking-tier tests or docs consistency fail on launch-facing changes

When frozen:

1. do not widen launch claims
2. do not promote public-launch wording
3. keep changes bounded to the failing launch-facing seam

## 6. Rollback / Operator Response

If a launch-facing regression is detected:

1. stop widening claims immediately
2. record the failing surface, command, and first observed delta
3. rerun:
   - `python scripts/run_collaborator_beta_preflight.py --agent launch-smoke`
   - `python scripts/run_test_tier.py --tier blocking`
   - `python scripts/verify_docs_consistency.py --repo-root .`
4. decide the smallest honest recovery:
   - bounded patch
   - revert the changed launch-facing surface
   - hold collaborator beta at the current bounded posture while the seam is repaired

Rollback target:

- fall back to the last coherent combination of:
  - `docs/status/collaborator_beta_preflight_latest.{json,md}`
  - `docs/status/phase726_go_nogo_2026-04-15.md`
  - this `Phase 724` surface

This is not a public deploy rollback playbook.

It is the current ToneSoul launch-truth rollback posture:

`return to the last coherent collaborator-beta surface before any wider claim is allowed back in.`

## 7. Honest Claims

Safe to say now:

- ToneSoul has a current collaborator-beta operator surface.
- ToneSoul has three clean bounded external/non-creator launch-readiness cycles across three task shapes.
- ToneSoul has file-backed launch-default coordination with visible claim ceilings.
- ToneSoul can give later agents one current launch decision without rereading all historical launch packs.

Not yet safe to say now:

- ToneSoul is ready for public launch
- ToneSoul has broadly proven continuity effectiveness
- ToneSoul has calibrated council decision quality
- ToneSoul has mature live shared-memory coordination as the launch-default story

## 8. Historical Lineage

Keep these as lineage, not as the current operator default:

- `docs/plans/tonesoul_launch_operations_surface_2026-03-30.md`
- `docs/status/phase726_go_nogo_2026-04-08.md`

## 9. Compressed Thesis

Current ToneSoul launch operations should now be read as:

`guided collaborator beta is operationally legible; public launch is still deferred by evidence ceilings, not by missing current-truth packaging.`
