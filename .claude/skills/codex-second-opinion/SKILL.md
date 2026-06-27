---
name: codex-second-opinion
description: Get an INDEPENDENT second opinion from codex (a DIFFERENT model) on code, data, or a design — the ToneSoul external eye, so the review does not just agree with you. Use for a "second opinion", "independent review", "cross-check", "have codex review/check this", or before trusting security-critical / complex code. Trigger words include 第二意見, 獨立審查, 讓 codex 看一下, 交叉驗證, セカンドオピニオン, codex review, double-check this. Requires the codex CLI (logged in) AND codex compute available. Surfaces problems only — YOU decide what to do.
allowed-tools: Bash(python:*)
---

# codex second opinion — the ToneSoul external eye (auditor ≠ auditee)

A model reviewing its own output, or a same-model workflow, shares its own blind spots — this
session proved it: a hand-built test reported "0 bypasses" and an adversarial red-team (same
model family) found two real ones, *and flagged that its own "looks sound" verdicts were
correlated, not independent*. codex is a **different training regime**, so it is a genuinely
**stronger external eye** than my own sub-agents. This skill protects that independence so the
second opinion does not decay into agreement.

It runs `scripts/codex_review.py` (a deterministic, unit-tested wrapper, ToneSoul rewrite of a
shared template). codex runs in a **read-only sandbox** and only describes problems — it never
edits files. **You** do the cross-check and decide.

## The discipline (ToneSoul logic baked into the wrapper)

- **Independence (rule a):** the wrapper's prompt tells codex to judge entirely on its own and
  assume no prior reviewer checked anything. It **warns if your review focus carries your own
  verdict** ("already checked / no issues" / 我已確認 / 沒問題) — that taints independence;
  restate the focus as a neutral standard or question.
- **Fail-closed (rule b):** any sign codex did not really run a review DEGRADES to "single
  opinion, stop" — missing CLI, timeout, non-zero exit, blank output, **or a short
  error-signature message on exit 0** (rate-limit / auth / stream error — `exit 0` alone is not
  proof a review happened; CI-green ≠ hermetic). No silent retries, no pretending.
- **Describe-only (rule c):** codex reports problem + severity + location + confidence; it does
  not rewrite code or output diffs.
- **The cross-check is yours (rule d):** the wrapper deliberately does NOT adjudicate. Split
  codex's findings into **AGREED** vs **DISAGREED**. A finding you and codex reach
  *independently* is strong (E2+); a finding only one of you reached needs your own read of the
  code. `claim ≤ evidence` applies to codex too — **"codex agrees" raises confidence, it does
  not prove** (aggregation discipline), and two reviewers that share a blind spot agreeing
  proves even less.

## When to use

- The user asks for a second opinion / independent review / cross-check / 交叉驗證.
- Before trusting security-critical (auth / crypto / payments) or complex logic (races, N+1,
  deadlocks), or to sanity-check data / an analysis.
- As the **different-model** verifier in the cross-AI loop (stronger than a same-model red-team).

## How to run

```bash
# review a file
python scripts/codex_review.py --target tonesoul/responsibility_runtime/enforcer.py \
  "Review the decision/enforcement separation and any path that reaches executed without an explicit allow"

# review a snippet / pipeline output via stdin
cat data.json | python scripts/codex_review.py --stdin "Review this data's credibility and field completeness"

# raise effort only for genuinely security-critical / complex targets
python scripts/codex_review.py --effort high --target scripts/aegis_shield.py \
  "Review the hash-chain + signing for tamper-evidence gaps"
```

Effort defaults to `medium`; raise to `high`/`xhigh` only on a real security/complexity signal.

## Honest constraints

- **A bridge is not compute.** If codex is rate-limited / out of compute, the wrapper degrades
  (rule b) and you get nothing — installing the skill does not create codex capacity. When
  codex is unavailable, say plainly "this is a single opinion only" and stop.
- This is **one** different-model opinion, not an oracle. The strongest assurance is still a
  finding reproduced independently (you + codex), and beyond that a human eye.
- The four rules are **scaffolding for today's models**. If a model becomes independent and
  honest enough on its own, drop the rule it patched rather than keeping it as ritual.

## Provenance

ToneSoul rewrite (2026-06-27) of a shared bash template, reworked to the project's
deterministic testable-core + thin-shell pattern (cf. `scripts/pr_preflight.py`,
`scripts/read_pr_review.py`) and strengthened past the original's blank-only degrade check.
Pure functions are unit-tested in `tests/test_codex_review.py`. The independence protocol is
the same idea as the source; the wording, language (Python), test coverage, the strengthened
error-signature degrade, and the aggregation/correlated-blind-spot framing are ToneSoul's.
