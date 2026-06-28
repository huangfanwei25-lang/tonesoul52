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
    PolicyDecision,
    RecordingMemoryAdapter,
    check_memory_claim_trace,
    render_memory_write_result,
    request_id_for_intent,
    validate_intent,
)


def _write_payload() -> dict[str, object]:
    return {
        "intent": "memory.write.propose",
        "claim": "user prefers Traditional Chinese",
        "evidence_refs": ["turn_2026_06_28_001"],
        "requested_scope": "long_term_memory",
    }


def test_memory_output_surface_acknowledges_only_executed_memory_write_trace() -> None:
    trace = InMemoryTraceStore()
    validation = validate_intent(_write_payload())
    decision = FakePolicyEngine().decide(validation)
    result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )

    rendered = render_memory_write_result(result)

    assert rendered.status == "memory_write_acknowledged"
    assert rendered.claim_check_status == "backed_by_trace"
    assert rendered.request_id == result.request_id
    assert rendered.trace_seq == result.trace_event.seq
    assert "I've saved this preference." in rendered.text
    assert check_memory_claim_trace(rendered.text, trace.events).status == "backed_by_trace"


def test_memory_output_surface_denies_without_memory_claim_when_policy_blocks() -> None:
    trace = InMemoryTraceStore()
    adapter = RecordingMemoryAdapter()
    validation = validate_intent(_write_payload())
    decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    result = Enforcer(memory_adapter=adapter, trace_store=trace).enforce(validation, decision)

    rendered = render_memory_write_result(result)

    assert adapter.call_count == 0
    assert rendered.status == "memory_write_denied"
    assert rendered.claim_check_status == "no_memory_claim"
    assert "I did not save this." in rendered.text
    assert check_memory_claim_trace(rendered.text, trace.events).status == "no_memory_claim"


def test_memory_output_surface_does_not_acknowledge_non_write_intent() -> None:
    trace = InMemoryTraceStore()
    validation = validate_intent(
        {
            "intent": "memory.read.request",
            "query": "user language preference",
            "requested_scope": "session_memory",
        }
    )
    decision = FakePolicyEngine().decide(validation)
    result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )

    rendered = render_memory_write_result(result)

    assert rendered.status == "not_memory_write"
    assert rendered.claim_check_status == "no_memory_claim"
    assert "No memory write was requested." in rendered.text


def test_memory_output_surface_does_not_trust_tampered_result_executed_flag() -> None:
    trace = InMemoryTraceStore()
    validation = validate_intent(_write_payload())
    decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    denied_result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    tampered_result = replace(denied_result, executed=True)

    rendered = render_memory_write_result(tampered_result)

    assert rendered.status == "memory_write_denied"
    assert rendered.claim_check_status == "no_memory_claim"


def test_memory_output_surface_sanitizes_denial_reason() -> None:
    trace = InMemoryTraceStore()
    validation = validate_intent(_write_payload())
    decision = PolicyDecision.deny_action(
        intent="memory.write.propose",
        requested_scope="long_term_memory",
        request_id=request_id_for_intent(validation.normalized_payload),
        reason="blocked\n| injected | table |\twith control chars",
        policy_id="test.policy",
    )
    result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )

    rendered = render_memory_write_result(result)

    assert "\n" not in rendered.text
    assert "\t" not in rendered.text
    assert "blocked | injected | table | with control chars" in rendered.text
    assert rendered.claim_check_status == "no_memory_claim"


def test_memory_output_surface_eval_cli_runs_from_repo_root() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        [sys.executable, "tools/probe/memory_output_surface_eval.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "scenarios: **4**" in completed.stdout
    assert "failures: **0**" in completed.stdout
