from __future__ import annotations

import json
from pathlib import Path

import scripts.skill_topology as topology


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_build_topology_collects_imports_and_skill_mentions(tmp_path: Path) -> None:
    _write(
        tmp_path / "tonesoul" / "tension_engine.py",
        "from tonesoul import resonance\n",
    )
    _write(
        tmp_path / "tonesoul" / "resonance.py",
        "VALUE = 1\n",
    )
    _write(
        tmp_path / ".agent" / "skills" / "sample_skill" / "SKILL.md",
        (
            "---\n"
            "name: sample_skill\n"
            "description: sample\n"
            "---\n\n"
            "Use `tonesoul/tension_engine.py` in this skill.\n"
        ),
    )
    _write(
        tmp_path / ".agent" / "workflows" / "pipeline.md",
        "---\ndescription: sample workflow\n---\n\n# Workflow\n",
    )

    payload = topology.build_topology(
        root=tmp_path / "tonesoul",
        skills_dir=tmp_path / ".agent" / "skills",
        workflows_dir=tmp_path / ".agent" / "workflows",
    )

    node_ids = {node["id"] for node in payload["nodes"]}
    assert "tonesoul.tension_engine" in node_ids
    assert "tonesoul.resonance" in node_ids
    assert "skill:sample_skill" in node_ids
    assert "workflow:pipeline" in node_ids

    links = {(link["source"], link["target"], link["type"]) for link in payload["links"]}
    assert ("tonesoul.tension_engine", "tonesoul.resonance", "import") in links
    assert ("skill:sample_skill", "tonesoul.tension_engine", "mentions") in links


def test_main_writes_json_and_mermaid_outputs(tmp_path: Path, monkeypatch, capsys) -> None:
    _write(tmp_path / "tonesoul" / "a.py", "from tonesoul import b\n")
    _write(tmp_path / "tonesoul" / "b.py", "VALUE = 1\n")
    _write(
        tmp_path / ".agent" / "skills" / "sample" / "SKILL.md",
        "---\nname: sample\ndescription: sample\n---\n",
    )
    _write(
        tmp_path / ".agent" / "workflows" / "w.md",
        "---\ndescription: workflow\n---\n",
    )
    monkeypatch.chdir(tmp_path)

    exit_code = topology.main(["--format", "json"])
    assert exit_code == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["meta"]["node_count"] >= 4

    json_path = tmp_path / "docs" / "status" / "skill_topology.json"
    mermaid_path = tmp_path / "docs" / "status" / "skill_topology.mmd"
    assert json_path.exists()
    assert mermaid_path.exists()

    exit_code = topology.main(["--format", "mermaid"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("graph TD")
