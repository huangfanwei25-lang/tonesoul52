from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_save_compaction_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "save_compaction.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_save_compaction_writes_noncanonical_summary(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    payload_path = tmp_path / "payload.json"

    payload_path.write_text(
        json.dumps(
            {
                "agent": "codex",
                "session_id": "sess-101",
                "summary": "Condense the runtime state into a resumability summary.",
                "carry_forward": ["keep Aegis before mutation"],
                "pending_paths": ["scripts/gateway.py"],
                "evidence_refs": [
                    "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md"
                ],
                "council_dossier": {
                    "dossier_version": "v1",
                    "final_verdict": "approve",
                    "confidence_posture": "contested",
                    "coherence_score": 0.62,
                    "dissent_ratio": 0.35,
                    "minority_report": [
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.75,
                            "reasoning": "migration path missing",
                            "evidence": ["docs/spec.md"],
                        }
                    ],
                    "vote_summary": [
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.75,
                        }
                    ],
                    "deliberation_mode": "standard_council",
                    "change_of_position": [],
                    "evidence_refs": ["docs/spec.md"],
                    "grounding_summary": {
                        "has_ungrounded_claims": False,
                        "total_evidence_sources": 1,
                    },
                    "opacity_declaration": "partially_observable",
                },
                "next_action": "teach the next agent to read packet first",
                "source": "file",
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "save_compaction.py",
            "--input",
            str(payload_path),
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)

    assert output["agent"] == "codex"
    assert output["session_id"] == "sess-101"
    assert output["summary"].startswith("Condense the runtime state")

    saved = json.loads((tmp_path / ".aegis" / "compacted.json").read_text(encoding="utf-8"))
    assert saved[0]["agent"] == "codex"
    assert saved[0]["next_action"] == "teach the next agent to read packet first"
    assert saved[0]["council_dossier"]["confidence_posture"] == "contested"


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    returned = module._ensure_repo_root_on_path()

    assert str(returned) == repo_root
    assert sys.path[0] == repo_root
