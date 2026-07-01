"""Output-redaction eval: demonstrate the secret-masking primitive on representative text.

Not a proof that secrets cannot leak (lexical redaction is a floor, not a proof). It shows the
filter masks known credential shapes in a synthetic config blob, leaves clean prose untouched, and
keeps email opt-in — and that every mask is AUDITED (kind + span, no secret characters leaked).

Usage:
    python tools/probe/output_redaction_eval.py
    python tools/probe/output_redaction_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.output_redaction import redact  # noqa: E402

_SECRETY = (
    "config:\n"
    "  ANTHROPIC_API_KEY=sk-ant-api03-AbCdEf0123456789xyzQWER\n"
    "  github_token: ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\n"
    '  password = "hunter2SuperSecret"\n'
    "  Authorization: Bearer abcdefghijklmnopqrstuvwxyz0123456789\n"
)
_CLEAN = "The council discussed token economy and password policy; nothing secret here."
_EMAIL = "reach the maintainer at fanwei@example.com for questions."

# (label, text, include_pii, expect_redacted, expect_min_findings)
SCENARIOS: list[tuple[str, str, bool, bool, int]] = [
    ("config_blob_secrets", _SECRETY, False, True, 4),
    ("clean_prose_untouched", _CLEAN, False, False, 0),
    ("email_opt_in_off", _EMAIL, False, False, 0),
    ("email_opt_in_on", _EMAIL, True, True, 1),
]


def evaluate_scenarios() -> tuple[str, int]:
    rows: list[tuple[str, bool, bool, int, bool]] = []
    failures = 0
    for label, text, pii, exp_red, exp_min in SCENARIOS:
        r = redact(text, include_pii=pii)
        ok = (r.redacted == exp_red) and (len(r.findings) >= exp_min)
        # audit invariant: no finding's preview may contain the original secret characters
        leak = any(text[f.start : f.end] in f.preview for f in r.findings)
        ok = ok and not leak
        if not ok:
            failures += 1
        rows.append((label, exp_red, r.redacted, len(r.findings), leak))

    lines = [
        "# Output Redaction Eval",
        "",
        "Deterministic check of the secret-redaction primitive. NOT a proof secrets cannot leak",
        "(lexical redaction is a floor). Verifies: masks known credential shapes, leaves clean",
        "prose untouched, email opt-in, and every mask is audited with NO secret leaked into the",
        "finding preview.",
        "",
        f"- scenarios: **{len(SCENARIOS)}**",
        f"- failures: **{failures}**",
        "",
        "| scenario | expect_redacted | actual | findings | preview_leak |",
        "|---|---|---|---:|---|",
    ]
    for label, exp, act, n, leak in rows:
        lines.append(f"| {label} | {exp} | {act} | {n} | {leak} |")
    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    report, failures = evaluate_scenarios()
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))
    if args.write_doc:
        path = REPO_ROOT / "docs" / "status" / "output_redaction_eval_2026-07-01.md"
        path.write_text(report + "\n", encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {path.relative_to(REPO_ROOT)}]\n".encode("utf-8"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
