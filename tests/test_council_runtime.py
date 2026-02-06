import uuid
from pathlib import Path

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime
from tonesoul.council.self_journal import load_recent_memory


def _journal_path() -> Path:
    base = Path("temp") / "pytest-runtime-journal"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"journal-{uuid.uuid4().hex}.jsonl"


def test_council_runtime_includes_genesis_fields():
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Simple response with clear intent.",
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
    )
    verdict = runtime.deliberate(request)

    assert verdict.genesis is not None
    assert verdict.responsibility_tier in {"TIER_1", "TIER_2", "TIER_3"}
    assert verdict.intent_id
    assert isinstance(verdict.transcript, dict)
    assert verdict.transcript.get("genesis")
    assert verdict.transcript.get("responsibility_tier")
    assert verdict.transcript.get("intent_id")


def test_council_runtime_attaches_role_summary():
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Another simple response.",
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
        role_summary={"governance_roles": ["guardian"]},
        role_catalog={"governance_roles": {"guardian": {"level": 2}}},
    )
    verdict = runtime.deliberate(request)

    assert isinstance(verdict.transcript, dict)
    role_summary = verdict.transcript.get("role_council")
    assert isinstance(role_summary, dict)
    assert role_summary.get("decision_status") in {"pass", "attention", "block"}


def test_council_runtime_handles_provenance_write_error(monkeypatch):
    import tonesoul.council.runtime as runtime_module

    class DummyManager:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def add_record(self, *args, **kwargs) -> None:
            raise RuntimeError("provenance failed")

    monkeypatch.setattr(runtime_module, "ProvenanceManager", DummyManager)

    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Simple response for provenance error handling.",
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
    )
    verdict = runtime.deliberate(request)

    assert isinstance(verdict.transcript, dict)
    assert "isnad_write_error" in verdict.transcript


def test_council_runtime_auto_record_contains_genesis_metadata():
    runtime = CouncilRuntime()
    journal_path = _journal_path()
    request = CouncilRequest(
        draft_output="kill instruction",
        context={
            "record_self_memory": str(journal_path),
            "tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0},
        },
        user_intent="ask",
    )
    runtime.deliberate(request)

    entries = load_recent_memory(limit=5, path=journal_path)
    assert len(entries) == 1
    latest = entries[0]
    assert latest.get("genesis") is not None
    assert latest.get("responsibility_tier") in {"TIER_1", "TIER_2", "TIER_3"}
    assert latest.get("intent_id")
