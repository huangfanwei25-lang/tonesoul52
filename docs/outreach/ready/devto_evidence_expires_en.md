# Your CI is green and your status files are lying: evidence rots

> Ready-to-post dev.to draft (2026-07). Post under the owner's account. Tags suggestion:
> #devops #testing #python #softwareengineering. Personalize before posting.

This is not a post about writing more tests. It's about a system with 8,000+ green tests
that rotted in its most load-bearing spot — silently, with every dashboard showing OK.

## An ok=true that had expired

My repo keeps machine-generated status artifacts: JSON files that record "check X ran,
7/7 passed, ok: true." In July, an external audit re-ran one of those checks and found a
live regression — two entrypoint docs had lost required references. The committed status
file still said `ok: true`.

That file wasn't lying. On the day it was generated — March 22 — everything did pass.
It was just old. And every human and AI that walked past it read it as *now*.

A system whose selling point is auditability had audit evidence three and a half months
stale, and nothing anywhere was going to complain.

## Why 8,000 tests didn't help

Tests verify what the code does *now*, on every run. But "when did someone last run that
verifier" is state about your process, not your code — and nobody writes a test for it.

We had an excellent ECG and never looked at the date printed on the report taped to the
wall. (The metaphor breaks down exactly where our problem was: the date *was* printed.
Nobody reads dates on green reports.)

## The fix: make staleness itself fail

One-time cleanup is worthless — three months later you're back in the same swamp. The fix
is structural: a verifier whose only job is watching the age of every status artifact.
Anything that asserts "things are fine now" (`ok` / `overall_ok` / `passed` fields) turns
red after 45 days without regeneration. The rule it encodes:

**An expired ok=true is worse than no ok at all, because it masks live regressions.**

Details that turned out to matter, each learned the annoying way:

- **Future-dated timestamps must fail too.** One typo'd year (2027 for 2026) would
  otherwise make an artifact immune to the check for its whole future window.
- **One non-UTF-8 file must not abort the sweep.** `UnicodeDecodeError` is a `ValueError`,
  not an `OSError` — catch accordingly, judge the rest.
- **The verifier's own outputs are excluded** — auditing them only ever says "fresh"
  and adds noise, not assurance.
- **Committed artifacts must not embed absolute local paths**, or every regeneration from
  a different checkout churns the diff and buries real changes.

First run: 16 stale assertive artifacts. Two days later: zero, and the gate now sits in
the repo healthcheck so the debt can't silently re-accumulate.

## The uncomfortable layer

Writing "we are fine" is an act that manufactures a new kind of lie over time — time
itself does the lying for you. The only defense I know is to stamp an expiry on every
"we're fine" and point something unblinking at the stamp.

Code: `scripts/verify_status_freshness.py` in https://github.com/Fan1234-1/tonesoul52
(Apache-2.0, ~200 lines, steal it). The incident and fix history is public in the repo's
PRs — including the part where the AI collaborator misquoted its own test count and had
to correct the record. That ledger is a story for another post.
