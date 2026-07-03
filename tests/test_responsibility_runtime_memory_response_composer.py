from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    check_memory_claim_trace,
    compose_memory_response,
    validate_intent,
)


def _write_payload() -> dict[str, object]:
    return {
        "intent": "memory.write.propose",
        "claim": "user prefers Traditional Chinese",
        "evidence_refs": ["turn_2026_06_28_001"],
        "requested_scope": "long_term_memory",
    }


def _read_payload() -> dict[str, object]:
    return {
        "intent": "memory.read.request",
        "query": "user language preference",
        "requested_scope": "session_memory",
    }


def _enforce(payload: dict[str, object], policy: FakePolicyEngine | None = None):
    trace = InMemoryTraceStore()
    validation = validate_intent(payload)
    decision = (policy or FakePolicyEngine()).decide(validation)
    result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    return result, trace


def test_composer_appends_trace_backed_acknowledgement_for_executed_write() -> None:
    result, trace = _enforce(_write_payload())

    composed = compose_memory_response("Done with the main answer.", [result])

    assert composed.status == "composed"
    assert composed.model_claim_check.status == "no_memory_claim"
    assert len(composed.memory_surfaces) == 1
    assert composed.memory_surfaces[0].status == "memory_write_acknowledged"
    assert "Done with the main answer." in composed.text
    assert "I've saved this preference." in composed.text
    assert check_memory_claim_trace(composed.text, trace.events).status == "backed_by_trace"


def test_composer_appends_non_claim_denial_for_blocked_write() -> None:
    result, trace = _enforce(_write_payload(), FakePolicyEngine(allowed_scopes={"session_memory"}))

    composed = compose_memory_response("Done with the main answer.", [result])

    assert composed.status == "composed"
    assert len(composed.memory_surfaces) == 1
    assert composed.memory_surfaces[0].status == "memory_write_denied"
    assert "I did not save this." in composed.text
    assert check_memory_claim_trace(composed.text, trace.events).status == "no_memory_claim"


def test_composer_ignores_non_write_enforcement_results() -> None:
    result, _trace = _enforce(_read_payload())

    composed = compose_memory_response("Here is the answer.", [result])

    assert composed.status == "composed"
    assert composed.text == "Here is the answer."
    assert composed.memory_surfaces == ()


def test_composer_blocks_model_authored_memory_acknowledgement_without_trace() -> None:
    composed = compose_memory_response("I've saved your preference for future use.", [])

    assert composed.status == "blocked_model_memory_claim"
    assert "I've saved your preference" not in composed.text
    assert composed.model_claim_check.status == "unbacked_memory_claim"
    assert composed.memory_surfaces == ()


def test_composer_blocks_model_authored_acknowledgement_even_when_runtime_write_exists() -> None:
    result, _trace = _enforce(_write_payload())

    composed = compose_memory_response("I've saved your preference for future use.", [result])

    assert composed.status == "blocked_model_memory_claim"
    assert composed.memory_surfaces == ()
    assert "I've saved this preference." not in composed.text


def test_composer_does_not_trust_tampered_executed_result_for_acknowledgement() -> None:
    denied_result, trace = _enforce(
        _write_payload(), FakePolicyEngine(allowed_scopes={"session_memory"})
    )
    tampered_result = replace(denied_result, executed=True)

    composed = compose_memory_response("Done.", [tampered_result])

    assert composed.status == "composed"
    assert composed.memory_surfaces[0].status == "memory_write_denied"
    assert check_memory_claim_trace(composed.text, trace.events).status == "no_memory_claim"


def test_composer_keeps_fuzzy_memory_claim_as_known_unresolved_gap() -> None:
    composed = compose_memory_response("I'll keep that in mind next time.", [])

    assert composed.status == "composed"
    assert composed.text == "I'll keep that in mind next time."
    assert composed.model_claim_check.status == "no_memory_claim"


def test_memory_response_composer_eval_cli_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, "tools/probe/memory_response_composer_eval.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenarios: **6**" in completed.stdout
    assert "failures: **0**" in completed.stdout
