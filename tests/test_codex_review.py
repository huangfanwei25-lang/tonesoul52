"""Tests for scripts/codex_review.py — the ToneSoul external-eye (codex second-opinion) wrapper.

Covers the pure functions only (no subprocess): the independence taint-guard, the strengthened
fail-closed outcome classifier (the part that fixes the original bash template's blank-only
check), and the independent-framing prompt.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "codex_review", Path(__file__).resolve().parents[1] / "scripts" / "codex_review.py"
)
cr = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
sys.modules[_SPEC.name] = cr
_SPEC.loader.exec_module(cr)


def test_independence_warning_flags_smuggled_conclusion_en_and_zh():
    assert cr.independence_warning("I already checked the auth, just confirm it's fine")
    assert cr.independence_warning("這段我已確認沒問題,幫我再看一下")
    assert cr.independence_warning("looks correct, double-check please")


def test_independence_warning_passes_neutral_focus():
    assert (
        cr.independence_warning("Review the token check for timing attacks and write races") is None
    )
    assert cr.independence_warning("審查 evidence 驗證是否能被隱形字元繞過") is None


def test_classify_timeout_and_nonzero_degrade():
    assert cr.classify_outcome(124, "anything")[0] is False
    assert "timeout" in cr.classify_outcome(124, "anything")[1]
    assert cr.classify_outcome(1, "a real-looking long review " * 20)[0] is False
    assert "nonzero" in cr.classify_outcome(1, "x" * 500)[1]


def test_classify_blank_degrades_even_on_exit_zero():
    assert cr.classify_outcome(0, "")[0] is False
    assert cr.classify_outcome(0, "   \n  ")[0] is False
    assert "blank" in cr.classify_outcome(0, "")[1]


def test_classify_strengthened_short_error_signature_degrades():
    # the gap the original bash template missed: exit 0 + a short rate-limit error string
    ok, reason = cr.classify_outcome(0, "Error: rate limit exceeded (429). Try again later.")
    assert ok is False
    assert "error-signature" in reason
    for msg in (
        "stream error: disconnected",
        "401 unauthorized",
        "you are not logged in",
        "insufficient_quota",
    ):
        assert cr.classify_outcome(0, msg)[0] is False


def test_classify_long_real_review_mentioning_ratelimit_is_not_falsely_degraded():
    # a genuine, structured review that happens to discuss rate limiting must still pass —
    # the strengthening is conservative (short AND signature), not a blanket keyword ban
    review = (
        "Finding 1 (high): the token check at auth.py:42 is vulnerable to a timing attack; use "
        "hmac.compare_digest. Finding 2 (medium): no rate limit on the login endpoint, so "
        "credential stuffing is possible; add a 429 throttle. Finding 3 (low): the error "
        "message leaks whether the user exists. Confidence: high on 1, medium on 2."
    )
    assert len(review) > cr._SHORT_MESSAGE_CHARS
    assert cr.classify_outcome(0, review)[0] is True


def test_classify_ok_on_real_review():
    assert cr.classify_outcome(0, "Finding 1 (high): SQL injection at db.py:10. " * 5)[0] is True


def test_build_prompt_is_independent_and_describe_only():
    prompt = cr.build_prompt("Review for race conditions", ["src/a.py"], None)
    assert "independent" in prompt.lower()
    assert "do not rewrite code" in prompt.lower() or "do not rewrite" in prompt.lower()
    assert "no prior reviewer" in prompt.lower() or "assume no prior" in prompt.lower()
    assert "src/a.py" in prompt
    assert "Review for race conditions" in prompt


def test_build_prompt_inlines_stdin():
    prompt = cr.build_prompt("check this", [], "def f(): return 1/0")
    assert "1/0" in prompt


def test_cross_check_reminder_carries_aggregation_discipline():
    msg = cr.cross_check_reminder()
    assert "AGREED" in msg and "DISAGREED" in msg
    assert "claim <= evidence" in msg
    assert "one opinion" in msg.lower() or "still one" in msg.lower()
