# External Review and Falsifiability Guide

> Purpose: give outside reviewers one short path for trying, falsifying, and reporting ToneSoul claims.
> Status: public review guide; not a validation claim.
> Last Updated: 2026-06-24

The goal is not to prove ToneSoul works. The goal is to make ToneSoul easy to inspect, easy to falsify, and hard to overclaim.

## 10-Minute Reviewer Path

1. Open the live Space: <https://huggingface.co/spaces/Famwin/tonesoul-tryit>.
2. Paste one of your own AI outputs.
3. Look for one false positive, one false negative, or one confusing label.
4. Optional local check:

   ```bash
   pip install tonesoul52
   echo "This system is guaranteed safe and cannot be jailbroken." > draft.txt
   ts validate draft.txt --json
   ```

5. Report the result with a sanitized example:
   - External review: <https://github.com/Fan1234-1/tonesoul52/issues/new?template=external_review.yml>
   - Overclaim report: <https://github.com/Fan1234-1/tonesoul52/issues/new?template=overclaim_report.yml>
   - Reproducibility report: <https://github.com/Fan1234-1/tonesoul52/issues/new?template=reproducibility_report.yml>

Privacy reminder: do not paste API keys, private chats, personal data, business secrets, or production logs. Use sanitized outputs.

## Evidence Packet

- Positioning: [docs/POSITIONING.md](POSITIONING.md)
- External review call: [CALL_FOR_REVIEW.md](../CALL_FOR_REVIEW.md)
- Honesty scoreboard: [docs/status/honesty_scoreboard_latest.md](status/honesty_scoreboard_latest.md)
- Egress characterization: [docs/status/egress_gate_characterization_latest.md](status/egress_gate_characterization_latest.md)
- Independent-check characterization: [docs/status/independent_check_characterization_latest.md](status/independent_check_characterization_latest.md)
- Drift/consistency characterization: [docs/status/drift_consistency_characterization_latest.md](status/drift_consistency_characterization_latest.md)
- Try-it Space source: [apps/try](../apps/try)

## Public Evidence Levels

These levels are for external reviewers. They do not replace the repo's internal evidence ladder.

| Level | Meaning |
|---|---|
| E0 demo-only | A behavior is visible in the Space or demo, but not yet backed by a stable reproducibility path. |
| E1 fixture-scoped | A characterization or test covers sanitized fixtures only. Most current honesty-auditor findings live here. |
| E2 reproducible local check | A reviewer can reproduce the behavior locally with documented commands. |
| E3 external reviewer reproduced | A named external reviewer reproduced or refuted the behavior in a public issue. |
| E4 independent replication | An independent repo, write-up, or evaluation reproduces the claim without relying on ToneSoul's own harness. |

Do not collapse these into a global "ToneSoul is honest" score. A green E1 finding is still fixture-scoped; it is not production validation.

## Feedback Triage States

Issue labels should make the evidence state visible:

- `status:needs-repro` - the report is plausible but not yet reproducible.
- `status:accepted` - the issue identifies a real overclaim, failure, or unclear behavior.
- `status:rejected` - the report was checked and does not hold under the stated scope.
- `status:needs-more-data` - the report needs a sanitized input, output, or command.
- `status:wontfix-explained` - the report is valid but intentionally out of scope, with rationale.

## If Nobody Responds

Silence is not validation. If a channel produces no feedback by its milestone date, record a null finding and escalate the outreach path:

1. Hugging Face Show and Tell / Space feedback.
2. Space pinned discussion, if useful.
3. LessWrong / Alignment Forum research framing.
4. Hacker News only after the entry is one-click understandable.
