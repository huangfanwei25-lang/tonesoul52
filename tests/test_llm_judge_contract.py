"""Parser / label-extraction contract for the LLM-judge sensors (offline).

`scripts/llm_judge.py` is the fail-closed parser every sensor-honesty experiment
rides on, and it shipped with zero test coverage. These tests pin its OBSERVABLE
label-extraction contract by monkeypatching the single `_generate` seam, so they
run in CI with no Ollama and no network.

Scope honesty: this pins the PARSER (how raw model text maps to a score/verdict),
NOT judge correctness (whether the real model emits clean labels — that stays at
local-eval evidence). It also pins the "never fake a verdict" contract: if the
model call raises, the public functions must propagate, not return a default.
"""

from __future__ import annotations

import urllib.error

import pytest

from scripts import llm_judge


def _canned(value: str):
    def _fake(prompt: str, model: str, timeout: float = 90.0) -> str:
        return value

    return _fake


# ── truth_score: TRUE -> 1.0, UNCERTAIN -> 0.5, FALSE -> 0.0 ──────────────────


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("TRUE", 1.0),
        ("FALSE", 0.0),
        ("UNCERTAIN", 0.5),
        ("true", 1.0),  # case-insensitive (.strip().upper())
        ("  TRUE  ", 1.0),  # whitespace tolerated
        ("The answer is TRUE.", 1.0),  # substring extraction
        ("???", 0.5),  # unparseable -> uncertain, not a silent pass
        ("", 0.5),
    ],
)
def test_truth_score_label_extraction(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: float
) -> None:
    monkeypatch.setattr(llm_judge, "_generate", _canned(raw))
    assert llm_judge.truth_score("any statement") == expected


def test_truth_score_false_takes_precedence_over_true(monkeypatch: pytest.MonkeyPatch) -> None:
    # The parser checks FALSE before TRUE; a hedged "TRUE or FALSE" resolves to FALSE.
    monkeypatch.setattr(llm_judge, "_generate", _canned("TRUE or FALSE"))
    assert llm_judge.truth_score("x") == 0.0


# ── is_safe: HARMFUL -> False, SAFE -> True, anything else -> fail-closed ─────


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("SAFE", True),
        ("HARMFUL", False),
        ("safe", True),  # case-insensitive
        ("This is HARMFUL content.", False),  # substring extraction
        ("garbled output", False),  # unparseable -> fail-closed
        ("", False),
    ],
)
def test_is_safe_label_extraction(
    monkeypatch: pytest.MonkeyPatch, raw: str, expected: bool
) -> None:
    monkeypatch.setattr(llm_judge, "_generate", _canned(raw))
    assert llm_judge.is_safe("any text") is expected


def test_is_safe_harmful_takes_precedence_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # HARMFUL is checked before SAFE; ambiguous output must fail closed (unsafe).
    monkeypatch.setattr(llm_judge, "_generate", _canned("Mostly SAFE but HARMFUL in parts"))
    assert llm_judge.is_safe("x") is False


# ── never fake a verdict: model errors must propagate, not default ────────────


def test_truth_score_propagates_model_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(prompt: str, model: str, timeout: float = 90.0) -> str:
        raise RuntimeError("model unreachable")

    monkeypatch.setattr(llm_judge, "_generate", _boom)
    with pytest.raises(RuntimeError):
        llm_judge.truth_score("x")


def test_is_safe_propagates_model_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(prompt: str, model: str, timeout: float = 90.0) -> str:
        raise RuntimeError("model unreachable")

    monkeypatch.setattr(llm_judge, "_generate", _boom)
    with pytest.raises(RuntimeError):
        llm_judge.is_safe("x")


# ── available(): probe truthiness without raising ────────────────────────────


def test_available_true_when_model_responds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_judge, "_generate", _canned("ok"))
    assert llm_judge.available() is True


def test_available_false_when_model_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(prompt: str, model: str, timeout: float = 90.0) -> str:
        raise urllib.error.URLError("no server")

    monkeypatch.setattr(llm_judge, "_generate", _boom)
    assert llm_judge.available() is False
