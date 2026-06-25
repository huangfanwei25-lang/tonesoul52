"""Tests for the PR preflight guard's pure scope-assessment logic."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "pr_preflight", Path(__file__).resolve().parents[1] / "scripts" / "pr_preflight.py"
)
pr_preflight = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(pr_preflight)

extract_agent_trailer = pr_preflight.extract_agent_trailer
assess_scope = pr_preflight.assess_scope


def test_extract_agent_trailer_present():
    msg = "docs: thing\n\nbody\n\nAgent: claude-opus-4-8\nTrace-Topic: x\n"
    assert extract_agent_trailer(msg) == "claude-opus-4-8"


def test_extract_agent_trailer_absent():
    assert extract_agent_trailer("docs: thing\n\nno trailer here\n") is None


def test_extract_agent_trailer_last_wins_and_case_insensitive():
    msg = "feat\n\nagent: codex-1\n\nmore\n\nAgent: claude-opus-4-8\n"
    assert extract_agent_trailer(msg) == "claude-opus-4-8"


def test_assess_scope_clean_single_agent():
    r = assess_scope(["a.md", "b.md"], ["claude-opus-4-8"])
    assert r["ok"] is True
    assert r["file_count"] == 2
    assert r["warnings"] == []


def test_assess_scope_flags_stacked_branch():
    # This is the PR #188 failure: two agents' commits on one branch.
    r = assess_scope(
        ["docs/x.md", "tonesoul/reviewer/report.py"],
        ["claude-opus-4-8", "codex-claim-evidence"],
    )
    assert r["ok"] is False
    assert any("STACKED" in w for w in r["warnings"])
    assert r["distinct_agents"] == ["claude-opus-4-8", "codex-claim-evidence"]


def test_assess_scope_flags_missing_attribution():
    r = assess_scope(["a.md"], [None])
    assert r["ok"] is False
    assert any("Agent: trailer" in w for w in r["warnings"])


def test_assess_scope_flags_github_mismatch():
    r = assess_scope(["a.md", "b.md"], ["claude-opus-4-8"], gh_files=["a.md"])
    assert r["ok"] is False
    assert any("GitHub-reported" in w for w in r["warnings"])


def test_assess_scope_clean_when_github_matches():
    r = assess_scope(["a.md", "b.md"], ["claude-opus-4-8"], gh_files=["b.md", "a.md"])
    assert r["ok"] is True
    assert r["warnings"] == []


def test_git_capture_uses_utf8_with_replacement_errors(monkeypatch):
    calls = []

    class Result:
        stdout = "ok\n"

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return Result()

    monkeypatch.setattr(pr_preflight.subprocess, "run", fake_run)

    assert pr_preflight._git("log", "--oneline") == "ok"
    kwargs = calls[0][1]
    assert kwargs["encoding"] == "utf-8"
    assert kwargs["errors"] == "replace"
