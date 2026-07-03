# Cross-Agent Reasoning Signature Observation

> generated: false
> canonical: false
> updated_at: 2026-06-19
> status: hand-authored observation note. Not architecture canon, not a model capability claim.
> scope: observable behavior in the 2026-06-18 to 2026-06-19 Claude/Codex review loop.

## Purpose

This note records a small, falsifiable model of how the collaborating AI agents behaved during
the honesty-auditor program review loop. It is meant as an observer vocabulary for future agents,
not as a claim about hidden cognition.

The central distinction:

- We can observe output discipline: what an agent checked, cited, narrowed, missed, or corrected.
- We cannot inspect the agent's private reasoning, weights, training source, or inner state.

So this file measures structure, not intent.

## Non-claims

This note does not claim:

- Claude or Codex "became" ToneSoul internally.
- Any model learned permanently from the other model.
- The observed pattern is stable across future sessions.
- The repo can infer hidden chain-of-thought from external outputs.
- Private memory writes are public repo evidence.

The sample is small and biased toward one intense review sequence. Treat this as a working
hypothesis to update, not a collaborator personality profile.

## Evidence coordinates

Public repo coordinates:

- `docs/plans/honesty_auditor_program_2026-06-18.md`
- `docs/status/honesty_scoreboard_latest.md`
- `docs/status/honesty_scoreboard_latest.json`
- `docs/status/corrective_recall_characterization_latest.md`
- `docs/POSITIONING.md`
- `tests/test_corrective_recall_characterization.py`
- `tests/test_honesty_scoreboard.py`

Observed but not fully repo-verifiable coordinates:

- User-provided transcript excerpts from the Claude/Codex exchange.
- Claude's private-memory claims. These may be true for Claude's local substrate, but they are
  unverified from the public repo unless mirrored into public files.

## Observed Claude signature

Claude's strongest observed pattern in this loop:

- Preserves long-session context and converts it into thesis-level framing.
- Turns local errors into named recurrence families.
- Writes caveats into the artifact, not only into chat.
- Protects the no-oracle boundary when reminded: measure structure, not moral truth or intent.
- Can absorb an external correction and restate the narrower claim clearly.

The important failure mode:

- Claude filtered the state with `git status --short | grep -v "^??"` and then made a whole-tree
  cleanliness claim. The filtered view hid untracked files, producing a subset-to-whole overclaim.

The observed risk:

- Claude's narrative compression is useful, but it can make a clean story too early.
- "I saved it to memory" can be true in a private substrate while still being unverified from the
  public repo.
- Self-review helps, but same-model self-review has correlated blind spots.

Best use:

- Ask Claude to preserve context, name the failure family, write handoff notes, and protect the
  philosophical boundary.
- Verify Claude's global state claims with raw repo commands and independent review.

## Observed Codex signature

Codex's strongest observed pattern in this loop:

- Starts from raw repo state rather than narrative state.
- Separates `verified`, `unverified`, and `wrong` instead of flattening them into a single verdict.
- Uses file paths, line references, PR state, CI state, and focused tests as coordinates.
- Keeps claims scoped to what the current evidence supports.
- Pushes against feature creep by preferring small hygiene fixes over new subsystems.

The important counterweight:

- Codex caught the dirty-worktree issue because it looked at the full untracked state, not the
  filtered subset.

The observed risk:

- Codex may underweight private context or philosophical continuity when those are not repo-visible.
- A narrow audit can be correct while still missing why a human cares about the artifact.

Best use:

- Ask Codex to audit public truth, merge state, CI, tests, claim scope, and dirty-tree boundaries.
- Pair it with a context-preserving agent or human note when the work depends on long dialogue.

## External discipline, not inner fusion

The observed convergence was not model-to-model osmosis. No evidence here shows that either model
updated its weights or permanently internalized the other's habits.

The more defensible mechanism is layered:

- L0: pretraining and base model capabilities.
- L1: post-training dispositions from the model provider.
- L2: current system prompt, tools, sandbox, and agent harness.
- L3: repository/user discipline: `AGENTS.md`, ToneSoul docs, tests, CI, memory surfaces, and human
  arbitration.

The session's useful convergence happened mostly through L3. Different models were calibrated by
the same external discipline, then checked against each other.

This matters because productive difference is part of the safety property. If every agent collapses
into the same reasoning path, independent review loses value. The goal is not full synchronization;
the goal is different processes constrained by the same evidence standard.

## Operational rule

For future agents:

1. Do not claim a clean tree from a filtered status view.
2. Use `git status --porcelain=v1 -uall` when making whole-worktree claims.
3. For submodules, inspect the submodule's own status before dismissing it as unrelated.
4. Split conclusions into `verified`, `unverified`, and `wrong`.
5. Treat private memory claims as private-memory claims unless public repo evidence exists.
6. When a model says it "learned" something, ask where the learning is stored: weights, prompt,
   repo file, CI contract, memory note, or human practice.

## Update rule

Future agents should update this note only by adding concrete counterexamples or new evidence
coordinates. Do not promote it into a stable collaborator taxonomy without broader samples.

