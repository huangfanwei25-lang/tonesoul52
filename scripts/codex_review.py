"""Independent second-opinion via a DIFFERENT model (codex) — ToneSoul external-eye style.

ToneSoul logic (auditor != auditee): a model reviewing its own output, or a same-model
workflow, shares its own blind spots. codex is a different training regime, so it is a
*stronger* external eye than my own sub-agents — but it is still ONE opinion, not an oracle:
- claim <= evidence applies to codex's findings too (it can be wrong / hallucinate);
- "codex agrees" != "verified" (aggregation discipline: agreement raises confidence, it does
  not prove — and if two reviewers share blind spots, agreement proves even less);
- a finding BOTH you and codex reach independently is strong; a finding only one reached needs
  your own judgment.

Fail-closed: any sign codex did not really run a review (missing CLI / timeout / non-zero /
blank OR a short error-signature message) DEGRADES to "single opinion, stop" — never pretend a
failed call was a review. This is the CI-green != hermetic / half-success-is-not-success
discipline: exit 0 alone is not proof a review happened.

This is a ToneSoul rewrite of a shared bash template — reworked to the project's deterministic
testable-core + thin-shell pattern (cf. scripts/pr_preflight.py, scripts/read_pr_review.py),
with the degrade detection strengthened past the original's blank-only check. The four rules
are scaffolding for today's models; drop a rule if a model becomes independent enough on its
own rather than keeping it as ritual.

The pure functions (independence_warning / build_prompt / classify_outcome) take no I/O and are
unit-tested; only run_codex() touches the subprocess. codex runs in a READ-ONLY sandbox and
only describes problems — it never edits files. YOU do the agreed/disagreed cross-check; this
module deliberately does not.
"""

from __future__ import annotations

import re
import subprocess
from typing import List, Optional, Sequence, Tuple

# rule (a): a review focus that carries YOUR conclusion taints codex's independence.
_TAINT = re.compile(
    r"i already|already (checked|verified|confirmed|reviewed)|no (bug|issue|problem)|"
    r"looks (fine|good|correct)|should be (fine|ok|correct)|"
    r"我已|已檢查|已確認|已驗證|沒問題|應該沒|確定沒",
    re.IGNORECASE,
)

# strengthened degrade: signatures of a codex call that did NOT produce a real review
# (rate limit / auth / transport). A real review is long + structured; these are short errors.
_FAILURE_SIGNATURE = re.compile(
    r"rate.?limit|quota|usage limit|too many requests|\b429\b|stream (error|disconnected)|"
    r"unauthorized|not logged in|authentication|login required|insufficient_quota|"
    r"context length|service unavailable|\b5\d\d\b error",
    re.IGNORECASE,
)
_SHORT_MESSAGE_CHARS = 240  # a genuine review is structured + longer than a one-line error


def independence_warning(focus: str) -> Optional[str]:
    """Return a warning if the review focus smuggles in the requester's own verdict."""
    if _TAINT.search(focus or ""):
        return (
            "review focus carries your own conclusion (e.g. 'already checked / no issues'); "
            "codex must judge independently — restate it as a neutral standard / question, not "
            "your verdict"
        )
    return None


def build_prompt(focus: str, targets: Sequence[str], stdin_content: Optional[str]) -> str:
    """Independent-framing prompt: judge alone, describe-only, no edits (rules a + c)."""
    parts: List[str] = [
        "You are an independent second-opinion reviewer (a different model from whoever wrote "
        "this). Evaluate entirely on your own: assume NO prior reviewer (human or AI) checked "
        "anything; your judgment must come only from what you read yourself.",
    ]
    if targets:
        parts.append(
            "\n## Review targets (read these yourself in the read-only sandbox)\n"
            + "\n".join(f"- {t}" for t in targets)
        )
    if stdin_content:
        parts.append("\n## Inlined target content\n```\n" + stdin_content + "\n```")
    parts.append("\n## Review focus (the original request)\n" + focus)
    parts.append(
        "\n## Output rules (follow strictly)\n"
        "1. Only describe 'problem + severity (high/medium/low)'. Do not rewrite code, apply "
        "fixes, or output diffs.\n"
        "2. One finding per item: problem / location (file:line) / severity / why / your "
        "confidence.\n"
        "3. Where you judge there is no problem, say 'no finding' — do not invent issues to pad.\n"
        "4. Do not rely on or agree with any external conclusion; be faithful only to what you "
        "read yourself."
    )
    return "\n".join(parts)


def classify_outcome(
    returncode: int, final_message: str, *, timeout_code: int = 124
) -> Tuple[bool, str]:
    """Decide if a codex run is a trustworthy review or a DEGRADE. Pure; fail-closed.

    Returns (ok, reason). ok=True only on a real, non-empty, non-error review.
    """
    if returncode == timeout_code:
        return (False, "degrade:timeout — codex timed out; single opinion only, no retry")
    if returncode != 0:
        return (False, f"degrade:nonzero — codex exited {returncode} (incl. signal-killed)")
    text = (final_message or "").strip()
    if not text:
        return (False, "degrade:blank — exit 0 but the final message is empty (half-success)")
    # strengthening past the original: a short message matching a failure signature is an
    # error masquerading as a review (e.g. a rate-limit line on exit 0), not a real review.
    if len(text) <= _SHORT_MESSAGE_CHARS and _FAILURE_SIGNATURE.search(text):
        return (
            False,
            "degrade:error-signature — short message looks like a transport/quota error, not a review",
        )
    return (True, "ok")


def cross_check_reminder() -> str:
    """Rule (d): the cross-check is yours. Framed in ToneSoul's aggregation discipline."""
    return (
        "Cross-check yourself (this tool does not): split codex's findings into AGREED vs "
        "DISAGREED. A finding you BOTH reach independently is strong (E2+); a finding only one "
        "reached needs your own read of the code before you act. codex is a different model (a "
        "stronger external eye than same-model review) but still ONE opinion — 'codex agrees' "
        "raises confidence, it does not prove (claim <= evidence)."
    )


def run_codex(
    focus: str,
    *,
    targets: Sequence[str] = (),
    stdin_content: Optional[str] = None,
    workdir: str = ".",
    effort: str = "medium",
    model: Optional[str] = None,
    output_path: str,
) -> Tuple[int, str]:  # pragma: no cover - subprocess shell
    """Thin shell over `codex exec` in a READ-ONLY sandbox. Returns (returncode, final_message)."""
    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "-C",
        workdir,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "-o",
        output_path,
    ]
    if model:
        cmd += ["-m", model]
    cmd.append(build_prompt(focus, targets, stdin_content))
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        with open(output_path, encoding="utf-8") as fh:
            final_message = fh.read()
    except OSError:
        final_message = ""
    return proc.returncode, final_message


def main(argv: Optional[Sequence[str]] = None) -> int:  # pragma: no cover - thin CLI
    import argparse
    import shutil
    import sys
    import tempfile

    p = argparse.ArgumentParser(prog="codex_review", description=__doc__)
    p.add_argument("focus", help="the review focus — a neutral standard/question, NOT your verdict")
    p.add_argument(
        "--target", action="append", default=[], help="file/dir for codex to read (repeatable)"
    )
    p.add_argument("--stdin", action="store_true", help="read content to review from stdin")
    p.add_argument("--dir", default=".", help="directory codex runs in")
    p.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh"])
    p.add_argument("--model", default=None)
    args = p.parse_args(argv)

    if not args.target and not args.stdin:
        print("ERROR: need at least one --target or --stdin", file=sys.stderr)
        return 2
    warn = independence_warning(args.focus)
    if warn:
        print(f"WARNING (independence): {warn}", file=sys.stderr)
    if shutil.which("codex") is None:
        print(
            "DEGRADE: no 'codex' CLI found (not installed / broken). This is a single opinion "
            "only — note that and stop. https://developers.openai.com/codex/cli",
            file=sys.stderr,
        )
        return 3

    stdin_content = sys.stdin.read() if args.stdin else None
    out_path = tempfile.NamedTemporaryFile(suffix=".md", delete=False).name
    rc, final_message = run_codex(
        args.focus,
        targets=args.target,
        stdin_content=stdin_content,
        workdir=args.dir,
        effort=args.effort,
        model=args.model,
        output_path=out_path,
    )
    ok, reason = classify_outcome(rc, final_message)
    if not ok:
        print(f"DEGRADE: {reason}. No retry, no pretending. log={out_path}", file=sys.stderr)
        return 4
    buf = (final_message.strip() + "\n\n--- " + cross_check_reminder() + "\n").encode(
        "utf-8", errors="replace"
    )
    sys.stdout.buffer.write(buf)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
