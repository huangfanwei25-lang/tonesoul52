"""Tests for scripts/read_pr_review.py — the PR-review reader (Tier-2 bridge read side)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "read_pr_review", Path(__file__).resolve().parents[1] / "scripts" / "read_pr_review.py"
)
rpr = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
sys.modules[_SPEC.name] = rpr
_SPEC.loader.exec_module(rpr)


REVIEWS = [
    {
        "author": {"login": "codex"},
        "state": "CHANGES_REQUESTED",
        "body": "vow harm wording is stale",
    },
    {"author": {"login": "someone-else"}, "state": "APPROVED", "body": "lgtm"},
]
INLINE = [
    {
        "user": {"login": "codex"},
        "path": "docs/map.md",
        "line": 34,
        "body": "line 34 contradicts headline",
    },
    {"user": {"login": "bot"}, "path": "a.py", "original_line": 9, "body": "nit"},
]
COMMENTS = [
    {"author": {"login": "codex"}, "body": "overall: mergeable after 2 cleanups"},
    {"author": {"login": "Fan1234-1"}, "body": "通過"},
]


def test_author_resolution_both_shapes():
    # gh pr view uses author.login; gh api uses user.login
    assert rpr._author({"author": {"login": "x"}}) == "x"
    assert rpr._author({"user": {"login": "y"}}) == "y"
    assert rpr._author({}) == "?"


def test_filter_to_codex_only():
    out = rpr.format_review(REVIEWS, INLINE, COMMENTS, author_filter="codex")
    assert "vow harm wording is stale" in out
    assert "line 34 contradicts headline" in out
    assert "overall: mergeable" in out
    # other authors filtered out
    assert "lgtm" not in out
    assert "通過" not in out
    assert "nit" not in out


def test_inline_carries_file_and_line():
    out = rpr.format_review(REVIEWS, INLINE, COMMENTS, author_filter="codex")
    assert "docs/map.md:34" in out  # the inline location is shown


def test_inline_falls_back_to_original_line():
    out = rpr.format_review([], INLINE, [], author_filter=None)
    assert "a.py:9" in out  # original_line used when line is absent


def test_no_filter_shows_everyone():
    out = rpr.format_review(REVIEWS, INLINE, COMMENTS, author_filter=None)
    assert "lgtm" in out and "通過" in out and "vow harm wording is stale" in out


def test_empty_is_explicit_not_silent():
    out = rpr.format_review([], [], [], author_filter="codex")
    assert "no review content found" in out
    assert "codex" in out  # names the filter so an empty result is not mistaken for "no review"


def test_counts_in_headers():
    out = rpr.format_review(REVIEWS, INLINE, COMMENTS, author_filter=None)
    assert "Review summaries (2)" in out
    assert "Inline comments (2)" in out
    assert "Conversation comments (2)" in out
