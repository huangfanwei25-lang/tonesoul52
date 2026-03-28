# ToneSoul Context Continuity Adoption Map

> Purpose: translate high-level context-transfer ideas into ToneSoul-native continuity lanes so later agents can preserve structure across sessions, tasks, agents, and models without turning handoff memory into hidden magic.
> Status: active adoption map and implementation-order aid.
> Last Updated: 2026-03-28

---

## Why This Exists

ToneSoul already has:

- packet-first session start
- bounded compaction handoff
- subject snapshot
- delta feed
- claim / checkpoint / release discipline
- council dossier carry surfaces

What it still needed was a compact answer to this question:

`when should context continue, through which surface, and with what authority boundary?`

This map is the answer.

It does **not** introduce a new memory layer by itself.
It translates a broad "context transfer" instinct into ToneSoul-native continuity discipline.

## Core Thesis

ToneSoul should transfer **structured continuity**, not raw cognition.

That means each later session should inherit only what is still load-bearing:

- hot operational state
- bounded carry-forward items
- replay-safe dissent
- stable working identity
- plan deltas

It should **not** inherit:

- hidden thoughts
- full unbounded transcripts
- transient emotions as durable identity
- theory-only claims as runtime truth

## ToneSoul-Native Vocabulary

| External instinct | ToneSoul-native framing | Current surface |
|---|---|---|
| context transfer | context continuity | packet + compaction + delta feed |
| handoff bundle | bounded resumability surface | checkpoint / compaction |
| persona state carry | durable working identity | subject snapshot |
| decision replay | replay-safe council carry | council dossier |
| task continuation | plan delta continuity | `task.md` + compaction `next_action` / `carry_forward` |
| live multi-agent awareness | hot-state coordination | claims + packet + observer cursor |

## Lane 1: Can Land Now

These ideas already fit ToneSoul's current surfaces and naming.

| Continuity idea | ToneSoul-native lane | Current surface | Authority posture | Immediate next step |
|---|---|---|---|---|
| Session handoff continuity | packet-first handoff | `start_agent_session.py`, `r_memory_packet()`, `end_agent_session.py` | active runtime | keep default entry/exit cadence |
| Cross-session next steps | bounded carry-forward | compaction `next_action`, `carry_forward` | non-canonical hot state | keep using compaction instead of inventing a new memo layer |
| Subject working-state carry | durable working identity | `subject_snapshot` | non-canonical but durable | keep refresh bounded below canonical posture |
| Dissent continuity | replay-safe dissent carry | council dossier in traces/compactions | bounded carry surface | use dossier instead of flat verdict-only handoff |
| Task continuation | plan delta continuity | `task.md` + readiness/track discipline + compaction | mixed: canonical plan + non-canonical handoff | keep plan truths in `task.md`, short resumability in compaction |
| Change awareness | since-last-seen continuity | observer cursor + `delta_feed` | active runtime | keep `--agent --ack` flow as default |

## Lane 2: Needs Boundary Contract First

These ideas are useful, but they should not be implemented from instinct alone.

| Continuity idea | Why it is attractive | Why it still needs a boundary | Best ToneSoul lane |
|---|---|---|---|
| Cross-model continuity | lets a new model inherit the same working posture | risks overclaiming equivalence between models with different strengths and blind spots | packet + subject snapshot + council dossier, with model-difference disclaimers |
| Track-aware continuity depth | lets small tasks stay light and system tasks carry more review state | easy to over-burden quick changes with heavy transfer baggage | task-track/readiness discipline |
| Dissent promotion rules | lets repeated minority reports shape later review | can silently turn one critic's pattern into durable truth | council dossier + future review contract |
| Subject refresh beyond `active_threads` | lets preferences or anti-patterns evolve more fluidly | identity inflation risk is high | subject refresh boundary contracts |
| Replay-driven deliberation carry | lets future councils inherit prior dossier structure and open questions | may flatten fresh judgment into stale precedent | council dossier + adaptive deliberation contract |
| Outcome-backed continuity | lets later sessions learn from real downstream effects | false causality risk is high without explicit impact evidence | future outcome / impact lane, not current handoff lane |

## Lane 3: Do Not Touch Yet

These ideas are tempting, but they currently conflict with ToneSoul's honesty and governance posture.

| Temptation | Why ToneSoul should reject it for now |
|---|---|
| Hidden-thought transfer | ToneSoul operates at the observable-shell level; private reasoning cannot be claimed as replay-safe memory. |
| Raw transcript carry as default | This collapses signal and noise together and destroys bounded continuity. |
| Auto-promoting compaction memos into vows | `carry_forward` is temporary resumability, not constitution. |
| Letting theory-only docs rewrite runtime carry rules | Adoption maps and contracts guide implementation; they are not executable truth by themselves. |
| Treating subject snapshot as canonical selfhood | It is durable working identity, not final ontology. |
| Importing an external framework name as first-class runtime vocabulary | ToneSoul should absorb transfer discipline, not outsource its architecture language. |

## Recommended Implementation Order

1. Strengthen session handoff continuity.
2. Strengthen plan delta continuity.
3. Strengthen dissent continuity through dossier use.
4. Add track-aware continuity hints to the control plane.
5. Only then explore cross-model continuity with explicit boundary language.

## Reading Order For This Topic

If the question is "how should usable structure survive into the next session" read:

1. `docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md`
2. `docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md`
3. `docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md`
4. `docs/architecture/TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md`
5. this map

If the question is "may I transfer this field into identity", read the subject-refresh boundary contracts first.

If the question is "may I transfer this dissent or verdict into later review", read the council dossier contract first.

If the question is "should this continuity become canonical", the answer is almost always **no** unless the canonical lane explicitly says so.

## Current Rule

Do not ask:

`how do I transfer everything?`

Ask:

`what should continue, through which surface, for how long, and under what authority boundary?`

That is the ToneSoul version of context continuity.
