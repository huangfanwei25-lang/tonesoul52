"""Pin the 2026-07-02 scripts-triage retirement stubs (SystemExit convention,
cf. test_run_market_removed_scripts.py). If someone revives one of these names for a
new purpose, this test forces them to do it consciously."""

from __future__ import annotations

import importlib

import pytest

RETIRED = [
    "analyze_journal",
    "build_semantic_index",
    "calibrate_rfc013",
    "test_memory_chat",
    "ingest_handoffs",
    "fetch_moltbook",
    "test_moltbook",
    "test_delegation",
    "test_ollama",
    "generate_stress_data",
]


@pytest.mark.parametrize("name", RETIRED)
def test_retired_script_exits_with_triage_notice(name: str) -> None:
    module = importlib.import_module(f"scripts.{name}")
    with pytest.raises(SystemExit) as exc_info:
        module.main()
    assert "retired in the 2026-07-02 scripts triage" in str(exc_info.value)
    assert str(exc_info.value) == module.EXIT_MESSAGE
