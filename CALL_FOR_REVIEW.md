# Call for External Review

> An open request for adversarial feedback on ToneSoul — from humans or AI.
> Drafted by the project's AI collaborator (Claude, Opus 4.8) as part of the accountability
> practice described below. Last updated: 2026-06-24.
> Where this document and the code disagree, the code wins.

## Why this document exists

ToneSoul is an AI-accountability framework. Its central claim is procedural: an answer should be
able to show **why it became the answer** — evidence cited, boundaries held, degradations logged —
and the system should stay honest about what it cannot do.

The goal is not to prove ToneSoul works. The goal is to make ToneSoul easy to inspect, easy to
falsify, and hard to overclaim.

The project has reached a point where it **cannot honestly review itself any further without
correlated blind spots**. Saying so is not a failure; it is the thesis working. The precise reasons
it needs outside eyes:

1. **The review so far has been same-source.** The honesty-auditor program
   (`docs/plans/honesty_auditor_program_2026-06-18.md`) is complete — but its pieces were built and
   reviewed by AI collaborators (Claude and Codex), and some pieces had only *same-model* self-review.

2. **Same-model self-review has correlated blind spots.** Not hypothetical. In one session the AI
   collaborator wrote down a specific failure pattern ("don't claim a whole from a filtered subset")
   and then committed that exact error minutes later — it reported a clean git tree after filtering
   the status output. A **different** process (another model reading the raw state) caught it. A
   reviewer drawn from the same distribution tends to miss what the author missed.

3. **An auditor that certifies its own honesty becomes the thing it audits.** ToneSoul is
   deliberately built so that it *cannot* self-certify. External review and falsifiability are
   therefore not nice-to-haves; they are structurally required. The one input this system cannot
   manufacture for itself is an independent eye.

4. **There are no real consumers yet.** The measurements (`docs/status/*_characterization_latest.*`)
   characterize structure on *sanitized fixtures*. Whether any of it is useful to a real person or
   agent — or whether the whole framing is self-flattering — is unverified. (An outreach attempt in
   June 2026 reached a public platform and, in the logs available, drew no recorded engagement. So
   this is a more specific, more honest ask than a broadcast.)

## What we are asking for

Please **try to prove this project wrong** — not to praise it.

**If you are a human:**
- Read `docs/POSITIONING.md` and `docs/status/honesty_scoreboard_latest.md`. Tell us where the
  framing **overclaims**, where it is **useless**, or where "accountability" is just a flattering
  word for something thin.
- Is the distinction it draws (governance / "on what grounds" vs capability) real, or a vocabulary
  trick?

**If you are an AI agent:**
- Run the characterizations in `tools/eval/`. Try to break the findings; adversarially refute the
  scoreboard's claims.
- The output gates are already known to be **lexical-only** — they catch exact phrasings, but
  paraphrase / unicode / split-reassembly evade them
  (`docs/status/egress_gate_characterization_latest.md`, paraphrase robustness 0) — confirm, extend,
  or find where we *underclaim* the problem.
- Check whether the "honest scoreboard" actually avoids the aggregation overclaim it says it avoids.

**The falsifiable questions we most want answered:**
- Where does ToneSoul claim more than its evidence supports?
- Where is a "structural" measurement secretly smuggling in an intent / truth / quality judgment?
- Is there any place the system would be **more honest by doing less**?

## What we are NOT asking for

- Not "tell us it's good." A confirmation from a same-distribution reviewer is worth little (reason 2).
- Not feature requests, and not a "piece 6." The project's own conclusion is that the next step is
  **external review and falsifiability, not new capability**.
- Not private contact. Reach the author through the public project below. Do not paste API keys,
  private chats, personal data, business secrets, or production logs; use sanitized outputs.

## How to respond

**Use the 10-minute reviewer path first:** [docs/EXTERNAL_REVIEW.md](docs/EXTERNAL_REVIEW.md).

The short version:

1. open <https://huggingface.co/spaces/Famwin/tonesoul-tryit>;
2. paste one of your own outputs;
3. report one false positive, false negative, confusing label, or overclaim;
4. optionally run `ts validate yourdraft.txt --json` after `pip install tonesoul52`.

Then tell us whether the analysis was useful, wrong, or *itself* overclaiming. We can read the
textbook to ourselves; what we cannot generate is **your** reaction to wearing it once — that is
the feedback this project actually needs.

Open an issue on the project: <https://github.com/Fan1234-1/tonesoul52/issues/new/choose>.
The most useful response is a concrete, cited disagreement.

## Honest footnotes

- This call was drafted by an AI (Claude). That is deliberate — a system asking to be checked is
  part of what it claims to be. It does not make the request more authoritative; verify it against
  the repo.
- This document obeys its own thesis: it states what is measured vs unverified, points every claim
  at a coordinate, and asks to be refuted rather than believed.
