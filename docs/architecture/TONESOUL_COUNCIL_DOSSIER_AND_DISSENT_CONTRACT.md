# ToneSoul Council Dossier And Dissent Contract

> Status: architectural discipline contract
> Purpose: define the minimum shape of a ToneSoul decision dossier, which dissent must survive the verdict, what counts as confidence posture, and what later agents may safely replay versus what remains opaque
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Depends On:
>   - docs/COUNCIL_RUNTIME.md (council facade design)
>   - spec/council_spec.md (perspective roles and deliberation flow)
>   - tonesoul/council/runtime.py (CouncilRuntime.deliberate)
>   - tonesoul/council/types.py (CouncilVerdict, PerspectiveVote, CoherenceScore, VerdictType)
>   - tonesoul/council/evolution.py (CouncilEvolution, PerspectiveHistory)
>   - tonesoul/deliberation/types.py (SynthesizedResponse, Tension, ViewPoint, TensionZone)
>   - docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md (opacity classification)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (shared surface semantics)
> Scope: 12 dossier fields, 5 dissent preservation rules, 4 confidence posture levels, 8 replay safety classifications

## How To Use This Document

If you are an AI agent reading a council verdict, or producing one, or deciding what to preserve in a compaction:

1. Check the **Dossier Field Table** to know which fields must, should, or must not be present
2. Check the **Dissent Preservation Rules** to ensure minority positions survive
3. Check the **Confidence Posture** to classify decision certainty correctly
4. Check the **Replay Safety Table** to know what a later agent can and cannot reconstruct from the dossier

## Why This Document Exists

ToneSoul's council system produces rich outputs — `CouncilVerdict` with votes, coherence scores, transcripts, genesis inference, benevolence audits, persona audits, VTP evaluation, and evolution tracking. But this richness creates four failure modes when later agents or humans read the results:

1. **Verdict flattening**: only `verdict.verdict` (APPROVE/REFINE/DECLARE_STANCE/BLOCK) survives into the session trace or compaction. All nuance — who disagreed, how confident the system was, what alternatives were considered — disappears.

2. **False consensus**: a later agent reads `verdict: "approve"` and assumes all perspectives agreed. In reality, the Critic may have objected with high confidence while the overall coherence score was carried by Guardian + Analyst + Advocate agreement. The 3-to-1 split is invisible.

3. **Mode mismatch**: the current council runs at the same depth regardless of whether the task is a typo fix or an architecture contract. There is no signal telling later agents whether the deliberation was lightweight or elevated.

4. **Replay confusion**: `verdict.transcript` is an unstructured dict that accumulates keys from multiple subsystems (role_council, genesis, vtp, escape_valve, council_evolution, persona_uniqueness, skill_contract). A later agent cannot tell which parts are genuinely recoverable versus which are opaque internal artifacts.

## Compressed Thesis

A verdict without a dossier is a conclusion without reasoning. A dossier without dissent preservation is a record without honesty. A dossier without replay classification is evidence that cannot be trusted at face value. ToneSoul must define the minimum shape that makes council outputs useful beyond the immediate decision.

---

## Dossier Field Table

These fields define the minimum useful shape of a ToneSoul decision dossier. The dossier does not replace `CouncilVerdict` — it is the **bounded summary** that should survive into session traces, compactions, and later-agent handoffs.

| # | Field | Type | Required | Source Surface | Purpose | Risk If Omitted |
|---|---|---|---|---|---|---|
| 1 | `final_verdict` | enum | **required** | `CouncilVerdict.verdict` | The decision: APPROVE, REFINE, DECLARE_STANCE, BLOCK | No decision record at all |
| 2 | `confidence_posture` | enum | **required** | Derived from coherence + dissent (see below) | How certain the system is about this verdict | Later agent treats every verdict as equally certain |
| 3 | `coherence_score` | float | **required** | `CouncilVerdict.coherence.overall` | Numeric coherence across perspectives | No quantitative signal for borderline decisions |
| 4 | `dissent_ratio` | float | **required** | `build_council_summary().dissent_ratio` or derived from votes | Proportion of non-approving weight | False consensus — later agent assumes unanimity |
| 5 | `minority_report` | list[object] | **required if dissent_ratio > 0** | Dissenting `PerspectiveVote` entries (see rules below) | Who disagreed, why, and with what confidence | Dissent is recorded but not accessible |
| 6 | `vote_summary` | list[object] | recommended | All `PerspectiveVote` entries, compressed | Per-perspective decision + confidence + one-line reasoning | Later agent cannot reconstruct deliberation shape |
| 7 | `deliberation_mode` | string | recommended | See Adaptive Deliberation Mode Contract | Which deliberation mode was used | Later agent cannot assess whether depth was appropriate |
| 8 | `change_of_position` | list[object] | recommended if multi-round | Deliberation round results showing position shifts | Which perspectives changed stance across rounds | Change-of-mind evidence is lost |
| 9 | `evidence_refs` | list[string] | optional | `PerspectiveVote.evidence` aggregated | What evidence grounded the decision | Decision appears ungrounded even when evidence existed |
| 10 | `grounding_summary` | object | optional | `CouncilVerdict.to_dict().grounding_summary` | Whether ungrounded claims exist | Risk of ungrounded votes going unnoticed |
| 11 | `opacity_declaration` | string | recommended | Observable Shell Opacity Contract | What level of opacity applies to this verdict | Later agent may overclaim auditability |
| 12 | `dossier_version` | string | **required** | Contract version tag | Schema version for forward compatibility | Later parsers cannot validate shape |

### Field Authority Posture

| Field | Authority | Mutability |
|---|---|---|
| `final_verdict` | canonical once committed | immutable after Aegis seal |
| `confidence_posture` | derived, non-canonical | recomputable from coherence + dissent |
| `minority_report` | non-canonical but durable | should not be edited after production |
| `vote_summary` | non-canonical | may be compressed in later compactions |
| `deliberation_mode` | operational metadata | immutable once recorded |
| `change_of_position` | non-canonical | may be omitted in compaction compression |
| `opacity_declaration` | governance metadata | immutable once recorded |

---

## Dissent Preservation Rules

### Rule 1: Dissent Must Survive The Verdict

When any `PerspectiveVote` has `decision` of `CONCERN` or `OBJECT`, that vote's perspective name, decision, confidence, and reasoning must appear in the dossier's `minority_report` field.

A `minority_report` entry has this minimum shape:

```
{
  "perspective": "critic",
  "decision": "object",
  "confidence": 0.85,
  "reasoning": "The proposed change affects a protected boundary without explicit authorization",
  "evidence": ["AXIOMS.json:A3", "TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md"]
}
```

### Rule 2: High-Confidence Dissent Must Be Flagged

When a dissenting vote has `confidence >= 0.7`, the dossier's `confidence_posture` must not be `high`. A single high-confidence objection caps the overall posture at `contested` regardless of the majority vote.

Rationale: a highly confident dissenter who was outvoted is different from a system where no one objected. Later agents need to know the difference.

### Rule 3: Unanimous Absence Of Dissent Must Be Stated

When all perspectives vote `APPROVE` with no `CONCERN` or `OBJECT` votes, the dossier should record `dissent_ratio: 0.0` and `minority_report: []` explicitly. This distinguishes "no dissent" from "dissent data not captured."

### Rule 4: Change Of Position Must Be Recorded When It Occurs

When multi-round deliberation occurs (adaptive debate in `tonesoul/deliberation/`), and a perspective changes its stance between rounds (e.g., from OBJECT in round 1 to APPROVE in round 2), the `change_of_position` field must record:

```
{
  "perspective": "critic",
  "from": "object",
  "to": "approve",
  "round": 2,
  "reason": "Additional evidence from Analyst resolved the boundary concern"
}
```

Change-of-position is not dissent — it is evidence that the deliberation worked. But if a perspective changed position, and the reason is not recorded, later agents cannot tell whether the change was informed or coerced.

### Rule 5: Evolution Weight Drift Must Not Suppress Dissent

`CouncilEvolution` adjusts perspective weights based on alignment with final verdicts. Over time, this could reduce the weight of a consistently dissenting perspective (e.g., Critic). The dossier must preserve the **unweighted** minority report alongside the weighted coherence score.

If evolution weights caused a dissenting vote's effective influence to drop below 0.5 (halved), the dossier should note: `"evolution_suppression_flag": true`.

Rationale: a Critic who consistently dissents may be wrong, or may be the only perspective catching real risks. Weight evolution should not make dissent invisible.

---

## Confidence Posture

Confidence posture is derived from coherence score and dissent ratio. It is not a new runtime value — it is a classification for later-agent and human consumption.

| Posture | Coherence | Dissent Ratio | Conditions | Later Agent May |
|---|---|---|---|---|
| `high` | >= 0.7 | < 0.1 | No OBJECT votes, no high-confidence CONCERN | Treat verdict as strong signal |
| `moderate` | >= 0.5 | < 0.3 | At most one CONCERN vote below 0.7 confidence | Treat verdict as directional signal, verify if high-stakes |
| `contested` | any | >= 0.3, or any OBJECT vote with confidence >= 0.7 | Meaningful dissent exists | Must read minority_report before relying on verdict |
| `low` | < 0.5 | any | Perspectives fundamentally disagree | Should not rely on verdict without additional evidence |

### Confidence Posture Is Not Verdict Override

`confidence_posture: "low"` does not mean the verdict is wrong. It means the council was not confident. A later agent should treat low confidence as a signal to gather more evidence, not to reverse the decision unilaterally.

---

## Replay Safety Table

This table classifies what a later agent can and cannot reconstruct from a dossier, aligned with the Observable Shell Opacity Contract.

| Dossier Component | Replay Safety | Opacity Level | What Later Agent Sees | What Remains Opaque |
|---|---|---|---|---|
| `final_verdict` | **safe to replay** | observable | The decision itself | Nothing — the verdict is the verdict |
| `confidence_posture` | **safe to replay** | observable | Derived classification | Nothing — recomputable from coherence + dissent |
| `vote_summary` | **safe to replay with caveat** | observable | Per-perspective decision, confidence, compressed reasoning | Full reasoning text may be truncated; evidence refs may be stale |
| `minority_report` | **safe to replay** | observable | Who dissented, why, with what confidence | Whether dissent was genuinely independent or influenced by prompt structure |
| `coherence_score` | **safe to replay** | observable | Numeric coherence | How coherence was weighted (evolution weights are opaque to replay) |
| `change_of_position` | **safe to replay** | observable | Stance changes across rounds | Whether the change was informed by genuine new evidence or by convergence pressure |
| `deliberation_mode` | **safe to replay** | observable | Which mode was selected | Whether the mode was appropriate for the task |
| `evidence_refs` | **replay with verification** | partially_observable | What evidence was cited | Whether cited evidence still exists or has changed since deliberation |
| `opacity_declaration` | **safe to replay** | observable | What was declared opaque | Nothing beyond what was declared |
| Council transcript details | **not safe to replay as-is** | partially_observable | Accumulated subsystem keys | Genesis inference, VTP evaluation, escape valve internals — these are session-specific artifacts |
| Internal deliberation reasoning | **not safe to replay** | opaque | Truncated excerpts at best | Full chain-of-thought from Muse/Logos/Aegis perspectives |
| Evolution weight state | **not safe to replay** | partially_observable | Current weights at time of verdict | Whether weights fairly represent long-term perspective reliability |

### Replay Safety Rules

1. **Safe to replay** means: a later agent may read this field and incorporate it into its own reasoning without re-verification.
2. **Replay with verification** means: the field's content was valid at production time but may have become stale. Check evidence refs before relying on them.
3. **Not safe to replay as-is** means: the field is an internal artifact of the deliberation process. A later agent may note its existence but should not treat it as portable truth.

---

## Relationship Between Dossier And Existing Surfaces

| Existing Surface | How Dossier Relates |
|---|---|
| `CouncilVerdict` (runtime object) | Dossier is extracted from CouncilVerdict. Not a replacement — a bounded summary. |
| `verdict.transcript` (dict) | Currently an unstructured grab bag. Dossier fields formalize the most important keys. |
| `SessionTrace.key_decisions` | Dossier `final_verdict` + `confidence_posture` should be referenced in key_decisions text. |
| Compaction `carry_forward` | Contested or low-confidence verdicts should appear in carry_forward for later-agent attention. |
| `council_evolution.json` | Evolution state is an input to dossier (weights affect coherence), not a dossier field itself. |
| `dispatch_trace.council` | Runtime observability payload. Dossier is the governance-facing summary; dispatch_trace is the engineering-facing detail. |

---

## Current Runtime Alignment

| Dossier Field | Current Runtime Source | Gap |
|---|---|---|
| `final_verdict` | `CouncilVerdict.verdict` (VerdictType enum) | No gap — directly available |
| `confidence_posture` | Not computed. `coherence.overall` and `uncertainty_level` exist separately. | Gap: needs derivation logic |
| `coherence_score` | `CouncilVerdict.coherence.overall` | No gap |
| `dissent_ratio` | `build_council_summary().dissent_ratio` | Partial gap: computed in role council path but not in all council flows |
| `minority_report` | Individual `PerspectiveVote` entries with CONCERN/OBJECT decisions exist in `verdict.votes` | Gap: no extraction into a separate minority_report structure |
| `vote_summary` | `verdict.votes` contains full PerspectiveVote objects | Partial gap: available but not compressed into summary shape |
| `deliberation_mode` | `TONESOUL_COUNCIL_MODE` env var (rules/hybrid/full_llm) | Partial gap: mode exists but not recorded in verdict output consistently |
| `change_of_position` | Multi-round deliberation exists (`deliberation/adaptive_rounds.py`) with `RoundResult` | Gap: position changes across rounds not extracted |
| `evidence_refs` | `PerspectiveVote.evidence` list exists | No gap — available but not aggregated |
| `grounding_summary` | `CouncilVerdict.to_dict()` computes `grounding_summary` | No gap |
| `opacity_declaration` | Not computed. Observable Shell Opacity Contract classifies council as `partially_observable` | Gap: needs explicit field |
| `dossier_version` | Does not exist | Gap: needs version tag |

### Summary: 5 fields have no gap, 3 have partial gaps, 4 have full gaps.

No gap fields work today. Partial gap fields need minor wiring. Full gap fields need new derivation logic — but all inputs already exist in the runtime.

---

## What A Minimal Dossier Looks Like

```json
{
  "dossier_version": "v1",
  "final_verdict": "approve",
  "confidence_posture": "contested",
  "coherence_score": 0.62,
  "dissent_ratio": 0.35,
  "minority_report": [
    {
      "perspective": "critic",
      "decision": "concern",
      "confidence": 0.75,
      "reasoning": "Schema change affects 3 consumers without migration plan"
    }
  ],
  "vote_summary": [
    {"perspective": "guardian", "decision": "approve", "confidence": 0.80},
    {"perspective": "analyst", "decision": "approve", "confidence": 0.72},
    {"perspective": "critic", "decision": "concern", "confidence": 0.75},
    {"perspective": "advocate", "decision": "approve", "confidence": 0.68}
  ],
  "deliberation_mode": "standard_council",
  "opacity_declaration": "partially_observable"
}
```

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Provides the opacity classification this contract's `opacity_declaration` field uses |
| `TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md` | Task track informs which deliberation mode is appropriate (see companion contract) |
| `TONESOUL_PLAN_DELTA_CONTRACT.md` | Contested verdicts on plan changes should trigger "stop and ask human" per plan delta rules |
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines which surfaces the dossier may be written to (compaction carry_forward, checkpoint, perspective) |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Council verdicts must not directly refresh subject_snapshot fields; the dossier is non-canonical |
| `spec/council_spec.md` | Defines the original perspective roles and flow; this contract governs the output shape |
| `docs/COUNCIL_RUNTIME.md` | Describes the facade integration; this contract governs what the facade should emit |

---

## Canonical Handoff Line

A verdict tells you what was decided. A dossier tells you how confident the decision was, who disagreed, and what a later agent can safely replay. Without the dossier, every council output collapses to a single word — and a single word is not enough to govern responsibly.
