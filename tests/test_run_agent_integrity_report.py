from __future__ import annotations

import json
from pathlib import Path

import scripts.run_agent_integrity_report as agent_integrity


def test_build_report_surfaces_embedded_hash_metadata_drift(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        agent_integrity,
        "PROTECTED_FILE_HASHES",
        {
            "AGENTS.md": "a" * 64,
            "HANDOFF.md": "b" * 64,
            "SOUL.md": "c" * 64,
        },
    )
    monkeypatch.setattr(agent_integrity, "EMBEDDED_HASH_METADATA_FILES", ("AGENTS.md",))
    monkeypatch.setattr(agent_integrity, "WATCHED_DIRS", ("skills/",))
    monkeypatch.setattr(agent_integrity, "UNAUTHORIZED_PATHS", (".agents",))

    (tmp_path / "AGENTS.md").write_text(
        "tracked\n| **Expected Hash** | `" + "d" * 64 + "` |\n",
        encoding="utf-8",
    )
    (tmp_path / "HANDOFF.md").write_text("handoff", encoding="utf-8")
    (tmp_path / "SOUL.md").write_text("soul", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / "skills" / "registry.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(agent_integrity, "check_hash_integrity", lambda repo_root: [])
    monkeypatch.setattr(agent_integrity, "check_hidden_characters", lambda repo_root: [])
    monkeypatch.setattr(agent_integrity, "check_unauthorized_paths", lambda repo_root: [])
    monkeypatch.setattr(
        agent_integrity,
        "check_embedded_hash_metadata",
        lambda repo_root: ["WARNING: embedded Expected Hash metadata drift in AGENTS.md"],
    )
    monkeypatch.setattr(
        agent_integrity,
        "check_watched_dirs",
        lambda repo_root: ["WARNING: skills/ contains 1 file(s)"],
    )

    payload = agent_integrity.build_report(tmp_path)

    assert payload["status"] == "warning"
    assert payload["summary"]["blocking_error_count"] == 0
    assert payload["summary"]["warning_count"] == 1
    assert payload["summary"]["review_warning_count"] == 1
    assert payload["primary_status_line"].startswith("agent_integrity_warning |")
    assert (
        payload["problem_route_status_line"] == "integrity | family=G1_integrity_contract_drift "
        "invariant=embedded_expected_hash_metadata "
        "repair=protected_file_documentation"
    )
    assert payload["handoff"]["queue_shape"] == "agent_integrity_guarded"
    assert payload["handoff"]["requires_operator_action"] is False
    markdown = agent_integrity.render_markdown(payload)
    assert "Agent Integrity Latest" in markdown
    assert "embedded_expected_hash_metadata" in markdown


def test_main_writes_agent_integrity_artifacts(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(agent_integrity, "_emit", lambda payload: None)
    out_dir = tmp_path / "status"
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_agent_integrity_report.py",
            "--repo-root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
    )

    exit_code = agent_integrity.main()

    assert exit_code == 0
    payload = json.loads((out_dir / agent_integrity.JSON_FILENAME).read_text(encoding="utf-8"))
    assert payload["handoff"]["queue_shape"] in {
        "agent_integrity_guarded",
        "agent_integrity_attention",
    }
    markdown = (out_dir / agent_integrity.MARKDOWN_FILENAME).read_text(encoding="utf-8")
    assert "Agent Integrity Latest" in markdown
