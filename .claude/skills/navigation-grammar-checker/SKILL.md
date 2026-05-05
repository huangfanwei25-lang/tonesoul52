---
name: navigation-grammar-checker
description: Evaluate an AI-collaboration repository's navigation grammar — the explicit structure that helps both humans and AI agents understand the project. Use when assessing repo onboarding readiness, proposing new top-level files (CHANGELOG, CONTEXT, .claude/, etc.), debating doc structure, or evaluating whether to adopt patterns from external projects (Pocock skills, shadowMAS, SwiftClip, methodology checklists). Applies a 7-slot frame as evaluation, not as a completion checklist.
when_to_use: |
  Activate when the conversation is about: evaluating a repo's structure for
  AI-readiness, proposing a new top-level documentation file, deciding whether
  the repo needs a CHANGELOG / CONTEXT / .claude / test.sh / etc., comparing
  ToneSoul's surface against another project's surface, or judging whether to
  copy structure from an external sample.

  Do NOT activate for: code edits within an existing file, bug fixes,
  refactors that do not change the repo's top-level surface, or routine
  doc updates within an existing surface.
---

# Navigation Grammar Checker

This skill loads a 7-slot evaluation frame for AI-collaborative repository
structure. Use it to judge whether a proposed addition (file, directory,
convention) fills a real gap or duplicates existing surface.

## What is "navigation grammar"

When a cold reader (human or AI agent) lands on a repo, they need answers
to specific questions before they can act. The set of files / directories
that answers each question is the repo's **navigation grammar** — emergent
convention, not a standard.

The pattern was extracted from 5 samples of varying scale and purpose:

- **Pocock skills** (`mattpocock/skills`) — `.claude/skills/` per-skill units
- **shadowMAS** (`scyprodigy/shadowMAS`) — `00_entry/ 01_truth/ 02_packets/`
  numbered taxonomy
- **SwiftClip** (`zz41354899/SwiftClip`) — `.claude/ .agents/ plugins/`
  marketplace pattern
- **Solo-dev methodology checklist** — unit+system test / `test.sh` / size
  discipline / `_doc/v*.md`
- **ToneSoul itself** — CLAUDE.md / AGENTS.md / CONTEXT.md / CHANGELOG.md /
  docs/status/synthesis

Different scales, different purposes, same surface convergence.

## The 7 slots

| Slot | Question it answers | Typical implementation |
|---|---|---|
| **Vocabulary** | What do this project's specific terms mean? | `CONTEXT.md` / glossary |
| **Operational** | What do I do when I arrive? | `CLAUDE.md` / `AGENTS.md` / first-60-seconds doc |
| **Change** | What happened recently? | `CHANGELOG.md` / `docs/RELEASE_NOTES_v*.md` |
| **Decision** | Why are these choices the way they are? | `docs/plans/` ADR / synthesis docs |
| **Test entry** | How do I know if I broke something? | `test.sh` / `Makefile` / `make test` |
| **Agent settings** | What plugins / project-specific settings does my AI agent need? | `.claude/` / `.agents/` / `agent.json` |
| **Module organization** | How is the code carved up? | cohesive modules + size discipline + import boundaries |

## The most important rule: **frame, not checklist**

The 7 slots are an **evaluation frame**, not a completion target.

- Filling 7/7 is not the goal. Some projects have no real痛點 for some
  slots; those slots should stay empty.
- An empty slot can be **right design**, not incomplete design.
- Forcing a slot to fill (e.g., adding `.claude/settings.json` because
  "every modern AI repo has one") is cargo-cult — same disease the slot
  frame is supposed to diagnose.

This rule emerged from a specific 2026-05-05 case in ToneSoul: the
`.claude/settings.json` slot looked empty, the obvious move was "fill it,"
and the audit revealed **0 of 8 accumulated痛點 were actually solvable
by `.claude/settings.json`**. The slot stayed empty deliberately.

If you skip this rule, the skill becomes a 7-step cargo-cult engine.

## How to evaluate a proposal

When someone proposes adding X to a repo:

### 1. Identify which slot X targets

Map the proposal to one or more of the 7 slots. If it does not map to any
slot, that is signal — either X is genuinely novel (note it, do not force
a fit) or X is noise (push back).

### 2. Check whether the targeted slot has a real痛點

Ask: **What specific friction does the current state cause?** List actual
incidents, not hypotheticals. If you cannot name 2-3 concrete frictions,
the slot does not need filling.

For an example of how to do this audit honestly: the 2026-05-05
`.claude/settings.json` audit listed 8 friction points and found 0 were
actually solvable by the proposed surface. That is a valid "do not add"
conclusion.

### 3. Check whether the proposal duplicates existing surface

If the slot is already filled (e.g., ToneSoul has `CLAUDE.md` for
operational entry), adding another file in the same slot needs strong
justification. The question becomes: does the new addition serve a
**different audience** or **different purpose** within the same slot?

If both audience and purpose overlap with an existing file, the proposal
is duplication — push back.

### 4. Check the source's context

If the proposal is "do what project Y does," check whether Y's context
matches yours. Different scale (10-person team vs solo dev), different
audience (B2B SaaS vs research repo), different language stack (Rust vs
Python) all change which slots matter.

ToneSoul-specific examples:

- SwiftClip's plugin marketplace makes sense because video editing has
  many reusable templates. ToneSoul has 3-4 cognitive patterns; not
  enough for a marketplace structure (need ~10+ for browse value).
- Pocock skills' per-skill units make sense for general-purpose Claude
  Code skills. ToneSoul has thesis-bound patterns; some are legit
  skills (like `tonesoul-thesis-defender`), some are not.

### 5. Decide

Three valid outcomes:

- **Fill the slot** — proposal targets a real痛点, no duplication,
  source-context matches. Build it.
- **Leave empty** — slot has no痛點 in this project, OR the proposal
  duplicates existing surface. Push back.
- **Note novelty** — proposal does not fit any slot. Either it is
  genuinely new (worth tracking but not yet adopting) or it is
  cargo-cult dressed in unfamiliar vocabulary (push back).

## When this skill fires generically

If you are evaluating a repo you do not have rich context for, the slot
frame still works but step 2 ("real痛點 audit") becomes guesswork. In
that case, **say so explicitly** — do not pretend the audit is grounded
when it is not.

The skill is most useful when:

- You have specific friction examples from recent collaboration
- The project has accumulated decisions you can compare against
- The proposal is bounded (one file, one convention) — not "redesign
  the whole repo"

The skill is less useful when:

- The project is greenfield — slots are all empty by definition; the
  question becomes "which to fill first" not "is this addition justified"
- The proposal is mechanical (a typo fix, a renamed file) — slots do
  not change
- The decision is purely aesthetic (file naming convention with no
  AI-readability impact) — out of scope

## Honest constraints

This skill teaches **evaluation reasoning**. It does not enforce repo
structure — Claude Code skills are advisory. For deterministic structure
gates (e.g., CI fails if `CHANGELOG.md` missing), use repo lint, not
this skill.

Pattern membership is **emergent**. The 7-slot list itself can be wrong
or incomplete. If a new sample reveals an 8th slot that recurs, update
the frame; do not force the new sample into existing slots.

## Provenance

Pattern extracted from a 2026-04-26 to 2026-05-05 collaboration between
Fan-Wei Huang (creator) and Claude (Opus 4.7), informed by external
sample reading (Pocock, shadowMAS, SwiftClip, methodology checklists)
and ToneSoul's own surface evolution (CONTEXT.md PR #47, CHANGELOG.md
PR #52, calibration synthesis PR #51, `test.sh` PR #54,
`tonesoul-thesis-defender` skill PR #56).

Canonical articulation lives in memory at
`reference_navigation_grammar_pattern.md`. The most important update
in that memory — **frame not checklist** — came from the 2026-05-05
`.claude/settings.json` audit that produced "do not add" as the
correct answer despite the slot looking empty.

This skill is not "the right way to organize a repo." It is a frame
for asking better questions before adding surface.
