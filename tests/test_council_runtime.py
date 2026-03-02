import uuid
from pathlib import Path

from tonesoul.council.model_registry import get_council_config
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


def test_council_runtime_includes_multi_agent_contract():
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Simple response with clear intent.",
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
    )
    verdict = runtime.deliberate(request)

    transcript = verdict.transcript or {}
    contract = transcript.get("multi_agent_contract")
    assert isinstance(contract, dict)
    assert contract.get("schema_version") == "1.0.0"
    assert isinstance(contract.get("records"), list)
    assert len(contract["records"]) == len(verdict.votes)

    validation = contract.get("validation")
    assert isinstance(validation, dict)
    assert validation.get("valid") is True


def test_council_runtime_attaches_persona_uniqueness_audit():
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Simple response with clear intent.",
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
    )
    verdict = runtime.deliberate(request)

    transcript = verdict.transcript or {}
    persona = transcript.get("persona_uniqueness")
    assert isinstance(persona, dict)
    assert "is_unique" in persona
    assert "similarity_scores" in persona
    payload = verdict.to_dict()
    assert isinstance(payload.get("persona_uniqueness_audit"), dict)
    assert isinstance(payload.get("persona_audit"), dict)


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


def test_runtime_resolve_perspective_config_defaults_to_hybrid(monkeypatch):
    monkeypatch.delenv("TONESOUL_COUNCIL_MODE", raising=False)
    runtime = CouncilRuntime()
    request = CouncilRequest(draft_output="test", context={})

    resolved = runtime._resolve_perspective_config(request)

    assert resolved == get_council_config("hybrid")


def test_runtime_resolve_perspective_config_supports_rules_alias(monkeypatch):
    monkeypatch.setenv("TONESOUL_COUNCIL_MODE", "rules")
    runtime = CouncilRuntime()
    request = CouncilRequest(draft_output="test", context={})

    resolved = runtime._resolve_perspective_config(request)

    assert resolved == get_council_config("rules")


def test_runtime_resolve_perspective_config_invalid_env_falls_back(monkeypatch):
    monkeypatch.setenv("TONESOUL_COUNCIL_MODE", "unknown_mode")
    runtime = CouncilRuntime()
    request = CouncilRequest(draft_output="test", context={})

    resolved = runtime._resolve_perspective_config(request)

    assert resolved == get_council_config("hybrid")


def test_runtime_resolve_perspective_config_respects_request_override(monkeypatch):
    monkeypatch.setenv("TONESOUL_COUNCIL_MODE", "full_llm")
    runtime = CouncilRuntime()
    custom = {"guardian": {"mode": "rules"}}
    request = CouncilRequest(
        draft_output="test",
        context={},
        perspective_config=custom,
    )

    resolved = runtime._resolve_perspective_config(request)

    assert resolved is custom


def test_runtime_resolve_perspective_config_skips_when_perspectives_explicit(monkeypatch):
    monkeypatch.setenv("TONESOUL_COUNCIL_MODE", "full_llm")
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="test",
        context={},
        perspectives=["guardian", "analyst"],
    )

    resolved = runtime._resolve_perspective_config(request)

    assert resolved is None


def test_runtime_resolve_perspective_config_with_meta_env_default(monkeypatch):
    monkeypatch.setenv("TONESOUL_COUNCIL_MODE", "rules")
    runtime = CouncilRuntime()
    request = CouncilRequest(draft_output="test", context={})

    resolved, meta = runtime._resolve_perspective_config_with_meta(request)

    assert resolved == get_council_config("rules")
    assert meta["source"] == "env_default"
    assert meta["mode"] == "rules"


def test_runtime_deliberate_attaches_council_mode_observability():
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Simple response with clear intent.",
        context={"council_mode_override": "full_llm"},
        perspective_config={"guardian": {"mode": "rules"}},
    )

    verdict = runtime.deliberate(request)
    observability = (verdict.transcript or {}).get("council_mode_observability")

    assert isinstance(observability, dict)
    assert observability.get("source") == "request_perspective_config"
    assert observability.get("mode") == "full_llm"


def test_runtime_deliberate_attaches_skill_contract_observability(monkeypatch):
    import tonesoul.council.skill_parser as skill_parser_module

    class DummyParser:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def resolve_for_request(self, *args, **kwargs):
            return [
                {
                    "skill_id": "local_llm",
                    "matched_trigger": "local llm",
                    "l3_excerpt": "Use local llm guidance payload.",
                }
            ]

    monkeypatch.setattr(skill_parser_module, "SkillContractParser", DummyParser)

    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output="Draft response.",
        user_intent="run local llm",
        context={"execution_profile": "engineering"},
    )

    verdict = runtime.deliberate(request)
    observability = (verdict.transcript or {}).get("skill_contract_observability")
    assert isinstance(observability, dict)
    assert observability.get("status") == "matched"
    assert observability.get("matched_skill_ids") == ["local_llm"]
    assert observability.get("l3_loaded_count") == 1
